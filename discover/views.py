from django.shortcuts import render

from . import graph
from . import web_methods
from .models import Collection, Subject
from .wd_utils import catch_err
from django.db.models import QuerySet
from .enums import RelColor

# globally accessible table caches
# todo: figure out caching issue: Django caching framework...

mod_curr_query = QuerySet()
mod_curr_search_str = ''


def home(request):
    return render(request, 'discover/base_home.html')


def people(request):
    from . import forms
    from .web_methods import get_images

    sform = forms.SearchForm()
    images = get_images('images_humans')  # record name in db query table
    context = {'search': sform, 'images': images}
    return render(request, 'discover/base_people.html', context)


def people_filtered(request):
    """Processes and renders search results. Callable only by search form and node-select form."""
    from .models import RelationType
    from . import forms
    from .models import Person

    the_set = RelationType.objects.filter(domain='people')
    people_choices = []
    for r in the_set:
        people_choices.append((r.relation_type, r.relation_type_label))

    nsform = forms.NodeSelectForm(dynamic_choices=people_choices)
    sform = forms.SearchForm()
    error_msg = ''
    try:
        return_search_form = forms.SearchForm(request.POST)
        return_node_form = forms.NodeSelectForm(request.POST, dynamic_choices=people_choices)
        peeps = Person.objects.all()
        init_choice = ['occupation']
        if return_search_form.is_valid():
            results = process_search_form(return_search_form, peeps)
            graph_data = graph.load_graph(results['filtered'], init_choice, 'people')
            curr_checks = []
        elif return_node_form.is_valid():
            results = process_node_form(return_node_form, peeps, 'people')
            graph_data = graph.load_graph(results['filtered'], results['choices'], 'people')
            curr_checks = results['checks']
        else:
            # creates empty objects for form rendering w/o awkward error handling.
            results = process_invalid_forms('people_filtered')
            error_msg = results['message']
            graph_data = graph.load_graph(results['filtered'], init_choice, 'people')
            curr_checks = []
        context = {'filtered_people': results['unique'], 'search': sform,
                   'num': results['num'], 'nodes': graph_data['nodes'], 'edges': graph_data['edges'],
                   'select': nsform, 'properties': graph_data['properties'],
                   'string': results['search_str'], 'checks': curr_checks, 'errors': error_msg}

        return render(request, 'discover/base_people_filtered.html', context)
    except Exception as e:
        errors = catch_err(e, 'people_filtered')
        context = {'search': sform, 'errors': errors}
        return render(request, 'discover/base_people.html', context)


def corpbodies(request):
    from .forms import SearchForm
    from .web_methods import get_images
    sform = SearchForm()
    images = get_images('images_others')  # record name in db query table
    context = {'search': sform, 'images': images}
    return render(request, 'discover/base_corpbodies.html', context)


def corpbodies_filtered(request):
    """Processes and renders search results for corporate bodies data. Callable only by search forms."""
    from .models import RelationType
    from . import forms
    from .models import CorpBody

    the_set = RelationType.objects.filter(domain='corps')
    corps_choices = []
    for r in the_set:
        corps_choices.append((r.relation_type, r.relation_type_label))
    nsform = forms.NodeSelectForm(dynamic_choices=corps_choices)
    sform = forms.SearchForm()
    init_choice = ['instanceof']
    error_msg = ''

    try:
        return_search_form = forms.SearchForm(request.POST)
        return_node_form = forms.NodeSelectForm(request.POST, dynamic_choices=corps_choices)
        corps = CorpBody.objects.all()
        if return_search_form.is_valid():
            results = process_search_form(return_search_form, corps)
            graph_data = graph.load_graph(results['filtered'], init_choice, 'corps')
            curr_checks = []
        elif return_node_form.is_valid():
            results = process_node_form(return_node_form, corps, 'corps')
            graph_data = graph.load_graph(results['filtered'], results['choices'], 'corps')
            curr_checks = results['checks']
        else:
            # creates empty stubs for form rendering w/o awkward error handling.
            results = process_invalid_forms('corpbodies_filtered')
            error_msg = results['message']
            graph_data = graph.load_graph(results['filtered'], init_choice, 'corps')
            curr_checks = []

        context = {'filtered_corps': results['unique'], 'search': sform,
                   'num': results['num'], 'nodes': graph_data['nodes'], 'edges': graph_data['edges'],
                   'select': nsform, 'properties': graph_data['properties'],
                   'string': results['search_str'], 'checks': curr_checks, 'errors': error_msg}

        return render(request, 'discover/base_corpbodies_filtered.html', context)

    except Exception as e:
        errors = catch_err(e, 'corpbodies_filtered')
        context = {'search': sform, 'errors': errors}
        return render(request, 'discover/base_corpbodies_filtered.html', context)


