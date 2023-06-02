from django.shortcuts import render
from . import graph
from . import web_methods
from .models import Collection, Subject
from .wd_utils import catch_err
from django.db.models import QuerySet
from .enums import RelColor, Domain
from . import queue

# globally accessible table caches
# todo: figure out caching issue: Django caching framework...

curr_query = QuerySet()
curr_query_label = ''


def home(request):
    return render(request, 'discover/base_home.html')


def people(request):
    from . import forms
    from .web_methods import get_images
    from .enums import Domain

    # if user has switched to this facet from a different facet, restart queue
    if not queue.curr_domain == Domain.people.value:
        queue.clear_queue()
        queue.curr_domain = Domain.people.value

    sform = forms.SearchForm()
    # 1)
    qform = forms.QueueForm(dynamic_choices=queue.set_prior_queries())
    images = get_images('images_humans')  # record name in db query table
    # 2)
    context = {'search': sform, 'images': images, 'priors': qform}
    return render(request, 'discover/base_people.html', context)


def people_filtered(request):
    """Processes and renders search results. Callable by search form, node-select form and queue form."""
    from . import forms
    from .models import Person
    from django.db.models import QuerySet
    global curr_query

    # use curr_request for all request evals below.
    qry = QuerySet()
    curr_request = request
    domain = Domain.people.value  # used for rendering item details page.

    # check to see if back button used on item details page; reload most recent search result.
    bbf = forms.BackButtonForm(curr_request.POST)
    if bbf.is_valid():
        obj = queue.get_request(0)
        curr_request = obj[0]
        curr_query = obj[2]

    # if posted from the prior queries form, substitute
    # the associated WSGIRequest object from queue.
    rtn_qform = forms.QueueForm(curr_request.POST, dynamic_choices=queue.set_prior_queries())
    if rtn_qform.is_valid():
        q_results = process_queue_form(rtn_qform)
        curr_request = q_results['request']  # request position in list
        curr_query = q_results['query']  # queryset position in list

    # new forms to pass to people_filtered
    nsform = forms.NodeSelectForm(dynamic_choices=set_relation_types(domain))
    sform = forms.SearchForm()
    error_msg = ''

    try:
        return_search_form = forms.SearchForm(curr_request.POST)
        return_node_form = forms.NodeSelectForm(curr_request.POST, dynamic_choices=set_relation_types(domain))
        peeps = Person.objects.all()
        init_choice = ['occupation']
        if return_search_form.is_valid():
            # 4) add request to session queue for reuse
            queue.add_request([curr_request, domain + ' - ' + return_search_form['search_text'].value(),
                             qry])  # note empty query object that will be updated by mod_curr_query below.
            # 5) create new queue form now that queue has been updated.
            qform = forms.QueueForm(dynamic_choices=queue.set_prior_queries())
            results = process_search_form(return_search_form, peeps)
            # 6) add valid query set now that form has been processed
            queue.update_query(curr_query, 0)
            graph_data = graph.load_graph(results['filtered'], init_choice, domain)
            curr_checks = []
        elif return_node_form.is_valid():
            # 7) process checks from node form; use for queue and for process_node_form()
            the_checks = process_choices(return_node_form['relation_types'].value(), domain)
            node = return_node_form['shape_label'].value()
            if node == '':
                the_label = the_checks['search_str']
            else:
                the_label = node
            # 8) add request to session queue for reuse
            queue.add_request([curr_request, domain + " - " + the_label, qry])
            qform = forms.QueueForm(dynamic_choices=queue.set_prior_queries())
            results = process_node_form(return_node_form, peeps, domain, the_checks)
            # 9)
            queue.update_query(curr_query, 0)
            graph_data = graph.load_graph(results['filtered'], results['choices'], domain)
            curr_checks = results['checks']
        else:
            # creates empty objects for form rendering w/o awkward error handling.
            results = process_invalid_forms('people_filtered')
            # 10)
            qform = forms.QueueForm(dynamic_choices=queue.set_prior_queries())
            error_msg = results['message']
            graph_data = graph.load_graph(results['filtered'], init_choice, domain)
            curr_checks = []
        # 11)
        context = {'domain': domain, 'filtered_people': results['unique'], 'search': sform, 'priors': qform,
                   'num': results['num'], 'nodes': graph_data['nodes'], 'edges': graph_data['edges'],
                   'select': nsform, 'properties': graph_data['properties'],
                   'string': results['search_str'], 'checks': curr_checks, 'errors': error_msg}

        return render(request, 'discover/base_people_filtered.html', context)
    except Exception as e:
        errors = catch_err(e, 'people_filtered')
        context = {'search': sform, 'errors': errors}
        return render(request, 'discover/base_people.html', context)


