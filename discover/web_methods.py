"""
web_models handles all on-the-fly queries to wikidata. Returned JSON entries are
instantiated as python objects.
"""
from .wd_utils import catch_err
from . import sparql


class ChartRow:
    label = ''
    value = ''

    def __init__(self, label):
        self.label = label

    def __str__(self):
        return self.label


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


def get_chart(qry):
    """Wrapper for retrieving basic chart data from wikidata source."""
    the_dict = sparql.build_wd_query(qry)
    return load_chart(the_dict)


def load_chart(the_dict):
    """Used by get_chart() to load source data into python list of objects."""
    labels = []
    data = []
    for r in the_dict["results"]["bindings"]:
        labels.append(r.get("_Label", {}).get("value"))
        data.append(r.get("count", {}).get("value"))

    return {'labels': labels, 'data': data}


def get_images(qry):
    """Wrapper for retrieving and transforming the wikidata into objects for views.item."""

    the_json = sparql.build_wd_query(qry)
    return load_images(the_json)


def load_images(the_dict):
    """Used by get_images() to load source data into python list of objects."""
    import re

    images = []
    for r in the_dict["results"]["bindings"]:
        i = Image(re.split(r'/', r.get("item", {}).get("value")).pop())
        i.itemlabel = r.get("itemLabel", {}).get("value")
        i.instanceof_id = re.split(r'/', r.get("instanceOf", {}).get("value")).pop()
        i.instanceoflabel = r.get("instanceOfLabel", {}).get("value")
        i.itemdesc = r.get("itemDescription", {}).get("value")
        i.image = r.get("image", {}).get("value")
        images.append(i)

    return images


def load_item_details(the_dict):
    """private method to create item objects passed to the view layer."""
    # Binds only to the "item" query saved in discover_wdquery.
    import re

    item_set = []
    for r in the_dict["results"]["bindings"]:
        # base query includes item (Q code) label, the property, English language prop value
        item_raw = r.get("item", {}).get("value")
        i = Item(re.split(r'/', item_raw).pop())
        i.item_label = r.get("itemLabel", {}).get("value")
        i.item_desc = r.get('itemDescription', {}).get('value')
        prop_raw = r.get("prop", {}).get("value")
        prop_code = re.split(r'/', prop_raw).pop()
        i.prop_code = prop_code
        i.prop_label = r.get("propLabel", {}).get("value")
        i.value_code = r.get("oraw", {}.get("value"))
        if prop_code == 'P8091':
            i.value_label = 'http://n2t.net/' + r.get("oValue", {}).get("value")
        else:
            i.value_label = r.get("oValue", {}).get("value")
        item_set.append(i)

    return item_set


def get_item_details(qcode):
    """Wrapper for retrieving and transforming item wikidata
    into objects for views.item"""

    the_json = sparql.build_wd_query('item', supplied_qcode=qcode)
    return load_item_details(the_json)


def reduce_search_results(query_obj, facet):
    """Creates a unique-rows version of filtered QuerySets,
    which contain duplicate item codes by design. Needed to
    replace missing 'SELECT IN' support in MySQL."""
    # checks for a special field to add to the search results,
    # such as colltypelabel, if the case requires.
    from .enums import Facet
    item_dict = {}
    return_list = []

    # force unique set via dictionary.
    for r in query_obj:
        if facet == Facet.colls.value:  # used to show type of collection
            item_dict[r.item_id] = {'itemlabel': r.itemlabel, 'itemdesc': r.itemdesc,
                                    'colltypelabel': r.colltypelabel}
        elif facet == Facet.orals.value:
            item_dict[r.item_id] = {'itemlabel': r.itemlabel, 'itemdesc': r.itemdesc,
                                    'inventorynum': r.inventorynum, 'describedat': r.describedat}
        elif facet == Facet.corps.value:
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
