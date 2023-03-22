from django.db import models
# ?image ?item ?itemLabel ?itemDescription ?dateOfBirth ?placeOfBirth ?placeOfBirthLabel ?dateOfDeath
# ?placeOfDeath ?placeOfDeathLabel ?occupation ?occupationLabel ?fieldOfWork ?fieldOfWorkLabel ?motherLabel
# ?fatherLabel ?siblingLabel ?spouseLabel ?childLabel ?relativeLabel

class Person(models.Model):
    item_id = models.CharField(max_length=20, primary_key=True)
    image = models.URLField()
    itemlabel = models.CharField(max_length=50)
    itemdesc = models.CharField(max_length=100)
    dob = models.DateField()
    placeofbirth_id = models.CharField(max_length=20)
    placeofbirthlabel = models.CharField(max_length=50)
    dateofdeath = models.DateField()
    placeofdeath_id = models.CharField(max_length=20)
    placeofdeathlabel = models.CharField(max_length=50)
    occupation_id = models.CharField(max_length=20)
    occupationlabel = models.CharField(max_length=50)
    fieldofwork_id = models.CharField(max_length=20)
    fieldofworklabel = models.CharField(max_length=50)
    motherlabel = models.CharField(max_length=50)
    fatherlabel = models.CharField(max_length=50)
    siblinglabel = models.CharField(max_length=50)
    spouselabel = models.CharField(max_length=50)
    childlabel = models.CharField(max_length=50)
    relativelabel = models.CharField(max_length=50)


    def __str__(self):
        return self.item_id


class WdQuery(models.Model):
    querytitle = models.CharField(max_length=30, primary_key=True)
    querytext = models.TextField()

    def __str__(self):
        return self.querytitle
