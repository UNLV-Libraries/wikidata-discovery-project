from django import forms

class SearchForm(forms.Form):
    search_text = forms.CharField(label='Search for a word or phrase', max_length=200)

class RestrictSubjectForm(forms.Form):
    restrict_text = forms.CharField(label='Values to filter collections and corps.', max_length=1000)

class NodeSelectForm(forms.Form):
    selected_text = forms.CharField(label='Selected node', max_length=200)

