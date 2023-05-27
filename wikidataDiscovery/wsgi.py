"""
WSGI config for wikidataDiscovery project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""
import os

from django.core.wsgi import get_wsgi_application

# from django.contrib.auth.handlers.modwsgi import check_password
# from django.core.handlers.wsgi import WSGIHandler

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wikidataDiscovery.settings')
# ensures other sites running on Apache locally don't overwrite this project's settings if all are running.
os.environ['DJANGO_SETTINGS_MODULE'] = 'wikidataDiscovery.settings'
application = get_wsgi_application()
