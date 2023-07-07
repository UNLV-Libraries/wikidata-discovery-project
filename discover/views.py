from django.shortcuts import render
from . import graph
from . import web_methods
from .models import Subject
from .wd_utils import catch_err
from django.db.models import QuerySet
from .enums import RelColor, Facet
from . import queue_mgr


def home(request):
    from .web_methods import get_chart

    chart_io_dict = get_chart('stats_instanceof_count')
    chart_subj_dict = get_chart('stats_subjects_count')
    context = {'chart_io_labels': chart_io_dict['labels'], 'chart_io_data': chart_io_dict['data'],
               'chart_subj_labels': chart_subj_dict['labels'], 'chart_subj_data': chart_subj_dict['data']}
    return render(request, 'discover/base_home.html', context)


def process_search(request):
    """Processes and renders search results for all facets.
    Callable by search form, node-select form, subject forms, and queue form."""
    from .forms import QueueForm, SearchForm, NodeSelectForm, RestrictSubjectForm, BackButtonForm

    # construct file path for rendering result template
    url_path = request.path[1:request.path.__len__() - 1]
    file_path = url_path.split('/')
    final_path = file_path[0] + '/base_' + file_path[1] + '.html'
    error_msg = ''
    curr_facet = ''
    bypass_large_graph = 0
    bypass_queue = False

    try:
        # check if queue form has been used to submit a prior search; run appropriate request setup.
        rtn_qform = QueueForm(request.POST,
                              dynamic_choices=queue_mgr.get_queue_list(request.session.session_key))
        if rtn_qform.is_valid():
            pos = rtn_qform.cleaned_data['run_qry']
            q_item = queue_mgr.get_queue_entry(pos, request.session.session_key)
            curr_facet = q_item['form_vals']['facet']
            final_path = get_prior_template_path(curr_facet)
            curr_request = queue_mgr.create_request(request.session.session_key, pos, bypass_queue)
        else:
            curr_request = request

        # check to see if back button used on item details page; reload most recent search result.
        bbf = BackButtonForm(curr_request.POST)
        if bbf.is_valid():
            bypass_queue = True
            bypass_large_graph = 1
            curr_request = queue_mgr.create_request(request.session.session_key, 'top', bypass_queue)

        # attempt to hydrate all search forms based on POST data. Only one will be valid.
        rtn_search_frm = SearchForm(curr_request.POST)
        curr_facet = rtn_search_frm['facet'].value()  # grab facet val off search form pre-validation
        if curr_facet == Facet.subjs.value:  # subject form has called this process_search
            curr_facet = Facet.colls.value
        the_checks = [get_default_rel_type(curr_facet)]
        rtn_node_frm = NodeSelectForm(curr_request.POST,
                                      dynamic_choices=set_relation_types(curr_facet))
        rtn_subject_frm = RestrictSubjectForm(curr_request.POST)

        # variables to track previous search values used on search, subject, or node forms.
        # set all to 'empty'; logic below fills fields for kw, subject, or node, depending on case.
        prior_kw_search = ''
        prior_node_search = ''
        prior_node_label = ''
        prior_color = ''
        prior_subj_search = ''
        prior_subj_label = ''

        # find valid form and process
        if rtn_search_frm.is_valid():
            prior_kw_search = rtn_search_frm.cleaned_data['search_text']
            qry = set_query(curr_facet)
            if not bypass_queue:
                queue_mgr.update_queue('search', rtn_search_frm, request.session.session_key)
            results = process_search_form(rtn_search_frm, qry, the_checks)
            the_checks = results['choices']  # all downstream relation type variables must be iterable.
            graph_data = graph.load_graph(results['filtered'], the_checks, curr_facet)
        elif rtn_subject_frm.is_valid():
            qry = set_query(Facet.colls.value)  # subject form used only for collections at present.
            if not bypass_queue:
                queue_mgr.update_queue('subject', rtn_subject_frm, request.session.session_key)
            results = process_restrictsubj_form(rtn_subject_frm, qry)
            the_checks = results['choices']
            graph_data = graph.load_graph(results['filtered'], the_checks, curr_facet)
        elif rtn_node_frm.is_valid():
            if rtn_node_frm.cleaned_data['node_id'] == '':  # node hasn't been clicked, just change in rel types
                if not rtn_node_frm.cleaned_data['prior_subj_search'] == '':  # descended from subj search
                    prior_subj_search = rtn_node_frm.cleaned_data['prior_subj_search']
                    prior_subj_label = rtn_node_frm.cleaned_data['prior_subj_labels']
                elif not rtn_node_frm.cleaned_data['prior_kw_search'] == '':  # descended from kw search
                    prior_kw_search = rtn_node_frm.cleaned_data['prior_kw_search']  # maintain last keyword search ref
                else:  # descended from a prior node search
                    prior_node_search = rtn_node_frm.cleaned_data['prior_node_search']
                    prior_node_label = rtn_node_frm.cleaned_data['prior_node_label']  # maintain prior label
                    prior_color = rtn_node_frm.cleaned_data['prior_color']  # maintain last color ref
            else:  # node was just clicked
                # The prior query will now be a node query, not a keyword or subject query.
                # See graph_functions.js::selectNode.
                prior_node_search = rtn_node_frm.cleaned_data['node_id']  # set last node search val
                prior_node_label = rtn_node_frm.cleaned_data['node_label']  # maintain prior label
                prior_color = rtn_node_frm.cleaned_data['color_type']  # maintain prior color
            qry = set_query(curr_facet)
            if not bypass_queue:
                queue_mgr.update_queue('node', rtn_node_frm, request.session.session_key)
            results = process_node_form(rtn_node_frm, qry, request.session.session_key)
            the_checks = results['choices']
            graph_data = graph.load_graph(results['filtered'], the_checks, curr_facet)
        else:
            # creates empty objects for form rendering w/o awkward error handling.
            results = process_invalid_forms('people_filtered')
            error_msg = results['message']
            graph_data = graph.load_graph(results['filtered'], the_checks, curr_facet)

        # new forms to pass to people_filtered
        nsform = NodeSelectForm(initial={'facet': curr_facet, 'prior_kw_search': prior_kw_search,
                                         'prior_color': prior_color, 'prior_node_label': prior_node_label,
                                         'prior_node_search': prior_node_search,
                                         'prior_subj_search': prior_subj_search,
                                         'prior_subject_labels': prior_subj_label},
                                dynamic_choices=set_relation_types(curr_facet))
        sform = SearchForm(initial={'facet': curr_facet, 'relation_type': get_default_rel_type(curr_facet)})
        qform = QueueForm(initial={'facet': curr_facet},
                          dynamic_choices=queue_mgr.get_queue_list(request.session.session_key))

        context = {'facet': curr_facet, 'unique_list': results['unique'], 'search': sform, 'priors': qform,
                   'num': results['num'], 'nodes': graph_data['nodes'], 'edges': graph_data['edges'],
                   'select': nsform, 'properties': graph_data['properties'], 'bypass_lg_graph': bypass_large_graph,
                   'string': results['search_str'], 'checks': the_checks, 'errors': error_msg}

        return render(request, final_path, context)

    except Exception as e:
        errors = catch_err(e, 'views.search_processed')
        context = {'errors': errors}
        return render(request, get_prior_template_path(curr_facet), context)


