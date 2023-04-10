import datetime
import sys

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
    from django.db.models import Q, QuerySet
    from .web_models import reduce_search_results
    try:
        the_string = ''
        filtpeeps = QuerySet()
        num = 0
        return_search_form = SearchForm(request.POST)
        return_node_form = NodeSelectForm(request.POST)
        nsform = NodeSelectForm()
        sform = SearchForm()
        peeps = Person.objects.all()
        if return_search_form.is_valid():
            filtpeeps = peeps.filter(Q(itemdesc__icontains=return_search_form.cleaned_data['search_text']) |
                                     Q(itemlabel__icontains=return_search_form.cleaned_data['search_text']))
            uniquepeeps = reduce_search_results(filtpeeps)
            num = uniquepeeps.__len__()
            the_string = "'" + return_search_form.cleaned_data['search_text'] + "'"
        elif return_node_form.is_valid():
            the_string = return_node_form.cleaned_data['shape_label']
            if return_node_form.cleaned_data['shape_type'] == 'ellipse':
                filtpeeps = peeps.filter(occupation_id__exact=return_node_form.cleaned_data['selected_text'])
                uniquepeeps = reduce_search_results(filtpeeps)
                num = uniquepeeps.__len__()
            else:
                uniquepeeps = peeps.filter(item_id__exact=return_node_form.cleaned_data['selected_text'])
                num = uniquepeeps.count()
        netobjs = graph.load_people(filtpeeps, 'occupation')
        context = {'filtered_people': filtpeeps, 'search': sform,
                   'num': num, 'nodes': netobjs['nodes'], 'edges': netobjs['edges'], 'select': nsform,
                   'properties': netobjs['properties'], 'string': the_string}
        return render(request, 'discover/base_people_filtered.html', context)
    except BaseException as e:
        errors = catch_err(e)
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
    from django.db.models import Q
    from .web_models import reduce_search_results
    try:
        colls = Collection.objects.all()
        sform = SearchForm()
        nsform = NodeSelectForm()
        return_rform = RestrictSubjectForm(request.POST) #page called via subject filtering
        return_sform = SearchForm(request.POST) #page called via search
        context = {}
        the_string = ''
        if return_rform.is_valid():
            qcodes = return_rform.cleaned_data['restrict_text'].split(',')
            qcodes.remove('') #remove empty member that causes trailing comma
            the_string = qcodes
            n = 1
            for q in qcodes:
                if n == qcodes.__len__():
                    q = '"' + q + '"'
                else:
                    q = '"' + q + '"' + ", "
                n += 1

            filtcolls2 = colls.filter(subject_id__in=qcodes)
            num = filtcolls2.count()
            context = {'filtered_collections': filtcolls2, 'search': sform, 'select': nsform,
                       'string': the_string, 'num': num}

        elif return_sform.is_valid():
            the_string = return_sform.cleaned_data['search_text']
            filtcolls = colls.filter(Q(itemdesc__icontains=the_string) |
                                               Q(itemlabel__icontains=the_string)).order_by('item_id')
            uniquecolls = reduce_search_results(filtcolls, 'colltypelabel')
            num = uniquecolls.__len__()
            context = {'filtered_collections': uniquecolls, 'search': sform, 'select': nsform,
                       'string': the_string, 'num': num}

        return render(request, 'discover/base_collections_filtered.html', context)
    except BaseException as e:
        errors = catch_err(e)
        context = {'errors': errors}
        return render(request, 'discover/base_people_filtered.html', context)

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
    except BaseException as e:
        errors = catch_err(e)
        context = {'errors': errors}
        return render(request, 'discover/base_people_filtered.html', context)

def item(request, item_code):
    details = web_models.get_item_details(item_code)
    the_item = details[0]
    context = {'details': details, 'item': the_item.item_label}
    return render(request, 'discover/base_item.html', context)

def catch_err(e):
    dt = datetime.datetime.now()
    try:
        # e contains BaseException
        if e.args[0] == 1064:  # bad search string that SQL doesn't like.
            the_message = "You've used an invalid search string. Try again."
        else:
            the_message = str(e.args)
        the_log.error(str(dt) + ": " + the_message)
        return "Error: " + the_message
    except BaseException as internal_e:
        the_log.error(str(internal_e.args))
        return "There was an error while handling an application exception. Contact your administrator."
