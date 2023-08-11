// initialize global variables.
let my_edges;
let my_nodes;
let network;
let the_data;
let keep_tooltip = false;

// This method is responsible for drawing the graph, returns the drawn network
function drawGraph() {
    let container = document.getElementById('graph_canvas');
  // create objects for network
    try {
        my_nodes = new vis.DataSet(inbound_nodes);
        my_edges = new vis.DataSet(inbound_edges);

        // adding nodes and edges to the graph
        the_data = {nodes: my_nodes, edges: my_edges};
        let options = {
            interaction: {
                hover: true
            },
            layout: {
                improvedLayout: true,
                clusterThreshold: 200
            },
            physics: {
                enabled: true,
                barnesHut: {
                    avoidOverlap: 0
                },
                solver: 'barnesHut',
                stabilization: {
                    enabled: true,
                    iterations: 250,
                    updateInterval: 12,
                    fit: true
                }
            }
        };
        network = new vis.Network(container, the_data, options);

    } catch (err) {
        alert("There was a problem drawing the graph. " + err.toString())
    }
    initialize(network);
    return network;
}

//Explicitly initializes needed events.
function initialize(net) {
  net.on("stabilizationIterationsDone", function () {
    document.getElementById('loading_div').hidden = true;
    if (bypass_lg_graph===0) {
        document.getElementById("modal_graph").style.display = 'block';
        moveGraphToModal();
    } else {
        moveGraphToColumn();
    }
    net.stopSimulation();
  });

  net.on('click', function (params) {
     if (params['nodes'][0] === undefined) {
        document.getElementById('id_node_id').value = '';
        document.getElementById('id_node_label').value = '';
        document.getElementById('id_color_type').value = '';
        keep_tooltip = false;
        tooltip_div.style.display = 'none';
     }
  });

  net.on('selectNode', function (params) {
      //set Qcode value in hidden node id field.
      let s = document.getElementById('id_node_id');
      s.value = params['nodes'][0];  //set node id field to curr selection
      //clear prior kw and subject search vals. New node searches now descended from curr node search.
      document.getElementById('id_prior_kw_search').value = ""; //ensure kw-facet search is switched off.
      document.getElementById('id_prior_facet_values').value = "";
      document.getElementById('id_prior_facet_labels').value = "";
      document.getElementById('id_prior_show_all').value = false;
      document.getElementById('id_prior_subj_search').value = ""; //ensure subj search is switched off.
      document.getElementById('id_prior_subj_labels').value = "";
      document.getElementById('id_prior_node_search').value = params['nodes'][0]; //new node search; prior=current
      //set label and color data for processing in views.process_search.
      let label_data = getLabel(params['nodes'][0]);
      let color_data = getColorType(params['nodes'][0]);
      document.getElementById('id_node_label').value = label_data; //set node label
      document.getElementById('id_prior_node_label').value = label_data; //prior label == curr label
      document.getElementById('id_color_type').value = color_data; //capture color of node
      document.getElementById('id_prior_color').value = color_data; // prior color == curr color
      //values have changed. Set dirty flag and enable search button.
      document.getElementById('id_dirty_flag').value = true;
      nodeFormButton.disabled = false;
    });

  net.on('hoverNode', function (params) {
      try {
        if (keep_tooltip === false) {
            let dict = showProperties(params['node']);
            tooltip_div.innerText = dict['the_list'];
            anchorForTooltip('image', dict['image_url']);
            anchorForTooltip('archival description', dict['da_url']);
            anchorForDetails(params['node']);
            tooltip_div.style.left = mouse_x + 'px';
            tooltip_div.style.top = mouse_y + 'px';
            tooltip_div.style.display = 'block';
        }
      } catch (err) {
          alert(err.message)
        }
    });

    net.on('doubleClick', function(params) {
        tooltip_div.style.display = 'block';
        keep_tooltip = true;
    });

    net.on('blurNode', function () {
        if (keep_tooltip!==true) {
            tooltip_div.style.display = 'none';
        } else {
            tooltip_div.style.display = 'block';
        }
    });

}