def people(request):
    from . import forms
    from .web_methods import get_images
    from .enums import Facet

    # initialize session for queue management
    init_session(request)
    relation = get_default_rel_type(Facet.people.value)
    sf = forms.SearchForm(initial={'facet': Facet.people.value, 'relation_type': relation})
    qf = forms.QueueForm(initial={'facet': Facet.people.value},
                         dynamic_choices=queue_mgr.get_queue_list(request.session.session_key))
    images = get_images('images_humans')  # record name in db query table
    context = {'search': sf, 'images': images, 'priors': qf}
    return render(request, 'discover/base_people.html', context)


def corpbodies(request):
    from . import forms
    from .web_methods import get_images
    from .enums import Facet

    # initialize session for queue management
    init_session(request)
    relation = get_default_rel_type(Facet.corps.value)
    sf = forms.SearchForm(initial={'facet': Facet.corps.value, 'relation_type': relation})
    qf = forms.QueueForm(initial={'facet': Facet.corps.value},
                         dynamic_choices=queue_mgr.get_queue_list(request.session.session_key))
    images = get_images('images_others')  # record name in db query table
    context = {'search': sf, 'images': images, 'priors': qf}
    return render(request, 'discover/base_corps.html', context)


def collections(request):
    from . import forms
    from .enums import Facet

    # initialize session for queue management
    init_session(request)
    relation = get_default_rel_type(Facet.colls.value)
    sf = forms.SearchForm(initial={'facet': Facet.colls.value, 'relation_type': relation})
    qf = forms.QueueForm(initial={'facet': Facet.colls.value},
                         dynamic_choices=queue_mgr.get_queue_list(request.session.session_key))
    # images = get_images('images_others')  # record name in db query table
    context = {'search': sf, 'priors': qf}
    return render(request, 'discover/base_collections.html', context)


