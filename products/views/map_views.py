# products/views/map_views.py

from django.shortcuts import render
from products.models import FarmerProfile, Product, Category
from products.forms import LocationSearchForm
from products.utils import geocode_address, filter_farmers_by_distance
from django.contrib import messages

def map_view(request):
    """Vue pour afficher la carte avec les fermiers et permettre la recherche par distance."""
    form = LocationSearchForm(request.GET or None)
    farmers = FarmerProfile.objects.filter(latitude__isnull=False, longitude__isnull=False)
    nearby_farmers = []
    user_location = None
    search_performed = False
    
    if request.GET and form.is_valid():
        search_performed = True
        address = form.cleaned_data['address']
        radius = form.cleaned_data['radius']
        production_method = form.cleaned_data['production_method']
        category = form.cleaned_data['category']
        visits_allowed = form.cleaned_data['visits_allowed']
        
        # Géocoder l'adresse pour obtenir les coordonnées
        lat, lng = geocode_address(address)
        
        if lat and lng:
            user_location = {'lat': lat, 'lng': lng, 'address': address}
            
            # Trouver les fermiers à proximité
            farmers_with_distance = filter_farmers_by_distance(farmers, lat, lng, radius)
            nearby_farmers = []
            
            # Extraire les fermiers de la liste de tuples (fermier, distance)
            for farmer, distance in farmers_with_distance:
                farmer.distance = distance  # Ajouter la distance comme attribut
                nearby_farmers.append(farmer)
            
            # Filtrer par méthode de production
            if production_method:
                nearby_farmers = [f for f in nearby_farmers if f.production_method == production_method]
            
            # Filtrer par visites autorisées
            if visits_allowed:
                nearby_farmers = [f for f in nearby_farmers if f.visits_allowed]
            
            # Filtrer par catégorie de produits
            if category:
                farmers_with_category = []
                for farmer in nearby_farmers:
                    # Vérifier si le fermier a des produits dans cette catégorie
                    products = Product.objects.filter(farmer=farmer.farmer, category=category)
                    if products.exists():
                        farmers_with_category.append(farmer)
                nearby_farmers = farmers_with_category
            
            if not nearby_farmers:
                messages.info(request, f"Aucun fermier trouvé dans un rayon de {radius} km de '{address}'.")
        else:
            messages.error(request, "Impossible de géolocaliser l'adresse fournie.")
    
    # Préparer les données pour la carte
    map_farmers = nearby_farmers if search_performed else farmers
    farmers_data = []
    
    for farmer in map_farmers:
        # N'inclure que les fermiers avec des coordonnées valides
        if farmer.latitude and farmer.longitude:
            farmers_data.append({
                'id': farmer.id,
                'name': farmer.farmer.username,
                'lat': float(farmer.latitude),
                'lng': float(farmer.longitude),
                'description': farmer.description,
                'address': farmer.address,
                'phone': farmer.phone_number,
                'profile_url': f"/profil_farmer/profile/{farmer.farmer.id}/",
                # Ajouter la distance si disponible
                'distance': f"{farmer.distance:.1f} km" if hasattr(farmer, 'distance') else None,
                'production_method': farmer.get_production_method_display() if farmer.production_method else "Non spécifié",
                'visits_allowed': "Oui" if farmer.visits_allowed else "Non"
            })
    
    # Categories pour filtrer sur la carte
    categories = Category.objects.all()
    
    return render(request, 'products/map_view.html', {
        'form': form,
        'farmers': farmers_data,
        'farmer_count': len(farmers_data),
        'categories': categories,
        'user_location': user_location,
        'search_performed': search_performed,
        'radius': radius if search_performed and lat and lng else None,
    })