def load_people(relation_type):
    from .models import Person
    from django.utils.safestring import mark_safe

    peeps = Person.objects.all()

    # prepare two lists to use in Javascript on template.
    # get unique lists of humans and occupations.
    # note: assigning a dup to a dict discards the dup.
    human_dict = {}
    relation_dict = {}
    node_list = []
    edge_list = []
    # create dicts plus add edge data to edge_list
    for p in peeps:
        e = []
        human_dict[p.item_id] = p.itemlabel
        if relation_type=='occupation':
            relation_dict[p.occupation_id] = p.occupationlabel
            e = {"from": p.item_id, "to": p.occupation_id}
        elif relation_type=='fieldofwork':
            relation_dict[p.fieldofwork_id] = p.fieldofworklabel
            e = {"from": p.item_id, "to": p.fieldofwork_id}

        edge_list.append(e)

    # add human nodes
    for k, v in human_dict.items():
        obj1 = {"id": k, "label": v, "shape": "circle", "color": "#00BFFF"}
        node_list.append(obj1)

    # relation nodes
    for k, v in relation_dict.items():
        obj2 = {"id": k, "label": v, "shape": "ellipse", "color": "#FF0000"}
        node_list.append(obj2)

    results = {"nodes": mark_safe(node_list), "edges": mark_safe(edge_list)}
    return results
