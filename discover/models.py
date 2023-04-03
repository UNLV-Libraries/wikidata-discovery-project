"""The wikidata cache table for all in-scope people."""
from django.db import models

class Person(models.Model):
    item_id = models.CharField(max_length=20, db_index=True)  #must exist; may have duplicates.
    image = models.URLField(null=True)
    itemlabel = models.CharField(max_length=50) #must exist; may have duplicates.
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


class Collection(models.Model):
    item_id = models.CharField(max_length=20, db_index=True)
    itemlabel = models.CharField(max_length=100, null=True)
    itemdesc = models.CharField(max_length=500, null=True)
    colltypelabel = models.CharField(max_length=30, null=True)
    inventorynum = models.CharField(max_length=30, null=True)
    describedat = models.URLField(max_length=500, null=True)

    def __str__(self):
        return self.item_id

"""Table for storing saved queries."""
class WdQuery(models.Model):
    querytitle = models.CharField(max_length=30, primary_key=True)
    querytext = models.TextField()

    def __str__(self):
        return self.querytitle


'''Table for storing saved query filters.'''
class Filter(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    qcode = models.CharField(max_length=20)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ErrorLog(models.Model):
    primarykey = models.BigAutoField(primary_key=True)
    errclasstype = models.CharField(max_length=50)
    errvalue = models.CharField(max_length=20)
    stacktrace = models.TextField()
    procedure = models.CharField(max_length=30)
    timestamp = models.DateTimeField()


