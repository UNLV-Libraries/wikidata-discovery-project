from django.test import TestCase
import unittest
from django.test import Client
from .forms import SearchForm, NodeSelectForm, RestrictSubjectForm


class PeopleTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_details(self):
        response = self.client.get('/discover/people/')
        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
        # Check that the rendered context contains valid form instances.
        self.assertIsInstance(response.context['search'], SearchForm)
        self.assertIsInstance(response.context['select'], NodeSelectForm)


class PeopleFilteredTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_details(self):
        # test two form inputs
        response = self.client.post('/discover/people_filtered/', {'search_text': 'Q12345'})
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/discover/people_filtered/',
                                    {'shape_type': 'ellipse', 'node_label': 'politician', 'selected_text': 'Q12345'})
        self.assertEqual(response.status_code, 200)
