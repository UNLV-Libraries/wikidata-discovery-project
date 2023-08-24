from .wd_utils import catch_err
from .enums import AppClass
from django.utils.safestring import mark_safe
import json
from . import mappings


def get_geo_properties(dataset, app_class):
    """Returns basic json data set of coordinates and address for entities with location data."""
    coord_dict = {}
    coord_list = []

    if app_class == AppClass.corps.value:  # currently only corp bodies have location data
        try:
            for r in dataset:
                # force uniqueness of results
                if r.coordinates:
                    long_lat = r.coordinates[6:r.coordinates.__len__() - 1]  # extract points from 'Point(...)' pattern.
                    coord_dict[r.item_id] = {"label": r.itemlabel, "long_lat": long_lat, "streetaddress": r.streetaddress}

            for k, v in coord_dict.items():
                # prep results for conversion to json
                obj = {"id": k, "long_lat": v['long_lat'], "streetaddress": v['streetaddress']}
                coord_list.append(obj)
        except Exception as e:
            catch_err(e, 'geog.get_geo_properties')
            coord_list.clear()
            coord_list.append({"id": "none", "label": "none"})
    else:
        coord_list.append({"id": "none", "label": "none"})

    # convert to json
    coord_json = mark_safe(json.dumps(coord_list, separators=(",", ":")))

    return coord_json