def corpbodies(request):
    from .forms import SearchForm, QueueForm
    from .web_methods import get_images

    # if user has switched to this facet from a different facet, empty queue
    if not queue.curr_domain == Domain.corps.value:
        queue.clear_queue()
        queue.curr_domain = Domain.corps.value

    sform = SearchForm()
    qform = QueueForm(dynamic_choices=queue.set_prior_queries())
    images = get_images('images_others')  # record name in db query table
    context = {'search': sform, 'images': images, 'priors': qform}
    return render(request, 'discover/base_corpbodies.html', context)


def corpbodies_filtered(request):
    """Processes and renders search results for corporate bodies data. Callable only by search forms."""
    from . import forms
    from .models import CorpBody
    from django.db.models import QuerySet
    global curr_query

    curr_request = request
    domain = Domain.corps.value

    # check to see if back button used on item details page; reload most recent search result.
    bbf = forms.BackButtonForm(curr_request.POST)
    if bbf.is_valid():
        obj = queue.get_request(0)
        curr_request = obj[0]
        curr_query = obj[2]

    # if posted from the prior queries form, substitute
    # the associated WSGIRequest object, search label and
    # original queryset from queue.
    rtn_qform = forms.QueueForm(curr_request.POST, dynamic_choices=queue.set_prior_queries())
    qry = QuerySet()
    if rtn_qform.is_valid():
        q_results = process_queue_form(rtn_qform)
        curr_request = q_results['request']  # request position in list
        curr_query = q_results['query']  # queryset position in list

    # Create relation type list for graph form
    nsform = forms.NodeSelectForm(dynamic_choices=set_relation_types(domain))
    sform = forms.SearchForm()
    init_choice = ['instanceof']
    error_msg = ''

    try:
        return_search_form = forms.SearchForm(curr_request.POST)
        return_node_form = forms.NodeSelectForm(curr_request.POST, dynamic_choices=set_relation_types(domain))
        corps = CorpBody.objects.all()
        if return_search_form.is_valid():
            # 4) add request to session queue for reuse
            queue.add_request([curr_request, domain + " - " + return_search_form['search_text'].value(),
                               qry])  # note empty query object that will be updated by mod_curr_query below.
            # 5) create new queue form now that queue has been updated.
            qform = forms.QueueForm(dynamic_choices=queue.set_prior_queries())
            results = process_search_form(return_search_form, corps)
            # 6) add valid query set now that form has been processed
            queue.update_query(curr_query, 0)
            graph_data = graph.load_graph(results['filtered'], init_choice, domain)
            curr_checks = []
        elif return_node_form.is_valid():
            # 7) process checks from node form; use for queue and for process_node_form()
            the_checks = process_choices(return_node_form['relation_types'].value(), domain)
            node = return_node_form['shape_label'].value()
            if node == '':
                the_label = the_checks['search_str']
            else:
                the_label = node
            # 8) add request to session queue for reuse
            queue.add_request([curr_request, domain + " - " + the_label, qry])
            qform = forms.QueueForm(dynamic_choices=queue.set_prior_queries())
            results = process_node_form(return_node_form, corps, domain, the_checks)
            # 9)
            queue.update_query(curr_query, 0)
            graph_data = graph.load_graph(results['filtered'], results['choices'], domain)
            curr_checks = results['checks']
        else:
            # creates empty stubs for form rendering w/o awkward error handling.
            results = process_invalid_forms('corpbodies_filtered')
            qform = forms.QueueForm(dynamic_choices=queue.set_prior_queries())
            error_msg = results['message']
            graph_data = graph.load_graph(results['filtered'], init_choice, domain)
            curr_checks = []

        context = {'domain': domain, 'filtered_corps': results['unique'], 'search': sform,
                   'num': results['num'], 'nodes': graph_data['nodes'], 'edges': graph_data['edges'],
                   'priors': qform, 'select': nsform, 'properties': graph_data['properties'],
                   'string': results['search_str'], 'checks': curr_checks, 'errors': error_msg}

        return render(request, 'discover/base_corpbodies_filtered.html', context)

    except Exception as e:
        errors = catch_err(e, 'corpbodies_filtered')
        context = {'search': sform, 'errors': errors}
        return render(request, 'discover/base_corpbodies_filtered.html', context)