def collections(request):
    from .forms import SearchForm
    sform = SearchForm()
    context = {'search': sform}
    return render(request, 'discover/base_collections.html', context)


def collections_filtered(request):
    """Processes and renders search results for collections data. Callable only by search forms."""
    from .forms import SearchForm, RestrictSubjectForm, NodeSelectForm
    from .models import RelationType

    the_set = RelationType.objects.filter(domain='collections')
    coll_choices = []
    for r in the_set:
        coll_choices.append((r.relation_type, r.relation_type_label))
    nsform = NodeSelectForm(dynamic_choices=coll_choices)
    sform = SearchForm()
    init_choice = ['subject']
    error_msg = ''

    try:
        colls = Collection.objects.all()
        return_rform = RestrictSubjectForm(request.POST)  # called via subject filtering on base_subjects_filtered.html
        return_sform = SearchForm(request.POST)  # page called via search
        return_nsform = NodeSelectForm(request.POST, dynamic_choices=coll_choices)    # called via graph node selection

        # determine which form has been returned
        if return_rform.is_valid():  # restrict-subject form on subjects_filtered.html
            results = process_restrictsubj_form(return_rform, colls)
            graph_data = graph.load_graph(results['filtered'], init_choice, 'collections')
            curr_checks = []
        elif return_sform.is_valid():
            results = process_search_form(return_sform, colls, 'colltypelabel')
            graph_data = graph.load_graph(results['filtered'], init_choice, 'collections')
            curr_checks = []
        elif return_nsform.is_valid():
            results = process_node_form(return_nsform, colls, 'collections')
            graph_data = graph.load_graph(results['filtered'], results['choices'], 'collections')
            curr_checks = results['checks']
        else:
            # creates empty stubs for form rendering w/o awkward error handling.
            results = process_invalid_forms('collections_filtered')
            error_msg = results['message']
            graph_data = graph.load_graph(results['filtered'], init_choice, 'collections')
            curr_checks = []

        context = {'filtered_collections': results['unique'], 'search': sform,
                   'num': results['num'], 'nodes': graph_data['nodes'], 'edges': graph_data['edges'],
                   'select': nsform, 'properties': graph_data['properties'],
                   'string': results['search_str'], 'checks': curr_checks, 'errors': error_msg}

        return render(request, 'discover/base_collections_filtered.html', context)

    except Exception as e:
        errors = catch_err(e, 'collections_filtered')
        context = {'search': sform, 'errors': errors}
        return render(request, 'discover/base_collections_filtered.html', context)


def oralhistories(request):
    from .forms import SearchForm
    sform = SearchForm()
    context = {'search': sform}
    return render(request, 'discover/base_oralhistories.html', context)


def oralhistories_filtered(request):
    """Processes and renders search results for oral histories data. Callable only by search or node form."""
    from .forms import SearchForm, NodeSelectForm
    from .models import OralHistory, RelationType
    from . import graph

    the_set = RelationType.objects.filter(domain='orals')
    orals_choices = []
    for r in the_set:
        orals_choices.append((r.relation_type, r.relation_type_label))
    nsform = NodeSelectForm(dynamic_choices=orals_choices)
    sform = SearchForm()
    init_choice = ['subject']
    error_msg = ''

    try:
        orals = OralHistory.objects.all()
        return_sform = SearchForm(request.POST)  # page called via search
        return_nsform = NodeSelectForm(request.POST, dynamic_choices=orals_choices)    # called via graph node selection

        if return_sform.is_valid():
            results = process_search_form(return_sform, orals, 'inventorynum')
            graph_data = graph.load_graph(results['filtered'], init_choice, 'orals')
            curr_checks = []
        elif return_nsform.is_valid():
            results = process_node_form(return_nsform, orals, 'orals')
            graph_data = graph.load_graph(results['filtered'], results['choices'], 'orals')
            curr_checks = results['checks']
        else:
            # creates empty stubs for form rendering w/o awkward error handling.
            results = process_invalid_forms('oralhistories_filtered')
            error_msg = results['message']
            graph_data = graph.load_graph(results['filtered'], init_choice, 'orals')
            curr_checks = []

        context = {'filtered_orals': results['unique'], 'search': sform,
                   'num': results['num'], 'nodes': graph_data['nodes'], 'edges': graph_data['edges'],
                   'select': nsform, 'properties': graph_data['properties'],
                   'string': results['search_str'], 'checks': curr_checks, 'errors': error_msg}

        return render(request, 'discover/base_oralhistories_filtered.html', context)
    except Exception as e:
        errors = catch_err(e, 'oralhistories_filtered')
        context = {'search': sform, 'errors': errors}
        return render(request, 'discover/base_oralhistories_filtered.html', context)


