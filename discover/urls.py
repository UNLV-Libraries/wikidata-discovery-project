
from django.urls import path
from discover import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('people/', views.people, name='people'),
    path('people_filtered/', views.people_filtered, name='people_filtered'),
    path('collections/', views.collections, name='collections'),
    path('collections_filtered/', views.collections_filtered, name='collections_filtered'),
    path('subjects/', views.subjects, name='subjects'),
    path('subjects_filtered/', views.subjects_filtered, name='subjects_filtered'),
    path('basic_vis/', views.basic_vis, name='basic_vis'),
    path('item/<str:item_code>/', views.item, name='item'),
    path('about/', views.about, name='about'),
]