def collections(request):
    from .forms import SearchForm, QueueForm

    # if user has switched to this facet from a different facet, empty queue
    if not queue.curr_domain == Domain.colls.value:
        queue.clear_queue()
        queue.curr_domain = Domain.colls.value

    sform = SearchForm()
    qform = QueueForm(dynamic_choices=queue.set_prior_queries())
    context = {'search': sform, 'priors': qform}
    return render(request, 'discover/base_collections.html', context)


def collections_filtered(request):
    """Processes and renders search results for collections data. Callable by search, node-select and
    queue forms."""
    from . import forms
    from django.db.models import QuerySet
    global curr_query

    # use curr_request for all request evals below.
    qry = QuerySet()
    curr_request = request
    domain = Domain.colls.value

    # check to see if back button used on item details page; reload most recent search result.
    bbf = forms.BackButtonForm(curr_request.POST)
    if bbf.is_valid():
        obj = queue.get_request(0)
        curr_request = obj[0]
        curr_query = obj[2]

    # if posted from the prior queries form, substitute
    # the associated WSGIRequest object from queue.
    rtn_qform = forms.QueueForm(curr_request.POST, dynamic_choices=queue.set_prior_queries())
    if rtn_qform.is_valid():
        q_results = process_queue_form(rtn_qform)
        curr_request = q_results['request']
        curr_query = q_results['query']

    nsform = forms.NodeSelectForm(dynamic_choices=set_relation_types(domain))
    sform = forms.SearchForm()
    init_choice = ['subject']
    error_msg = ''

    try:
        colls = Collection.objects.all()
        return_rform = forms.RestrictSubjectForm(curr_request.POST)  # called via subject filtering on base_subjects_filtered.html
        return_sform = forms.SearchForm(curr_request.POST)  # page called via search
        return_nsform = forms.NodeSelectForm(curr_request.POST, dynamic_choices=set_relation_types(domain))    # called via graph node selection

        # determine which form has been returned
        if return_rform.is_valid():  # restrict-subject form on subjects_filtered.html
            # add request to session queue for reuse
            queue.add_request([curr_request, domain + " - " + return_rform['restrict_labels'].value(),
                             qry])  # note empty query object that will be updated by curr_query below.
            qform = forms.QueueForm(dynamic_choices=queue.set_prior_queries())
            results = process_restrictsubj_form(return_rform, colls)
            # add valid query set now that form has been processed
            queue.update_query(curr_query, 0)
            graph_data = graph.load_graph(results['filtered'], init_choice, domain)
            curr_checks = []
        elif return_sform.is_valid():
            # add request to session queue for reuse
            queue.add_request([curr_request, domain + " - " + return_sform['search_text'].value(),
                             qry])  # note empty query object that will be updated by curr_query below.
            # create new queue form now that queue has been updated.
            qform = forms.QueueForm(dynamic_choices=queue.set_prior_queries())
            results = process_search_form(return_sform, colls, 'colltypelabel')
            # add valid query set now that form has been processed
            queue.update_query(curr_query, 0)  # add to top of queue
            graph_data = graph.load_graph(results['filtered'], init_choice, domain)
            curr_checks = []
        elif return_nsform.is_valid():
            # process checks from node form; use for queue and for process_node_form()
            the_checks = process_choices(return_nsform['relation_types'].value(), domain)
            node = return_nsform['shape_label'].value()
            if node == '':
                the_label = the_checks['search_str']
            else:
                the_label = node
            # 8) add request to session queue for reuse
            queue.add_request([curr_request, domain + " - " + the_label, qry])
            qform = forms.QueueForm(dynamic_choices=queue.set_prior_queries())
            results = process_node_form(return_nsform, colls, domain, the_checks)
            queue.update_query(curr_query, 0)
            graph_data = graph.load_graph(results['filtered'], results['choices'], domain)
            curr_checks = results['checks']
        else:
            # creates empty stubs for form rendering w/o awkward error handling.
            results = process_invalid_forms('collections_filtered')
            qform = forms.QueueForm(dynamic_choices=queue.set_prior_queries())
            error_msg = results['message']
            graph_data = graph.load_graph(results['filtered'], init_choice, domain)
            curr_checks = []

        context = {'domain': domain, 'filtered_collections': results['unique'], 'search': sform,
                   'num': results['num'], 'nodes': graph_data['nodes'], 'edges': graph_data['edges'],
                   'priors': qform, 'select': nsform, 'properties': graph_data['properties'],
                   'string': results['search_str'], 'checks': curr_checks, 'errors': error_msg}

        return render(request, 'discover/base_collections_filtered.html', context)

    except Exception as e:
        errors = catch_err(e, 'collections_filtered')
        context = {'search': sform, 'errors': errors}
        return render(request, 'discover/base_collections_filtered.html', context)


