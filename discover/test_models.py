from django.test import TestCase
from .models import RelationType, Collection, CorpBody, Person, OralHistory, WdQuery, Filter


class RelationTypeTest(TestCase):
    def setUp(self):
        self.instance = RelationType()

    def test_details(self):
        self.assertIsInstance(self.instance, RelationType)


class FilterTest(TestCase):
    def setUp(self):
        self.instance = Filter()

    def test_details(self):
        self.assertIsInstance(self.instance, Filter)


class WdQueryTest(TestCase):
    def setUp(self):
        self.instance = WdQuery()

    def test_details(self):
        self.assertIsInstance(self.instance, WdQuery)


class CollectionTest(TestCase):
    def setUp(self):
        self.instance = Collection()

    def test_details(self):
        self.assertIsInstance(self.instance, Collection)


class CorpBodyTest(TestCase):
    def setUp(self):
        self.instance = CorpBody()

    def test_details(self):
        self.assertIsInstance(self.instance, CorpBody)


class OralHistoryTest(TestCase):
    def setUp(self):
        self.instance = OralHistory()

    def test_details(self):
        self.assertIsInstance(self.instance, OralHistory)


class PersonTest(TestCase):
    def setUp(self):
        self.instance = Person()

    def test_details(self):
        self.assertIsInstance(self.instance, Person)

