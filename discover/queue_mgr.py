"""Functions for managing a prior searches queue in the session object."""
# from django.http import QueryDict
# from django.core.handlers.wsgi import WSGIRequest
# from io import StringIO
# from django.http.request import HttpRequest
from django.contrib.sessions.backends.db import SessionStore
from django import forms
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from .wd_utils import catch_err


def update_queue(form_type, form: forms.Form, session_key):
    """Places the most recent search results at the top of the queue
    after moving older results down the queue."""
    sess = SessionStore(session_key=session_key)

    # Move existing entries down the queue -- 3 deep.
    sess['bottom'] = sess['middle']
    sess['middle'] = sess['top']

    if form.is_valid():  # checked a 2nd time only for rehydrated form objects coming from create_request()
        if form_type == 'search':
            sess['top'] = {}
            sess['top']['form_type'] = form_type
            sess['top']['form_vals'] = {}
            sess['top']['form_vals']['search_text'] = form.cleaned_data['search_text']
            sess['top']['form_vals']['facet'] = form.cleaned_data['facet']
            sess['top']['form_vals']['relation_type'] = form.cleaned_data['relation_type']
        elif form_type == 'node':
            form_choices = '|'.join(form.cleaned_data['relation_types'])
            sess['top'] = {}
            sess['top']['form_type'] = form_type
            sess['top']['form_vals'] = {}
            sess['top']['form_vals']['node_id'] = form.cleaned_data['node_id']
            sess['top']['form_vals']['node_label'] = form.cleaned_data['node_label']
            sess['top']['form_vals']['relation_types'] = form_choices
            sess['top']['form_vals']['color_type'] = form.cleaned_data['color_type']
            sess['top']['form_vals']['facet'] = form.cleaned_data['facet']
            sess['top']['form_vals']['prior_kw_search'] = form.cleaned_data['prior_kw_search']
            sess['top']['form_vals']['prior_subj_search'] = form.cleaned_data['prior_subj_search']
            sess['top']['form_vals']['prior_subj_labels'] = form.cleaned_data['prior_subj_labels']
            sess['top']['form_vals']['prior_node_search'] = form.cleaned_data['prior_node_search']
            sess['top']['form_vals']['prior_color'] = form.cleaned_data['prior_color']
            sess['top']['form_vals']['prior_node_label'] = form.cleaned_data['prior_node_label']
            sess['top']['form_vals']['dirty_flag'] = form.cleaned_data['dirty_flag']

        elif form_type == 'subject':
            sess['top'] = {}
            sess['top']['form_type'] = form_type
            sess['top']['form_vals'] = {}
            sess['top']['form_vals']['restrict_text'] = form.cleaned_data['restrict_text']
            sess['top']['form_vals']['restrict_labels'] = form.cleaned_data['restrict_labels']
            sess['top']['form_vals']['facet'] = form.cleaned_data['facet']
        else:
            print('Uh oh!')

        sess.save()


def create_request(session_key, queue_key, bypass):
    """Places form values from queue into a new request object
    and returns the object for use in view functions."""
    from . import forms
    from .enums import Facet

    try:
        frm = object
        factory = RequestFactory()
        sess = SessionStore(session_key=session_key)
        form_data = sess[queue_key]

        url = '/'  # initial value; will be overwritten.

        # perform any mods needed to the form data, esp. deserializing list values
        if form_data['form_type'] == 'node':
            choices = form_data['form_vals']['relation_types']
            form_data['form_vals']['relation_types'] = choices.split('|')

        # set request url
        if form_data['form_vals']['facet'] == Facet.people.value:
            url = '/discover/people_filtered/'
        elif form_data['form_vals']['facet'] == Facet.corps.value:
            url = '/discover/corps_filtered/'
        elif form_data['form_vals']['facet'] == Facet.colls.value:
            url = '/discover/collections_filtered/'
        elif form_data['form_vals']['facet'] == Facet.orals.value:
            url = '/discover/orals_filtered/'

        # create request
        request = RequestFactory.post(factory, url,
                                      form_data['form_vals'], secure=True)
        request.user = AnonymousUser()

        # create form based on form type for update_queue function.
        if form_data['form_type'] == 'search':
            frm = forms.SearchForm(request.POST)
        elif form_data['form_type'] == 'node':
            frm = forms.NodeSelectForm(request.POST)
        elif form_data['form_type'] == 'subject':
            frm = forms.RestrictSubjectForm(request.POST)

        # if not bypass:
            # update_queue(form_data['form_type'], frm, session_key)

        return request
    except Exception as e:
        catch_err(e, 'queue_mgr.create_request')


