from .wf_utils import catch_err
from .enums import AppClass
from django.utils.safestring import mark_safe
import json
from . import mappings
import random
import re


class MapLayer:
    instanceof_id = ""
    instanceoflabel = ""
    color_code = ""

    def __init__(self, id, label, color):
        self.instanceof_id = id
        self.instanceoflabel = label
        self.color_code = color


def get_geo_properties(dataset: mappings.QuerySet, app_class):
    """Returns basic json data set of coordinates and address for entities with location data."""
    coord_dict = {}
    coord_list = []
    layers_dict = {}
    layers_json_list = []
    layers_obj_list = []

    if app_class == AppClass.corps.value:  # currently only corp bodies have location data
        try:
            for r in dataset:
                # force uniqueness of results
                if r.coordinates:
                    long_lat = r.coordinates[6:r.coordinates.__len__() - 1]  # extract points from 'Point(...)' pattern.
                    chunks = re.split(r' ', long_lat)
                    long_lat_f = chunks[0] + "," + chunks[1]
                    key = r.item_id + r.instanceof_id
                    coord_dict[key] = {"itemlabel": r.itemlabel, "long_lat": long_lat_f,
                                       "streetaddress": r.streetaddress, "instanceof_id": r.instanceof_id,
                                       "instanceoflabel": r.instanceoflabel, "item_id": r.item_id}
                    layers_dict[r.instanceof_id] = r.instanceoflabel

            for k, v in coord_dict.items():
                # prep results for conversion to json
                obj = {"item_id": v['item_id'], "itemlabel": v['itemlabel'], "long_lat": v['long_lat'],
                       "streetaddress": v['streetaddress'], "instanceof_id": v['instanceof_id'],
                       "instanceoflabel": v['instanceoflabel']}
                coord_list.append(obj)

            for k, v in layers_dict.items():
                f = random.randint(0, 255)
                s = random.randint(0, 255)
                t = random.randint(0, 255)
                std_color = '#%02X%02X%02X' % (f, s, t)
                obj_json = {'instanceof_id': k, 'instanceoflabel': v, 'color_code': std_color}
                layers_json_list.append(obj_json)
                ml = MapLayer(k, v, std_color)
                layers_obj_list.append(ml)

        except Exception as e:
            catch_err(e, 'geog.get_geo_properties')
            coord_list.clear()
            coord_list.append({"id": "none", "label": "none"})
            layers_json_list.clear()
            layers_json_list.append({"id": "none", "label": "none"})
            layers_obj_list.clear()
    else:
        coord_list.append({"id": "none", "label": "none"})
        layers_json_list.append({"id": "none", "label": "none"})
        layers_obj_list.clear()

    # convert to json
    coord_json = mark_safe(json.dumps(coord_list, separators=(",", ":")))
    layers_json = mark_safe(json.dumps(layers_json_list, separators=(",", ":")))
    return {'coords': coord_json, 'layers': layers_json, 'layer_objects': layers_obj_list}
