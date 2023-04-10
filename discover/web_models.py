"""
web_models handles all on-the-fly queries to wikidata. Returned JSON is
instantiated as python objects and those are persisted in the
application session.
"""

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

class SearchResult:
    item_id = ''
    itemlabel = ''
    itemdesc = ''
    colltypelabel = ''

    def __init__(self, pitem_id):
        self.item_id = pitem_id

    def __str__(self):
        return self.item_id

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

def reduce_search_results(query_obj, special_col=None):
    # works only for sets that include item_id and itemdesc.
    # also checks for a special column, such as colltype if the case requires.
    # NOTE: run order_by on QuerySet object before calling this.
    return_list = []
    curr_item = ''
    for o in query_obj:
        if curr_item == o.item_id:
            pass
        else:
            i = SearchResult(o.item_id)
            i.itemlabel = o.itemlabel
            i.itemdesc = o.itemdesc
            if special_col== 'colltypelabel':
                i.colltypelabel = o.colltypelabel
            return_list.append(i)
            curr_item = o.item_id

    return return_list
