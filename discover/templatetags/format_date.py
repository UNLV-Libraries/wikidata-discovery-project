"""Used to add 'target' attribute to <a> links."""
from django import template
from datetime import date
from django.template.defaultfilters import stringfilter

register = template.Library()


@stringfilter
def format_date_string(text):
    """Determines if 'text' is in Wikidata's yyyy-mm-dd format and converts to Eng lang date; or, returns 'text'."""

    if text.__len__() > 9:
        year = text[:4]
        month = text[5:7]
        day = text[8:10]
        if year.isnumeric() and month.isnumeric() and day.isnumeric():
            d = date(int(year), int(month), int(day))
            return str(d.strftime('%d %B, %Y'))
        else:
            return text
    else:
        return text


format_date = register.filter('format_date', format_date_string, is_safe=True)
