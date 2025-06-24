# products/views/payment_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from products.models.models import Order
from products.services import PaymentService, OrderService
import stripe
import json
import logging

logger = logging.getLogger(__name__)

# Initialiser Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def payment_options(request, order_id):
    """Affiche les options de paiement pour une commande"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    # Vérifier que la commande est en attente de paiement
    if order.payment_status != 'unpaid':
        messages.warning(request, "Cette commande a déjà été payée ou est en cours de traitement.")
        return redirect('order_detail', order_id=order.id)
    
    return render(request, 'products/payment_options.html', {
        'order': order,
        'stripe_key': settings.STRIPE_PUBLISHABLE_KEY  # Clé publique pour le frontend
    })

@login_required
def process_payment(request, order_id):
    """Traite le paiement d'une commande"""
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        
        # Vérifier que la méthode de paiement est valide
        if payment_method not in ['card', 'transfer']:
            messages.error(request, "Méthode de paiement non valide.")
            return redirect('payment_options', order_id=order.id)
        
        # Traiter le paiement
        payment_response = PaymentService.process_payment(
            order=order,
            payment_method=payment_method,
            payment_details=None
        )
        
        if payment_response['success']:
            if payment_method == 'card' and 'redirect_url' in payment_response:
                # Rediriger vers la page de paiement Stripe
                return redirect(payment_response['redirect_url'])
            elif payment_method == 'transfer':
                # Pour les virements, afficher un message d'instruction
                messages.success(request, "Les instructions de paiement par virement ont été envoyées à votre adresse email.")
                return redirect('order_detail', order_id=order.id)
        else:
            # En cas d'erreur
            messages.error(request, f"Erreur lors du traitement du paiement: {payment_response.get('error', 'Erreur inconnue')}")
            return redirect('payment_options', order_id=order.id)
    
    return redirect('payment_options', order_id=order.id)

@csrf_exempt
def stripe_webhook(request):
    """Webhook pour les notifications de Stripe"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Payload invalide
        logger.error(f"Webhook de Stripe invalide: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Signature invalide
        logger.error(f"Erreur de vérification de signature Stripe: {str(e)}")
        return HttpResponse(status=400)
    
    # Gérer les événements
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Récupérer l'ID de commande depuis les métadonnées
        order_id = session.get('metadata', {}).get('order_id')
        if not order_id:
            logger.warning("Webhook Stripe: pas d'ID de commande trouvé dans les métadonnées.")
            return HttpResponse(status=400)
        
        # Confirmer le paiement
        success = PaymentService.confirm_payment(order_id)
        if success:
            logger.info(f"Paiement confirmé pour la commande #{order_id}")
        else:
            logger.error(f"Erreur lors de la confirmation du paiement pour la commande #{order_id}")
    
    return HttpResponse(status=200)

@login_required
def payment_success(request):
    """Page de succès après un paiement réussi"""
    order_id = request.GET.get('order_id')
    if not order_id:
        return redirect('account_orders')
    
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    # Générer la facture si elle n'existe pas déjà
    if not hasattr(order, 'invoice') or not order.invoice:
        invoice_path = PaymentService.generate_invoice(order)
        if invoice_path:
            messages.success(request, "Votre facture a été générée avec succès et est disponible au téléchargement.")
    
    return render(request, 'products/payment_success.html', {'order': order})

@login_required
def payment_cancel(request):
    """Page d'annulation après un paiement annulé"""
    order_id = request.GET.get('order_id')
    if not order_id:
        return redirect('account_orders')
    
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    return render(request, 'products/payment_cancel.html', {'order': order})

@login_required
def download_invoice(request, order_id):
    """Télécharger la facture d'une commande"""
    order = get_object_or_404(Order, id=order_id)
    
    # Vérifier que l'utilisateur a le droit d'accéder à cette facture
    if order.customer != request.user and not request.user.is_staff:
        messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette facture.")
        return redirect('account_orders')
    
    # Vérifier que la facture existe
    if not hasattr(order, 'invoice') or not order.invoice:
        # Générer la facture si elle n'existe pas
        invoice_path = PaymentService.generate_invoice(order)
        if not invoice_path:
            messages.error(request, "Impossible de générer la facture.")
            return redirect('order_detail', order_id=order.id)
    
    # Servir le fichier
    from django.http import FileResponse
    import os
    from django.conf import settings
    
    file_path = os.path.join(settings.MEDIA_ROOT, order.invoice)
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="facture_{order.reference_number}.pdf"'
        return response
    else:
        messages.error(request, "Facture introuvable.")
        return redirect('order_detail', order_id=order.id)
