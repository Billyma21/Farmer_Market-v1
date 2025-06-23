# products/views/review_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from products.models.product import Product
from products.models.models import Review, Order, OrderItem
from products.forms import ReviewForm

@login_required
def add_review(request, product_id):
    """Ajouter un avis sur un produit - accessible à tous les utilisateurs connectés"""
    product = get_object_or_404(Product, id=product_id)
    
    # Vérifier si l'utilisateur a déjà laissé un avis sur ce produit
    existing_review = Review.objects.filter(product=product, user=request.user).first()
    if existing_review:
        messages.warning(request, "Vous avez déjà laissé un avis pour ce produit. Vous pouvez le modifier.")
        return redirect('edit_review', review_id=existing_review.id)
    
    # Vérifier si l'utilisateur n'est pas le fermier du produit
    if request.user == product.farmer:
        messages.error(request, "Vous ne pouvez pas laisser un avis sur votre propre produit.")
        return redirect('product_detail', product_id=product.id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            try:
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                messages.success(request, "Votre avis a été ajouté avec succès. Merci pour votre retour !")
                return redirect('product_detail', product_id=product.id)
            except IntegrityError:
                messages.error(request, "Vous avez déjà laissé un avis pour ce produit.")
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'product': product
    }
    return render(request, 'products/add_review.html', context)

@login_required
def edit_review(request, review_id):
    """Modifier un avis existant"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre avis a été modifié avec succès.")
            return redirect('product_detail', product_id=review.product.id)
    else:
        form = ReviewForm(instance=review)
    
    context = {
        'form': form,
        'review': review,
        'product': review.product
    }
    return render(request, 'products/edit_review.html', context)

@login_required
def delete_review(request, review_id):
    """Supprimer un avis"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        product_id = review.product.id
        review.delete()
        messages.success(request, "Votre avis a été supprimé avec succès.")
        return redirect('product_detail', product_id=product_id)
    
    context = {
        'review': review
    }
    return render(request, 'products/confirm_delete_review.html', context)

@login_required
def reply_to_review(request, review_id):
    """Répondre à un avis (pour les fermiers)"""
    review = get_object_or_404(Review, id=review_id)
    
    # Vérifier que l'utilisateur est le fermier du produit
    if request.user != review.product.farmer:
        messages.error(request, "Vous n'êtes pas autorisé à répondre à cet avis.")
        return redirect('product_detail', product_id=review.product.id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            # Ici vous pourriez ajouter un modèle pour les réponses aux avis
            messages.success(request, "Votre réponse a été ajoutée avec succès.")
        else:
            messages.error(request, "Le contenu de la réponse ne peut pas être vide.")
    
    return redirect('product_detail', product_id=review.product.id)

def get_product_reviews(request, product_id):
    """Obtenir les avis d'un produit en AJAX"""
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product).select_related('user').order_by('-created_at')
    
    # Formatage des avis pour JSON
    reviews_data = []
    for review in reviews:
        reviews_data.append({
            'id': review.id,
            'user': review.user.username,
            'rating': review.rating,
            'title': review.title,
            'comment': review.comment,
            'created_at': review.created_at.strftime('%d/%m/%Y'),
            'is_owner': review.user == request.user if request.user.is_authenticated else False
        })
    
    return JsonResponse({
        'average_rating': product.get_average_rating(),
        'review_count': reviews.count(),
        'reviews': reviews_data
    }) 