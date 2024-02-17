"""
WSGI config for wikidataDiscovery project.

"""
from django.core.wsgi import get_wsgi_application
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wikidataDiscovery.settings')
# os.environ['DJANGO_SETTINGS_MODULE'] = 'wikidataDiscovery.settings'

_application = get_wsgi_application()


def application(environ, start_response):
    return _application(environ, start_response)



