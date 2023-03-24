from django.contrib import admin
from .models import WdQuery, Filter

# Allow tables for these classes to be edited in the admin interface.
admin.site.register(WdQuery)
admin.site.register(Filter)
# admin.site.register(ErrorLog)
