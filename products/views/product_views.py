# roducts/views/product_farmer.py

import base64
from io import BytesIO
from django.core.files.base import ContentFile
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.translation import gettext as _
from products.models import Product, FarmerProfile, Category
from products.models.models import Review
from products.forms import ProductForm

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

@login_required
def add_product(request):
    if not request.user.is_farmer:
        return redirect('home')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)  # Assurez-vous d'utiliser request.FILES

        if form.is_valid():
            product = form.save(commit=False)
            product.farmer = request.user  # Associer le produit à l'utilisateur fermier
            product.save()  # Sauvegarder le produit avec l'image

            messages.success(request, "Le produit a été ajouté avec succès!")
            return redirect('farmer_dashboard')  # Rediriger après ajout
        else:
            messages.error(request, "Il y a une erreur dans le formulaire.")
            return render(request, 'profil_farmer/add_product.html', {'form': form})
    else:
        form = ProductForm()

    return render(request, 'profil_farmer/add_product.html', {'form': form})

# Vue pour éditer un produit existant
@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Vérifiez si l'utilisateur est le fermier propriétaire du produit
    if request.user != product.farmer:
        return HttpResponseForbidden("Vous n'êtes pas autorisé à modifier ce produit.")

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            updated_product = form.save(commit=False)

            # Si une nouvelle image est téléchargée, on l'ajoute
            image = request.FILES.get('image')
            if image:
                updated_product.image = image  # Mise à jour de l'image avec le fichier téléchargé

            # Si aucune image n'est fournie mais qu'une image URL est donnée
            image_url = form.cleaned_data.get('image_url')  # Utilisation des données validées du formulaire
            if image_url:
                updated_product.image_url = image_url  # Mise à jour de l'URL de l'image

            updated_product.save()

            messages.success(request, "Produit mis à jour avec succès.")
            return redirect('farmer_dashboard')
        else:
            # Si le formulaire n'est pas valide, afficher les erreurs
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
            return render(request, 'products/edit_product.html', {
                'form': form,
                'product': product
            })

    else:
        # Initialisation du formulaire avec les données du produit
        form = ProductForm(instance=product)

    return render(request, 'products/edit_product.html', {
        'form': form,
        'product': product,
    })
    
# Vue pour supprimer un produit
@login_required
def delete_product(request, product_id):
    # Récupérer le produit à supprimer
    product = get_object_or_404(Product, id=product_id, farmer=request.user)

    if request.method == 'POST':
        product.delete()
        messages.success(request, f"Le produit {product.name} a été supprimé avec succès.")
        return redirect('farmer_dashboard')  # Rediriger après la suppression

    return render(request, 'profil_farmer/confirm_delete.html', {'product': product})

def product_detail(request, product_id):
    """Vue détaillée d'un produit"""
    product = get_object_or_404(Product, id=product_id)
    
    # Récupérer l'avis de l'utilisateur connecté s'il existe
    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(product=product, user=request.user).first()
    
    # Récupérer les produits similaires
    similar_products = Product.objects.filter(
        category=product.category
    ).exclude(id=product.id)[:4]
    
    # Récupérer les produits du même fermier
    farmer_products = Product.objects.filter(
        farmer=product.farmer
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'user_review': user_review,
        'similar_products': similar_products,
        'farmer_products': farmer_products,
    }
    
    return render(request, 'products/product_detail.html', context)
