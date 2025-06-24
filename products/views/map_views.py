from django.shortcuts import render
<<<<<<< HEAD
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
=======
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Avg
from products.models import FarmerProfile
from products.models.product import Product, Category
from markt_farme.logging_filters import log_audit_event

def map_view(request):
    """
    Vue pour afficher la carte des fermiers avec leur localisation,
    avec possibilité de filtrer par type de produit ou certification.
    """
    # Récupérer tous les profils de fermiers ayant des coordonnées
    farmers = FarmerProfile.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False
    ).select_related('farmer')
    
    # Récupérer les catégories pour le filtre
    categories = Category.objects.all()
    
    # Filtres
    selected_category = request.GET.get('category')
    certification = request.GET.get('certification')
    
    # Appliquer les filtres si nécessaire
    filtered_farmers = farmers
    if selected_category:
        # Filtrer les fermiers qui ont des produits dans cette catégorie
        farmer_ids = Product.objects.filter(
            category__id=selected_category, 
            farmer__profile__in=farmers
        ).values_list('farmer', flat=True).distinct()
        filtered_farmers = farmers.filter(farmer__id__in=farmer_ids)
    
    if certification and certification == 'bio':
        filtered_farmers = filtered_farmers.filter(is_organic_certified=True)
    
    # Log de l'accès à la carte
    log_audit_event(
        user=request.user,
        action='map_viewed',
        details='Carte des fermiers consultée',
        ip=request.META.get('REMOTE_ADDR', 'unknown')
    )
    
    # Préparation des données pour la vue
    farmers_data = []
    for farmer in filtered_farmers:
        # Calculer le nombre de produits
        product_count = Product.objects.filter(farmer=farmer.farmer, is_active=True).count()
        
        # Calculer la note moyenne
        avg_rating = Product.objects.filter(
            farmer=farmer.farmer
        ).aggregate(
            avg_rating=Avg('reviews__rating')
        )['avg_rating'] or 0
        
        farmer_data = {
            'profile': farmer,
            'product_count': product_count,
            'avg_rating': avg_rating
        }
        farmers_data.append(farmer_data)
    
    total_organic_farmers = filtered_farmers.filter(is_organic_certified=True).count()
    context = {
        'farmers': farmers_data,
        'categories': categories,
        'selected_category': selected_category,
        'certification': certification,
        'total_farmers': filtered_farmers.count(),
        'total_organic_farmers': total_organic_farmers,
        'page_title': 'Carte des fermiers'
    }
    
    return render(request, 'products/map_view.html', context)

def get_farmers_data(request):
    """API pour récupérer les données des fermiers en JSON"""
    farmers = FarmerProfile.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False
    ).select_related('farmer')
    
    farmers_data = []
    for farmer in farmers:
        # Calculer le nombre de produits
        product_count = Product.objects.filter(farmer=farmer.farmer, is_active=True).count()
        
        # Calculer la note moyenne
        avg_rating = Product.objects.filter(
            farmer=farmer.farmer
        ).aggregate(
            avg_rating=Avg('reviews__rating')
        )['avg_rating'] or 0
        
        farmers_data.append({
            'id': farmer.id,
            'name': farmer.farm_name or f"Ferme de {farmer.farmer.username}",
            'farmer_name': f"{farmer.farmer.first_name} {farmer.farmer.last_name}".strip() or farmer.farmer.username,
            'latitude': farmer.latitude,
            'longitude': farmer.longitude,
            'description': farmer.description[:200] + '...' if len(farmer.description) > 200 else farmer.description,
            'address': farmer.address,
            'phone': farmer.phone_number,
            'email': farmer.email,
            'website': farmer.website,
            'is_organic': farmer.is_organic_certified,
            'product_count': product_count,
            'avg_rating': avg_rating,
            'image_url': '/static/images/default-farm.jpg',
            'profile_url': f'/farmer/{farmer.farmer.username}/',
        })
    
    return JsonResponse({'farmers': farmers_data})

def search_farmers(request):
    """Recherche de fermiers par nom ou localisation"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        farmers = FarmerProfile.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False
        ).select_related('farmer')
    else:
        farmers = FarmerProfile.objects.filter(
            Q(latitude__isnull=False) & Q(longitude__isnull=False) &
            (Q(farm_name__icontains=query) |
             Q(farmer__username__icontains=query) |
             Q(farmer__first_name__icontains=query) |
             Q(farmer__last_name__icontains=query) |
             Q(city__icontains=query) |
             Q(description__icontains=query))
        ).select_related('farmer')
    
    farmers_data = []
    for farmer in farmers:
        # Calculer le nombre de produits
        product_count = Product.objects.filter(farmer=farmer.farmer, is_active=True).count()
        
        # Calculer la note moyenne
        avg_rating = Product.objects.filter(
            farmer=farmer.farmer
        ).aggregate(
            avg_rating=Avg('reviews__rating')
        )['avg_rating'] or 0
        
        farmers_data.append({
            'id': farmer.id,
            'name': farmer.farm_name or f"Ferme de {farmer.farmer.username}",
            'farmer_name': f"{farmer.farmer.first_name} {farmer.farmer.last_name}".strip() or farmer.farmer.username,
            'latitude': farmer.latitude,
            'longitude': farmer.longitude,
            'description': farmer.description[:200] + '...' if len(farmer.description) > 200 else farmer.description,
            'address': farmer.address,
            'phone': farmer.phone_number,
            'email': farmer.email,
            'website': farmer.website,
            'is_organic': farmer.is_organic_certified,
            'product_count': product_count,
            'avg_rating': avg_rating,
            'image_url': '/static/images/default-farm.jpg',
            'profile_url': f'/farmer/{farmer.farmer.username}/',
        })
    
    return JsonResponse({'farmers': farmers_data}) 
>>>>>>> V1.01
