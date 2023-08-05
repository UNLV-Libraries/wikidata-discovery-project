
from django.urls import path
from discover import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('people/', views.people, name='people'),
    path('people_filtered/', views.process_search, name='process_search_people'),
    path('corps/', views.corp_bodies, name='corps'),
    path('corps_filtered/', views.process_search, name='process_search_corps'),
    path('collections/', views.collections, name='collections'),
    path('collections_filtered/', views.process_search, name='process_search_collections'),
    path('orals/', views.oral_histories, name='orals'),
    path('orals_filtered/', views.process_search, name='process_search_orals'),
    path('subjects/', views.subjects, name='subjects'),
    path('subjects_filtered/', views.subjects_filtered, name='subjects_filtered'),
    path('<str:app_class>/item/<str:item_code>/', views.item, name='item'),
    path('about/', views.about, name='about'),
    path('utils/', views.utilities, name='utils'),
    path('app_error/', views.error_message, name='app_error'),
]
