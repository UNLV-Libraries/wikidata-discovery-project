from django.test import TestCase
from django.test import Client
from .forms import SearchForm, QueueForm
from django.urls import reverse
from .models import RelationType, WdQuery, Filter


class SetUpRelationTypes:
    # test data needed for all GET test calls to application classes
    def __init__(self):
        RelationType.objects.create(app_class='people', relation_type='occupation',
                                    relation_type_label='occupation', list_order=0)
        RelationType.objects.create(app_class='corps', relation_type='instanceof',
                                    relation_type_label='category', list_order=0)
        RelationType.objects.create(app_class='collections', relation_type='subject',
                                    relation_type_label='subject', list_order=0)
        RelationType.objects.create(app_class='orals', relation_type='subject',
                                    relation_type_label='subject', list_order=0)


class UtilitiesTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_details(self):
        response = self.client.get('/discover/utils/')
        self.assertEqual(response.status_code, 200)


class OralHistoriesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.relation_types = SetUpRelationTypes()

    def test_details(self):
        response = self.client.get('/discover/orals/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['search'], SearchForm)
        self.assertIsInstance(response.context['priors'], QueueForm)


class OralsFilteredTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_details(self):
        url = reverse('process_search_orals')
        # keyword form input
        response = self.client.post(url, {'search_text': 'african'})
        self.assertEqual(response.status_code, 200)
        # Node form input
        response = self.client.post(url,
                                    {'color_type': '#b3ffb3', 'node_id': 'Q87654'})
        self.assertEqual(response.status_code, 200)
        # Queue form input
        response = self.client.post(url,
                                    {'run_qry': 'top'})
        self.assertEqual(response.status_code, 200)


class CollectionsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.relation_types = SetUpRelationTypes()

    def test_details(self):
        response = self.client.get('/discover/collections/')
        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
        # Check that the rendered context contains valid form instances.
        self.assertIsInstance(response.context['search'], SearchForm)
        self.assertIsInstance(response.context['priors'], QueueForm)


class CollectionsFilteredTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_details(self):
        url = reverse('process_search_collections')
        # keyword form input
        response = self.client.post(url, {'search_text': 'blue diamond'})
        self.assertEqual(response.status_code, 200)
        # Node form input
        response = self.client.post(url,
                                    {'color_type': '#b3ffb3', 'node_id': 'Q93947'})

        self.assertEqual(response.status_code, 200)
        # Queue form input
        response = self.client.post(url,
                                    {'run_qry': 'top'})
        self.assertEqual(response.status_code, 200)


class PeopleTest(TestCase):
    def setUp(self):
        # test data setup also tests Wikidata Query Service call as part of test_details
        self.client = Client()
        self.relation_types = SetUpRelationTypes()
        desc = 'Organization value for the on-focus-list-of-wikimedia-project property (P5008).'
        Filter.objects.create(name='filt-wm-focus-list', qcode='Q100202113', description=desc)
        txt = ('SELECT DISTINCT ?item ?itemLabel ?instanceOf ?instanceOfLabel ?itemDescription ?image WHERE '
               '{ ?item wdt:P5008 wd:~filt-wm-focus-list~ ; wdt:P31 wd:Q5 ; wdt:P31 ?instanceOf ; wdt:P18 ?image . '
               'BIND(UUID() AS ?uuid) SERVICE wikibase:label { bd:serviceParam wikibase:language \"en\". } } LIMIT 6')
        WdQuery.objects.create(querytitle='images_humans', querytext=txt)

    def test_details(self):
        response = self.client.get('/discover/people/')
        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
        # Check that the rendered context contains valid form instances.
        self.assertIsInstance(response.context['search'], SearchForm)
        self.assertIsInstance(response.context['priors'], QueueForm)


class PeopleFilteredTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_details(self):
        url = reverse('process_search_people')
        # keyword form input
        response = self.client.post(url, {'search_text': 'Ruby Duncan'})
        self.assertEqual(response.status_code, 200)
        # Node form input
        response = self.client.post(url,
                                    {'color_type': '#ff8533', 'node_id': 'Q72916'})
        self.assertEqual(response.status_code, 200)
        # Queue form input
        response = self.client.post(url,
                                    {'run_qry': 'top'})
        self.assertEqual(response.status_code, 200)


class CorpsTest(TestCase):
    def setUp(self):
        # test data setup also tests Wikidata Query Service call as part of test_details
        self.client = Client()
        self.relation_types = SetUpRelationTypes()
        desc = 'Organization value for the on-focus-list-of-wikimedia-project property (P5008).'
        Filter.objects.create(name='filt-wm-focus-list', qcode='Q100202113', description=desc)
        txt = ('SELECT DISTINCT ?item ?itemLabel ?instanceOf ?instanceOfLabel ?itemDescription ?image WHERE '
               '{ ?item wdt:P5008 wd:~filt-wm-focus-list~ ; wdt:P31 ?instanceOf; wdt:P18 ?image . '
               'FILTER(?instanceOf NOT IN (wd:Q5)) BIND(UUID() AS ?uuid) '
               'SERVICE wikibase:label { bd:serviceParam wikibase:language \"en\". } } LIMIT 4')
        WdQuery.objects.create(querytitle='images_others', querytext=txt)

    def test_details(self):
        response = self.client.get('/discover/corps/')
        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
        # Check that the rendered context contains valid form instances.
        self.assertIsInstance(response.context['search'], SearchForm)
        self.assertIsInstance(response.context['priors'], QueueForm)


class CorpsFilteredTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_details(self):
        url = reverse('process_search_corps')
        # keyword form input
        response = self.client.post(url, {'search_text': 'Derby'})
        self.assertEqual(response.status_code, 200)
        # Node form input
        response = self.client.post(url,
                                    {'color_type': '#ff1a75', 'node_id': 'Q87654'})
        self.assertEqual(response.status_code, 200)
        # Queue form input
        response = self.client.post(url,
                                    {'run_qry': 'top'})
        self.assertEqual(response.status_code, 200)
