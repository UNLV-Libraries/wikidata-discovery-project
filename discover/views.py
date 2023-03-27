from django.shortcuts import render
from .models import Person
from discover import graph
from . import web_models
def home(request):
    return render(request, 'discover/base_home.html')

def people(request):
    peeps = Person.objects.order_by('itemlabel').distinct('item_id', 'itemlabel', 'itemdesc' )[:20]
    netobjs = graph.load_people('occupation')
    context = {'people': peeps, 'nodes': netobjs['nodes'], 'edges': netobjs['edges']}
    return render(request, 'discover/base_people.html', context)

def collections(request):
    return render(request, 'discover/base_collections.html')


def about(request):
    return render(request, 'discover/base_about.html')

def topics(request):
    return render(request, 'discover/base_topics.html')

def basic_vis(request):
    from django.utils.safestring import mark_safe
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