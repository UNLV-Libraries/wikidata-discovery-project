import datetime
from django.shortcuts import render
from . import graph
from . import web_models
from .models import Collection, Subject
import logging
the_log = logging.getLogger(__name__)

# globally accessible table caches
# todo: figure out caching issue: Django caching framework...

def home(request):
    return render(request, 'discover/base_home.html')

def people(request):
    from .forms import SearchForm, NodeSelectForm
    sform = SearchForm()
    nsform = NodeSelectForm()
    context = {'search': sform, 'select': nsform}
    return render(request, 'discover/base_people.html', context)

def people_filtered(request):
    from .forms import SearchForm, NodeSelectForm
    from .models import Person
    # todo: refactor search & select form construction and filtering into separate method?
    try:
        the_string = ''
        return_search_form = SearchForm(request.POST)
        return_node_form = NodeSelectForm(request.POST)
        nsform = NodeSelectForm()
        sform = SearchForm()
        peeps = Person.objects.all()
        if return_search_form.is_valid():
            results = process_search_form(return_search_form, peeps)
        elif return_node_form.is_valid():
            results = process_node_form(return_node_form, peeps, 'people')
        else:
            people(request) # return landing page url if filter url called some other way, e.g. typing in addr bar.

        graph_data = graph.load_people(results['filtered'], 'occupation')
        context = {'filtered_people': results['filtered'], 'search': sform,
                   'num': results['num'], 'nodes': graph_data['nodes'], 'edges': graph_data['edges'], 'select': nsform,
                   'properties': graph_data['properties'], 'string': results['search_str']}
        return render(request, 'discover/base_people_filtered.html', context)
    except Exception as e:
        errors = catch_err(e, 'people_filtered')
        context = {'errors': errors}
        return render(request, 'discover/base_people_filtered.html', context)

def collections(request):
    from .forms import SearchForm, NodeSelectForm
    sform = SearchForm()
    nsform = NodeSelectForm()
    context = {'search': sform, 'select': nsform}
    return render(request, 'discover/base_collections.html', context)

def collections_filtered(request):
    from .forms import SearchForm, RestrictSubjectForm, NodeSelectForm
    from .graph import load_collections
    try:
        colls = Collection.objects.all()
        sform = SearchForm()
        nsform = NodeSelectForm()
        return_rform = RestrictSubjectForm(request.POST) #page called via subject filtering
        return_sform = SearchForm(request.POST) #page called via search
        return_nsform = NodeSelectForm(request.POST) # called via graph node selection

        # determine which form has been returned
        if return_rform.is_valid():
            results = process_restrictsubj_form(return_rform, colls)
            graph_data = load_collections(results['filtered'], 'mainsubject')

        elif return_nsform.is_valid():
            results = process_node_form(return_nsform, colls, 'collections')
            graph_data = load_collections(results['filtered'], 'mainsubject')

        elif return_sform.is_valid():
            results = process_search_form(return_sform, colls)
            graph_data = load_collections(results['filtered'], 'mainsubject')
        else:
            collections(request) # page called w/o submitting a form. Reload landing page.

        context = {'filtered_collections': results['unique'], 'search': sform, 'select': nsform,
                   'string': results['search_str'], 'num': results['num'], 'nodes': graph_data['nodes'],
                   'edges': graph_data['edges'], 'properties': graph_data['properties']}

        return render(request, 'discover/base_collections_filtered.html', context)
    except Exception as e:
        errors = catch_err(e, 'subjects_filtered')
        context = {'errors': errors}
        return render(request, 'discover/base_people_filtered.html', context)

def oralhistories(request):
    from .forms import SearchForm
    sform = SearchForm()
    context = {'search': sform}
    return render(request, 'discover/base_oralhistories.html', context)