def oralhistories(request):
    from .forms import SearchForm, QueueForm

    # if user has switched to this facet from a different facet, empty queue
    if not queue.curr_domain == Domain.orals.value:
        queue.clear_queue()
        queue.curr_domain = Domain.orals.value

    sform = SearchForm()
    qform = QueueForm(dynamic_choices=queue.set_prior_queries())
    context = {'search': sform, 'priors': qform}
    return render(request, 'discover/base_oralhistories.html', context)


def oralhistories_filtered(request):
    """Processes and renders search results for oral histories data. Callable only by search or node form."""
    from . import forms
    from .models import OralHistory
    from . import graph
    from django.db.models import QuerySet
    global curr_query

    qry = QuerySet()
    curr_request = request
    domain = Domain.orals.value

    # check to see if back button used on item details page; reload most recent search result.
    bbf = forms.BackButtonForm(curr_request.POST)
    if bbf.is_valid():
        obj = queue.get_request(0)
        curr_request = obj[0]
        curr_query = obj[2]

    # if posted from the prior queries form, substitute
    # the associated WSGIRequest object from queue.

    rtn_qform = forms.QueueForm(curr_request.POST, dynamic_choices=queue.set_prior_queries())
    if rtn_qform.is_valid():
        q_results = process_queue_form(rtn_qform)
        curr_request = q_results['request']  # request position in list
        curr_query = q_results['query']  # queryset position in list

    nsform = forms.NodeSelectForm(dynamic_choices=set_relation_types(domain))
    sform = forms.SearchForm()
    init_choice = ['subject']
    error_msg = ''

    try:
        orals = OralHistory.objects.all()
        return_sform = forms.SearchForm(curr_request.POST)  # page called via search
        return_nsform = forms.NodeSelectForm(curr_request.POST, dynamic_choices=set_relation_types(domain))    # called via graph node selection
        if return_sform.is_valid():
            # 4) add request to session queue for reuse
            queue.add_request([curr_request, "oral hist. - " + return_sform['search_text'].value(),
                             qry])  # note empty query object that will be updated by mod_curr_query below.
            # 5) create new queue form now that queue has been updated.
            qform = forms.QueueForm(dynamic_choices=queue.set_prior_queries())
            results = process_search_form(return_sform, orals, 'inventorynum')
            # 6) add valid query set now that form has been processed
            queue.update_query(curr_query, 0)
            graph_data = graph.load_graph(results['filtered'], init_choice, domain)
            curr_checks = []
        elif return_nsform.is_valid():
            # 7) process checks from node form; use for queue and for process_node_form()
            the_checks = process_choices(return_nsform['relation_types'].value(), domain)
            node = return_nsform['shape_label'].value()
            if node == '':
                the_label = the_checks['search_str']
            else:
                the_label = node
            # 8) add request to session queue for reuse
            queue.add_request([curr_request, domain + " - " + the_label, qry])
            qform = forms.QueueForm(dynamic_choices=queue.set_prior_queries())
            results = process_node_form(return_nsform, orals, domain, the_checks)
            queue.update_query(curr_query, 0)
            graph_data = graph.load_graph(results['filtered'], results['choices'], domain)
            curr_checks = results['checks']
        else:
            # creates empty stubs for form rendering w/o awkward error handling.
            results = process_invalid_forms('oralhistories_filtered')
            qform = forms.QueueForm(dynamic_choices=queue.set_prior_queries())
            error_msg = results['message']
            graph_data = graph.load_graph(results['filtered'], init_choice, domain)
            curr_checks = []

        context = {'domain': domain, 'filtered_orals': results['unique'], 'search': sform, 'priors': qform,
                   'num': results['num'], 'nodes': graph_data['nodes'], 'edges': graph_data['edges'],
                   'select': nsform, 'properties': graph_data['properties'],
                   'string': results['search_str'], 'checks': curr_checks, 'errors': error_msg}

        return render(request, 'discover/base_oralhistories_filtered.html', context)
    except Exception as e:
        errors = catch_err(e, 'oralhistories_filtered')
        context = {'search': sform, 'errors': errors}
        return render(request, 'discover/base_oralhistories_filtered.html', context)


