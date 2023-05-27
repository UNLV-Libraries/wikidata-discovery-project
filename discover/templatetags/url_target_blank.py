"""Used to add target attribute to <a> links."""
from django import template
register = template.Library()

def url_target_blank(text):
    return text.replace('<a ', '<a target="_blank" ')

url_target_blank = register.filter(url_target_blank, is_safe = True)