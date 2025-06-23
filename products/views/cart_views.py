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