from django.shortcuts import render
from .models import Person, Collection
from . import graph
from . import web_models

# globally accessible table caches
glb_People = Person.objects.all()
glb_Collections = Collection.objects.all()

def home(request):
    return render(request, 'discover/base_home.html')

def people(request):
    from .forms import SearchForm

    peeps = glb_People.order_by('itemlabel').distinct('item_id', 'itemlabel', 'itemdesc' )[:20]
    netobjs = graph.load_people('occupation')
    sform = SearchForm()
    context = {'people': peeps, 'nodes': netobjs['nodes'], 'edges': netobjs['edges'], 'search': sform}
    return render(request, 'discover/base_people.html', context)

def people_filtered(request):
    from .forms import SearchForm
    from .models import Person
    from django.db.models import Q

    return_form = SearchForm(request.POST)
    if return_form.is_valid():
        filtpeeps = glb_People.filter(Q(itemdesc__icontains=return_form.cleaned_data['search_text']) | Q(itemlabel__icontains=return_form.cleaned_data['search_text']))
        sform = SearchForm()
        context = {'filtered_people': filtpeeps.distinct('item_id', 'itemlabel', 'itemdesc'), 'search': sform}
        return render(request, 'discover/base_people_filtered.html', context)

def collections(request):
    from .forms import SearchForm

    colls = glb_Collections.order_by('inventorynum')[:20]
    # netobjs = graph.load_people('occupation')
    sform = SearchForm()
    context = {'collections': colls, 'search': sform}  #'nodes': netobjs['nodes'], 'edges': netobjs['edges'],
    return render(request, 'discover/base_collections.html', context)

def collections_filtered(request):
    from .forms import SearchForm
    from .models import Collection
    from django.db.models import Q

    return_form = SearchForm(request.POST)
    if return_form.is_valid():
        filtcolls = glb_Collections.filter(Q(itemdesc__icontains=return_form.cleaned_data['search_text']) | Q(itemlabel__icontains=return_form.cleaned_data['search_text']))
        sform = SearchForm()
        context = {'filtered_collections': filtcolls, 'search': sform}
        return render(request, 'discover/base_collections_filtered.html', context)

def about(request):
    return render(request, 'discover/base_about.html')

def topics(request):
    from . import web_models
    from .forms import SearchForm

    the_topics = web_models.get_topics()
    sform = SearchForm()
    context = {'topics': the_topics, 'search': sform}
    return render(request, 'discover/base_topics.html', context)

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