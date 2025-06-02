# Farmer_Market-v1/products/views/home_views.py

# products/views/client_views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from products.models import Product, Category

# Vue de la page d'accueil, qui affiche tous les produits et catégories
def home(request):
    categories = Category.objects.all()
    products = Product.objects.all()

    # Filtrage par catégorie
    selected_category = request.GET.get('category')
    if selected_category:
        products = products.filter(category__slug=selected_category)

    # Recherche de produits
    query = request.GET.get('query', '')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    return render(request, 'products/home.html', {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'query': query
    })

# Vue des détails d'un produit
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'products/product_detail.html', {'product': product})

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
