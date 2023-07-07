"""
This module handles all CREATE/UPDATE/DELETE transactions with the database tables,
at least for version 1 of the prototype.
"""
from discover.wd_utils import catch_err
from discover import sparql


def cache_people():

    try:
        people_json = sparql.build_wd_query('people')
        n = write_people(people_json)
        return n
    except Exception as e:
        catch_err(e, 'cache_people')
        return 0


def write_people(people_json):
    # internal function: parse JSON and save to Person table
    from discover.models import Person
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
            p.item_id = item_id  # required
            p.itemlabel = r.get("itemLabel", {}).get("value")  # required
            item_desc = r.get("itemDescription", {}).get('value')  # possibly required
            p.itemdesc = item_desc[:100]
            image = r.get('image', {}).get('value')
            if image:
                p.image = mark_safe(image)
            dob = r.get("dateOfBirth", {}).get('value')
            if dob:
                p.dob = dob[:10]
            pobirth = r.get("placeOfBirth", {}).get('value')
            if pobirth:
                p.placeofbirth_id = re.split(r'/', pobirth).pop()
                p.placeofbirthlabel = r.get('placeOfBirthLabel', {}).get('value')
            dodeath = r.get('dateOfDeath', {}).get('value')
            if dodeath:
                p.dateofdeath = dodeath[:10]
            podeath = r.get('placeOfDeath', {}).get('value')
            if podeath:
                p.placeofdeath_id = re.split(r'/', podeath).pop()
                p.placeofdeathlabel = r.get('placeOfDeathLabel', {}).get('value')
            occ = r.get('occupation', {}).get('value')
            if occ:
                p.occupation_id = re.split(r'/', occ).pop()
                p.occupationlabel = r.get('occupationLabel', {}).get('value')
            fow = r.get('fieldOfWork', {}).get('value')
            if fow:
                p.fieldofwork_id = re.split(r'/', fow).pop()
                p.fieldofworklabel = r.get('fieldOfWorkLabel', {}).get('value')
            p.motherlabel = r.get('motherLabel', {}).get('value')
            p.fatherlabel = r.get('fatherLabel', {}).get('value')
            p.siblinglabel = r.get('siblingLabel', {}).get('value')
            p.spouselabel = r.get('spouseLabel', {}).get('value')
            p.childlabel = r.get('childLabel', {}).get('value')
            p.relativelabel = r.get('relativeLabel', {}).get('value')

            p.save()
        except Exception as e:
            catch_err(e, 'write_people: ' + item_id)

    c = Person.objects.count()

    return [c, n]


def cache_corp_bodies():
    """Queries SPARQL endpoint and writes results to db with the CorpBody object."""
    try:
        corp_json = sparql.build_wd_query('corp_bodies')
        n = write_corp_bodies(corp_json)
        return n
    except Exception as e:
        catch_err(e, 'cache_corp_bodies')
        return 0


def write_corp_bodies(corp_json):
    """Internal function that writes json values to db. Call db.cache_corp_bodies instead."""
    from discover.models import CorpBody
    import re

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
            item_desc = r.get("itemDescription", {}).get('value')
            if item_desc:
                c.itemdesc = item_desc[:199]
            c.streetaddress = r.get("streetAddress", {}).get("value")
            inst = r.get('instanceOf', {}).get('value')
            if inst:
                instval = re.split(r'/', inst).pop()
                c.instanceof_id = instval
                c.instanceoflabel = r.get('instanceOfLabel', {}).get('value')
            inception = r.get('inception', {}).get('value')
            if inception:
                c.inception = inception[:10]
            dissolved = r.get('dissolved', {}).get('value')
            if dissolved:
                c.dissolved = dissolved[:10]
            doo = r.get('dateOfOpening', {}).get('value')
            if doo:
                c.dateofopening = doo[:10]
            doc = r.get('dateOfClosure', {}).get('value')
            if doc:
                c.dateofclosure = doc[:10]
            site = r.get('website', {}).get('value')
            if site:
                c.website = site
            loc = r.get('location', {}).get('value')
            if loc:
                locval = re.split(r'/', loc).pop()
                c.location = locval
                c.locationlabel = r.get('locationLabel', {}).get('value')
            c.coordinates = r.get('coordinates', {}).get('value')
            subj = r.get('subject', {}).get('value')
            if subj:
                subjval = re.split(r'/', subj).pop()
                c.subject_id = subjval
                c.subjectlabel = r.get('subjectLabel', {}).get('value')
            p_org = r.get('parentOrg', {}).get('value')
            if p_org:
                p_orgval = re.split(r'/', p_org).pop()
                c.parentorg_id = p_orgval
                c.parentorglabel = r.get('parentOrgLabel', {}).get('value')[:49]
            owner = r.get('owner', {}).get('value')
            if owner:
                ownerval = re.split(r'/', owner).pop()
                c.owner_id = ownerval
                c.ownerlabel = r.get('ownerLabel', {}).get('value')
                c.ownerdesc = r.get('ownerDescription', {}).get('value')
            c.collection = r.get('collection', {}).get('value')
            c.inventorynum = r.get('inventoryNum', {}).get('value')
            c.describedat = r.get('describedAt', {}).get('value')

            c.save()  # object data saved to database
        except Exception as e:
            catch_err(e, 'write_corp_bodies: ' + item_id)

    c = CorpBody.objects.count()  # get total records actually cached

    return [c, n]


