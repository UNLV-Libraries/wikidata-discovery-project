
from django.urls import path, include
from discover import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('people/', views.people, name='people'),
    path('collections/', views.collections, name='collections'),
    path('topics/', views.topics, name='topics'),
    path('basic_vis/', views.basic_vis, name='basic_vis'),
    path('item/<str:item_code>/', views.item, name='item'),
    path('about/', views.about, name='about'),
]


