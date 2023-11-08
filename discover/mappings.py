from django.forms.models import model_to_dict
from .enums import AppClass, RelColor
from .models import RelationType
from django.db.models import QuerySet

# The set of valid relation types is controlled in the backend table, 'discover_relationtypes.'
RELATION_TYPES = RelationType.objects.values_list('relation_type')

# Manage properties that appear in the graph by adding or removing properties from these lists
# that appear in the model for each application class. The spelling and case must match the model property.
PEOPLE_PROPERTIES = ['itemlabel', 'image', 'dob', 'placeofbirthlabel', 'dateofdeath', 'placeofdeathlabel',
                     'motherlabel', 'fatherlabel', 'spouselabel', 'childlabel', 'relativelabel']

CORP_PROPERTIES = ['itemlabel', 'instanceoflabel', 'describedat', 'inception', 'dissolved', 'locationlabel']

COLL_PROPERTIES = ['itemlabel', 'donatedbylabel', 'colltypelabel', 'inventorynum', 'describedat']

ORAL_PROPERTIES = ['itemlabel', 'inventorynum', 'describedat']

# Define in-graph labels for each property listed above.
PROP_LABEL_DICT = {
    "itemlabel": "name", "donatedbylabel": "donor", "colltypelabel": "type of",
    "inventorynum": "inventory #", "describedat": "described at",
    "instanceoflabel": "type", "inception": "inception", "dissolved": "dissolved",
    "locationlabel": "location", "image": "image", "dob": "date born", "placeofbirthlabel": "place born",
    "dateofdeath": "date died", "placeofdeathlabel": "place died", "motherlabel": "mother", "fatherlabel": "father",
    "spouselabel": "spouse", "childlabel": "child", "relativelabel": "relative"
    }

FACETS = {AppClass.colls.value: 'subject_id',
          AppClass.corps.value: 'instanceof_id',
          AppClass.orals.value: 'subject_id',
          AppClass.people.value: 'occupation_id'}

# set alarm time and job times used in wf_sched.py. Hours = 0-23; Minutes = 0-59
SCHED_ALARM_TIME = [23, 50]
COLLS_JOB_TIME = [23, 51]
CORPS_JOB_TIME = [23, 52]
ORALS_JOB_TIME = [23, 53]
PEOPLE_JOB_TIME = [23, 54]
LOGS_JOB_TIME = [23, 55]


# CLASSES
class FacetValue:
    facet_id = ''
    facet_label = ''

    def __init__(self, facet_id):
        self.facet_id = facet_id

    def __str__(self):
        return self.facet_id


# MAPPING FUNCTIONS START BELOW.
def map_properties(qry_row, app_class) -> dict:
    """Used in graph.load_graph to create property dictionaries for each node."""

    row_dict = model_to_dict(qry_row)  # convert QuerySet instance to dict bec. instance can't be sub-scripted.
    prop_dict = {}
    if app_class == AppClass.people.value:
        for p in PEOPLE_PROPERTIES:
            prop_dict[p] = row_dict[p]
    elif app_class == AppClass.corps.value:
        for cp in CORP_PROPERTIES:
            prop_dict[cp] = row_dict[cp]
    elif app_class == AppClass.colls.value:
        for cl in COLL_PROPERTIES:
            prop_dict[cl] = row_dict[cl]
    elif app_class == AppClass.orals.value:
        for o in ORAL_PROPERTIES:
            prop_dict[o] = row_dict[o]

    return prop_dict


def map_node_and_edge(qry_row, rel_type) -> dict:
    """Constructs unique node and edge data for an app class instance (row)."""

    node_dict = {}
    edge_dict = {}

    if rel_type == 'occupation':
        if qry_row.occupation_id:
            node_dict[qry_row.occupation_id] = {"label": 'occup: ' + qry_row.occupationlabel,
                                                "color": RelColor.occup.value}
            edge_dict[qry_row.item_id + qry_row.occupation_id] = \
                {"from": qry_row.item_id, "to": qry_row.occupation_id}
    elif rel_type == 'fieldofwork':
        if qry_row.fieldofwork_id:
            node_dict[qry_row.fieldofwork_id] = {"label": 'field: ' + qry_row.fieldofworklabel,
                                          "color": RelColor.fow.value}
            edge_dict[qry_row.item_id + qry_row.fieldofwork_id] = \
                {"from": qry_row.item_id, "to": qry_row.fieldofwork_id}
    elif rel_type == 'placeofbirth':
        if qry_row.placeofbirth_id:
            edge_dict[qry_row.item_id + qry_row.placeofbirth_id] = \
                {"from": qry_row.item_id, "to": qry_row.placeofbirth_id}
            node_dict[qry_row.placeofbirth_id] = {"label": 'birth: ' + qry_row.placeofbirthlabel,
                                                  "color": RelColor.pob.value}
    elif rel_type == 'placeofdeath':
        if qry_row.placeofdeath_id:
            node_dict[qry_row.placeofdeath_id] = {"label": 'death: ' + qry_row.placeofdeathlabel,
                                                  "color": RelColor.pod.value}
            edge_dict[qry_row.item_id + qry_row.placeofdeath_id] = \
                {"from": qry_row.item_id, "to": qry_row.placeofdeath_id}
    elif rel_type == 'instanceof':
        if qry_row.instanceof_id:
            node_dict[qry_row.instanceof_id] = {"label": 'cat: ' + qry_row.instanceoflabel,
                                                "color": RelColor.instanceof.value}
            edge_dict[qry_row.item_id + qry_row.instanceof_id] = \
                {"from": qry_row.item_id, "to": qry_row.instanceof_id}

    elif rel_type == 'subject':
        if qry_row.subject_id:
            node_dict[qry_row.subject_id] = {"label": 'subj: ' + qry_row.subjectlabel,
                                             "color": RelColor.subj.value}
            edge_dict[qry_row.item_id + qry_row.subject_id] = \
                {"from": qry_row.item_id, "to": qry_row.subject_id}

    node_edge_dict = {'node': node_dict, 'edge': edge_dict}
    return node_edge_dict


