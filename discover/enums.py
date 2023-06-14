from enum import Enum


class RelColor(Enum):
    """Controls evaluation of graph node types by color."""
    item = '#f2f2f2'
    occup = '#ff8533'
    fow = '#e6e600'
    pob = '#80dfff'
    pod = '#b3b3ff'
    subj = '#b3ffb3'
    instanceof = '#ff1a75'


class Facet(Enum):
    """Establishes allowable names in code for facets within the data domain. """
    people = 'people'
    corps = 'corps'
    colls = 'collections'
    orals = 'orals'
    subjs = 'subjects'

