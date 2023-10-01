from django import forms


class SearchForm(forms.Form):
    search_text = forms.CharField(required=False, label='Search for a word/phrase', max_length=200)
    show_all = forms.BooleanField(required=False, widget=forms.CheckboxInput())
    app_class = forms.CharField(widget=forms.HiddenInput())
    relation_type = forms.CharField(required=False, widget=forms.HiddenInput())
    facet_values = forms.CharField(required=False, widget=forms.HiddenInput(), max_length=500)
    facet_labels = forms.CharField(required=False, widget=forms.HiddenInput(), max_length=500)
    search_dirty_flag = forms.BooleanField(widget=forms.HiddenInput())  # required to set form to 'valid'


class RestrictSubjectForm(forms.Form):
    restrict_labels = forms.CharField(label='', max_length=1000)
    restrict_text = forms.CharField(label='', max_length=1000)
    app_class = forms.CharField(widget=forms.HiddenInput())


class NodeSelectForm(forms.Form):
    color_type = forms.CharField(required=False, label='', max_length=20)
    node_label = forms.CharField(required=False, label='Search by Selected Node:', max_length=200)
    node_id = forms.CharField(required=False, label='', max_length=200)
    relation_types = forms.MultipleChoiceField(required=False, label='Show links:',
                                               widget=forms.CheckboxSelectMultiple(attrs={'class': 'rel_row'}),
                                               choices=())
    app_class = forms.CharField(widget=forms.HiddenInput())
    dirty_flag = forms.BooleanField(widget=forms.HiddenInput())  # required to set form to 'valid'
    prior_kw_search = forms.CharField(required=False, widget=forms.HiddenInput())
    prior_node_search = forms.CharField(required=False, widget=forms.HiddenInput())
    prior_color = forms.CharField(required=False, widget=forms.HiddenInput())
    prior_node_label = forms.CharField(required=False, widget=forms.HiddenInput())
    prior_subj_search = forms.CharField(required=False, widget=forms.HiddenInput())
    prior_subj_labels = forms.CharField(required=False, widget=forms.HiddenInput())
    prior_facet_values = forms.CharField(required=False, widget=forms.HiddenInput())
    prior_facet_labels = forms.CharField(required=False, widget=forms.HiddenInput())
    prior_show_all = forms.BooleanField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        dynamic_choices = kwargs.pop('dynamic_choices', ())
        super().__init__(*args, **kwargs)
        self.fields['relation_types'] = forms.MultipleChoiceField(required=False, label='Show links:',
                                                                  widget=forms.CheckboxSelectMultiple(
                                                                      attrs={'class': 'rel-row'}),
                                                                  choices=dynamic_choices)


class WikiLoadForm(forms.Form):
    run_it = forms.ChoiceField(required=True, label="Choose process",
                               choices=[(0, ' -- '), (1, 'run all'), (2, 'people'),
                                        (3, 'corp bodies'), (4, 'collections'),
                                        (5, 'oral histories'), (6, 'subjects')])


class QueueForm(forms.Form):
    run_qry = forms.ChoiceField(label='Run a previous search',
                                choices=())
    app_class = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        dynamic_choices = kwargs.pop('dynamic_choices', ())
        super().__init__(*args, **kwargs)
        self.fields['run_qry'] = forms.ChoiceField(label='Run a previous search',
                                                   choices=dynamic_choices)


class BackButtonForm(forms.Form):
    back_value = forms.CharField(required=True, max_length=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['back_value'].widget = forms.HiddenInput()


class DownloadForm(forms.Form):
    file_format = forms.ChoiceField(label='Download search results', choices=[('csv', 'csv'), ('json', 'json')])
