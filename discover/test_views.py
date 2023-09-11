from django.test import TestCase
import unittest
from django.test import Client
from .forms import SearchForm, NodeSelectForm, QueueForm


class PeopleTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_details(self):
        response = self.client.get('/discover/people/')
        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
        # Check that the rendered context contains valid form instances.
        self.assertIsInstance(response.context['search'], SearchForm)
        self.assertIsInstance(response.context['priors'], QueueForm)


class PeopleFilteredTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_details(self):
        # Search form input
        response = self.client.post('/discover/people_filtered/', {'search_text': 'Q12345'})
        self.assertEqual(response.status_code, 200)
        # Node form input
        response = self.client.post('/discover/people_filtered/',
                                    {'shape_type': 'ellipse', 'node_label': 'politician', 'selected_text': 'Q12345'})
        self.assertEqual(response.status_code, 200)
        # Queue form input
        response = self.client.post('/discover/people_filtered/',
                                    {'run_qry': 'top'})
        self.assertEqual(response.status_code, 200)


