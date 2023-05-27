from django import forms


class SearchForm(forms.Form):
    search_text = forms.CharField(label='Search for a word or phrase', max_length=200)


class RestrictSubjectForm(forms.Form):
    restrict_labels = forms.CharField(label="Selected Subjects", max_length=1000)
    restrict_text = forms.CharField(label='', max_length=1000)


class NodeSelectForm(forms.Form):
    color_type = forms.CharField(required=False, label='', max_length=20)
    shape_label = forms.CharField(required=False, label='Search by selected node:', max_length=200)
    selected_text = forms.CharField(required=False, label='', max_length=200)
    relation_types = forms.MultipleChoiceField(required=False, label='Show relation types',
                                               widget=forms.CheckboxSelectMultiple, choices=())

    def __init__(self, *args, **kwargs):
        dynamic_choices = kwargs.pop('dynamic_choices', ())
        super().__init__(*args, **kwargs)
        self.fields['relation_types'] = forms.MultipleChoiceField(required=False, label='Show relation types',
                                                                  widget=forms.CheckboxSelectMultiple,
                                                                  choices=dynamic_choices)
        # self.fields['relation_types'].choices = dynamic_choices


class WikiLoadForm(forms.Form):
    run_it = forms.ChoiceField(required=True, label="Choose process",
                               choices=[(0, ' -- '), (1, 'run all')])

class QueueForm(forms.Form):
    run_qry = forms.ChoiceField(label='Run a previous search',
                                choices=())

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