function setChecks() {
    //Picks up js array of checkboxes to set, based on prior user selections.
    //Checkboxes are referred to by ordinal position; 0. 1. 2...
    inbound_checks.forEach(function (c) {
        $('#id_relation_types div').each(function (i) {
            let key = '#id_relation_types_' + i.toString();
            if ($(key).prop('value') === c) {
                $(key).prop('checked', true);
            }
        });
    });
}

function getColorType(pitem_id) {
    //Finds and returns color-as-guid for graph nodes.
    let color_data = _.find(inbound_nodes, function (o) //inbound nodes init on template render.
    {return o.id === pitem_id;}, 0);
    if (color_data['color']) {
        return color_data['color'];
    } else {
        alert("Could not find color!")
        return "#00BFFF"
    }
}
function getLabel(pitem_id) {
    try {
        let lbl;
        let label_data = _.find(js_objects, function (o) //js_objects init on window load.
            {return o.id === pitem_id;}, 0);
        if (label_data['label']) {
            lbl = label_data['label'];
        } else {
             lbl = label_data.itemprops['itemlabel'];
        }
        return lbl;
    } catch (err) {
        alert(err.message + " " + pitem_id);
    }
}

function moveGraphToModal() {
    let c = document.getElementById('col-graph-parent');
    let m = document.getElementById('mod-graph-parent');
    let v = document.getElementById('graph_canvas');
    if (c.childElementCount > 0) {
        m.appendChild(c.lastChild);
        }
    v.style.height = '699px';
    centerGraph();
}
function centerGraph() {
    //let options = {position: {x: 0, y: 0}, scale: 1.15};
    network.redraw();
    network.fit();
}

function moveGraphToColumn() {
    let c = document.getElementById('col-graph-parent');
    let m = document.getElementById('mod-graph-parent');
    let v = document.getElementById('graph_canvas');
    if (m.childElementCount > 0) {
        c.appendChild(m.lastChild);
    }
    v.style.height = '436px';
    centerGraph();
}

function anchorForTooltip(label, href_val) {
    if (href_val !== '') {
        let newA = document.createElement("a");
        newA.href = href_val;
        newA.target = '_blank'
        newA.text = label
        document.getElementById('graph_tooltip').appendChild(newA);
    }
}

function anchorForDetails(item_id) {
    let curr_app_class = document.getElementById('id_app_class').value;
    let curr_color = getColorType(item_id);
    if (curr_color === '#f2f2f2') {
        let url = '/discover/' + curr_app_class + '/item/' + item_id;
        let newA = document.createElement("a");
        let br = document.createElement("br");
        newA.href = url;
        newA.text = "full item details";
        document.getElementById('graph_tooltip').appendChild(br);
        document.getElementById('graph_tooltip').appendChild(newA);
    }
}
function mapPropertyLabel (prop) {
    let label = property_labels[prop];
    if (!label) {
        return prop;
    } else {
        return label;
    }
}

function showProperties(pitem_id) {
    try {
        let i_data = _.find(js_objects, function (o) //js_objects init on window load.
            {return o.id === pitem_id;}, 0);
        if (i_data) {
            let da_url = '';
            let image_url = '';
            if (i_data["label"]) {
                return {the_list: i_data["label"], da_url: '', image_url: ''};
            } else {
                let list_vals = '';
                let da_url = '';
                let image_url = '';
                let item_props = i_data.itemprops;
                for (const p in item_props) {
                    if (!item_props[p]) {
                        //skip to next p
                    } else {
                        let label = mapPropertyLabel(`${p}`);
                        if (label === 'described at') {
                            da_url = `${item_props[p]}`;
                        } else if (label === 'image') {
                            image_url = `${item_props[p]}`;
                        } else {
                            list_vals += label + ": " + `${item_props[p]}` + '\n';
                        }
                    }
                }
                return {the_list: list_vals, image_url: image_url, da_url: da_url};

            }
        } else {
            return "";
        }
    } catch (err) {
        alert(err.message + err.code);
    }
}

function changeNodeFormState(){
    nodeFormButton.disabled = dirtyField.value !== true;
}

function changeQueueFormState() {
    queueFormButton.disabled = q_list.value === 'none';
}