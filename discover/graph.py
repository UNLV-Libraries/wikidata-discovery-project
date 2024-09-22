from .wf_utils import catch_err


def load_graph(dataset, relation_types, app_class):
    """Loads graph visualizer with item, relations, and edges for all app classes.
    Properties list created for on-page graph tooltip via JavaScript. """
    from django.utils.safestring import mark_safe
    from .enums import RelColor
    import json
    from . import mappings

    try:
        # prepare three lists to use in Javascript on template. Get unique lists of nodes, node properties
        # and edges for graph display.
        item_dict = {}  # takes item node data
        relation_dict = {}  # takes relation type node data
        props_dict = {}  # takes properties data
        edge_dict = {}  # takes edge data
        eval_dict = {}  # special dict for duplicate node id problem. See below.

        node_list = []
        node_list_final = []  # special list for duplicate node id problem. See below.
        edge_list = []
        props_list = []

        # create dictionaries (force uniqueness)
        for i in dataset:
            item_dict[i.item_id] = i.itemlabel
            props_dict[i.item_id] = mappings.map_properties(i, app_class)

            # create one or more graph relation nodes for each item
            for r in relation_types:
                node_edge_dict = mappings.map_node_and_edge(i, r)
                relation_dict.update(node_edge_dict['node'])
                edge_dict.update(node_edge_dict['edge'])

        # put unique item nodes in list
        for k, v in item_dict.items():
            obj1 = {"id": k, "label": v[:20] + '.', "shape": "ellipse", "color": RelColor.item.value}
            node_list.append(obj1)

        # put unique relation nodes in list
        for k, v in relation_dict.items():
            obj2 = {"id": k, "label": v['label'], "shape": "ellipse", "color": v['color']}
            node_list.append(obj2)
            props_list.append(obj2)  # add here to provide on-page label to access via javascript.
            # node_dict[k] = v

        # force unique key set from node_list: this hack is currently needed because entities have occasionally
        # been added to the data as both an item and a relation type, like "subject." This ends up
        # producing graph nodes with duplicate keys, which breaks the graph rendering.
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

        node_json = json.dumps(node_list_final, separators=(",", ":"))  # convert python lists to JSON
        edge_json = json.dumps(edge_list, separators=(",", ":"))
        props_json = json.dumps(props_list, separators=(",", ":"))

        results = {"nodes": mark_safe(node_json), "edges": mark_safe(edge_json), "properties": mark_safe(props_json)}
        return results
    except Exception as e:
        errors = catch_err(e, "graph.load_graph")
        return errors