def subjects(request):
    from .forms import SearchForm
    sform = SearchForm()
    context = {'search': sform}
    return render(request, 'discover/base_subjects.html', context)


def subjects_filtered(request):
    """Callable only by search forms."""
    # todo: fix. Updates to other views broke the transition to collections_filtered.
    # todo: add item details method and links to results
    from .forms import SearchForm, RestrictSubjectForm
    try:
        sform = SearchForm()
        rform = RestrictSubjectForm()
        return_sform = SearchForm(request.POST)
        if return_sform.is_valid():
            subjs = Subject.objects.all().filter(subjectlabel__icontains=return_sform.cleaned_data['search_text'])
            search_string = return_sform.cleaned_data['search_text']
            context = {'subjects': subjs, 'search': sform, 'search_string': search_string, 'restrict': rform}
            return render(request, 'discover/base_subjects_filtered.html', context)
        else:
            return render(request, 'discover/base_subjects_filtered.html')
    except Exception as e:
        errors = catch_err(e)
        context = {'errors': errors}
        return render(request, 'discover/base_subjects_filtered.html', context)


def item(request, item_code, domain):
    from .forms import BackButtonForm, NodeSelectForm

    bb_form = BackButtonForm()
    details = web_methods.get_item_details(item_code)
    the_domain = domain
    the_item = details[0]
    ns_form = NodeSelectForm(dynamic_choices=set_relation_types(domain))
    context = {'details': details, 'item': the_item.item_label, 'itemdesc': the_item.item_desc,
               'bb_form': bb_form, 'select': ns_form, 'domain': the_domain}
    return render(request, 'discover/base_item.html', context)


