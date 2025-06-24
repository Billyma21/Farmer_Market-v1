from django import template
from datetime import datetime, timedelta
import json

register = template.Library()

@register.filter
def date_offset(value, days):
    """Ajoute un nombre de jours à une date"""
    if not value:
        return value
    return value + timedelta(days=int(days))

@register.filter
def get(dictionary, key):
    """Obtenir un élément d'un dictionnaire en utilisant une clé"""
    return dictionary.get(key, None)

@register.filter
def split(value, delimiter):
    """Divise une chaîne de caractères selon un délimiteur"""
    return value.split(delimiter)

@register.filter
def to_json(value):
    """Convertit une valeur en JSON"""
    return json.dumps(value)

@register.filter
def multiply(value, arg):
    """Multiplie la valeur par l'argument"""
    return float(value) * float(arg)

@register.filter
def subtract(value, arg):
    """Soustrait l'argument de la valeur"""
    return float(value) - float(arg)

@register.filter
def percentage(value, total):
    """Calcule le pourcentage"""
    if float(total) == 0:
        return 0
    return (float(value) / float(total)) * 100 