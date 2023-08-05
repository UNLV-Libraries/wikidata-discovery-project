from django.shortcuts import render
from . import graph
from . import web_methods
from .models import Subject
from .wd_utils import catch_err
from .enums import AppClass
from . import queue_mgr
from . import mappings


def home(request):
    from .web_methods import get_chart

    init_session(request)

    chart_io_dict = get_chart('stats_instanceof_count')
    chart_subj_dict = get_chart('stats_subjects_count')
    context = {'chart_io_labels': chart_io_dict['labels'], 'chart_io_data': chart_io_dict['data'],
               'chart_subj_labels': chart_subj_dict['labels'], 'chart_subj_data': chart_subj_dict['data']}
    return render(request, 'discover/base_home.html', context)


def process_search(request):
    """Processes and renders search results for all app classes.
    Callable by search form, node-select form, subject forms, and queue form."""
    from .forms import QueueForm, SearchForm, NodeSelectForm, RestrictSubjectForm, BackButtonForm

    # construct file path for rendering result template
    url_path = request.path[1:request.path.__len__() - 1]
    file_path = url_path.split('/')
    final_path = file_path[0] + '/base_' + file_path[1] + '.html'
    error_msg = ''
    curr_class = ''
    bypass_large_graph = 0
    bypass_queue = False

    try:
        # check if queue form has been used to submit a prior search; run appropriate request setup.
        rtn_qform = QueueForm(request.POST,
                              dynamic_choices=queue_mgr.get_queue_list(request.session.session_key))
        if rtn_qform.is_valid():
            pos = rtn_qform.cleaned_data['run_qry']
            q_item = queue_mgr.get_queue_entry(pos, request.session.session_key)
            curr_class = q_item['form_vals']['app_class']
            final_path = get_prior_template_path(curr_class)
            curr_request = queue_mgr.create_request(request.session.session_key, pos)
        else:
            curr_request = request

        # check to see if back button used on item details page; reload most recent search result.
        bbf = BackButtonForm(curr_request.POST)
        if bbf.is_valid():
            bypass_queue = True
            bypass_large_graph = 1
            curr_request = queue_mgr.create_request(request.session.session_key, 'top')

        # attempt to hydrate all search forms based on POST data. Only one will be valid.
        rtn_search_frm = SearchForm(curr_request.POST)
        curr_class = rtn_search_frm['app_class'].value()  # grab app class val off search form pre-validation
        if curr_class == AppClass.subjs.value:  # subject form has called this process_search
            curr_class = AppClass.colls.value
        the_checks = [get_default_rel_type(curr_class)]
        rtn_node_frm = NodeSelectForm(curr_request.POST,
                                      dynamic_choices=set_relation_types(curr_class))
        rtn_subject_frm = RestrictSubjectForm(curr_request.POST)

        # variables to track previous search values used on search, subject, or node forms.
        # set all to 'empty'; logic below fills fields for kw, subject, or node, depending on case.
        prior_kw_search = ''
        prior_facet_values = ''
        prior_facet_labels = ''
        prior_node_search = ''
        prior_node_label = ''
        prior_color = ''
        prior_subj_search = ''
        prior_subj_label = ''
        prior_show_all = False

        # find valid form and process
        if rtn_search_frm.is_valid():
            prior_kw_search = rtn_search_frm.cleaned_data['search_text']
            prior_facet_values = rtn_search_frm.cleaned_data['facet_values']
            prior_facet_labels = rtn_search_frm.cleaned_data['facet_labels']
            prior_show_all = rtn_search_frm.cleaned_data['show_all']
            qry = mappings.get_search_queryset(curr_class)
            if not bypass_queue:
                queue_mgr.update_queue('search', rtn_search_frm, request.session.session_key)
            results = process_search_form(rtn_search_frm, qry, the_checks)
            the_checks = results['choices']  # all downstream relation type variables must be iterable.
            graph_data = graph.load_graph(results['filtered'], the_checks, curr_class)
        elif rtn_subject_frm.is_valid():
            qry = mappings.get_search_queryset(AppClass.colls.value)  # subject form used only for collections
            if not bypass_queue:
                queue_mgr.update_queue('subject', rtn_subject_frm, request.session.session_key)
            results = process_restrictsubj_form(rtn_subject_frm, qry)
            the_checks = results['choices']
            graph_data = graph.load_graph(results['filtered'], the_checks, curr_class)
        elif rtn_node_frm.is_valid():
            if rtn_node_frm.cleaned_data['node_id'] == '':  # node hasn't been clicked, just change in rel types
                if rtn_node_frm.cleaned_data['prior_subj_search'].__len__() > 0:  # descended from subj search
                    prior_subj_search = rtn_node_frm.cleaned_data['prior_subj_search']
                    prior_subj_label = rtn_node_frm.cleaned_data['prior_subj_labels']
                elif (rtn_node_frm.cleaned_data['prior_kw_search'].__len__() > 0 or
                      rtn_node_frm.cleaned_data['prior_facet_values'].__len__() > 0 or
                        rtn_node_frm.cleaned_data['prior_show_all']):  # descended from kw-facet search
                    prior_kw_search = rtn_node_frm.cleaned_data['prior_kw_search']  # maintain last kw search ref
                    prior_facet_values = rtn_node_frm.cleaned_data['prior_facet_values']  # maintain facet search refs
                    prior_facet_labels = rtn_node_frm.cleaned_data['prior_facet_labels']
                    prior_show_all = rtn_node_frm.cleaned_data['prior_show_all']
                else:  # descended from a prior node search
                    prior_node_search = rtn_node_frm.cleaned_data['prior_node_search']
                    prior_node_label = rtn_node_frm.cleaned_data['prior_node_label']  # maintain prior label
                    prior_color = rtn_node_frm.cleaned_data['prior_color']  # maintain last color ref
                    prior_kw_search = rtn_node_frm.cleaned_data['prior_kw_search']
                    prior_facet_values = rtn_node_frm.cleaned_data['prior_facet_values']
                    prior_facet_labels = rtn_node_frm.cleaned_data['prior_facet_labels']
                    prior_show_all = rtn_node_frm.cleaned_data['prior_show_all']
            else:  # node was just clicked
                # The prior query will now be a node query, not a keyword-facet or subject query.
                # See graph_functions.js::selectNode.
                prior_node_search = rtn_node_frm.cleaned_data['node_id']  # set last node search val
                prior_node_label = rtn_node_frm.cleaned_data['node_label']  # maintain prior label
                prior_color = rtn_node_frm.cleaned_data['color_type']  # maintain prior color
            qry = mappings.get_search_queryset(curr_class)
            if not bypass_queue:
                queue_mgr.update_queue('node', rtn_node_frm, request.session.session_key)
            results = process_node_form(rtn_node_frm, qry, request.session.session_key)
            the_checks = results['choices']
            graph_data = graph.load_graph(results['filtered'], the_checks, curr_class)
        else:  # edge case in which no forms are valid
            results = process_invalid_form()  # pass empty set
            graph_data = graph.load_graph(results, the_checks, curr_class)

        # obtain facet values list for faceted search
        facet_vals = mappings.get_facet_queryset(curr_class)

        # new forms to pass to people_filtered
        nsform = NodeSelectForm(initial={'app_class': curr_class, 'prior_kw_search': prior_kw_search,
                                         'prior_facet_values': prior_facet_values,
                                         'prior_facet_labels': prior_facet_labels,
                                         'prior_color': prior_color, 'prior_node_label': prior_node_label,
                                         'prior_node_search': prior_node_search,
                                         'prior_subj_search': prior_subj_search,
                                         'prior_subject_labels': prior_subj_label,
                                         'prior_show_all': prior_show_all},
                                dynamic_choices=set_relation_types(curr_class))
        sform = SearchForm(initial={'app_class': curr_class, 'relation_type': get_default_rel_type(curr_class)})
        qform = QueueForm(initial={'app_class': curr_class},
                          dynamic_choices=queue_mgr.get_queue_list(request.session.session_key))

        context = {'app_class': curr_class, 'unique_list': results['unique'], 'search': sform, 'priors': qform,
                   'num': results['num'], 'nodes': graph_data['nodes'], 'edges': graph_data['edges'],
                   'select': nsform, 'properties': graph_data['properties'], 'bypass_lg_graph': bypass_large_graph,
                   'string': results['search_str'], 'facet': facet_vals, 'checks': the_checks, 'errors': error_msg}

        return render(request, final_path, context)

    except Exception as e:
        errors = catch_err(e, 'views.process_search')
        # error_message(request, errors)
        context = {'errors': errors}
        return render(request, 'discover/base_error_message.html', context)


