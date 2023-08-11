import sys
import django
sys.path.extend(['/home/ed/PycharmProjects/wikidataDiscovery'])

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '/home/ed/PycharmProjects/wikidataDiscovery.settings')

django.setup()
print('made it.')
