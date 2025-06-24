<<<<<<< HEAD
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from products.models import Product
from products.models.models import Order, OrderItem
from products.forms import OrderForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db import transaction
from decimal import Decimal
import json

def cart_detail(request):
    """Affiche le contenu du panier de l'utilisateur."""
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    
    for product_id, item_data in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            quantity = item_data['quantity']
            price = Decimal(item_data['price'])
            subtotal = price * quantity
            total += subtotal
            
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'price': price,
                'subtotal': subtotal
            })
        except Product.DoesNotExist:
            # Si le produit n'existe plus, on le retire du panier
            cart.pop(product_id, None)
            request.session['cart'] = cart
    
    return render(request, 'products/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

def add_to_cart(request, product_id):
    """Ajoute un produit au panier ou augmente sa quantité."""
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    
    if product.stock > 0:
        if str(product_id) in cart:
            # Vérifier si la quantité demandée n'excède pas le stock
            if cart[str(product_id)]['quantity'] < product.stock:
                cart[str(product_id)]['quantity'] += 1
                messages.success(request, f"Quantité de {product.name} augmentée dans votre panier.")
            else:
                messages.warning(request, f"Désolé, il n'y a plus de stock disponible pour {product.name}.")
        else:
            cart[str(product_id)] = {
                'name': product.name,
                'price': str(product.price),
                'quantity': 1
            }
            messages.success(request, f"{product.name} a été ajouté à votre panier.")
    else:
        messages.error(request, f"Désolé, {product.name} est en rupture de stock.")
    
    request.session['cart'] = cart
    return redirect('cart_detail')

def remove_from_cart(request, product_id):
    """Retire un produit du panier."""
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        product_name = cart[str(product_id)]['name']
        del cart[str(product_id)]
        request.session['cart'] = cart
        messages.success(request, f"{product_name} a été retiré de votre panier.")
    
    return redirect('cart_detail')

def update_cart(request):
    """Met à jour les quantités dans le panier."""
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        for key, value in request.POST.items():
            if key.startswith('quantity_'):
                product_id = key.replace('quantity_', '')
                try:
                    quantity = int(value)
                    if quantity > 0:
                        product = Product.objects.get(id=product_id)
                        if quantity <= product.stock:
                            cart[product_id]['quantity'] = quantity
                        else:
                            cart[product_id]['quantity'] = product.stock
                            messages.warning(request, f"La quantité de {product.name} a été ajustée au stock disponible.")
                    else:
                        del cart[product_id]
                except (ValueError, Product.DoesNotExist, KeyError):
                    pass
        
        request.session['cart'] = cart
        messages.success(request, "Votre panier a été mis à jour.")
    
    return redirect('cart_detail')

@login_required
def checkout(request):
    """Affiche et traite le formulaire de commande."""
    cart = request.session.get('cart', {})
    
    # Vérifier si le panier est vide
    if not cart:
        messages.warning(request, "Votre panier est vide. Veuillez ajouter des produits avant de passer commande.")
        return redirect('home')
    
    # Récupérer les produits du panier
    cart_items = []
    total = 0
    
    for product_id, item_data in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            quantity = item_data['quantity']
            price = Decimal(item_data['price'])
            subtotal = price * quantity
            total += subtotal
            
            # Vérifier si le stock est toujours disponible
            if product.stock < quantity:
                messages.warning(request, 
                    f"Désolé, il n'y a que {product.stock} unités de {product.name} disponibles. Votre panier a été mis à jour.")
                if product.stock > 0:
                    cart[product_id]['quantity'] = product.stock
                else:
                    del cart[product_id]
                request.session['cart'] = cart
                return redirect('cart_detail')
            
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'price': price,
                'subtotal': subtotal
            })
        except Product.DoesNotExist:
            # Si le produit n'existe plus, on le retire du panier
            cart.pop(product_id, None)
            request.session['cart'] = cart
            messages.warning(request, "Certains produits de votre panier ne sont plus disponibles et ont été retirés.")
            return redirect('cart_detail')
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Créer la commande
                    order = Order.objects.create(
                        customer=request.user,
                        shipping_address=form.cleaned_data['shipping_address'],
                        shipping_city=form.cleaned_data['shipping_city'],
                        shipping_zip_code=form.cleaned_data['shipping_zip_code'],
                        contact_email=form.cleaned_data['contact_email'],
                        contact_phone=form.cleaned_data['contact_phone'],
                        notes=form.cleaned_data['notes'],
                        payment_method=form.cleaned_data['payment_method'],
                        total_price=total
                    )
                    
                    # Créer les éléments de commande et mettre à jour les stocks
                    for item in cart_items:
                        product = item['product']
                        quantity = item['quantity']
                        
                        # Vérifier à nouveau le stock avant de finaliser
                        if product.stock < quantity:
                            raise ValueError(f"Stock insuffisant pour {product.name}")
                        
                        # Créer l'item de commande
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            farmer=product.farmer,
                            price=product.price,
                            quantity=quantity
                        )
                        
                        # Mettre à jour le stock et les compteurs de vente
                        product.stock -= quantity
                        product.sales_count += quantity
                        product.save()
                    
                    # Vider le panier
                    request.session['cart'] = {}
                    
                    # Rediriger vers la page de paiement ou de confirmation
                    if form.cleaned_data['payment_method'] == 'stripe':
                        # Créer la session de paiement Stripe
                        return redirect('payment_process', order_id=order.id)
                    else:
                        return redirect('order_confirmation', order_id=order.id)
            
            except ValueError as e:
                messages.error(request, str(e))
                return redirect('cart_detail')
    else:
        # Préremplir le formulaire avec les informations de l'utilisateur
        initial_data = {}
        if hasattr(request.user, 'email'):
            initial_data['contact_email'] = request.user.email
        
        form = OrderForm(initial=initial_data)
    
    return render(request, 'products/checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'total': total
    })