def oralhistories(request):
    from . import forms

    # initialize session for queue management
    init_session(request)
    relation = get_default_rel_type(Facet.orals.value)
    sf = forms.SearchForm(initial={'facet': Facet.orals.value, 'relation_type': relation})
    qf = forms.QueueForm(initial={'facet': Facet.orals.value},
                         dynamic_choices=queue_mgr.get_queue_list(request.session.session_key))
    # images = get_images('images_others')  # record name in db query table
    context = {'search': sf, 'priors': qf}
    return render(request, 'discover/base_orals.html', context)


def subjects(request):
    from . import forms

    init_session(request)
    sf = forms.SearchForm(initial={'facet': Facet.subjs.value, 'relation_type': 'none'})
    context = {'search': sf}
    return render(request, 'discover/base_subjects.html', context)


def subjects_filtered(request):
    from .forms import SearchForm, RestrictSubjectForm

    try:
        sf = SearchForm(initial={'facet': Facet.subjs.value, 'relation_type': 'none'})
        rf = RestrictSubjectForm(initial={'facet': Facet.subjs.value})
        return_sf = SearchForm(request.POST)
        if return_sf.is_valid():
            subjs = Subject.objects.all().filter(subjectlabel__icontains=return_sf.cleaned_data['search_text'])
            search_string = return_sf.cleaned_data['search_text']
            context = {'subjects': subjs, 'search': sf, 'search_string': search_string, 'restrict': rf}
            return render(request, 'discover/base_subjects_filtered.html', context)
        else:
            return render(request, 'discover/base_subjects_filtered.html')
    except Exception as e:
        errors = catch_err(e)
        context = {'errors': errors}
        return render(request, 'discover/base_subjects_filtered.html', context)


def item(request, item_code, facet):
    from .forms import BackButtonForm

    bb_form = BackButtonForm()
    details = web_methods.get_item_details(item_code)
    the_facet = facet
    the_item = details[0]
    context = {'details': details, 'item': the_item.item_label, 'itemdesc': the_item.item_desc,
               'bb_form': bb_form, 'facet': the_facet}
    return render(request, 'discover/base_item.html', context)


def utilities(request):
    from . import db
    from .forms import WikiLoadForm

    msgs = ""
    val = ''
    nf = WikiLoadForm()
    cf = WikiLoadForm(request.POST)
    if cf.is_valid():
        val = cf.cleaned_data['run_it']
    if val == '1':
        n = db.cache_collections()
        msgs += str(n[0]) + " of " + str(n[1]) + " collection records cached." + '\n'
        n = db.cache_corp_bodies()
        msgs += str(n[0]) + " of " + str(n[1]) + " corp bodies records cached." + '\n'
        n = db.cache_oral_histories()
        msgs += str(n[0]) + " of " + str(n[1]) + " oral histories records cached." + '\n'
        n = db.cache_people()
        msgs += str(n[0]) + " of " + str(n[1]) + " people records cached." + '\n'
        n = db.cache_subjects()
        msgs += str(n[0]) + " of " + str(n[1]) + " subject records cached." + '\n'
    elif val == '2':
        n = db.cache_people()
        msgs += str(n[0]) + " of " + str(n[1]) + " people records cached." + '\n'
    elif val == '3':
        n = db.cache_corp_bodies()
        msgs += str(n[0]) + " of " + str(n[1]) + " corp bodies records cached." + '\n'
    elif val == '4':
        n = db.cache_collections()
        msgs += str(n[0]) + " of " + str(n[1]) + " collection records cached." + '\n'
    elif val == '5':
        n = db.cache_oral_histories()
        msgs += str(n[0]) + " of " + str(n[1]) + " oral histories records cached." + '\n'
    elif val == '6':
        n = db.cache_subjects()
        msgs += str(n[0]) + " of " + str(n[1]) + " subject records cached." + '\n'

    context = {'form': nf, 'messages': msgs}
    return render(request, 'discover/base_utilities.html', context)


def about(request):
    from wikidataDiscovery import settings
    ver = settings.APP_VERSION
    auth = settings.APP_AUTHOR
    email = settings.APP_EMAIL
    contact = settings.APP_CONTACT
    contact_email = settings.APP_CONTACT_EMAIL
    context = {'version': ver, 'author': auth, 'email': email, 'contact': contact, 'contact_email': contact_email}
    return render(request, 'discover/base_about.html', context)


