let tooltip_div;
let mouse_x, mouse_y;
let js_objects;

window.onload = function () {
    tooltip_div = document.getElementById('vis-tooltip');
    js_objects = JSON.parse(document.getElementById('property_data').innerHTML);
    drawGraph();
    setChecks();  //sets one or more checks based on prior user selection.
}

//track mouse positions for tooltip
window.addEventListener('mousemove', function (event) {
    mouse_x = event.clientX;
    mouse_y = event.clientY;
})
