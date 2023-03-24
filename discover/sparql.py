"""
Manages all query interactions with Wikidata.
"""
import sys

from SPARQLWrapper import SPARQLWrapper, JSON
from .models import WdQuery, Filter
from . import db
import re

WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"
FILTER_KEYS = {"people": "on-wm-focus-list", "other": "some-other-bogus-value"}

def apply_filter(qry, filterval):
    # insert wd entity value into query string
    if filterval:
        parts = re.split(r'~', qry)
        l = parts[0]
        r = parts[2]
        return l + filterval + r
    else:
        return -1

def get_wd_people():
    # loads source query from database, applies filter and submits to Wikidata.
    # Returns JSON.
    try:
        # insert filter value into query string
        q = WdQuery.objects.get(querytitle='people')
        f = Filter.objects.get(name=FILTER_KEYS['people'])
        qry = apply_filter(q.querytext, f.qcode)

        # execute query with SPARQLWrapper
        people_json = run_wd_query(qry) #internal function
        # print(people_json)
        return people_json
    except:
        db.log_exception(sys.exc_info(), 'sparql.get_wd_people')

def run_wd_query(query):
    # takes query, either compiled for retrieved from disk, and submits to Wikidata.
    # Returns JSON.
    user_agent = 'PyDiscoverApp/0.1 (https://linkedin.com/andre_hulet; andrehulet@gmail.com)'
    spql = SPARQLWrapper(WIKIDATA_ENDPOINT, agent=user_agent)
    spql.setQuery(query)
    spql.setReturnFormat(JSON)
    the_json = spql.query().convert()
    return the_json