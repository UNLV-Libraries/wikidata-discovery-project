let queueFormButton, nodeForm, nodeFormButton, q_list, searchForm, searchFormButton;
let searchText, searchShowAll, facetValues, facetLabels, facetLabelsDiv;
let tooltip_div;
let mouse_x, mouse_y;
let js_objects;
let typeahead;

window.onload = function () {
    //highlight selected menu text
    let the_menu = ".site-menu ul #" + app_class + " a";
    $(the_menu).css('background-color', '#9c1616');

    //type-ahead text box for facet value filtering
    typeahead = document.getElementById('typeahead');

    //control states of 'submit' buttons
    searchForm = document.getElementById('search_form');
    searchFormButton = document.getElementById('search_submit');
    searchFormButton.disabled = true;
    searchShowAll = document.getElementById('id_show_all');
    searchText = document.getElementById('id_search_text');
    facetValues = document.getElementById('id_facet_values');
    facetLabels = document.getElementById('id_facet_labels');
    facetLabelsDiv = document.getElementById('facet_labels_div');
    queueFormButton = document.getElementById('q_submit');
    queueFormButton.disabled = true;
    //Don't allow download action if no records returned
    let num = document.getElementById('num_val');
    if (num) {
        if (num.innerText === '0') {
            document.getElementById("download_button").disabled = true;
        }
    }
    // events to handle type-ahead filtering
    typeahead.addEventListener('pointerenter', function () {
        if (typeahead.value === '[filter]') {
            typeahead.value = '';
        }
    })

    typeahead.addEventListener('input', function () {
        $('.picker_row').each(function () {
            let tds = this.children[1].innerHTML.toLowerCase();
            if (tds.includes(typeahead.value.toLowerCase())) {
                this.style.display = 'block';
            } else {
                this.style.display = 'none';
            }
        })
    })
    //enable-disable search form submit btn.
    searchForm.addEventListener('input', function () {
        let n = 0;
        let dirty = document.getElementById('id_search_dirty_flag')
        if (searchText.value.trim() !== '') {
            n = 1;
        }
        if (searchShowAll.checked) {
            n = 1;
            //clear any existing search values if searchShowAll is checked.
            searchText.value = '';
            facetValues.value = '';
            facetLabels.value = '';
            facetLabelsDiv.innerHTML = '';
        }
        if (facetValues.value.trim() !== '') {
            n = 1;
        }
        if (n > 0) {
            searchFormButton.disabled = false;
            dirty.value = true;
        } else {
            searchFormButton.disabled = true;
            dirty.value = false;
        }

    });

    //set up _filtered page type if node form is present.
    nodeForm = document.getElementById('node_form');
    if (nodeForm !== null) {
        // search result graph controls and data
        modal = document.getElementById("modal_graph");
        tooltip_div = document.getElementById('graph_tooltip');
        js_objects = JSON.parse(document.getElementById('property_data').innerHTML);

        // node form controls
        nodeFormButton = document.getElementById('node_submit');
        nodeFormButton.disabled = true;
        nodeForm.addEventListener('input', function () {
            document.getElementById('id_dirty_flag').value = true;
            nodeFormButton.disabled = false;
        });

        //hide loading graph gif if zero records have been returned.
        if (!js_objects.length) {document.getElementById('loading_div').hidden = true;}

        drawGraph(); //loads on-page data into vis.js graph.
        setChecks();  //sets one or more checks based on prior user selection.
    }

    //enable-disable queue form submit button
    q_list = document.querySelector('#id_run_qry');
    q_list.addEventListener('change', function () {
        queueFormButton.disabled = q_list.value === 'none';
    });

    window.addEventListener('mousemove', function (event) {
        mouse_x = event.clientX;
        mouse_y = event.clientY;
    });

}