@login_required
def order_confirmation(request, order_id):
    """Affiche la confirmation de la commande."""
    try:
        order = Order.objects.get(id=order_id, customer=request.user)
    except Order.DoesNotExist:
        messages.error(request, "Commande introuvable.")
        return redirect('home')
    
    return render(request, 'products/order_confirmation.html', {'order': order})

@login_required
def order_list(request):
    """Affiche la liste des commandes de l'utilisateur."""
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'products/order_list.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    """Affiche les détails d'une commande spécifique."""
    try:
        order = Order.objects.get(id=order_id, customer=request.user)
    except Order.DoesNotExist:
        messages.error(request, "Commande introuvable.")
        return redirect('order_list')
    
    return render(request, 'products/order_detail.html', {'order': order}) 
=======
# products/views/cart_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from products.models.product import Product
from products.models.models import Cart, CartItem

@login_required
def view_cart(request):
    """Affiche le contenu du panier de l'utilisateur."""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    
    return render(request, 'products/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'total': cart.get_total_cost(),
    })

@login_required
def add_to_cart(request, product_id=None):
    """Vue pour ajouter un produit au panier"""
    if request.method == 'POST':
        # Si product_id est passé en paramètre, l'utiliser, sinon le prendre du POST
        if product_id is None:
            data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
            product_id = data.get('product_id')
        
        quantity = int(request.POST.get('quantity', 1)) if request.method == 'POST' else 1
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            
            # Vérifier le stock
            if product.stock < quantity:
                messages.error(request, 'Stock insuffisant')
                return redirect('product_detail', product_id=product_id)
            
            # Ajouter au panier (session)
            cart = request.session.get('cart', {})
            if str(product_id) in cart:
                cart[str(product_id)] += quantity
            else:
                cart[str(product_id)] = quantity
            
            request.session['cart'] = cart
            request.session.modified = True
            
            messages.success(request, 'Produit ajouté au panier')
            return redirect('view_cart')
            
        except Product.DoesNotExist:
            messages.error(request, 'Produit non trouvé')
            return redirect('product_list')
    
    return redirect('product_list')

@login_required
def update_cart(request, item_id=None):
    """Vue pour mettre à jour le panier"""
    if request.method == 'POST':
        if item_id:
            # Mise à jour d'un item spécifique
            try:
                cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
                quantity = int(request.POST.get('quantity', 1))
                
                if quantity > 0:
                    cart_item.quantity = quantity
                    cart_item.save()
                else:
                    cart_item.delete()
                    
                messages.success(request, 'Quantité mise à jour')
            except (ValueError, CartItem.DoesNotExist):
                messages.error(request, 'Erreur lors de la mise à jour')
        else:
            # Mise à jour générale du panier
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
def clear_cart(request):
    """Vide complètement le panier."""
    if request.method == 'POST':
        cart = get_object_or_404(Cart, user=request.user)
        cart.clear()
        messages.success(request, "Votre panier a été vidé.")
    return redirect('view_cart')

@login_required
def cart_count(request):
    """Renvoie le nombre d'articles dans le panier (pour AJAX)."""
    cart = request.session.get('cart', {})
    count = sum(cart.values())
    return JsonResponse({'count': count}) 
>>>>>>> V1.01
