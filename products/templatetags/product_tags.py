from django import template
from django.utils import timezone
from datetime import datetime, timedelta

register = template.Library()

@register.filter
def get(dictionary, key):
    """Récupère une valeur dans un dictionnaire avec une clé"""
    return dictionary.get(key, None)

@register.filter
def date_offset(date, offset):
    """Ajoute un nombre de jours à une date"""
    if not date:
        return None
    return date + timedelta(days=int(offset))

@register.filter
def split(value, delimiter):
    """Divise une chaîne selon un délimiteur"""
    return value.split(delimiter)

@register.filter
def to_date(date_str):
    """Convertit une chaîne de caractères en date"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        return None

@register.filter
def date_in_week(date, start_of_week):
    """Vérifie si une date est dans la même semaine qu'une autre date"""
    if not date or not start_of_week:
        return False
    
    # Calculer le début de la semaine
    start_of_week_date = start_of_week
    if isinstance(start_of_week, datetime):
        start_of_week_date = start_of_week.date()
    
    # Calculer le premier jour de la semaine (lundi)
    weekday = start_of_week_date.weekday()
    week_start = start_of_week_date - timedelta(days=weekday)
    week_end = week_start + timedelta(days=6)
    
    # Vérifier si la date est dans cette semaine
    return week_start <= date <= week_end

@register.simple_tag
def get_product_avg_rating(product):
    """Récupère la note moyenne d'un produit"""
    from products.services import ReviewService
    return ReviewService.get_product_average_rating(product)

@register.simple_tag
def get_farmer_avg_rating(farmer):
    """Récupère la note moyenne d'un fermier"""
    from products.services import ReviewService
    return ReviewService.get_farmer_average_rating(farmer)

@register.simple_tag
def get_top_rated_products(limit=5, min_reviews=3):
    """Récupère les produits les mieux notés"""
    from products.services import ReviewService
    return ReviewService.get_top_rated_products(limit, min_reviews)

@register.simple_tag
def get_available_slots_for_order(order):
    """Récupère les créneaux disponibles pour une commande"""
    from products.services import PickupService
    return PickupService.get_available_slots_for_order(order)

@register.filter
def get_notification_count(user):
    """Récupère le nombre de notifications non lues pour un utilisateur"""
    if not user.is_authenticated:
        return 0
    return user.notifications.filter(read=False).count() 