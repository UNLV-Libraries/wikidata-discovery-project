from django import forms

class SearchForm(forms.Form):
    search_text = forms.CharField(label='Search for a word or phrase', max_length=200)