def error_message(request, errors):
    context = {'errors': errors}
    req = create_error_request()
    return render(req, 'discover/base_error_message.html', context)


def create_error_request():
    from django.contrib.auth.models import AnonymousUser
    from django.test import RequestFactory

    factory = RequestFactory()
    request = RequestFactory.get(factory, '/discover/app_error/', secure=True)
    request.user = AnonymousUser()

    return request


def people(request):
    from . import forms
    from .web_methods import get_images

    # initialize session for queue management
    init_session(request)

    relation = get_default_rel_type(AppClass.people.value)
    facet_vals = mappings.get_facet_queryset(AppClass.people.value)

    sf = forms.SearchForm(initial={'app_class': AppClass.people.value, 'relation_type': relation})
    qf = forms.QueueForm(initial={'app_class': AppClass.people.value},
                         dynamic_choices=queue_mgr.get_queue_list(request.session.session_key))
    images = get_images('images_humans')
    context = {'search': sf, 'images': images, 'priors': qf,
               'app_class': AppClass.people.value, 'facet': facet_vals}
    return render(request, 'discover/base_people.html', context)


def corp_bodies(request):
    from . import forms
    from .web_methods import get_images

    # initialize session for queue management
    init_session(request)

    relation = get_default_rel_type(AppClass.corps.value)
    facet_vals = mappings.get_facet_queryset(AppClass.corps.value)

    sf = forms.SearchForm(initial={'app_class': AppClass.corps.value, 'relation_type': relation})
    qf = forms.QueueForm(initial={'app_class': AppClass.corps.value},
                         dynamic_choices=queue_mgr.get_queue_list(request.session.session_key))
    images = get_images('images_others')  # record name in db query table
    context = {'search': sf, 'images': images, 'priors': qf, 'app_class': AppClass.corps.value,
               'facet': facet_vals}
    return render(request, 'discover/base_corps.html', context)


