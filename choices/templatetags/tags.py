import re

from django import template
from django.core.urlresolvers import reverse, NoReverseMatch

register = template.Library()


@register.assignment_tag(takes_context=True)
def active_url(context, url):
    try:
        pattern = '^%s$' % reverse(url)
    except NoReverseMatch:
        pattern = url

    path = context['request'].path
    return "class=active" if re.search(pattern, path) else ''


@register.filter(name='times')
def times(number):
    return range(number)


@register.filter(name='minus')
def subtract(value, arg):
    return value - arg