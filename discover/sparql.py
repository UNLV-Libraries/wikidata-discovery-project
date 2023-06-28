"""
Manages all query interactions with Wikidata.
"""
from SPARQLWrapper import SPARQLWrapper, JSON
from .models import WdQuery, Filter
import re

WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"

FILTER_KEYS = {"people": "filt-wm-focus-list", "item": "filt-item-qcode", 'collections': 'filt-wm-focus-list',
               'subjects': 'filt-wm-focus-list', 'oralhistories': 'filt-oralhistory-at',
               'corp_bodies': 'filt-wm-focus-list', 'images_humans': 'filt-wm-focus-list',
               'images_others': 'filt-wm-focus-list', 'stats_instanceof_count': 'filt-wm-focus-list',
               'stats_subjects_count': 'filt-wm-focus-list'}


def apply_filter(qry, filterval):

    # insert wd entity value into query string
    parts = re.split(r'~', qry)
    new_string = ''
    for v in parts:
        if v[:4] == 'filt':
            new_string += filterval
        else:
            new_string += v

    return new_string


def build_wd_query(query_key, supplied_qcode=None):
    # loads source query from database, applies filter and submits to Wikidata.
    # Returns JSON-like list of dictionaries

    # insert filter value into query string
    q = WdQuery.objects.get(querytitle=query_key)
    f = Filter.objects.get(name=FILTER_KEYS[query_key])
    if f.qcode[:10] == '[variable]':
        the_qcode = supplied_qcode
    else:
        the_qcode = f.qcode

    qry = apply_filter(q.querytext, the_qcode) #used as private function

    # execute query with SPARQLWrapper
    return_json = run_wd_query(qry) #used internal function
    return return_json


def run_wd_query(query):
    """Internal function that makes the call to Wikidata and returns json"""
    # takes query, either compiled on-the-fly or retrieved from disk, and submits to Wikidata.
    # Returns JSON.
    user_agent = 'PyDiscoverApp/0.1 (https://linkedin.com/andre_hulet; andre.hulet@unlv.edu)'
    spql = SPARQLWrapper(WIKIDATA_ENDPOINT, agent=user_agent)
    spql.setQuery(query)
    spql.setReturnFormat(JSON)
    the_json = spql.query().convert()
    return the_json