def collections(request):
    from . import forms

    # initialize session for queue management
    init_session(request)

    relation = get_default_rel_type(AppClass.colls.value)
    facet_vals = mappings.get_facet_queryset(AppClass.colls.value)

    sf = forms.SearchForm(initial={'app_class': AppClass.colls.value, 'relation_type': relation})
    qf = forms.QueueForm(initial={'app_class': AppClass.colls.value},
                         dynamic_choices=queue_mgr.get_queue_list(request.session.session_key))
    # images = get_images('images_others')  # record name in db query table
    context = {'search': sf, 'priors': qf, 'facet': facet_vals, 'app_class': AppClass.colls.value}
    return render(request, 'discover/base_collections.html', context)


def oral_histories(request):
    from . import forms

    # initialize session for queue management
    init_session(request)

    relation = get_default_rel_type(AppClass.orals.value)
    facet_vals = mappings.get_facet_queryset(AppClass.orals.value)
    sf = forms.SearchForm(initial={'app_class': AppClass.orals.value, 'relation_type': relation})
    qf = forms.QueueForm(initial={'app_class': AppClass.orals.value},
                         dynamic_choices=queue_mgr.get_queue_list(request.session.session_key))
    # images = get_images('images_others')  # record name in db query table
    context = {'search': sf, 'priors': qf, 'facet': facet_vals, 'app_class': AppClass.orals.value}
    return render(request, 'discover/base_orals.html', context)


def subjects(request):
    from . import forms

    init_session(request)

    sf = forms.SearchForm(initial={'app_class': AppClass.subjs.value, 'relation_type': 'none'})
    context = {'search': sf}
    return render(request, 'discover/base_subjects.html', context)


def subjects_filtered(request):
    from .forms import SearchForm, RestrictSubjectForm

    try:
        sf = SearchForm(initial={'app_class': AppClass.subjs.value, 'relation_type': 'none'})
        rf = RestrictSubjectForm(initial={'app_class': AppClass.subjs.value})
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


