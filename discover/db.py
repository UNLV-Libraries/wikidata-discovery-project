"""
This module handles all CREATE/UPDATE/DELETE transactions with the database tables,
at least for version 1 of the prototype.
"""
from .wd_utils import catch_err


def cache_people():
    from . import sparql
    try:
        people_json = sparql.build_wd_query('people')
        write_people(people_json)
    except BaseException as e:
        catch_err(e, 'cache_people')


def write_people(people_json):
    # internal function: parse JSON and save to Person table
    from .models import Person
    import re
    from django.utils.safestring import mark_safe

    # Delete existing table records
    Person.objects.all().delete()

    n = 0

    for r in people_json["results"]["bindings"]:
        p = Person()  # construct empty object
        n += 1
        try:
            item = r.get("item", {}).get("value")
            item_id = re.split(r'/', item).pop()
            p.item_id = item_id  # must be there
            p.image = mark_safe(supply_val(r.get('image', {}).get('value'), 'string'))
            p.itemlabel = r.get("itemLabel", {}).get("value")  # must be there
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
            fow = supply_val(r.get('fieldOfWork', {}).get('value'), 'string')
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
        except BaseException as e:
            catch_err(e, 'write_people')
    return n


def cache_corp_bodies():
    """Queries SPARQL endpoint and writes results to db with the CorpBody object."""
    from . import sparql
    try:
        corp_json = sparql.build_wd_query('corp_bodies')
        write_corp_bodies(corp_json)
    except Exception as e:
        catch_err(e, 'cache_corp_bodies')


def write_corp_bodies(corp_json):
    """Internal function that writes json values to db. Call db.cache_corp_bodies instead."""
    from .models import CorpBody
    import re
    from django.utils.safestring import mark_safe

    # clear yesterday's cache
    CorpBody.objects.all().delete()
    n = 0

    for r in corp_json["results"]["bindings"]:
        c = CorpBody()  # construct empty object
        n += 1
        try:
            item = r.get("item", {}).get("value")
            item_id = re.split(r'/', item).pop()
            c.item_id = item_id  # must be there
            c.itemlabel = r.get("itemLabel", {}).get("value")[:99]  # must be there
            item_desc = supply_val(r.get("itemDescription", {}).get('value'), 'string')
            c.itemdesc = item_desc[:199]
            c.streetaddress = supply_val(r.get("streetAddress", {}).get("value"), 'string')
            inst = supply_val(r.get('instanceOf', {}).get('value'), 'string')
            if not inst.__len__() <= 0:
                instval = re.split(r'/', inst).pop()
                c.instanceof_id = instval
                c.instanceoflabel = r.get('instanceOfLabel', {}).get('value')
            incept = supply_val(r.get('inception', {}).get('value'), 'datetime')[:10]
            if not incept == 'none':
                c.inception = incept
            dissolved = supply_val(r.get('dissolved', {}).get('value'), 'datetime')[:10]
            if not dissolved == 'none':
                c.dissolved = dissolved
            doo = supply_val(r.get('dateOfOpening', {}).get('value'), 'datetime')[:10]
            if not doo == 'none':
                c.dateofopening = doo
            doc = supply_val(r.get('dateOfClosure', {}).get('value'), 'datetime')[:10]
            if not doc == 'none':
                c.dateofclosure = doc
            c.website = supply_val(r.get('website', {}).get('value'), 'string')
            loc = supply_val(r.get('location', {}).get('value'), 'string')
            if loc.__len__() <= 0:
                pass
            else:
                locval = re.split(r'/', loc).pop()
                c.location = locval
                c.locationlabel = r.get('locationLabel', {}).get('value')
            c.coordinates = supply_val(r.get('coordinates', {}).get('value'), 'string')
            subj = supply_val(r.get('subject', {}).get('value'), 'string')
            if subj.__len__() <= 0:
                pass
            else:
                subjval = re.split(r'/', subj).pop()
                c.subject_id = subjval
                c.subjectlabel = r.get('subjectLabel', {}).get('value')
            p_org = supply_val(r.get('parentOrg', {}).get('value'), 'string')
            if p_org.__len__() <= 0:
                pass
            else:
                p_orgval = re.split(r'/', p_org).pop()
                c.parentorg_id = p_orgval
                c.parentorglabel = r.get('parentOrgLabel', {}).get('value')[:49]
            owner = supply_val(r.get('owner', {}).get('value'), 'string')
            if owner.__len__() <= 0:
                pass
            else:
                ownerval = re.split(r'/', owner).pop()
                c.owner_id = ownerval
                c.ownerlabel = r.get('ownerLabel', {}).get('value')
                c.ownerdesc = r.get('ownerDescription', {}).get('value')
            c.collection = supply_val(r.get('collection', {}).get('value'), 'string')
            c.inventorynum = supply_val(r.get('inventoryNum', {}).get('value'), 'string')
            c.describedat = supply_val(r.get('describedAt', {}).get('value'), 'string')

            c.save()  # object data saved to database
        except TypeError:
            continue
        except Exception as e:
            catch_err(e, 'write_corp_bodies')
    return n