# def get_middle_request(session_key):
    """Returns data from most recent prior search without updating the queue."""
#    sess = SessionStore(session_key=session_key)
#    return sess['middle']


def get_queue_entry(position, session_key):
    """Returns all data for the given queue position."""
    sess = SessionStore(session_key=session_key)
    return sess[position]


def get_queue_list(session_key) -> list:
    """Builds a list of prior searches to show in the
    prior searches select box on web pages."""
    sess = SessionStore(session_key=session_key)
    top_rel_types = ''
    mid_rel_types = ''
    bottom_rel_types = ''
    try:
        if sess['top']['form_type'] == 'search':
            top_search_key = 'search_text'
            top_facet = sess['top']['form_vals']['facet']
            top_rel_types = ' + ' + sess['top']['form_vals']['relation_type']
        elif sess['top']['form_type'] == 'node':
            if sess['top']['form_vals']['prior_node_search'] == '':  # no previous node search
                top_search_key = 'prior_kw_search'  # use the old key-phrase search instead
                top_rel_types = ' + ' + sess['top']['form_vals']['relation_types']
            else:
                top_search_key = 'prior_node_label'  # use the old label for node search
                top_rel_types = ' + ' + sess['top']['form_vals']['relation_types']
            top_facet = sess['top']['form_vals']['facet']
        elif sess['top']['form_type'] == 'subject':
            top_facet = 'subjects'
            top_search_key = 'restrict_labels'
        else:
            top_search_key = 'data'  # empty form stub created on views.init_session.
            top_facet = ''

        if sess['middle']['form_type'] == 'search':
            mid_search_key = 'search_text'
            mid_facet = sess['middle']['form_vals']['facet']
            mid_rel_types = ' + ' + sess['middle']['form_vals']['relation_type']
        elif sess['middle']['form_type'] == 'node':
            if sess['middle']['form_vals']['prior_node_search'] == '':  # no previous node search
                mid_search_key = 'prior_kw_search'  # use the old key-phrase search instead
                mid_rel_types = ' + ' + sess['middle']['form_vals']['relation_types']
            else:
                mid_search_key = 'prior_node_label'  # use the old label from the old node search
                mid_rel_types = ' + ' + sess['middle']['form_vals']['relation_types']
            mid_facet = sess['middle']['form_vals']['facet']
        elif sess['middle']['form_type'] == 'subject':
            mid_search_key = 'restrict_labels'
            mid_facet = 'subjects'
        else:
            mid_search_key = 'data'
            mid_facet = ''

        if sess['bottom']['form_type'] == 'search':
            bottom_search_key = 'search_text'
            bottom_facet = sess['bottom']['form_vals']['facet']
            bottom_rel_types = ' + ' + sess['bottom']['form_vals']['relation_type']
        elif sess['bottom']['form_type'] == 'node':
            if sess['bottom']['form_vals']['prior_node_search'] == '':  # no previous node search
                bottom_search_key = 'prior_kw_search'  # use the old key-phrase search instead
                bottom_rel_types = ' + ' + sess['bottom']['form_vals']['relation_types']
            else:
                bottom_search_key = 'prior_node_label'  # use the old label from the old node search
                bottom_rel_types = ' + ' + sess['bottom']['form_vals']['relation_types']
            bottom_facet = sess['bottom']['form_vals']['facet']
        elif sess['bottom']['form_type'] == 'subject':
            bottom_search_key = 'restrict_labels'
            bottom_facet = 'subjects'
        else:
            bottom_search_key = 'data'
            bottom_facet = ''

        the_choices = [('none', ' ---- ')]
        # Don't add slugs -- those that ='data' -- from queue initialization to pick list
        if not top_search_key == 'data':
            the_choices.append(('top', top_facet + ": " +
                                sess['top']['form_vals'][top_search_key][:50] + '...' + top_rel_types))

        if not mid_search_key == 'data':
            the_choices.append(('middle', mid_facet + ": " +
                                sess['middle']['form_vals'][mid_search_key][:50] + '...' + mid_rel_types))

        if not bottom_search_key == 'data':
            the_choices.append(('bottom', bottom_facet + ": " +
                                sess['bottom']['form_vals'][bottom_search_key][:50] + '...' + bottom_rel_types))

        return the_choices
    except Exception as e:
        catch_err(e, 'queue_mgr.get_queue_list')
