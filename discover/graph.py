def load_people(dataset, relation_type):
    from django.utils.safestring import mark_safe
    from . import db
    import json

    peeps = dataset
    # prepare two lists to use in Javascript on template.
    # get unique lists of humans and occupations, and a JSON
    # dict of properties by human for graph display.
    # note: assigning a dup to a dict discards the dup.
    human_dict = {}
    relation_dict = {}
    props_dict = {}

    node_list = []
    edge_list = []
    # props_json = json.JSONEncoder
    props_list = []
    # create dicts plus add edge data to edge_list
    for p in peeps:
        e = []
        human_dict[p.item_id] = p.itemlabel
        props_dict[p.item_id] = {"itemlabel": p.itemlabel, "image": p.image, "dob": p.dob,
                                 "placeofbirth": p.placeofbirthlabel,
                                 "dateofdeath": p.dateofdeath, "placeofdeath": p.placeofdeathlabel,
                                 "mother": p.motherlabel, "father": p.fatherlabel, "spouse": p.spouselabel,
                                 "child": p.childlabel, "relative": p.relativelabel}
        if relation_type=='occupation':
            if p.occupation_id:
                relation_dict[p.occupation_id] = p.occupationlabel
                e = {"from": p.item_id, "to": db.supply_val(p.occupation_id, 'string')}
            else:
                pass
        elif relation_type=='fieldofwork':
            if p.fieldofwork_id:
                relation_dict[p.fieldofwork_id] = p.fieldofworklabel
                e = {"from": p.item_id, "to": db.supply_val(p.fieldofwork_id, 'string')}
            else:
                pass
        if not e.__len__() == 0:
            edge_list.append(e)  # todo: change to dict to avoid occ. dupes in results

    # add human nodes
    for k, v in human_dict.items(): # todo: pull nodes & edges creation into its own def.
        obj1 = {"id": k, "label": v[:12]+'.', "shape": "circle", "color": "#00BFFF"}
        node_list.append(obj1)

    # relation nodes
    for k, v in relation_dict.items():
        obj2 = {"id": k, "label": v, "shape": "ellipse", "color": "#FF0000"}
        node_list.append(obj2)
        props_list.append(obj2)  # add here to provide on-page data to access via javascript.
    # additional properties for humans
    for k, v in props_dict.items():
        obj3 = {"id": k, "itemprops": v}
        props_list.append(obj3)

    props_json = json.dumps(props_list, separators=(",", ":")) # creates ragged json of relation & human nodes


    results = {"nodes": mark_safe(node_list), "edges": mark_safe(edge_list), 'properties': mark_safe(props_json)}
    return results

def load_collections(dataset, relation_type):
    from django.utils.safestring import mark_safe
    from . import db
    import json

    colls = dataset
    # prepare two lists to use in Javascript on template.
    # get unique lists of collections and main subjects, and a JSON
    # dict of properties by collection for graph display.
    # note: assigning a dup to a dict discards the dup.
    collection_dict = {}
    relation_dict = {}
    props_dict = {}

    node_list = []
    edge_list = []
    props_list = []
    # create dicts plus add edge data to edge_list
    for c in colls:
        e = []
        collection_dict[c.item_id] = c.itemlabel
        props_dict[c.item_id] = {"itemlabel": c.itemlabel, "donatedby": c.donatedbylabel,
                                 "colltypelabel": c.colltypelabel,
                                 "inventorynum": c.inventorynum, "describedat": c.describedat}
        if relation_type=='mainsubject': # currently only one relation type for collections. May change
            if c.subject_id:
                relation_dict[c.subject_id] = c.subjectlabel
                e = {"from": c.item_id, "to": db.supply_val(c.subject_id, 'string')}
            else:
                pass
        if not e.__len__() == 0:
            edge_list.append(e)  # todo: change to dict to avoid occ. dupes in results

    # add human nodes
    for k, v in collection_dict.items():
        obj1 = {"id": k, "label": v[:10]+'.', "shape": "circle", "color": "#00BFFF"}
        node_list.append(obj1)

    # relation nodes
    for k, v in relation_dict.items():
        obj2 = {"id": k, "label": v, "shape": "ellipse", "color": "#FF0000"}
        node_list.append(obj2)
        props_list.append(obj2)  # add here to provide on-page data to access via javascript.
    # additional properties for humans
    for k, v in props_dict.items():
        obj3 = {"id": k, "itemprops": v}
        props_list.append(obj3)

    props_json = json.dumps(props_list, separators=(",", ":")) # creates ragged json of relation & human nodes


    results = {"nodes": mark_safe(node_list), "edges": mark_safe(edge_list), 'properties': mark_safe(props_json)}
    return results

def load_oral_histories(dataset, relation_type):
    from django.utils.safestring import mark_safe
    from . import db
    import json

    orals = dataset