def about(request):
    return render(request, 'discover/base_about.html')


def subjects(request):
    from .forms import SearchForm
    # subj = Subject.objects.all().order_by('subjectlabel')
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


def item(request, item_code):
    details = web_methods.get_item_details(item_code)
    the_item = details[0]
    context = {'details': details, 'item': the_item.item_label, 'itemdesc': the_item.item_desc}
    return render(request, 'discover/base_item.html', context)


def process_node_form(nsform, qset, domain):
    """Private function for form processing."""
    # generic node selection form handler for all views that use it
    from .web_methods import reduce_search_results
    from .models import RelationType
    global mod_curr_query
    global mod_curr_search_str
    # get selected checkboxes for relation types in graph; grab other needed values
    the_choices = nsform.cleaned_data['relation_types']
    the_string = nsform.cleaned_data['shape_label']
    the_color = nsform.cleaned_data['color_type']

    # get checkbox select order for domain from db; gets applied on template render
    dom = RelationType.objects.filter(domain=domain)
    choice_sel = []
    for c in the_choices:
        o = dom.get(relation_type=c)
        if o:
            choice_sel.append(o.list_order)

    # filter according to unique node, based on color type
    if the_color == RelColor.item.value:
        filtset = qset.filter(item_id__exact=nsform.cleaned_data['selected_text']).order_by('item_id')
        uniqueset = reduce_search_results(filtset)
        mod_curr_query = filtset
    elif the_color == RelColor.occup.value:
        filtset = qset.filter(occupation_id__exact=nsform.cleaned_data['selected_text'])
        uniqueset = reduce_search_results(filtset)
        mod_curr_query = filtset
    elif the_color == RelColor.fow.value:
        filtset = qset.filter(fieldofwork_id__exact=nsform.cleaned_data['selected_text'])
        uniqueset = reduce_search_results(filtset)
        mod_curr_query = filtset
    elif the_color == RelColor.pob.value:
        filtset = qset.filter(placeofbirth_id__exact=nsform.cleaned_data['selected_text'])
        uniqueset = reduce_search_results(filtset)
        mod_curr_query = filtset
    elif the_color == RelColor.pod.value:
        filtset = qset.filter(placeofdeath_id__exact=nsform.cleaned_data['selected_text'])
        uniqueset = reduce_search_results(filtset)
        mod_curr_query = filtset
    elif the_color == RelColor.subj.value:
        filtset = qset.filter(subject_id__exact=nsform.cleaned_data['selected_text'])
        mod_curr_query = filtset
        if domain == 'collections':
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
        mod_curr_query = filtset
    else:
        filtset = mod_curr_query  # new relations have been specified and no nodes have been selected.
        uniqueset = reduce_search_results(filtset)

    num = uniqueset.__len__()
    mod_curr_search_str += " > " + the_string

    return {'filtered': filtset, 'unique': uniqueset, 'num': num,
            'search_str': mod_curr_search_str, 'choices': the_choices, 'checks': choice_sel}


def process_search_form(sform, qset, special_col=None):
    """Private function for form processing. Generic form handler for all views that use the search form."""
    from django.db.models import Q
    from .web_methods import reduce_search_results

    global mod_curr_query
    global mod_curr_search_str

    filtset = qset.filter(Q(itemdesc__icontains=sform.cleaned_data['search_text']) |
                          Q(itemlabel__icontains=sform.cleaned_data['search_text']))

    if special_col:
        uniqueset = reduce_search_results(filtset, special_col)
    else:
        uniqueset = reduce_search_results(filtset)
    num = uniqueset.__len__()
    the_string = "'" + sform.cleaned_data['search_text'] + "'"
    mod_curr_query = filtset
    mod_curr_search_str = the_string

    return {'filtered': filtset, 'unique': uniqueset, 'num': num, 'search_str': the_string}


def process_restrictsubj_form(rsform, qset):
    """Private function for form processing."""
    # Posted from the Subjects page only. Processed by subjects_filtered and corp_filtered.
    from .web_methods import reduce_search_results

    global mod_curr_query
    global mod_curr_search_str

    qcodes = rsform.cleaned_data['restrict_text'].split(',')
    qcodes.remove('')  # remove empty member that causes trailing comma
    search_str = rsform.cleaned_data['restrict_labels'].split(',')
    search_str.remove('')

    filtset = qset.filter(subject_id__in=qcodes)
    mod_curr_query = filtset
    mod_curr_search_str = str(search_str)
    uniqueset = reduce_search_results(filtset, 'colltypelabel')
    num = uniqueset.__len__()

    return {'filtered': filtset, 'unique': uniqueset, 'num': num, 'search_str': mod_curr_search_str}


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



