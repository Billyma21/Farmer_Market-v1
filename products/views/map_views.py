from django.shortcuts import render
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