def process_search_form(sform, qset, rel_type_list):
    """Private function for form processing. Generic form handler for all views
    that use the search form. Initiates new search workflow for any query set."""
    from django.db.models import Q
    from .web_methods import reduce_search_results

    the_facet = sform.cleaned_data['facet']
    rel_type_str = rel_type_list[0]
    if rel_type_str == 'instanceof':  # instanceof label is jargon
        rel_type_str = 'category'

    if the_facet == Facet.colls.value:  # a temporary hack; to be replaced by faceted filtering tool.
        filtset = qset.filter(Q(itemdesc__icontains=sform.cleaned_data['search_text']) |
                              Q(itemlabel__icontains=sform.cleaned_data['search_text']) |
                              Q(colltypelabel__icontains=sform.cleaned_data['search_text']))
    else:
        filtset = qset.filter(Q(itemdesc__icontains=sform.cleaned_data['search_text']) |
                              Q(itemlabel__icontains=sform.cleaned_data['search_text']))

    uniqueset = reduce_search_results(filtset, the_facet)

    num = uniqueset.__len__()
    the_string = "'" + sform.cleaned_data['search_text'] + "' + " + rel_type_str
    return {'filtered': filtset, 'unique': uniqueset, 'num': num,
            'search_str': the_string, 'choices': rel_type_list}


def process_node_form(nsform, qset, session_key):
    """Handles node form processing using any query set, a given facet,
    and all relation type checkboxes selected by the user."""
    # generic node selection form handler for all views that use it
    from .web_methods import reduce_search_results
    from django.db.models import Q

    # get selected checkboxes for relation types in graph; grab other needed values
    the_choices = nsform.cleaned_data['relation_types']
    choices_temp = ''
    for c in the_choices:
        if c == 'instanceof':  # replace jargon
            c = 'category'
        choices_temp += c + '|'
    choices_str = choices_temp[:choices_temp.__len__() - 1]
    the_facet = nsform.cleaned_data['facet']

    # filter acc to unique node, based on color type.
    # User may have NOT selected a node but only changed relation type options.
    if not nsform.cleaned_data['node_id'] == '':  # user selected a node; new query.
        the_label = nsform.cleaned_data['node_label']
        filtset = set_node_query(nsform, qset)
    else:  # node frm is descendent of one of three search forms: search, subject, or a prev node.
        mid_req = queue_mgr.get_queue_entry('middle', session_key)  # get prior search request
        if mid_req['form_type'] == 'search':
            string_to_use = mid_req['form_vals']['search_text']  # use the current search text
            the_label = string_to_use
            filtset = qset.filter(Q(itemdesc__icontains=string_to_use) |
                                  Q(itemlabel__icontains=string_to_use))
        elif mid_req['form_type'] == 'subject':
            the_label = mid_req['form_vals']['restrict_labels']
            filtset = qset.filter(subject_id__in=mid_req['form_vals']['restrict_text'])
        else:  # current form is descended form another node form; use 'prior_' fields.
            if not mid_req['form_vals']['prior_subj_search'] == '':
                the_label = mid_req['form_vals']['prior_subj_labels']
                filtset = qset.filter(subject_id__in=mid_req['form_vals']['prior_subj_search'])
            elif not mid_req['form_vals']['prior_kw_search'] == '':
                search_str = mid_req['form_vals']['prior_kw_search']
                the_label = search_str
                filtset = qset.filter(Q(itemdesc__icontains=search_str) |
                                      Q(itemlabel__icontains=search_str))
            else:
                the_label = mid_req['form_vals']['prior_node_label']
                filtset = set_node_query(nsform, qset)

    uniqueset = reduce_search_results(filtset, the_facet)
    num = uniqueset.__len__()
    total_label = "'" + the_label + "' + " + choices_str

    return {'filtered': filtset, 'unique': uniqueset, 'num': num,
            'search_str': total_label, 'choices': the_choices}


def process_restrictsubj_form(rsform, qset):
    """Private function for form processing."""
    # Posted from the Subjects page only. Processed by subjects_filtered and corp_filtered.
    from .web_methods import reduce_search_results

    qcodes = rsform.cleaned_data['restrict_text'].split(',')
    qcodes.remove('')  # remove empty member that causes trailing comma
    search_str = rsform.cleaned_data['restrict_labels'].split(',')
    search_str.remove('')

    filtset = qset.filter(subject_id__in=qcodes)
    uniqueset = reduce_search_results(filtset, Facet.colls.value)
    num = uniqueset.__len__()
    choice = get_default_rel_type(Facet.colls.value)  # subject form only supports collection results.
    return {'filtered': filtset, 'unique': uniqueset, 'num': num,
            'choices': [choice], 'search_str': str(search_str)}


