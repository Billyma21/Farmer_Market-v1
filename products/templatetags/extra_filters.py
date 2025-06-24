# products/templatetags/extra_filters.py
from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """Split a string by a given separator"""
    if isinstance(value, str):
        return value.split(arg)
    return value
