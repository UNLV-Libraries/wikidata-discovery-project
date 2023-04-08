'''
web_models handles all on-the-fly queries to wikidata. Returned JSON is
instantiated as python objects and those are persisted in the
application session.
'''


class Item:
    item_code = ''
    item_label = ''
    prop_code = ''
    prop_label = ''
    value_code = ''
    value_label = ''

    def __init__(self, item_code):
        self.item_code = item_code

    def __str__(self):
        return self.item_code

class Subject:
    item_code = ''
    item_label = ''

    def __init__(self, item_code):
        self.item_code = item_code

    def __str__(self):
        return self.item_code

def load_item_details(json_dict):
    # Binds only to the "item" query saved in discover_wdquery.
    import re

    item_set = []
    for r in json_dict["results"]["bindings"]:
        # base query includes item (Q code) label, the property, English language prop value
        item_raw = r.get("item", {}).get("value")
        i = Item(re.split(r'/', item_raw).pop())
        i.item_label = r.get("itemLabel", {}).get("value")
        i.prop_code = r.get("prop", {}).get("value")
        i.prop_label = r.get("propLabel", {}).get("value")
        i.value_code = r.get("oraw", {}.get("value"))
        i.value_label = r.get("oValue", {}).get("value")
        item_set.append(i)

    return item_set

def get_item_details(qcode):
    # call stack for retrieving and transforming the wikidata
    # into objects for views.item
    from . import sparql
    the_json = sparql.build_wd_query('item', supplied_qcode=qcode)
    return load_item_details(the_json)

def load_subjects(json_dict):
    import re
    # TEMPORARY: loads all topics on the fly. Should be replaced by a
    # conventional model structure.
    subject_set = []
    for r in json_dict["results"]["bindings"]:
        #
        subject_raw = r.get("subject", {}).get("value")
        s = Subject(re.split(r'/', subject_raw).pop())
        s.item_label = r.get("subjectLabel", {}).get("value")
        subject_set.append(s)

    return subject_set

def get_subjects():
    # call stack for retrieving and transforming the wikidata
    # into objects for views.item
    from . import sparql

    the_json = sparql.build_wd_query('subjects')
    return load_subjects(the_json)
