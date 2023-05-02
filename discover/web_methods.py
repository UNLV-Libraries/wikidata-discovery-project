"""
web_models handles all on-the-fly queries to wikidata. Returned JSON is
instantiated as python objects.
"""
from .wd_utils import catch_err


class Image:
    item_id = ''
    itemlabel = ''
    instanceof_id = ''
    instanceoflabel = ''
    itemdesc = ''
    image = ''

    def __init__(self, item_id):
        self.item_id = item_id

    def __str__(self):
        return self.item_id


class Item:
    item_code = ''
    item_label = ''
    item_desc = ''
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
    def __init__(self, pitem_id):
        self.record = {'item_id': pitem_id,
                       'itemlabel': '',
                       'itemdesc': '',
                       'colltypelabel': '',
                       'instanceoflabel': '',
                       'inventorynum': '',
                       'describedat': ''}

    def __str__(self):
        return self.record['item_id']

    def __setitem__(self, key, value):
        self.record[key] = value

    def getitemid(self):
        return self.record['item_id']

    def getlabel(self):
        return self.record['itemlabel']

    def getdesc(self):
        return self.record['itemdesc']

    def getcolltypelabel(self):
        return self.record['colltypelabel']

    def getinventorynum(self):
        return self.record['inventorynum']

    def getdescribedat(self):
        return self.record['describedat']

    def getinstanceoflabel(self):
        return self.record['instanceoflabel']


def get_images(qry):
    # wrapper for retrieving and transforming the wikidata
    # into objects for views.item
    from . import sparql
    the_json = sparql.build_wd_query(qry)
    return load_images(the_json)


def load_images(json_dict):
    import re

    images = []
    for r in json_dict["results"]["bindings"]:
        i = Image(re.split(r'/', r.get("item", {}).get("value")).pop())
        i.itemlabel = r.get("itemLabel", {}).get("value")
        i.instanceof_id = re.split(r'/', r.get("instanceOf", {}).get("value")).pop()
        i.instanceoflabel = r.get("instanceOfLabel", {}).get("value")
        i.itemdesc = r.get("itemDescription", {}).get("value")
        i.image = r.get("image", {}).get("value")
        images.append(i)

    return images


def load_item_details(json_dict):
    """private method to create item object passed to the view layer."""
    # Binds only to the "item" query saved in discover_wdquery.
    import re

    item_set = []
    for r in json_dict["results"]["bindings"]:
        # base query includes item (Q code) label, the property, English language prop value
        item_raw = r.get("item", {}).get("value")
        i = Item(re.split(r'/', item_raw).pop())
        i.item_label = r.get("itemLabel", {}).get("value")
        i.item_desc = r.get('itemDescription', {}).get('value')
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


def reduce_search_results(query_obj, special_field=None):
    """Creates a unique-rows version of filtered QuerySets,
    which contain duplicate item codes by design. Needed to
    replace missing 'SELECT IN' support in MySQL."""
    # checks for a special field to add to the search results,
    # such as colltypelabel, if the case requires.
    # todo: change special_col to enum
    item_dict = {}
    return_list = []

    # force unique set via dictionary type.
    for r in query_obj:
        if special_field == 'colltypelabel':  # used to show type of collection
            item_dict[r.item_id] = {'itemlabel': r.itemlabel, 'itemdesc': r.itemdesc,
                                    'colltypelabel': r.colltypelabel}
        elif special_field == 'inventorynum':  # for oral histories todo: and collections?
            item_dict[r.item_id] = {'itemlabel': r.itemlabel, 'itemdesc': r.itemdesc,
                                    'inventorynum': r.inventorynum, 'describedat': r.describedat}
        elif special_field == 'instanceoflabel':  # for corporate bodies
            item_dict[r.item_id] = {'itemlabel': r.itemlabel, 'itemdesc': r.itemdesc,
                                    'instanceoflabel': r.instanceoflabel}
        else:
            item_dict[r.item_id] = {'itemlabel': r.itemlabel, 'itemdesc': r.itemdesc}
    try:
        for k, v in item_dict.items():
            o = SearchResult(k)
            for p, d in v.items():
                o[p] = d
            return_list.append(o)
    except Exception as e:
        catch_err(e, 'reduce_search_results')

    return return_list
