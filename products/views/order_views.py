# products/views/order_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from products.models.models import Cart, Order, OrderItem
from products.models.product import Product
from products.forms import OrderForm, OrderNoteForm
from django.http import HttpResponse
from django.template.loader import render_to_string



@login_required
def checkout(request):
    """Affiche le processus de finalisation de commande."""
    cart = get_object_or_404(Cart, user=request.user)
    
    if not cart.items.exists():
        messages.warning(request, "Votre panier est vide. Veuillez ajouter des produits avant de passer commande.")
        return redirect('view_cart')
    
    # Vérifier le stock disponible
    out_of_stock_items = []
    for item in cart.items.all():
        if item.quantity > item.product.stock:
            out_of_stock_items.append(f"{item.product.name} (demandé: {item.quantity}, disponible: {item.product.stock})")
    
    if out_of_stock_items:
        messages.error(request, "Certains produits ne sont plus disponibles en quantité suffisante: " + ", ".join(out_of_stock_items))
        return redirect('view_cart')
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Créer la commande
                    order = Order.objects.create(
                        customer=request.user,
                        pickup_date=form.cleaned_data['pickup_date'],
                        pickup_time_slot=form.cleaned_data['pickup_time_slot'],
                        notes=form.cleaned_data['notes'],
                        status='pending'
                    )
                    
                    # Ajouter les articles à la commande
                    for item in cart.items.all():
                        OrderItem.objects.create(
                            order=order,
                            product=item.product,
                            quantity=item.quantity,
                            price=item.product.price
                        )
                        
                        # Mettre à jour le stock et les ventes
                        product = item.product
                        product.stock -= item.quantity
                        product.sales_count += item.quantity
                        product.save()
                    
                    # Calculer le total
                    order.calculate_total()
                    
                    # Vider le panier
                    cart.clear()
                    
                    # Envoyer email de confirmation
                    send_order_confirmation_email(order)
                    
                    messages.success(request, f"Votre commande #{order.id} a été créée avec succès. Vous pouvez la suivre dans votre espace personnel.")
                    return redirect('order_detail', order_id=order.id)
            except Exception as e:
                messages.error(request, f"Une erreur s'est produite lors de la création de votre commande: {str(e)}")
    else:
        form = OrderForm()
    
    return render(request, 'products/checkout.html', {
        'cart': cart,
        'total': cart.get_total_cost(),
        'form': form
    })

@login_required
def order_detail(request, order_id):
    """Affiche les détails d'une commande."""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    if request.method == 'POST':
        note_form = OrderNoteForm(request.POST, instance=order)
        if note_form.is_valid():
            note_form.save()
            messages.success(request, "Vos notes ont été mises à jour.")
            return redirect('order_detail', order_id=order.id)
    else:
        note_form = OrderNoteForm(instance=order)
    
    return render(request, 'products/order_detail.html', {
        'order': order,
        'items': order.items.all(),
        'note_form': note_form
    })

@login_required
def my_orders(request):
    """Affiche toutes les commandes de l'utilisateur."""
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'products/my_orders.html', {'orders': orders})

@login_required
def cancel_order(request, order_id):
    """Annule une commande si elle est encore en attente."""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    if order.status != 'pending':
        messages.error(request, "Seules les commandes en attente peuvent être annulées.")
        return redirect('order_detail', order_id=order.id)
    
    if request.method == 'POST':
        with transaction.atomic():
            # Remettre les produits en stock
            for item in order.items.all():
                product = item.product
                product.stock += item.quantity
                product.sales_count -= item.quantity
                product.save()
            
            # Mettre à jour le statut de la commande
            order.status = 'cancelled'
            order.save()
            
            messages.success(request, f"La commande #{order.id} a été annulée.")
        
        return redirect('my_orders')
    
    return render(request, 'products/confirm_cancel_order.html', {'order': order})

def send_order_confirmation_email(order):
    """Envoie un email de confirmation pour une commande."""
    subject = f"Confirmation de votre commande #{order.id}"
    message = f"""
    Bonjour {order.customer.username},
    
    Nous vous remercions pour votre commande sur Farmer Market.
    
    Détails de la commande:
    - Numéro de commande: {order.id}
    - Date de création: {order.created_at.strftime('%d/%m/%Y %H:%M')}
    - Date de retrait prévue: {order.pickup_date.strftime('%d/%m/%Y')}
    - Créneau horaire: {order.pickup_time_slot}
    - Montant total: {order.total_amount} €
    
    Vous serez informé(e) lorsque votre commande sera prête à être récupérée.
    
    L'équipe Farmer Market
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.customer.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Erreur lors de l'envoi du mail de confirmation: {str(e)}") 
        