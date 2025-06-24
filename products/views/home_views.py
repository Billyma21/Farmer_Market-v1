# Farmer_Market-v1/products/views/home_views.py

# products/views/client_views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Prefetch, Count, Avg
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from products.models import Product, Category, Review
from django.views.decorators.vary import vary_on_cookie
from django.core.paginator import Paginator
from django.utils.translation import gettext as _
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


# Logique principale partagée pour récupérer les produits et catégories
def _get_home_page_data(request):
    """Logique pour récupérer les produits et catégories."""
    categories = Category.objects.all()
    
    # Optimisation des requêtes avec select_related et prefetch_related
    products = Product.objects.select_related('category', 'farmer').prefetch_related(
        Prefetch('reviews', queryset=Review.objects.only('rating'), to_attr='prefetched_reviews')
    ).annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    )

    # Filtrage par catégorie
    selected_category = request.GET.get('category')
    if selected_category:
        products = products.filter(category__slug=selected_category)

    # Recherche de produits
    query = request.GET.get('query', '')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    return {
        'categories': categories,
        'products': products,
        'selected_category': selected_category,
        'query': query
    }

@cache_page(60 * 15)  # Cache de 15 minutes pour les utilisateurs anonymes
def home_anonymous(request):
    """Page d'accueil avec cache pour les utilisateurs anonymes."""
    context = _get_home_page_data(request)
    return render(request, 'products/home.html', context)


@vary_on_cookie  # Cache différencié en fonction de l'authentification de l'utilisateur
def home(request):
    """Page d'accueil avec cache pour les utilisateurs anonymes et mise à jour pour les utilisateurs connectés."""
    if request.user.is_authenticated:
        # Si l'utilisateur est connecté, on ne met pas en cache la page. Elle est mise à jour à chaque requête.
        context = _get_home_page_data(request)
        return render(request, 'products/home.html', context)
    else:
        # Si l'utilisateur n'est pas connecté, la page est mise en cache pour 15 minutes.
        return home_anonymous(request)

# Vue des détails d'un produit
def product_detail(request, product_id):
    # Optimisation avec select_related et prefetch_related
    product = get_object_or_404(
        Product.objects.select_related('category', 'farmer')
        .prefetch_related(
            Prefetch('reviews', queryset=Review.objects.select_related('user'))
        ),
        id=product_id
    )
    
    # Récupérer les produits similaires de la même catégorie
    similar_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    
    return render(request, 'products/product_detail.html', {
        'product': product, 
        'similar_products': similar_products
    })

# Vue pour ajouter un produit au panier
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})

    if product.stock > 0:
        if str(product.id) in cart:
            cart[str(product.id)]['quantity'] += 1
        else:
            cart[str(product.id)] = {'name': product.name, 'price': str(product.price), 'quantity': 1}

        request.session['cart'] = cart
        messages.success(request, f"{product.name} a été ajouté à votre panier.")
    else:
        messages.error(request, f"Désolé, {product.name} est en rupture de stock.")

    return redirect('home')
