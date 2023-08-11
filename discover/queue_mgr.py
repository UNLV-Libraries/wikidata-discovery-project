"""Functions for managing a prior searches queue in the session object."""

from django.contrib.sessions.backends.db import SessionStore
from django import forms
from .wd_utils import catch_err


def update_queue(form_type, form: forms.Form, session_key):
    """Places the most recent search results at the top of the queue
    after moving older results down the queue."""
    sess = SessionStore(session_key=session_key)

    # Move existing entries down the queue -- 3 deep.
    sess['bottom'] = sess['middle']
    sess['middle'] = sess['top']

    try:
        if form.is_valid():  # checked a 2nd time only for rehydrated form objects coming from create_request()
            if form_type == 'search':
                sess['top'] = {}
                sess['top']['form_type'] = form_type
                sess['top']['form_vals'] = {}
                sess['top']['form_vals']['search_text'] = form.cleaned_data['search_text']
                sess['top']['form_vals']['app_class'] = form.cleaned_data['app_class']
                sess['top']['form_vals']['relation_type'] = form.cleaned_data['relation_type']
                sess['top']['form_vals']['facet_values'] = form.cleaned_data['facet_values']
                sess['top']['form_vals']['facet_labels'] = form.cleaned_data['facet_labels']
                sess['top']['form_vals']['search_dirty_flag'] = form.cleaned_data['search_dirty_flag']
                sess['top']['form_vals']['show_all'] = form.cleaned_data['show_all']
            elif form_type == 'node':
                form_choices = '|'.join(form.cleaned_data['relation_types'])
                sess['top'] = {}
                sess['top']['form_type'] = form_type
                sess['top']['form_vals'] = {}
                sess['top']['form_vals']['node_id'] = form.cleaned_data['node_id']
                sess['top']['form_vals']['node_label'] = form.cleaned_data['node_label']
                sess['top']['form_vals']['relation_types'] = form_choices
                sess['top']['form_vals']['color_type'] = form.cleaned_data['color_type']
                sess['top']['form_vals']['app_class'] = form.cleaned_data['app_class']
                sess['top']['form_vals']['prior_kw_search'] = form.cleaned_data['prior_kw_search']
                sess['top']['form_vals']['prior_facet_values'] = form.cleaned_data['prior_facet_values']
                sess['top']['form_vals']['prior_facet_labels'] = form.cleaned_data['prior_facet_labels']
                sess['top']['form_vals']['prior_subj_search'] = form.cleaned_data['prior_subj_search']
                sess['top']['form_vals']['prior_subj_labels'] = form.cleaned_data['prior_subj_labels']
                sess['top']['form_vals']['prior_node_search'] = form.cleaned_data['prior_node_search']
                sess['top']['form_vals']['prior_color'] = form.cleaned_data['prior_color']
                sess['top']['form_vals']['prior_node_label'] = form.cleaned_data['prior_node_label']
                sess['top']['form_vals']['dirty_flag'] = form.cleaned_data['dirty_flag']
                sess['top']['form_vals']['prior_show_all'] = form.cleaned_data['prior_show_all']
            elif form_type == 'subject':
                sess['top'] = {}
                sess['top']['form_type'] = form_type
                sess['top']['form_vals'] = {}
                sess['top']['form_vals']['restrict_text'] = form.cleaned_data['restrict_text']
                sess['top']['form_vals']['restrict_labels'] = form.cleaned_data['restrict_labels']
                sess['top']['form_vals']['app_class'] = form.cleaned_data['app_class']
            else:
                raise ValueError("Wikiframe is trying to send a form type that doesn't exist.")

            sess.save()
    except Exception as e:
        catch_err(e, 'queue_mgr.update_queue')


def create_request(session_key, queue_key, path):
    """Places form values from queue into a new request object
    and returns the object for use in view functions."""
    from .enums import AppClass
    from django.contrib.auth.models import AnonymousUser
    from django.test import RequestFactory

    try:

        factory = RequestFactory()
        sess = SessionStore(session_key=session_key)
        form_data = sess[queue_key]

        # perform any mods needed to the form data, esp. deserializing list values
        if form_data['form_type'] == 'node':
            choices = form_data['form_vals']['relation_types']
            form_data['form_vals']['relation_types'] = choices.split('|')

        # create request
        request = RequestFactory.post(factory, path,
                                      form_data['form_vals'], secure=True)
        request.user = AnonymousUser()

        return request
    except Exception as e:
        catch_err(e, 'queue_mgr.create_request')


def get_queue_entry(position, session_key):
    """Returns all data for the given queue position."""
    sess = SessionStore(session_key=session_key)
    return sess[position]


def get_queue_list(session_key) -> list:
    """Builds a list of prior searches to show in the
    prior searches select box on web pages."""
    sess = SessionStore(session_key=session_key)
    q_positions = ['top', 'middle', 'bottom']
    the_choices = [('none', ' ---- ')]

    try:
        for pos in q_positions:
            if sess[pos]['form_type'] == 'search':
                search_str = make_search_label(sess[pos]['form_vals']['search_text'],
                                               sess[pos]['form_vals']['facet_labels'])
                the_class = sess[pos]['form_vals']['app_class']
                rel_types = sess[pos]['form_vals']['relation_type']
            elif sess[pos]['form_type'] == 'node':
                if sess[pos]['form_vals']['prior_node_search'] == '':  # no previous node search
                    search_str = make_search_label(sess[pos]['form_vals']['prior_kw_search'],
                                                   sess[pos]['form_vals']['prior_facet_labels'])
                    rel_types = sess[pos]['form_vals']['relation_types']
                else:
                    search_str = sess[pos]['form_vals']['prior_node_label']  # use the old label for node search
                    rel_types = sess[pos]['form_vals']['relation_types']
                the_class = sess[pos]['form_vals']['app_class']
            elif sess[pos]['form_type'] == 'subject':
                the_class = 'subjects'
                search_str = sess[pos]['form_vals']['restrict_labels']
                rel_types = 'subject'
            else:
                search_str = 'data'  # empty form stub created on views.init_session.
                the_class = ''
                rel_types = ''

            # Don't add placeholders -- those that ='data' -- from queue initialization to pick list
            if not search_str == 'data':
                the_choices.append((pos, the_class + ": " + search_str[:50] + '. link=' + rel_types))

        return the_choices
    except Exception as e:
        catch_err(e, 'queue_mgr.get_queue_list')


def make_search_label(search_text, facet_labels):
    """Formats a search string label based on the terms and/or facet
    values used."""
    n = 0
    if search_text.__len__() > 0:
        n += 1
    if facet_labels.__len__() > 0:
        n += 2

    if n == 1:
        return search_text
    elif n == 2:
        return facet_labels
    elif n == 3:
        return search_text + " & " + facet_labels
    else:
        return "All"
