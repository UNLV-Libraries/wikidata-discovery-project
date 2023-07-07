from .wd_utils import catch_err
from .enums import RelColor


def load_graph(dataset, relation_types, facet):
    """Loads graph visualizer with item, relations, and edges for all domains.
    Properties list created for on-page graph tooltip via JavaScript. """
    from django.utils.safestring import mark_safe
    from .enums import RelColor, Facet
    import json

    try:
        # prepare two lists to use in Javascript on template. Get unique lists of nodes and edges,
        # and a JSON dict of properties by item for graph display.
        item_dict = {}
        relation_dict = {}
        props_dict = {}
        edge_dict = {}
        node_dict = {}
        eval_dict = {}

        node_list = []
        node_list_final = []
        edge_list = []
        props_list = []
        # create dictionaries (force uniqueness)
        for i in dataset:

            item_dict[i.item_id] = i.itemlabel
            if facet == Facet.people.value:
                props_dict[i.item_id] = {"itemlabel": i.itemlabel, "image": i.image, "dob": i.dob,
                                         "placeofbirth": i.placeofbirthlabel, "dateofdeath": i.dateofdeath,
                                         "placeofdeath": i.placeofdeathlabel,  "mother": i.motherlabel,
                                         "father": i.fatherlabel, "spouse": i.spouselabel,
                                         "child": i.childlabel, "relative": i.relativelabel}
            elif facet == Facet.corps.value:
                props_dict[i.item_id] = {"itemlabel": i.itemlabel, "instanceoflabel": i.instanceoflabel,
                                         "describedat": i.describedat,
                                         "inception": i.inception, "dissolved": i.dissolved,
                                         "locationlabel": i.locationlabel}
            elif facet == Facet.colls.value:
                props_dict[i.item_id] = {"itemlabel": i.itemlabel, "donatedbylabel": i.donatedbylabel,
                                         "colltypelabel": i.colltypelabel, "inventorynum": i.inventorynum,
                                         "describedat": i.describedat}
            elif facet == Facet.orals.value:
                props_dict[i.item_id] = {"itemlabel": i.itemlabel, "inventorynum": i.inventorynum,
                                         "describedat": i.describedat}

            for r in relation_types:
                if r == 'occupation':
                    if i.occupation_id:
                        relation_dict[i.occupation_id] = {"label": 'occup: ' + i.occupationlabel,
                                                          "color": RelColor.occup.value}
                        edge_dict[i.item_id + i.occupation_id] = \
                            {"from": i.item_id, "to": i.occupation_id}
                elif r == 'fieldofwork':
                    if i.fieldofwork_id:
                        relation_dict[i.fieldofwork_id] = {"label": 'field: ' + i.fieldofworklabel,
                                                           "color": RelColor.fow.value}
                        edge_dict[i.item_id + i.fieldofwork_id] = \
                            {"from": i.item_id, "to": i.fieldofwork_id}
                elif r == 'placeofbirth':
                    if i.placeofbirth_id:
                        edge_dict[i.item_id + i.placeofbirth_id] = \
                                {"from": i.item_id, "to": i.placeofbirth_id}
                        relation_dict[i.placeofbirth_id] = {"label": 'birth: ' + i.placeofbirthlabel,
                                                            "color": RelColor.pob.value}
                elif r == 'placeofdeath':
                    if i.placeofdeath_id:
                        relation_dict[i.placeofdeath_id] = {"label": 'death: ' + i.placeofdeathlabel,
                                                            "color": RelColor.pod.value}
                        edge_dict[i.item_id + i.placeofdeath_id] = \
                            {"from": i.item_id, "to": i.placeofdeath_id}
                elif r == 'instanceof':
                    if i.instanceof_id:
                        relation_dict[i.instanceof_id] = {"label": 'cat: ' + i.instanceoflabel,
                                                          "color": RelColor.instanceof.value}
                        edge_dict[i.item_id + i.instanceof_id] = \
                            {"from": i.item_id, "to": i.instanceof_id}

                elif r == 'subject':
                    if i.subject_id:
                        relation_dict[i.subject_id] = {"label": 'subj: ' + i.subjectlabel,
                                                       "color": RelColor.subj.value}
                        edge_dict[i.item_id + i.subject_id] = \
                            {"from": i.item_id, "to": i.subject_id}

        # add item nodes
        for k, v in item_dict.items():
            obj1 = {"id": k, "label": v[:20] + '.', "shape": "ellipse", "color": RelColor.item.value}
            node_list.append(obj1)
            node_dict[k] = v

        # add relation nodes
        for k, v in relation_dict.items():
            obj2 = {"id": k, "label": v['label'], "shape": "ellipse", "color": v['color']}
            node_list.append(obj2)
            props_list.append(obj2)  # add here to provide on-page label to access via javascript.
            node_dict[k] = v

        # force unique key set from node_list
        for n in node_list:
            count1 = eval_dict.keys().__len__()
            eval_dict[n['id']] = n['label']
            count2 = eval_dict.keys().__len__()
            if count2 > count1:
                node_list_final.append(n)

        # add edges
        for k, v in edge_dict.items():
            edge_list.append(v)

        # additional properties for items
        for k, v in props_dict.items():
            obj3 = {"id": k, "itemprops": v}
            props_list.append(obj3)

        # print('bad list: ' + str(node_list.__len__()))
        # print('dict: ' + str(node_dict.keys().__len__()))
        # print('good list: ' + str(node_list_final.__len__()))

        node_json = json.dumps(node_list_final, separators=(",", ":"))  # convert python lists to JSON
        edge_json = json.dumps(edge_list, separators=(",", ":"))
        props_json = json.dumps(props_list, separators=(",", ":"))

        results = {"nodes": mark_safe(node_json), "edges": mark_safe(edge_json), "properties": mark_safe(props_json)}
        return results
    except Exception as e:
        errors = catch_err(e, "graph.load_graph")
        return errors
