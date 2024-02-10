"""
WSGI config for wikidataDiscovery project.

For more information on this file, see
"""
from django.core.wsgi import get_wsgi_application
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wikidataDiscovery.settings')
# os.environ['DJANGO_SETTINGS_MODULE'] = 'wikidataDiscovery.settings'

_application = get_wsgi_application()


def application(environ, start_response):
    return _application(environ, start_response)