def about(request):
    from . import db
    from .forms import WikiLoadForm
    from wikidataDiscovery import settings
    ver = settings.APP_VERSION
    auth = settings.APP_AUTHOR
    email = settings.APP_EMAIL

    msgs = ""
    val = ''
    nf = WikiLoadForm()
    cf = WikiLoadForm(request.POST)
    if cf.is_valid():
        val = cf.cleaned_data['run_it']
    if val == '1':
        n = db.cache_collections()
        msgs += str(n) + " collection records returned." + '\n'
        n = db.cache_corp_bodies()
        msgs += str(n) + " corp bodies records returned." + '\n'
        n = db.cache_oral_histories()
        msgs += str(n) + " oral history records returned." + '\n'
        n = db.cache_people()
        msgs += str(n) + " people records returned." + '\n'
        n = db.cache_subjects()
        msgs += str(n) + " subjects records returned." + '\n'

    context = {'form': nf, 'version': ver, 'author': auth, 'email': email, 'messages': msgs}
    return render(request, 'discover/base_about.html', context)


def process_search_form(sform, qset, special_col=None):
    """Private function for form processing. Generic form handler for all views that use the search form.
    Initiates new search workflow for any query set."""
    from django.db.models import Q
    from .web_methods import reduce_search_results
    global curr_query
    global curr_query_label

    filtset = qset.filter(Q(itemdesc__icontains=sform.cleaned_data['search_text']) |
                          Q(itemlabel__icontains=sform.cleaned_data['search_text']))

    if special_col:
        uniqueset = reduce_search_results(filtset, special_col)
    else:
        uniqueset = reduce_search_results(filtset)
    num = uniqueset.__len__()
    the_string = "'" + sform.cleaned_data['search_text'] + "'"
    curr_query = filtset
    curr_query_label = the_string
    return {'filtered': filtset, 'unique': uniqueset, 'num': num, 'search_str': the_string}


def process_node_form(nsform, qset, domain, selections):
    """Handles node form processing using any query set, a given data domain,
    and all relation type checkboxes selected by the user."""
    # generic node selection form handler for all views that use it
    from .web_methods import reduce_search_results
    global curr_query

    # get selected checkboxes for relation types in graph; grab other needed values
    the_choices = nsform.cleaned_data['relation_types']
    the_string = nsform.cleaned_data['shape_label']
    the_color = nsform.cleaned_data['color_type']

    if the_string =='':  # create search str val if only relation type(s) are selected
            the_string = selections['search_str']

    # filter according to unique node, based on color type
    if the_color == RelColor.item.value:
        filtset = qset.filter(item_id__exact=nsform.cleaned_data['selected_text']).order_by('item_id')
        uniqueset = reduce_search_results(filtset)
        curr_query = filtset
    elif the_color == RelColor.occup.value:
        filtset = qset.filter(occupation_id__exact=nsform.cleaned_data['selected_text'])
        uniqueset = reduce_search_results(filtset)
        curr_query = filtset
    elif the_color == RelColor.fow.value:
        filtset = qset.filter(fieldofwork_id__exact=nsform.cleaned_data['selected_text'])
        uniqueset = reduce_search_results(filtset)
        curr_query = filtset
    elif the_color == RelColor.pob.value:
        filtset = qset.filter(placeofbirth_id__exact=nsform.cleaned_data['selected_text'])
        uniqueset = reduce_search_results(filtset)
        curr_query = filtset
    elif the_color == RelColor.pod.value:
        filtset = qset.filter(placeofdeath_id__exact=nsform.cleaned_data['selected_text'])
        uniqueset = reduce_search_results(filtset)
        curr_query = filtset
    elif the_color == RelColor.subj.value:
        filtset = qset.filter(subject_id__exact=nsform.cleaned_data['selected_text'])
        curr_query = filtset
        if domain == 'collections':  #todo: move domain logic inside reduce_search_results. Fixes specialcol bug.
            uniqueset = reduce_search_results(filtset, 'colltypelabel')
        elif domain == 'corps':
            uniqueset = reduce_search_results(filtset)
        elif domain == 'orals':  # domain is oral history
            uniqueset = reduce_search_results(filtset, 'inventorynum')
        else:
            uniqueset = reduce_search_results(filtset)
    elif the_color == RelColor.instanceof.value:
        filtset = qset.filter(instanceof_id__exact=nsform.cleaned_data['selected_text'])
        uniqueset = reduce_search_results(filtset)
        curr_query = filtset
    else:
        filtset = curr_query  # new relations have been specified and no nodes have been selected.
        uniqueset = reduce_search_results(filtset)

    num = uniqueset.__len__()
    total_string = the_string

    return {'filtered': filtset, 'unique': uniqueset, 'num': num,
            'search_str': total_string, 'choices': the_choices, 'checks': selections['checks']}


