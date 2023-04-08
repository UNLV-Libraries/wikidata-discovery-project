"""
This module handles all CREATE/UPDATE/DELETE transactions with the database, at least for version 1 of the prototype.
"""
import sys

def cache_people():
    from . import sparql
    people_json = sparql.build_wd_query('people')
    write_people(people_json)

def write_people(people_json):
    # internal function: parse JSON and save to Person table
    from .models import Person
    import re
    from django.utils.safestring import mark_safe

    # Delete existing table records
    Person.objects.all().delete()

    n = 0

    for r in people_json["results"]["bindings"]:
        p = Person()  #construct empty object
        n += 1
        try:
            item = r.get("item", {}).get("value")
            item_id = re.split(r'/', item).pop()
            p.item_id = item_id #must be there
            p.image = mark_safe(supply_val(r.get('image', {}).get('value'), 'string'))
            p.itemlabel = r.get("itemLabel", {}).get("value") #must be there
            item_desc = r.get("itemDescription", {}).get('value')
            p.itemdesc = item_desc[:100]
            p.dob = supply_val(r.get("dateOfBirth", {}).get('value'), 'datetime')
            pobirth = supply_val(r.get("placeOfBirth", {}).get('value'), 'string')
            if pobirth.__len__() <= 0:
                pass
            else:
                p.placeofbirth_id = re.split(r'/', pobirth).pop()
                p.placeofbirthlabel = supply_val(r.get('placeOfBirthLabel', {}).get('value'), 'string')
            p.dateofdeath = supply_val(r.get('dateOfDeath', {}).get('value'), 'datetime')
            podeath = supply_val(r.get('placeOfDeath', {}).get('value'), "string")
            if podeath.__len__() <= 0:
                pass
            else:
                p.placeofdeath_id = re.split(r'/', podeath).pop()
                p.placeofdeathlabel = supply_val(r.get('placeOfDeathLabel', {}).get('value'), 'string')
            occ = supply_val(r.get('occupation', {}).get('value'), 'string')
            if occ.__len__() <= 0:
                pass
            else:
                p.occupation_id = supply_val(re.split(r'/', occ).pop(), 'string')
                p.occupationlabel = supply_val(r.get('occupationLabel', {}).get('value'), 'string')
            fow  = supply_val(r.get('fieldOfWork', {}).get('value'), 'string')
            if fow.__len__() <= 0:
                pass
            else:
                p.fieldofwork_id = supply_val(re.split(r'/', fow).pop(), 'string')
                p.fieldofworklabel = supply_val(r.get('fieldOfWorkLabel', {}).get('value'), 'string')
            p.motherlabel = supply_val(r.get('motherLabel', {}).get('value'), 'string')
            p.fatherlabel = supply_val(r.get('fatherLabel', {}).get('value'), 'string')
            p.siblinglabel= supply_val(r.get('siblingLabel', {}).get('value'), 'string')
            p.spouselabel = supply_val(r.get('spouseLabel', {}).get('value'), 'string')
            p.childlabel = supply_val(r.get('childLabel', {}).get('value'), 'string')
            p.relativelabel = supply_val(r.get('relativeLabel', {}).get('value'), 'string')

            p.save()
        except TypeError:
            continue
        except:
            log_exception(sys.exc_info(), "db.write_people")
    return n

def cache_collections():
    from . import sparql
    coll_json = sparql.build_wd_query('collections')
    write_collections(coll_json)

def write_collections(collections_json):
    # internal function: receive the collections query in wikidata and write results to db.
    from .models import Collection
    import re
    from django.utils.safestring import mark_safe
    # Delete existing table records
    Collection.objects.all().delete()

    n = 0
    for r in collections_json["results"]["bindings"]:
        c = Collection()  #construct empty object
        n += 1
    #try:
        item = r.get("item", {}).get("value")
        c.item_id = re.split(r'/', item).pop()
        c.itemlabel = supply_val(r.get('itemLabel', {}).get('value'), 'string')[:99]
        c.itemdesc  = supply_val(r.get('itemDescription', {}).get('value'), 'string')
        subject = r.get('subject', {}).get('value')
        c.subject_id = re.split(r'/', subject).pop()
        c.subjectlabel = supply_val(r.get('subjectLabel', {}).get('value'), 'string')[:99]
        donor = supply_val(r.get('donatedBy', {}).get('value'), 'string')
        if donor.__len__() <= 0:
            pass
        else:
            c.donatedby_id = re.split(r'/', donor).pop()
            c.donatedbylabel = supply_val(r.get('donatedByLabel', {}).get('value'), 'string')[:99]

        colltype = supply_val(r.get('instanceOf', {}).get('value'), 'string')
        if colltype.__len__() <= 0:
            pass
        else:
            c.colltypelabel = supply_val(r.get('instanceOfLabel', {}).get('value'), 'string')

        invnum = supply_val(r.get('inventoryNum', {}).get('value'), 'string')
        if invnum.__len__() <= 0:
            pass
        else:
            c.inventorynum = supply_val(r.get('inventoryNum', {}).get('value'), 'string')

        da = supply_val(r.get('describedAt', {}).get('value'), 'string')
        if da.__len__() <= 0:
            pass
        else:
            c.describedat = mark_safe(supply_val(r.get('describedAt', {}).get('value'), 'string'))

        c.save()
    #except TypeError:
        # log_exception(sys.exc_info(), "db.write_collections")
    #except:
        # log_exception(sys.exc_info(), "db.write_collections")
    return n

def cache_subjects():
    from . import sparql
    subject_json = sparql.build_wd_query('subjects')
    write_subjects(subject_json)

def write_subjects(json_dict):
    from .models import Subject
    import re

    Subject.objects.all().delete()
    n = 0

    for r in json_dict["results"]["bindings"]:
        s = Subject()

        subject_raw = r.get("subject", {}).get("value")
        s.subject_id = Subject(re.split(r'/', subject_raw).pop())
        s.subjectlabel = r.get("subjectLabel", {}).get("value")

        s.save()
        n += 1

def log_exception(e, proc: str):
    from .models import ErrorLog
    from datetime import datetime
    processbit = 0
    # create new log table object
    el = ErrorLog()

    # populate and save to table
    el.errclasstype = e[0]
    el.errvalue = e[1]
    el.stacktrace = e[2]
    el.procedure = proc
    el.timestamp = datetime.now()
    try:
        el.save(force_insert=True)
    except Exception as exc:
        processbit = -1
        raise RuntimeError("Exception logging failure.") from exc
    finally:
        print(e)
        return processbit
"""
Internal function to supply slug value when writing
to a table from a ragged json array.
"""
def supply_val(val, the_type):
    if val:
        return val
    else:
        if the_type == 'datetime':
            d = '0000-00-00T00:00:00Z'
            return d
        elif the_type == 'string':
            return ''
        elif the_type == 'numeric':
            return 0

def fuzzy_filter_test(filterval):
    from django.db.models import Q
    from .models import Person

    peeps = Person.objects.all()
    results = peeps.filter(Q(itemdesc__icontains=filterval) | Q(itemlabel__icontains=filterval))
    print(results.distinct('item_id', 'itemlabel', 'itemdesc' ))
