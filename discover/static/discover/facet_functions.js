        function handleFacetCheck(subj_id) {
            let si = document.getElementById(subj_id);
            let sl = document.getElementById(subj_id + '_label');
            let form_id = document.getElementById('id_facet_values');
            let form_label = document.getElementById('id_facet_labels');
            let fd = document.getElementById('facet_labels_div');
            let dirty = document.getElementById('id_search_dirty_flag');
            if (si.checked) {
                form_id.value += si.id + ',';
                form_label.value += sl.innerText + ',';
                fd.innerHTML = form_label.value;
                searchFormButton.disabled = false;
                dirty.value = true;
            } else {
                let old_ids = form_id.value;
                let old_labels = form_label.value;
                form_id.value = old_ids.replace(subj_id + ',', '');
                form_label.value = old_labels.replace(sl.innerText + ",", '')
                fd.innerHTML = form_label.value;
                if (fd.innerHTML === '') {
                    if (searchText.value === '') {
                        searchFormButton.disabled = true;
                        dirty.value = false;
                    }
                }
            }
        }

        function showFacetPicker() {
            let facet_labels = document.getElementById('id_facet_labels');
            let picker = document.getElementById('fp_wrapper_id');
            picker.style.left = mouse_x + 'px';
            picker.style.top = mouse_y + 'px';
           picker.style.display = 'block';

        }

        function hideFacetPicker() {
             let picker = document.getElementById('fp_wrapper_id');
             picker.style.display = 'none';
        }