def cache_collections():
    from . import sparql
    try:
        coll_json = sparql.build_wd_query('collections')
        write_collections(coll_json)
    except Exception as e:
        catch_err(e, 'cache_collections')


def write_collections(collections_json):
    # internal function: receive the collections query in wikidata and write results to db.
    from .models import Collection
    import re
    from django.utils.safestring import mark_safe
    # Delete existing table records
    Collection.objects.all().delete()

    n = 0
    for r in collections_json["results"]["bindings"]:
        c = Collection()  # construct empty object
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
    try:
        subject_json = sparql.build_wd_query('subjects')
        write_subjects(subject_json)
    except BaseException as e:
        catch_err(e, 'cache_subjects')


def write_subjects(json_dict):
    from .models import Subject
    import re

    Subject.objects.all().delete()
    n = 0

    for r in json_dict["results"]["bindings"]:
        s = Subject()

        subject_raw = r.get("subject", {}).get("value")
        s.subject_id = re.split(r'/', subject_raw).pop()
        s.subjectlabel = r.get("subjectLabel", {}).get("value")

        s.save()
        n += 1
    return n


def cache_oral_histories():
    from . import sparql
    try:
        oralh_json = sparql.build_wd_query('oralhistories')
        write_oral_histories(oralh_json)
    except BaseException as e:
        catch_err(e, 'cache_oral_histories')


def write_oral_histories(json_dict):
    from .models import OralHistory
    import re
    n = 0
    OralHistory.objects.all().delete()
    for r in json_dict['results']['bindings']:
        o = OralHistory()

        item_raw = r.get('item', {}).get('value')
        o.item_id = re.split(r'/', item_raw).pop()
        o.itemlabel = supply_val(r.get('itemLabel', {}).get('value'), 'string')
        oh = supply_val(r.get('oralHistory', {}).get('value'), 'string')
        if oh.__len__() == 0:
            o.itemdesc = r.get('itemDescription', {}).get('value')
        else:
            o.itemdesc = oh
        subj = supply_val(r.get('subject', {}).get('value'), 'string')
        if not subj.__len__() == 0:
            o.subject_id = re.split(r'/', subj).pop()
            o.subjectlabel = r.get('subjectLabel', {}).get('value')
        o.inventorynum = supply_val(r.get('inventoryNum', {}).get('value'), 'string')
        o.describedat = supply_val(r.get('describedAt', {}).get('value'), 'string')
        o.save()
        n += 1

    return n


def supply_val(val, the_type):
    """
    Internal function to supply slug value when writing
    to a table from a ragged json array.
    """
    if val:
        return val
    else:
        if the_type == 'datetime':
            d = 'none'
            return d
        elif the_type == 'string':
            return ''
        elif the_type == 'numeric':
            return 0


