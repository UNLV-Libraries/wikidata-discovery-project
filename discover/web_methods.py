"""
web_methods handles all on-the-fly queries to Wikidata. Returned JSON entries are
instantiated as python objects for processing and rendering in templates.
"""
from .wf_utils import catch_err
from . import sparql


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
    qual_code = ''
    qual_label = ''
    qual_value_code = ''
    qual_value_label = ''
    has_url = True

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
    # Binds only to the "item" query saved in the database in discover_wdquery.
    import re

    item_set = []
    try:
        for r in the_dict["results"]["bindings"]:
            # base query includes item (Q code) label, the property, English language prop value
            item_raw = r.get("item", {}).get("value")
            i = Item(re.split(r'/', item_raw).pop())
            i.item_label = r.get("itemLabel", {}).get("value")
            i.item_desc = r.get('itemDescription', {}).get('value')
            prop_raw = r.get("wdprop", {}).get("value")
            prop_code = re.split(r'/', prop_raw).pop()
            i.prop_code = prop_code
            i.prop_label = r.get("wdpropLabel", {}).get("value")
            i.value_code = r.get("pso", {}).get("value")
            qual_raw = r.get("wdpq", {}).get("value")
            if qual_raw:
                i.qual_code = re.split(r'/', qual_raw).pop()
                i.qual_label = r.get('wdpqLabel', {}).get('value')
            qual_val_raw = r.get("pqo", {}).get("value")
            if qual_val_raw:
                i.qual_value_code = re.split(r'/', qual_val_raw).pop()
                i.qual_value_label = r.get('pqoLabel', {}).get('value')

            # format item authority codes or other 'https' values for web retrieval
            if prop_code == 'P8091':
                i.value_label = 'http://n2t.net/' + r.get("psoLabel", {}).get("value")
            elif prop_code == 'P244':
                i.value_label = 'http://id.loc.gov/authorities/names/' + r.get("psoLabel", {}).get("value")
            elif prop_code == 'P214':
                i.value_label = 'http://viaf.org/viaf/' + r.get("psoLabel", {}).get("value")
            elif prop_code == 'P2163':
                i.value_label = 'https://experimental.worldcat.org/fast/' + r.get("psoLabel", {}).get("value")
            elif prop_code == 'P646':
                i.value_label = 'https://www.google.com/search?kgmid=' + r.get("psoLabel", {}).get("value")
            elif prop_code == 'P8189':
                i.value_label = 'http://uli.nli.org.il/F/?func=find-b&local_base=NLX10&find_code=UID&request=' \
                                + r.get("psoLabel", {}).get("value")
            elif prop_code == 'P3430':
                i.value_label = 'https://snaccooperative.org/ark:/99166/' + r.get("psoLabel", {}).get("value")
            elif prop_code == 'P973':  # 'described at URL'
                i.value_label = r.get("psoLabel", {}).get("value")  # value is already http-formatted.
            elif prop_code == 'P2671':
                i.value_label = 'https://www.google.com/search?kgmid=' + r.get("psoLabel", {}).get("value")
            else:
                i.value_label = r.get("psoLabel", {}).get("value")
                i.has_url = False
            item_set.append(i)

        return item_set
    except Exception as e:
        catch_err(e, 'web_methods.load_item_details')
        return item_set


def get_item_details(qcode):
    """Wrapper for retrieving and transforming item wikidata
    into objects for views.item"""

    the_json = sparql.build_wd_query('item', supplied_qcode=qcode)
    return load_item_details(the_json)


def reduce_search_results(query_obj, app_class):
    """Creates a unique-rows version of filtered QuerySets,
    which contain duplicate item codes by design. Needed to
    replace missing 'SELECT IN' support in MySQL."""
    # checks for a special field to add to the search results,
    # such as colltypelabel, if the case requires.
    from .enums import AppClass
    item_dict = {}
    return_list = []

    # force unique set via dictionary.
    for r in query_obj:
        if app_class == AppClass.colls.value:  # used to show type of collection
            item_dict[r.item_id] = {'itemlabel': r.itemlabel, 'itemdesc': r.itemdesc,
                                    'colltypelabel': r.colltypelabel}
        elif app_class == AppClass.orals.value:
            item_dict[r.item_id] = {'itemlabel': r.itemlabel, 'itemdesc': r.itemdesc,
                                    'inventorynum': r.inventorynum, 'describedat': r.describedat}
        elif app_class == AppClass.corps.value:
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
        catch_err(e, 'web_methods.reduce_search_results')

    return return_list
