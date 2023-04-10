from django.test import TestCase
import unittest
from django.test import Client
from .forms import SearchForm, NodeSelectForm, RestrictSubjectForm

class PeopleTest(unittest.TestCase):
    def setUp(self):
        self.client = Client()

    def test_details(self):
        response = self.client.get("/discover/people/")
        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
        # Check that the rendered context contain.
        self.assertIsInstance(response.context["search"], SearchForm)
        self.assertIsInstance(response.context['select'], NodeSelectForm)
