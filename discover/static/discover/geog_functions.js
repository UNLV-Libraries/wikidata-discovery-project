let layer_cln = new Map();
let layer_cln_keys = [];
let map_obj, map_view;

class AppLayer {
    constructor(id, label, color_code) {
        this.instanceof_id = id;
        this.instanceoflabel = label;
        this.color_code = color_code;
        this.layer_source = new ol.source.Vector({useSpatialIndex: false});
        this.layer_map = new ol.layer.Vector(
            {'layer_id': id}
        );
    }
    configLayer() {
        this.layer_map.setSource(this.layer_source);
    }

    addPoint(long_lat, item_id, itemlabel) {
        let point_strings = long_lat.split(',');
        let long = Number.parseFloat(point_strings[0]);
        let lat = Number.parseFloat(point_strings[1]);
        let point = new ol.geom.Point([long, lat]);
        let point_feature = new ol.Feature({
            id: item_id,
            geometry: point,
            name: itemlabel,
        });
        let text_style = new ol.style.Style({
            text: new ol.style.Text({
                text: itemlabel,
                font: 'bold 12px Calibri,sans-serif',
                fill: new ol.style.Fill({
                    color: '#262873',
                }),
                stroke: new ol.style.Stroke({
                    color: 'white',
                    width: 1
                }),
                offsetY: 15
            }),
        });
        let point_style = new ol.style.Style({
            image: new ol.style.Circle({
                radius: 5,
                fill: new ol.style.Fill({
                    color: this.color_code,
                }),
            stroke: new ol.style.Stroke({
                color: 'white',
                width: 1,
                }),
            }),
        });

        point_feature.setStyle([point_style, text_style]);
        this.layer_source.addFeature(point_feature);

    }
}

function createLayers() {
    for (let l in geog_layers) {
        let curr_layer = new AppLayer(
            geog_layers[l].instanceof_id,
            geog_layers[l].instanceoflabel,
            geog_layers[l].color_code,
        );
        layer_cln.set(geog_layers[l].instanceof_id, curr_layer);
        layer_cln_keys.push(geog_layers[l].instanceof_id);
    }
}

function mapPoints() {
    let itemlabel;
    for (let p in geog_points) {
        let long_lat = geog_points[p].long_lat;
        let item_id = geog_points[p].item_id;
        itemlabel = geog_points[p].itemlabel;
        let lyr = layer_cln.get(geog_points[p].instanceof_id);
        lyr.addPoint(long_lat, item_id, itemlabel);
    }
}

function composeMap() {
    let osm_source = new ol.source.OSM();
    let osm_layer = new ol.layer.Tile({'layer_id': 'tiles', source: osm_source});

    map_view = new ol.View({
        projection: 'EPSG:4326',
        center: [-115.176468, 36.188110],
        zoom: 10,
    });

     map_obj = new ol.Map({
        view: map_view,
    });
    map_obj.addLayer(osm_layer);
    layer_cln_keys.forEach( function (element) {
        let curr_layer = layer_cln.get(element);
        curr_layer.configLayer();
        let ready_layer = curr_layer.layer_map;
        map_obj.addLayer(ready_layer);
    });
    map_obj.setTarget('results_map');

    map_obj.on('moveend', function (evt) {
        let m = evt.map;
        let v = m.getView();
        if (v.getZoom() > 14) {

        } else {

        }
    });
}

function handleLegendCheck(layer_id) {
    //alert(layer_id + " handled");
    let layers = map_obj.getLayers();
    layers.forEach(function (layer) {
        if (layer.getProperties()['layer_id'] === layer_id) {
            let vis = layer.isVisible();
            //alert(chk);
            if (vis === true) {
                //alert('is checked');
                layer.setVisible(false);
            } else {
                //alert('is not checked');
                layer.setVisible(true);
            }
        }
    });
}

function toggleMapView(show) {
    let m = document.getElementById('map_wrapper');
    if (show===true) {
        m.style.display = 'block';
    } else {
        m.style.display = 'none';
    }
}
