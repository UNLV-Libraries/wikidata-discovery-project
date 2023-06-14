// initialize global variables.
let my_edges;
let my_nodes;
let network;
let the_data;

// This method is responsible for drawing the graph, returns the drawn network
function drawGraph() {
    let container = document.getElementById('vis-container');
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
                improvedLayout: true
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
    net.on("stabilizationProgress", function (params) {
        //document.getElementById('loading_div').hidden = false;
    });

  net.on("stabilizationIterationsDone", function () {
    document.getElementById('loading_div').hidden = true;
  });

  net.on('selectNode', function (params) {
      let s = document.getElementById('id_node_id');
      s.value = params['nodes'][0];  //set node id field to curr selection
      document.getElementById('id_prior_kw_search').value = ""; //ensure kw search is switched off.
      document.getElementById('id_prior_subj_search').value = ""; //ensure subj search is switched off.
      document.getElementById('id_prior_subj_labels').value = ""; //ensure subj label is empty.
      document.getElementById('id_prior_node_search').value = params['nodes'][0]; //new node search; prior=current
      let label_data = getLabel(params['nodes'][0]);
      let color_data = getColorType(params['nodes'][0]);
      document.getElementById('id_node_label').value = label_data; //set node label
      document.getElementById('id_prior_node_label').value = label_data; //prior label == curr label
      document.getElementById('id_color_type').value = color_data; //capture color of node
      document.getElementById('id_prior_color').value = color_data; // prior color == curr color
      document.getElementById('id_dirty_flag').value = true;
    });

  net.on('hoverNode', function (params) {
      try {
        tooltip_div.innerText = showProperties(params['node']);
        tooltip_div.style.left = mouse_x + 'px';
        tooltip_div.style.top = mouse_y + 'px';
        tooltip_div.hidden = false;
      } catch (err) {
          alert(err.message)
        }
    });

    net.on('blurNode', function () {
        tooltip_div.hidden = true;
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
