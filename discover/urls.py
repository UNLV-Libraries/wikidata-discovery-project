
from django.urls import path
from discover import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('people/', views.people, name='people'),
    path('people_filtered/', views.people_filtered, name='people_filtered'),
    path('corps/', views.corpbodies, name='corps'),
    path('corps_filtered/', views.corpbodies_filtered, name='corps_filtered'),
    path('collections/', views.collections, name='collections'),
    path('collections_filtered/', views.collections_filtered, name='collections_filtered'),
    path('orals/', views.oralhistories, name='orals'),
    path('orals_filtered/', views.oralhistories_filtered, name='orals_filtered'),
    path('subjects/', views.subjects, name='subjects'),
    path('subjects_filtered/', views.subjects_filtered, name='subjects_filtered'),
    path('<str:domain>/item/<str:item_code>/', views.item, name='item'),
    path('about/', views.about, name='about'),
]
