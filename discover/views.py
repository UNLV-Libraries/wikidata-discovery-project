from django.shortcuts import render
from .models import Person
from discover import graph

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