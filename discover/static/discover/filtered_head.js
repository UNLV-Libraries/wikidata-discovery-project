let tooltip_div;
let mouse_x, mouse_y;
let js_objects;
let queueFormButton, nodeForm, nodeFormButton, q_list;

window.onload = function () {
    modal = document.getElementById("modal_graph");
    tooltip_div = document.getElementById('graph_tooltip');
    js_objects = JSON.parse(document.getElementById('property_data').innerHTML);

    //control states of 'submit' buttons
    nodeForm = document.getElementById('node_form');
    queueFormButton = document.getElementById('q_submit');
    nodeFormButton = document.getElementById('node_submit');
    queueFormButton.disabled = true;
    nodeFormButton.disabled = true;

    nodeForm.addEventListener('input', function (){
        document.getElementById('id_dirty_flag').value = true;
        nodeFormButton.disabled = false;
    });

    //dirtyField = document.querySelector('#id_dirty_flag');
    q_list = document.querySelector('#id_run_qry');

    q_list.addEventListener('change', function () {
        queueFormButton.disabled = q_list.value === 'none';
    });

    //hide loading graph if zero records have been returned.
    if (!js_objects.length) {document.getElementById('loading_div').hidden = true;}

    drawGraph(); //loads on-page data into vis.js graph.
    setChecks();  //sets one or more checks based on prior user selection.

}

//track mouse positions for tooltip
window.addEventListener('mousemove', function (event) {
    mouse_x = event.clientX;
    mouse_y = event.clientY;
})

//window.addEventListener('change', function (event) {
//    document.getElementById('id_dirty_flag').value = true;
//})

