from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from datetime import datetime


def delete_template_fragment_cache_key(fragment_name, *variables):
    cache_key = make_template_fragment_key(
        fragment_name, vary_on=variables)
    cache.delete(cache_key)


def get_template_fragment_cache_key(fragment_name, *variables):
    cache_key = make_template_fragment_key(fragment_name, vary_on=variables)
    return cache_key


def set_template_fragment_timestamp(fragment_name, status, client_or_selection):
    key = "%s_%s_%s" % (fragment_name, status, str(client_or_selection.id))
    cache.set(key, client_or_selection.last_modified, 9999999)


def get_template_fragment_timestamp(fragment_name, status, client_or_selection):
    key = "%s_%s_%s" % (fragment_name, status, str(client_or_selection.id))
    return cache.get(key)
