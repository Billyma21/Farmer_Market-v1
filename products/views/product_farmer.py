# products/views/product_farmer.py


import base64
from io import BytesIO
from django.core.files.base import ContentFile
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product, FarmerProfile
from products.forms import ProductForm



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