def item(request, item_code, app_class):
    from .forms import BackButtonForm

    bb_form = BackButtonForm()
    details = web_methods.get_item_details(item_code)
    the_class = app_class
    the_item = details[0]
    context = {'details': details, 'item': the_item.item_label, 'itemdesc': the_item.item_desc,
               'bb_form': bb_form, 'app_class': the_class}
    return render(request, 'discover/base_item.html', context)


def utilities(request):
    from . import db
    from .forms import WikiLoadForm

    init_session(request)
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

    init_session(request)
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
    from .web_methods import reduce_search_results

    the_class = sform.cleaned_data['app_class']
    rel_type_str = rel_type_list[0]
    if rel_type_str == 'instanceof':  # instanceof label is jargon
        rel_type_str = 'category'

    search_str = sform.cleaned_data['search_text']
    facet_list = sform.cleaned_data['facet_values']
    facet_str = sform.cleaned_data['facet_labels']
    show_all = sform.cleaned_data['show_all']
    query_data = get_search_query(show_all, search_str, facet_list, facet_str, qset, the_class)
    filtered_set = query_data['query']
    search_label = query_data['search_label']
    unique_set = reduce_search_results(filtered_set, the_class)

    num = unique_set.__len__()
    the_string = search_label + ". link=" + rel_type_str
    return {'filtered': filtered_set, 'unique': unique_set, 'num': num,
            'search_str': the_string, 'choices': rel_type_list}


