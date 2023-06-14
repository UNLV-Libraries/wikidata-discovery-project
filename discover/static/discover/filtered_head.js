let tooltip_div;
let mouse_x, mouse_y;
let js_objects;

window.onload = function () {
    tooltip_div = document.getElementById('vis-tooltip');
    js_objects = JSON.parse(document.getElementById('property_data').innerHTML);
    //hide loading graph if zero records have been returned.
    if (!js_objects.length) {document.getElementById('loading_div').hidden = true;}
    drawGraph();
    setChecks();  //sets one or more checks based on prior user selection.
}

//track mouse positions for tooltip
window.addEventListener('mousemove', function (event) {
    mouse_x = event.clientX;
    mouse_y = event.clientY;
})

window.addEventListener('change', function (event) {
    //alert('changed');
    document.getElementById('id_dirty_flag').value = true;
})