def cache_collections():
    try:
        coll_json = sparql.build_wd_query('collections')
        n = write_collections(coll_json)
        return n
    except Exception as e:
        catch_err(e, 'cache_collections')
        return 0


def write_collections(collections_json):
    # internal function: receive the collections query in wikidata and write results to db.
    from discover.models import Collection
    import re
    from django.utils.safestring import mark_safe
    # Delete existing table records
    Collection.objects.all().delete()

    n = 0
    for r in collections_json["results"]["bindings"]:
        c = Collection()  # construct empty object
        n += 1
        item = r.get("item", {}).get("value")
        c.item_id = re.split(r'/', item).pop()
        c.itemlabel = r.get('itemLabel', {}).get('value')[:99]
        c.itemdesc = r.get('itemDescription', {}).get('value')
        subject = r.get('subject', {}).get('value')
        if subject:
            c.subject_id = re.split(r'/', subject).pop()
            c.subjectlabel = r.get('subjectLabel', {}).get('value')[:99]
        donor = r.get('donatedBy', {}).get('value')
        if donor:
            c.donatedby_id = re.split(r'/', donor).pop()
            c.donatedbylabel = r.get('donatedByLabel', {}).get('value')[:99]
        colltype = r.get('instanceOf', {}).get('value')
        if colltype:
            c.colltypelabel = r.get('instanceOfLabel', {}).get('value')
        invnum = r.get('inventoryNum', {}).get('value')
        if invnum:
            c.inventorynum = r.get('inventoryNum', {}).get('value')

        da = r.get('describedAt', {}).get('value')
        if da:
            c.describedat = mark_safe(r.get('describedAt', {}).get('value'))

        c.save()
    c = Collection.objects.count()

    return [c, n]


def cache_subjects():
    try:
        subject_json = sparql.build_wd_query('subjects')
        n = write_subjects(subject_json)
        return n
    except Exception as e:
        catch_err(e, 'cache_subjects')
        return 0


def write_subjects(json_dict):
    from discover.models import Subject
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

    c = Subject.objects.count()

    return [c, n]


def cache_oral_histories():
    try:
        oralh_json = sparql.build_wd_query('oralhistories')
        n = write_oral_histories(oralh_json)
        return n
    except Exception as e:
        catch_err(e, 'cache_oral_histories')
        return 0


def write_oral_histories(json_dict):
    from discover.models import OralHistory
    import re
    n = 0
    OralHistory.objects.all().delete()
    for r in json_dict['results']['bindings']:
        o = OralHistory()

        item_raw = r.get('item', {}).get('value')
        o.item_id = re.split(r'/', item_raw).pop()
        o.itemlabel = r.get('itemLabel', {}).get('value')
        oh = r.get('oralHistory', {}).get('value')
        if oh:
            o.itemdesc = oh
        else:
            o.itemdesc = r.get('itemDescription', {}).get('value')  # use in case oral history text not present.
        subj = supply_val(r.get('subject', {}).get('value'))
        if subj:
            o.subject_id = re.split(r'/', subj).pop()
            o.subjectlabel = r.get('subjectLabel', {}).get('value')
        o.inventorynum = r.get('inventoryNum', {}).get('value')
        o.describedat = r.get('describedAt', {}).get('value')
        o.save()
        n += 1

    c = OralHistory.objects.count()

    return [c, n]


def supply_val(val):
    """
    Internal function to supply 'None' value when JSON element
    is not present.
    """
    if val:
        return val
    else:
        return None