def process_node_form(nsform, qset, session_key):
    """Handles node form processing using any query set, a given app class,
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
    curr_class = nsform.cleaned_data['app_class']

    # Get data from prior search request
    mid_req = queue_mgr.get_queue_entry('middle', session_key)
    form_type = mid_req['form_type']

    # filter acc to unique node, based on color type.
    # User may have NOT selected a node but only changed relation type options.
    if nsform.cleaned_data['node_id'].__len__() > 0:  # user selected a node; new query.
        the_label = nsform.cleaned_data['node_label']
        filtset = mappings.get_node_queryset(nsform, qset)
    else:  # node frm is descendent of one of three search forms: search, subject, or a prev node.
        if form_type == 'search':
            facet_vals = mid_req['form_vals']['facet_values']
            facet_lbls = mid_req['form_vals']['facet_labels']
            search_str = mid_req['form_vals']['search_text']
            show_all = mid_req['form_vals']['show_all']
            query_data = get_search_query(show_all, search_str, facet_vals, facet_lbls, qset, curr_class)
            the_label = query_data['search_label']
            filtset = query_data['query']
        elif form_type == 'subject':
            the_label = mid_req['form_vals']['restrict_labels']
            filtset = qset.filter(subject_id__in=mid_req['form_vals']['restrict_text'])
        else:  # current form is descended form another node form; use 'prior_' fields.
            prior_subject_search = mid_req['form_vals']['prior_subj_search']
            prior_kw_search = mid_req['form_vals']['prior_kw_search']
            prior_facet_values = mid_req['form_vals']['prior_facet_values']
            prior_facet_labels = mid_req['form_vals']['prior_facet_labels']
            prior_show_all = mid_req['form_vals']['prior_show_all']
            if prior_subject_search.__len__() > 0:
                the_label = mid_req['form_vals']['prior_subj_labels']
                filtset = qset.filter(subject_id__in=mid_req['form_vals']['prior_subj_search'])
            elif (prior_kw_search.__len__() > 0 or
                  prior_facet_values.__len__() > 0 or
                    prior_show_all):
                query_data = get_search_query(prior_show_all, prior_kw_search, prior_facet_values,
                                              prior_facet_labels, qset, curr_class)
                the_label = query_data['search_label']
                filtset = query_data['query']
            else:
                the_label = mid_req['form_vals']['prior_node_label']
                filtset = mappings.get_node_queryset(nsform, qset)

    uniqueset = reduce_search_results(filtset, curr_class)
    num = uniqueset.__len__()
    total_label = the_label + ". link=" + choices_str

    return {'filtered': filtset, 'unique': uniqueset, 'num': num,
            'search_str': total_label, 'choices': the_choices}


def process_restrictsubj_form(rsform, qset):
    """Private function for form processing."""
    # Posted from the Subjects page only. Processed by subjects_filtered and corp_filtered.
    from .web_methods import reduce_search_results

    query_pair = get_list_and_string(rsform.cleaned_data['restrict_text'], rsform.cleaned_data['restrict_labels'])

    filtset = qset.filter(subject_id__in=query_pair['codes'])
    uniqueset = reduce_search_results(filtset, AppClass.colls.value)
    num = uniqueset.__len__()
    choice = get_default_rel_type(AppClass.colls.value)  # subject form only supports collection results.
    return {'filtered': filtset, 'unique': uniqueset, 'num': num,
            'choices': [choice], 'search_str': query_pair['string'] + '. link= ' + choice}


def process_invalid_form() -> dict:
    """Used for edge case in which all incoming forms in process_search are invalid. Returns
     dict with empty values that mimic processed forms data."""
    filtset = mappings.QuerySet()
    uniqueset = mappings.QuerySet()
    search_str = "error in search"
    choices = []
    num = 0
    return {'filtered': filtset, 'unique': uniqueset, 'num': num,
            'choices': choices, 'search_str': search_str}


def set_relation_types(app_class: str) -> list:
    """Creates list for relation type options on the node form."""
    from .models import RelationType

    the_set = RelationType.objects.filter(domain=app_class)
    rel_types = []
    for r in the_set:
        rel_types.append((r.relation_type, r.relation_type_label))
    return rel_types


def process_choices(choices: list, app_class) -> dict:
    """Used with returned node form to create a list of selected relationship
    types and a corresponding search string label. Called prior to process node form."""
    from .models import RelationType
    # get checkbox select order for domain from db; gets applied on template render
    fac = RelationType.objects.filter(domain=app_class)
    choice_sel = []
    alt_str = ''
    for c in choices:
        o = fac.get(relation_type=c)
        if o:
            choice_sel.append(o.list_order)
            alt_str += o.relation_type_label + ' + '
    total_str = '' + ": " + alt_str.rstrip(' + ')

    return {'checks': choice_sel, 'search_str': total_str}


def get_default_rel_type(app_class):
    """Returns the top-of-list relation type for a given app_class."""
    from .models import RelationType
    check_set = RelationType.objects.get(domain=app_class, list_order=0)
    return check_set.relation_type


def get_prior_template_path(app_class):  # todo: move to mappings.py or implement with urls.py
    """Used to retrieve doc path based on app_class of queue form in process_search."""
    if app_class == AppClass.people.value:
        path = 'discover/base_people_filtered.html'
    elif app_class == AppClass.corps.value:
        path = 'discover/base_corps_filtered.html'
    elif app_class == AppClass.colls.value:
        path = 'discover/base_collections_filtered.html'
    elif app_class == AppClass.orals.value:
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
            request.session[i]['form_vals']['app_class'] = 'none'

        request.session.save()
    else:
        pass


def get_list_and_string(codes, string):
    """Needed for search form data processing."""
    qcodes = codes.split(',')
    qcodes.remove('')  # remove empty member that causes trailing comma
    search_str = string.split(',')
    search_str.remove('')

    return {'codes': qcodes, 'string': str(search_str)}


def get_search_query(show_all, search_str, facet_list, facet_str, queryset, the_class) -> dict:
    from django.db.models import Q
    query_pair = get_list_and_string(facet_list, facet_str)
    kw_arg = mappings.get_facet_filter_kwarg(the_class, query_pair['codes'])

    n = 0
    if search_str.__len__() > 0:
        n += 1
    if facet_list.__len__() > 0:
        n += 2
    if show_all:
        n += 4

    if n == 1:  # keyword only
        filtset = queryset.filter(Q(itemdesc__icontains=search_str) |
                                  Q(itemlabel__icontains=search_str))
        the_string = search_str
    elif n == 2:  # facet value(s) only
        filtset = queryset.filter(**kw_arg)
        the_string = query_pair['string']
    elif n == 3:  # both keyword and facet values
        fs1 = queryset.filter(Q(itemdesc__icontains=search_str) |
                              Q(itemlabel__icontains=search_str))
        filtset = fs1.filter(**kw_arg)
        the_string = search_str + " & " + query_pair['string']
    elif n == 4: # user clicked the "show all" checkbox
        filtset = queryset
        the_string = "All " + the_class
    else:
        filtset = queryset  # if all tests fail
        the_string = "All " + the_class

    return {'query': filtset, 'search_label': the_string}
