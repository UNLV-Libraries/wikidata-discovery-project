"""The wikidata cache tables for all in-scope people, corporations, collections, oral histories, and subjects."""
from django.db import models


class Person(models.Model):
    item_id = models.CharField(max_length=20, db_index=True)  # must exist; may have duplicates.
    image = models.URLField(null=True)
    itemlabel = models.CharField(max_length=50)  # must exist; may have duplicates.
    itemdesc = models.CharField(max_length=100, null=True)
    dob = models.CharField(max_length=30, null=True)
    placeofbirth_id = models.CharField(max_length=20, null=True)
    placeofbirthlabel = models.CharField(max_length=50, null=True)
    dateofdeath = models.CharField(max_length=30, null=True)
    placeofdeath_id = models.CharField(max_length=20, null=True)
    placeofdeathlabel = models.CharField(max_length=50, null=True)
    occupation_id = models.CharField(max_length=20, null=True)
    occupationlabel = models.CharField(max_length=50, null=True)
    fieldofwork_id = models.CharField(max_length=20, null=True)
    fieldofworklabel = models.CharField(max_length=50, null=True)
    motherlabel = models.CharField(max_length=50, null=True)
    fatherlabel = models.CharField(max_length=50, null=True)
    siblinglabel = models.CharField(max_length=50, null=True)
    spouselabel = models.CharField(max_length=50, null=True)
    childlabel = models.CharField(max_length=50, null=True)
    relativelabel = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.item_id


class CorpBody(models.Model):
    item_id = models.CharField(max_length=20, db_index=True)  # must exist; may have duplicates.
    itemlabel = models.CharField(max_length=100)  # must exist; may have duplicates.
    itemdesc = models.CharField(max_length=200, null=True)
    streetaddress = models.CharField(max_length=255, null=True)
    instanceof_id = models.CharField(max_length=20, null=True)
    instanceoflabel = models.CharField(max_length=50, null=True)
    inception = models.CharField(max_length=10, null=True)
    dissolved = models.CharField(max_length=10, null=True)
    dateofopening = models.CharField(max_length=10, null=True)
    dateofclosure = models.CharField(max_length=10, null=True)
    website = models.URLField(max_length=255, null=True)
    location = models.CharField(max_length=20, null=True)
    locationlabel = models.CharField(max_length=50, null=True)
    coordinates = models.CharField(max_length=200, null=True)
    subject_id = models.CharField(max_length=20, null=True)
    subjectlabel = models.CharField(max_length=50, null=True)
    parentorg_id = models.CharField(max_length=20, null=True)
    parentorglabel = models.CharField(max_length=100, null=True)
    owner_id = models.CharField(max_length=20, null=True)
    ownerlabel = models.CharField(max_length=50, null=True)
    ownerdesc = models.CharField(max_length=200, null=True)
    collection = models.CharField(max_length=200, null=True)
    inventorynum = models.CharField(max_length=20, null=True)
    describedat = models.URLField(max_length=500, null=True)

    def __str__(self):
        return self.item_id


class Collection(models.Model):
    item_id = models.CharField(max_length=20, db_index=True)
    itemlabel = models.CharField(max_length=100, null=True)
    itemdesc = models.CharField(max_length=500, null=True)
    subject_id = models.CharField(max_length=20, null=True)
    subjectlabel = models.CharField(max_length=100, null=True)
    donatedby_id = models.CharField(max_length=20, null=True)
    donatedbylabel = models.CharField(max_length=100, null=True)
    colltypelabel = models.CharField(max_length=30, null=True)
    inventorynum = models.CharField(max_length=30, null=True)
    describedat = models.URLField(max_length=500, null=True)

    def __str__(self):
        return self.item_id


class OralHistory(models.Model):
    item_id = models.CharField(max_length=20, db_index=True)
    itemlabel = models.CharField(max_length=100, null=True)
    itemdesc = models.CharField(max_length=200, null=True)
    subject_id = models.CharField(max_length=20, null=True)
    subjectlabel = models.CharField(max_length=100, null=True)
    inventorynum = models.CharField(max_length=20, null=True)
    describedat = models.URLField(max_length=255, null=True)

    def __str__(self):
        return self.item_id


class Subject(models.Model):
    subject_id = models.CharField(max_length=20, primary_key=True)
    subjectlabel = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.subject_id


class WdQuery(models.Model):
    """Table for storing saved SPARQL queries."""
    querytitle = models.CharField(max_length=30, primary_key=True)
    querytext = models.TextField()

    def __str__(self):
        return self.querytitle


class Filter(models.Model):
    """Table for storing saved SPARQL query filters."""
    name = models.CharField(max_length=20, primary_key=True)
    qcode = models.CharField(max_length=20)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class RelationType(models.Model):
    """Stores/retrieves allowable relation types for graphing data."""
    app_class = models.CharField(max_length=20, db_index=True)
    relation_type = models.CharField(max_length=20)
    relation_type_label = models.CharField(max_length=50, null=True)
    list_order = models.IntegerField(null=True)

