from django.shortcuts import render
from . import graph
from . import web_models
from .models import Person, Collection, Subject

# globally accessible table caches
# todo: figure out caching for real

def home(request):

    return render(request, 'discover/base_home.html')

def people(request):
    from .forms import SearchForm
    peeps = Person.objects.all()
    distinctpeeps = peeps.order_by('itemlabel').distinct('item_id', 'itemlabel', 'itemdesc' )[:5]
    netobjs = graph.load_people(distinctpeeps, 'occupation')
    sform = SearchForm()
    context = {'people': distinctpeeps, 'nodes': netobjs['nodes'], 'edges': netobjs['edges'], 'search': sform}
    return render(request, 'discover/base_people.html', context)

def people_filtered(request):
    from .forms import SearchForm, NodeSelectForm
    from .models import Person
    from django.db.models import Q
    num = 0
    return_form = SearchForm(request.POST)
    selected = NodeSelectForm()
    if return_form.is_valid():
        peeps = Person.objects.all()
        filtpeeps = peeps.filter(Q(itemdesc__icontains=return_form.cleaned_data['search_text']) |
                                 Q(itemlabel__icontains=return_form.cleaned_data['search_text']))
        num = filtpeeps.distinct('item_id', 'itemlabel', 'itemdesc').count()
        sform = SearchForm()
        netobjs = graph.load_people(filtpeeps, 'occupation')
        context = {'filtered_people': filtpeeps.distinct('item_id', 'itemlabel', 'itemdesc'), 'search': sform,
                   'num': num, 'nodes': netobjs['nodes'], 'edges': netobjs['edges'], 'selected': selected,
                   'properties': netobjs['properties']}
        return render(request, 'discover/base_people_filtered.html', context)

def collections(request):
    from .forms import SearchForm
    colls = Collection.objects.all()
    distinctcolls = colls.distinct('item_id', 'itemlabel', 'itemdesc')[:20]
    # netobjs = graph.load_people('occupation')
    sform = SearchForm()
    context = {'collections': distinctcolls, 'search': sform}  #'nodes': netobjs['nodes'], 'edges': netobjs['edges'],
    return render(request, 'discover/base_collections.html', context)

def collections_filtered(request):
    from .forms import SearchForm, RestrictSubjectForm
    from django.db.models import Q

    colls = Collection.objects.all()
    sform = SearchForm()
    return_rform = RestrictSubjectForm(request.POST) #page called via subject filtering
    return_sform = SearchForm(request.POST) #page called via search
    context = {}
    the_string = ''
    if not return_rform.is_valid():
        if return_sform.is_valid():
            the_string = return_sform.cleaned_data['search_text']
            filtcolls = colls.filter(Q(itemdesc__icontains=the_string) |
                                               Q(itemlabel__icontains=the_string))
            num = filtcolls.count()
            context = {'filtered_collections': filtcolls, 'search': sform, 'string': the_string,
                       'num': num}
    else:
        qcodes = return_rform.cleaned_data['restrict_text'].split(',')
        qcodes.remove('') #remove empty member caused trailing comma
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
        context = {'filtered_collections': filtcolls2, 'search': sform, 'string': the_string,
                   'num': num}
    return render(request, 'discover/base_collections_filtered.html', context)

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

def basic_vis(request):
    # the_nodes = [{'id': 'Q107006300', 'label': 'Faye Todd', 'shape': 'circle', 'color': '#00BFFF'}, {'id': 'Q107064683', 'label': 'Claude Evans', 'shape': 'circle', 'color': '#00BFFF'}, {'id': 'Q112233', 'label': 'painter', 'shape': 'ellipse'}]
    # the_edges = [{'from': 'Q107006300', 'to': 'Q112233'}, {'from': 'Q107064683', 'to': 'Q112233'}, {'from': 'Q107064683', 'to': ''}]
    netobjs = graph.load_people('occupation')
    context = {'nodes': netobjs['nodes'], 'edges': netobjs['edges']}
    # context = {'nodes': mark_safe(the_nodes), 'edges': mark_safe(the_edges)}
    return render(request, 'discover/basic_vis.html', context)

def item(request, item_code):
    details = web_models.get_item_details(item_code)
    the_item = details[0]
    context = {'details': details, 'item': the_item.item_label}
    return render(request, 'discover/base_item.html', context)