def get_search_queryset(app_class) -> QuerySet:
    """Returns the needed queryset objected based on the
    app class value of the form being processed in search_processed"""
    from . import models
    if app_class == AppClass.people.value:
        qry = models.Person.objects.all()
    elif app_class == AppClass.corps.value:
        qry = models.CorpBody.objects.all()
    elif app_class == AppClass.colls.value:
        qry = models.Collection.objects.all()
    elif app_class == AppClass.orals.value:
        qry = models.OralHistory.objects.all()
    elif app_class == AppClass.subjs.value:  # todo: redesign or refactor out of GLAM app.
        qry = models.Collection.objects.all()
    else:
        qry = QuerySet()

    return qry


def get_node_queryset(nsform, qset) -> QuerySet:
    """Used by views.process_node_form. Can be called from multiple places
    inside that function."""
    if nsform.cleaned_data['node_id'] == '':
        the_id = nsform.cleaned_data['prior_node_search']
        the_color = nsform.cleaned_data['prior_color']
    else:
        the_id = nsform.cleaned_data['node_id']
        the_color = nsform.cleaned_data['color_type']

    if the_color == RelColor.item.value:
        filtset = qset.filter(item_id__exact=the_id).order_by('item_id')
    elif the_color == RelColor.occup.value:
        filtset = qset.filter(occupation_id__exact=the_id)
    elif the_color == RelColor.fow.value:
        filtset = qset.filter(fieldofwork_id__exact=the_id)
    elif the_color == RelColor.pob.value:
        filtset = qset.filter(placeofbirth_id__exact=the_id)
    elif the_color == RelColor.pod.value:
        filtset = qset.filter(placeofdeath_id__exact=the_id)
    elif the_color == RelColor.subj.value:
        filtset = qset.filter(subject_id__exact=the_id)
    elif the_color == RelColor.instanceof.value:
        filtset = qset.filter(instanceof_id__exact=the_id)
    else:
        filtset = QuerySet()

    return filtset


def get_facet_queryset(app_class) -> list:
    """Provides queryset to populate values list for an application class's facet."""
    from .models import Collection, CorpBody, OralHistory, Person
    query = QuerySet()
    if app_class == AppClass.corps.value:
        query = CorpBody.objects.values_list('instanceof_id', 'instanceoflabel').order_by('instanceoflabel')
    elif app_class == AppClass.colls.value:
        query = Collection.objects.values_list('subject_id', 'subjectlabel').order_by('subjectlabel')
    elif app_class == AppClass.orals.value:
        query = OralHistory.objects.values_list('subject_id', 'subjectlabel').order_by('subjectlabel')
    elif app_class == AppClass.people.value:
        query = Person.objects.values_list('occupation_id', 'occupationlabel').order_by('occupationlabel')

    return get_unique_facet_vals(query)


def get_unique_facet_vals(query) -> list:
    """Creates unique list of key-value pairs within a facet. Note: Django+MySQL doesn't support
    SELECT DISTINCT on multiple fields in the ORM."""
    facet_dict = {}
    facet_obj_list = []

    for i in query:
        facet_dict[i[0]] = i[1]

    for k, v in facet_dict.items():
        n = FacetValue(k)
        n.facet_label = v
        facet_obj_list.append(n)

    return facet_obj_list


def get_facet_filter_kwarg(app_class, qcode_list) -> dict:
    """Formats keyword argument for query filters in views.py"""
    kwarg = FACETS[app_class] + '__in'
    kwarg_dict = {kwarg: qcode_list}

    return kwarg_dict


def get_prior_template_path(app_class):
    """Used to retrieve doc path based on app_class of queue form in process_search."""
    if app_class == AppClass.people.value:
        path = 'discover/base_people_filtered.html'
    elif app_class == AppClass.corps.value:
        path = 'discover/base_corps_filtered.html'
    elif app_class == AppClass.colls.value:
        path = 'discover/base_collections_filtered.html'
    elif app_class == AppClass.orals.value:
        path = 'discover/base_orals_filtered.html'
    else:  # based on subjects search
        path = 'discover/base_collections_filtered.html'

    return path

