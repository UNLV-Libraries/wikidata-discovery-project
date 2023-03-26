
from django.urls import path, include
from discover import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('home/', views.home, name='home'),
    path('people/', views.people, name='people'),
    path('collections/', views.collections, name='collections'),
    path('topics/', views.topics, name='topics'),
    path('about/', views.about, name='about'),
]

# + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
