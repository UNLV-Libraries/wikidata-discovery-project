"""
Manages all query interactions with Wikidata.
"""
import sys

from SPARQLWrapper import SPARQLWrapper, JSON
from .models import WdQuery, Filter
from . import db
import re

WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"

FILTER_KEYS = {"people": "filt-wm-focus-list", "item": "filt-item-qcode", 'collections': 'filt-wm-focus-list',
               'topics': 'filt-wm-focus-list'}

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

def build_wd_query(filterkey, supplied_qcode=None):
    # loads source query from database, applies filter and submits to Wikidata.
    # Returns JSON.
    try:
        # insert filter value into query string
        q = WdQuery.objects.get(querytitle=filterkey)
        f = Filter.objects.get(name=FILTER_KEYS[filterkey])
        if f.qcode[:10] == '[variable]':
            the_qcode = supplied_qcode
        else:
            the_qcode = f.qcode

        qry = apply_filter(q.querytext, the_qcode)

        # execute query with SPARQLWrapper
        return_json = run_wd_query(qry) #internal function
        return return_json
    except:
        db.log_exception(sys.exc_info(), 'sparql.build_wd_query')


def run_wd_query(query):
    # takes query, either compiled for retrieved from disk, and submits to Wikidata.
    # Returns JSON.
    user_agent = 'PyDiscoverApp/0.1 (https://linkedin.com/andre_hulet; andrehulet@gmail.com)'
    spql = SPARQLWrapper(WIKIDATA_ENDPOINT, agent=user_agent)
    spql.setQuery(query)
    spql.setReturnFormat(JSON)
    the_json = spql.query().convert()
    return the_json