def process_restrictsubj_form(rsform, qset):
    """Private function for form processing."""
    # Posted from the Subjects page only. Processed by subjects_filtered and corp_filtered.
    from .web_methods import reduce_search_results
    global curr_query

    qcodes = rsform.cleaned_data['restrict_text'].split(',')
    qcodes.remove('')  # remove empty member that causes trailing comma
    search_str = rsform.cleaned_data['restrict_labels'].split(',')
    search_str.remove('')

    filtset = qset.filter(subject_id__in=qcodes)
    curr_query = filtset
    uniqueset = reduce_search_results(filtset, 'colltypelabel')
    num = uniqueset.__len__()

    return {'filtered': filtset, 'unique': uniqueset, 'num': num, 'search_str': str(search_str)}

def process_queue_form(q_form) -> dict:
    n = int(q_form.cleaned_data['run_qry'])
    request = object
    label = ''
    query = object
    if not n == 0:
        n = n - 1
        prior_search = queue.get_request(n)
        request = prior_search[0]  # WSGIRequest position in list
        label = prior_search[1]  # label for search string used
        query = prior_search[2]  # queryset position in list
    return {'request': request, 'label': label, 'query': query}

def process_invalid_forms(the_form):
    from django.db.models.query import QuerySet
    filterset = QuerySet()
    uniqueset = QuerySet()
    num = 0
    search_str = ''
    if the_form == 'people_filtered':
        the_msg = "There was a problem with the search service for People."
    elif the_form == 'corpbodies_filtered':
        the_msg = "There was a problem with the search service for Corporate Bodies."
    elif the_form == 'collections_filtered':
        the_msg = "There was a problem with the search service for Collections."
    else:
        the_msg = "There was a problem with the search service for Oral Histories."

    return {'filtered': filterset, 'unique': uniqueset, 'num': num, 'search_str': search_str, 'message': the_msg}


def set_relation_types(domain: str) -> list:
    """Creates list for relation type options on the node form."""
    from .models import RelationType

    the_set = RelationType.objects.filter(domain=domain)
    rel_types = []
    for r in the_set:
        rel_types.append((r.relation_type, r.relation_type_label))
    return rel_types


def process_choices(choices: list, domain) -> dict:
    """Used with returned node form to create a list of selected relationship
    types and a corresponding search string label. Called prior to process node form."""
    from .models import RelationType
    # get checkbox select order for domain from db; gets applied on template render
    dom = RelationType.objects.filter(domain=domain)
    choice_sel = []
    alt_str = ''
    for c in choices:
        o = dom.get(relation_type=c)
        if o:
            choice_sel.append(o.list_order)
            alt_str += o.relation_type_label + ' + '
    total_str = curr_query_label + ": " + alt_str.rstrip(' + ')

    return {'checks': choice_sel, 'search_str': total_str}