def oralhistories_filtered(request):
    from .forms import SearchForm, NodeSelectForm
    from django.db.models import Q
    from .models import OralHistory
    from .web_models import reduce_search_results

    context = {}
    num = 0
    return_search_form = SearchForm(request.POST)
    return_node_form = NodeSelectForm(request.POST)
    nsform = NodeSelectForm()
    sform = SearchForm()
    orals = OralHistory.objects.all()

    if return_search_form.is_valid():
        the_string = return_search_form.cleaned_data['search_text']
        filtorals = orals.filter(Q(itemlabel__icontains=the_string) |
                                 Q(itemdesc__icontains=the_string)).order_by('item_id')
        # uniqueorals = reduce_search_results(filtorals)
        num = filtorals.count()
        context = {'filtered_orals': filtorals, 'search': sform, 'select': nsform,
                   'string': the_string, 'num': num}

    elif return_node_form.is_valid():
        the_string = return_node_form.cleaned_data['shape_label']
        if return_node_form.cleaned_data['shape_type'] == 'ellipse':
            filtorals = orals.filter(occupation_id__exact=return_node_form.cleaned_data['selected_text'])
            uniqueorals = reduce_search_results(filtorals)
            num = uniqueorals.__len__()
            context = {'filtered_orals': uniqueorals, 'search':sform, 'num': num, 'select': nsform,
                       'string': the_string}
        else:
            filtorals = orals.filter(item_id__exact=return_node_form.cleaned_data['selected_text'])
            num = filtorals.count()
            # netobjs = graph.load_oral_histories(filtorals, 'occupation')
            context = {'filtered_orals': filtorals, 'search': sform, 'num': num,  'select': nsform, 'string': the_string}
            # 'nodes': netobjs['nodes'], 'edges': netobjs['edges'], 'properties': netobjs['properties'],

    return render(request, 'discover/base_oralhistories_filtered.html', context)
def about(request):
    return render(request, 'discover/base_about.html')

def subjects(request):
    from .forms import SearchForm

    subj = Subject.objects.all().order_by('subjectlabel')
    sform = SearchForm()
    context = {'subjects': subj, 'search': sform}
    return render(request, 'discover/base_subjects.html', context)

def subjects_filtered(request):
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
    details = web_models.get_item_details(item_code)
    the_item = details[0]
    context = {'details': details, 'item': the_item.item_label}
    return render(request, 'discover/base_item.html', context)

def process_node_form(nsform, qset, vw_called_from):
# generic form handler for all views that use it
    from .web_models import reduce_search_results
    the_string = nsform.cleaned_data['shape_label']
    if nsform.cleaned_data['shape_type'] == 'ellipse':
        if vw_called_from == 'people':
            filtset = qset.filter(occupation_id__exact=nsform.cleaned_data['selected_text']).order_by('item_id')
        elif vw_called_from == 'collections':
            filtset = qset.filter(subject_id__exact=nsform.cleaned_data['selected_text']).order_by('item_id')

        uniqueset = reduce_search_results(filtset)
        num = uniqueset.__len__()
    else:
        filtset = qset.filter(item_id__exact=nsform.cleaned_data['selected_text'])
        uniqueset = filtset #duplicating to support standard return statement.
        num = uniqueset.count()

    return {"filtered": filtset, 'unique': uniqueset, 'num': num, 'search_str': the_string}

def process_search_form(sform, qset):
    # generic form handler for all views that use it
    from django.db.models import Q
    from .web_models import reduce_search_results
    filtset = qset.filter(Q(itemdesc__icontains=sform.cleaned_data['search_text']) |
                             Q(itemlabel__icontains=sform.cleaned_data['search_text'])).order_by('item_id')
    uniqueset = reduce_search_results(filtset)
    num = uniqueset.__len__()
    the_string = "'" + sform.cleaned_data['search_text'] + "'"
    return {'filtered': filtset, 'unique': uniqueset, 'num': num, 'search_str': the_string}

def process_restrictsubj_form(rsform, qset):
    # Posted from the Subjects page only. Processed by subjects_filtered and corp_filtered.
    from .web_models import reduce_search_results
    # todo: switch search string message to labels
    qcodes = rsform.cleaned_data['restrict_text'].split(',')
    qcodes.remove('')  # remove empty member that causes trailing comma

    filtset = qset.filter(subject_id__in=qcodes).order_by('item_id')
    uniqueset = reduce_search_results(filtset, 'colltypelabel')
    num = filtset.count()
    # filtset is returned twice in this case bec. it's already unique and a
    # unique entry is required.
    return {'filtered': filtset, 'unique': uniqueset, 'num': num, 'search_str': qcodes.join()}

def catch_err(e, proc=None):
    # generic handler for error messages and logging
    dt = datetime.datetime.now()
    try:
        # e contains BaseException
        if e.args[0] == 1064:  # bad search string that SQL doesn't like.
            the_message = "You've used an invalid search string. Try again."
        else:
            the_message = str(e.args)
        the_log.error(str(dt) + ": " + the_message + str(e.args[0] + ' ' + proc))
        return "Error: " + the_message
    except Exception as internal_e:
        the_log.error(str(dt) + ": " + str(internal_e.args) + ", " + str(internal_e.args[0]))
        return "There was an error while handling an application exception. Contact your administrator."