def process_invalid_forms(the_form):
    from django.db.models.query import QuerySet
    filterset = QuerySet()
    uniqueset = QuerySet()
    num = 0
    search_str = ''
    if the_form == 'people_filtered':
        the_msg = "There was a problem with the search service."
    elif the_form == 'corpbodies_filtered':
        the_msg = "There was a problem with the search service for Corporate Bodies."
    elif the_form == 'collections_filtered':
        the_msg = "There was a problem with the search service for Collections."
    else:
        the_msg = "There was a problem with the search service for Oral Histories."

    return {'filtered': filterset, 'unique': uniqueset, 'num': num, 'search_str': search_str, 'message': the_msg}


def set_node_query(nsform, qset):
    """Used by process node form. Is separate because it may be called
    twice during node form processing."""
    if nsform.cleaned_data['node_id'] == '':
        the_id = nsform.cleaned_data['prior_node_search']
        the_color = nsform.cleaned_data['prior_color']
    else:
        the_id = nsform.cleaned_data['node_id']
        the_color = nsform.cleaned_data['color_type']

    if the_color == RelColor.item.value:
        filtset = qset.filter(item_id__exact=the_id).order_by('item_id')
    elif the_color == RelColor.occup.value:
        filtset = qset.filter(occupation_id__exact=the_id)
    elif the_color == RelColor.fow.value:
        filtset = qset.filter(fieldofwork_id__exact=the_id)
    elif the_color == RelColor.pob.value:
        filtset = qset.filter(placeofbirth_id__exact=the_id)
    elif the_color == RelColor.pod.value:
        filtset = qset.filter(placeofdeath_id__exact=the_id)
    elif the_color == RelColor.subj.value:
        filtset = qset.filter(subject_id__exact=the_id)
    elif the_color == RelColor.instanceof.value:
        filtset = qset.filter(instanceof_id__exact=the_id)
    else:
        filtset = QuerySet()

    return filtset


def set_relation_types(facet: str) -> list:
    """Creates list for relation type options on the node form."""
    from .models import RelationType

    the_set = RelationType.objects.filter(domain=facet)
    rel_types = []
    for r in the_set:
        rel_types.append((r.relation_type, r.relation_type_label))
    return rel_types


def process_choices(choices: list, facet) -> dict:
    """Used with returned node form to create a list of selected relationship
    types and a corresponding search string label. Called prior to process node form."""
    from .models import RelationType
    # get checkbox select order for domain from db; gets applied on template render
    fac = RelationType.objects.filter(domain=facet)
    choice_sel = []
    alt_str = ''
    for c in choices:
        o = fac.get(relation_type=c)
        if o:
            choice_sel.append(o.list_order)
            alt_str += o.relation_type_label + ' + '
    total_str = '' + ": " + alt_str.rstrip(' + ')

    return {'checks': choice_sel, 'search_str': total_str}


def set_query(facet):
    """Returns the needed queryset objected based on the
    facet value of the form being processed in search_processed"""
    from . import models
    if facet == Facet.people.value:
        qry = models.Person.objects.all()
    elif facet == Facet.corps.value:
        qry = models.CorpBody.objects.all()
    elif facet == Facet.colls.value:
        qry = models.Collection.objects.all()
    elif facet == Facet.orals.value:
        qry = models.OralHistory.objects.all()
    elif facet == Facet.subjs.value:  # this domain is used to find results in collections only.
        qry = models.Collection.objects.all()
    else:
        qry = QuerySet()

    return qry


def get_default_rel_type(facet):
    """Returns the top-of-list relation type for a given facet."""
    from .models import RelationType
    check_set = RelationType.objects.get(domain=facet, list_order=0)
    return check_set.relation_type


def get_prior_template_path(facet):
    """Used to retrieve doc path based on facet of queue form in process_search."""
    if facet == Facet.people.value:
        path = 'discover/base_people_filtered.html'
    elif facet == Facet.corps.value:
        path = 'discover/base_corps_filtered.html'
    elif facet == Facet.colls.value:
        path = 'discover/base_collections_filtered.html'
    elif facet == Facet.orals.value:
        path = 'discover/base_orals_filtered.html'
    else:  # based on subjects search
        path = 'discover/base_collections_filtered.html'

    return path


def init_session(request):
    """Initializes browser session for storing prior search terms."""
    iterate = ['top', 'middle', 'bottom']

    if not request.session.session_key:
        request.session.create()
        for i in iterate:
            request.session[i] = {}
            request.session[i]['form_type'] = 'none'
            request.session[i]['form_vals'] = {}
            request.session[i]['form_vals']['data'] = 'empty'
            request.session[i]['form_vals']['facet'] = 'none'

        request.session.save()
    else:
        pass
