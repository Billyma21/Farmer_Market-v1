import requests
import math
import time
from django.conf import settings

def geocode_address(address):
    """
    Convertit une adresse en coordonnées GPS (latitude, longitude) en utilisant 
    le service de geocodage Nominatim d'OpenStreetMap.
    
    Args:
        address (str): L'adresse à géocoder
        
    Returns:
        tuple: (latitude, longitude) ou (None, None) si le géocodage échoue
    """
    # Ajouter un délai pour respecter la politique d'utilisation de Nominatim
    time.sleep(1)
    
    # Construire l'URL de requête Nominatim
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1,
        "addressdetails": 1,
    }
    
    # Ajouter l'en-tête User-Agent comme requis par Nominatim
    headers = {
        "User-Agent": "FarmerMarketApp/1.0"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        results = response.json()
        
        if results:
            lat = float(results[0]['lat'])
            lon = float(results[0]['lon'])
            return lat, lon
        else:
            return None, None
    except Exception as e:
        # Log l'erreur si nécessaire
        print(f"Erreur de géocodage: {str(e)}")
        return None, None

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calcule la distance en kilomètres entre deux points géographiques 
    en utilisant la formule haversine.
    
    Args:
        lat1, lon1: Coordonnées du premier point
        lat2, lon2: Coordonnées du second point
        
    Returns:
        float: Distance en kilomètres
    """
    # Rayon de la Terre en kilomètres
    R = 6371.0
    
    # Conversion des degrés en radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Différence de longitude et latitude
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    # Formule haversine
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return distance

def filter_farmers_by_distance(farmers, center_lat, center_lon, radius_km):
    """
    Filtre une liste de fermiers en fonction de leur distance par rapport à un point central.
    
    Args:
        farmers (QuerySet): QuerySet de FarmerProfile
        center_lat (float): Latitude du point central
        center_lon (float): Longitude du point central
        radius_km (int): Rayon de recherche en kilomètres
        
    Returns:
        list: Liste de tuples (farmer, distance) où distance est en kilomètres
    """
    farmers_with_distance = []
    
    for farmer in farmers:
        # Vérifier que les coordonnées sont valides
        if farmer.latitude is not None and farmer.longitude is not None:
            distance = calculate_distance(
                center_lat, center_lon, 
                farmer.latitude, farmer.longitude
            )
            
            if distance <= radius_km:
                farmers_with_distance.append((farmer, distance))
    
    # Trier par distance
    farmers_with_distance.sort(key=lambda x: x[1])
    
    return farmers_with_distance 