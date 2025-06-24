import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from .models import FarmerProfile, Category, Product, Order, OrderItem
from .forms import ProductForm, OrderForm
from accounts.models import User

def map_view(request):
    farmers = FarmerProfile.objects.all()
    categories = Category.objects.all()
    
    # Préparer les données pour le template
    farmers_data = []
    for farmer in farmers:
        if farmer.latitude and farmer.longitude:
            farmers_data.append({
                'latitude': float(farmer.latitude),
                'longitude': float(farmer.longitude),
                'name': farmer.farm_name or farmer.farmer.username,
                'id': farmer.farmer.id,
                'address': farmer.get_full_address(),
                'description': farmer.description[:100] if farmer.description else '',
                'phone': farmer.phone_number or '',
                'sector': farmer.agriculture_sector or '',
                'productCount': farmer.product_count,
                'hours': farmer.opening_hours[:50] if farmer.opening_hours else '',
                'isOrganic': farmer.is_organic_certified
            })
    
    context = {
        'farmers': farmers,
        'categories': categories,
        'farmers_data': json.dumps(farmers_data),
        'selected_category': request.GET.get('category'),
        'certification': request.GET.get('certification'),
        'total_farmers': len(farmers_data)
    }
    return render(request, 'products/map_view.html', context) 

def home(request):
    """Vue pour la page d'accueil"""
    # Récupérer les catégories
    categories = Category.objects.all()[:8]
    
    # Récupérer les produits vedettes (les plus populaires)
    featured_products = Product.objects.filter(
        is_active=True,
        stock_quantity__gt=0
    ).order_by('-created_at')[:8]
    
    # Statistiques
    stats = {
        'farmers_count': User.objects.filter(user_type='farmer').count(),
        'products_count': Product.objects.filter(is_active=True).count(),
        'orders_count': Order.objects.filter(status='delivered').count(),
        'customers_count': User.objects.filter(user_type='customer').count(),
    }
    
    context = {
        'categories': categories,
        'featured_products': featured_products,
        'stats': stats,
    }
    
    return render(request, 'home.html', context)

def product_list(request):
    """Vue pour la liste des produits"""
    products = Product.objects.filter(is_active=True)
    
    # Filtrage par catégorie
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Recherche
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(farmer__username__icontains=query)
        )
    
    # Tri
    sort = request.GET.get('sort', 'name')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    elif sort == 'name':
        products = products.order_by('name')
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Catégories pour le filtre
    categories = Category.objects.all()
    
    context = {
        'products': page_obj,
        'categories': categories,
        'current_category': category_id,
        'current_sort': sort,
        'query': query,
    }
    
    return render(request, 'products/product_list.html', context)

def product_detail(request, product_id):
    """Vue pour le détail d'un produit"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Produits similaires
    similar_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'similar_products': similar_products,
    }
    
    return render(request, 'products/product_detail.html', context)

@login_required
def add_to_cart(request):
    """Vue AJAX pour ajouter un produit au panier"""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            
            # Vérifier le stock
            if product.stock_quantity < quantity:
                return JsonResponse({
                    'success': False,
                    'message': 'Stock insuffisant'
                })
            
            # Ajouter au panier (session)
            cart = request.session.get('cart', {})
            if str(product_id) in cart:
                cart[str(product_id)] += quantity
            else:
                cart[str(product_id)] = quantity
            
            request.session['cart'] = cart
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'message': 'Produit ajouté au panier'
            })
            
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Produit non trouvé'
            })
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})

@login_required
def view_cart(request):
    """Vue pour afficher le panier"""
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            item_total = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
            total += item_total
        except Product.DoesNotExist:
            # Supprimer le produit du panier s'il n'existe plus
            del cart[product_id]
    
    request.session['cart'] = cart
    request.session.modified = True
    
    context = {
        'cart_items': cart_items,
        'total': total,
    }
    
    return render(request, 'cart/cart.html', context)

@login_required
def update_cart(request):
    """Vue pour mettre à jour le panier"""
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        
        for product_id, quantity in request.POST.items():
            if product_id.startswith('quantity_'):
                actual_product_id = product_id.replace('quantity_', '')
                quantity = int(quantity)
                
                if quantity > 0:
                    cart[actual_product_id] = quantity
                else:
                    cart.pop(actual_product_id, None)
        
        request.session['cart'] = cart
        request.session.modified = True
        
        messages.success(request, 'Panier mis à jour')
        return redirect('view_cart')
    
    return redirect('view_cart')

@login_required
def remove_from_cart(request, product_id):
    """Vue pour supprimer un produit du panier"""
    cart = request.session.get('cart', {})
    cart.pop(str(product_id), None)
    request.session['cart'] = cart
    request.session.modified = True
    
    messages.success(request, 'Produit supprimé du panier')
    return redirect('view_cart')

@login_required
def checkout(request):
    """Vue pour le processus de commande"""
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, 'Votre panier est vide')
        return redirect('product_list')
    
    cart_items = []
    total = 0
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            item_total = product.price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total
            })
            total += item_total
        except Product.DoesNotExist:
            del cart[product_id]
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = request.user
            order.total_amount = total
            order.save()
            
            # Créer les éléments de commande
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['product'].price
                )
                
                # Mettre à jour le stock
                item['product'].stock_quantity -= item['quantity']
                item['product'].save()
            
            # Vider le panier
            request.session['cart'] = {}
            request.session.modified = True
            
            messages.success(request, 'Commande passée avec succès !')
            return redirect('order_detail', order_id=order.id)
    else:
        form = OrderForm()
    
    context = {
        'cart_items': cart_items,
        'total': total,
        'form': form,
    }
    
    return render(request, 'orders/checkout.html', context)

@login_required
def order_list(request):
    """Vue pour la liste des commandes de l'utilisateur"""
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    
    return render(request, 'orders/order_list.html', context)

@login_required
def order_detail(request, order_id):
    """Vue pour le détail d'une commande"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    context = {
        'order': order,
    }
    
    return render(request, 'orders/order_detail.html', context)

def cart_count(request):
    """Vue AJAX pour obtenir le nombre d'articles dans le panier"""
    cart = request.session.get('cart', {})
    count = sum(cart.values())
    return JsonResponse({'count': count})

# Vues pour les fermiers
@login_required
def farmer_dashboard(request):
    """Tableau de bord pour les fermiers"""
    if request.user.user_type != 'farmer':
        messages.error(request, 'Accès non autorisé')
        return redirect('home')
    
    # Statistiques du fermier
    products = Product.objects.filter(farmer=request.user)
    orders = OrderItem.objects.filter(product__farmer=request.user)
    
    # Statistiques des 30 derniers jours
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_orders = orders.filter(order__created_at__gte=thirty_days_ago)
    
    stats = {
        'total_products': products.count(),
        'active_products': products.filter(is_active=True).count(),
        'total_orders': orders.count(),
        'recent_orders': recent_orders.count(),
        'total_revenue': sum(order.price * order.quantity for order in orders),
        'recent_revenue': sum(order.price * order.quantity for order in recent_orders),
    }
    
    # Commandes récentes
    recent_orders_list = OrderItem.objects.filter(
        product__farmer=request.user
    ).select_related('order', 'product').order_by('-order__created_at')[:10]
    
    context = {
        'stats': stats,
        'recent_orders': recent_orders_list,
    }
    
    return render(request, 'farmer/dashboard.html', context)

@login_required
def add_product(request):
    """Vue pour ajouter un produit"""
    if request.user.user_type != 'farmer':
        messages.error(request, 'Accès non autorisé')
        return redirect('home')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.farmer = request.user
            product.save()
            messages.success(request, 'Produit ajouté avec succès')
            return redirect('farmer_dashboard')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'farmer/add_product.html', context)

@login_required
def edit_product(request, product_id):
    """Vue pour éditer un produit"""
    product = get_object_or_404(Product, id=product_id, farmer=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produit mis à jour avec succès')
            return redirect('farmer_dashboard')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
    }
    
    return render(request, 'farmer/edit_product.html', context)

@login_required
def delete_product(request, product_id):
    """Vue pour supprimer un produit"""
    product = get_object_or_404(Product, id=product_id, farmer=request.user)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Produit supprimé avec succès')
        return redirect('farmer_dashboard')
    
    context = {
        'product': product,
    }
    
    return render(request, 'farmer/delete_product.html', context) 