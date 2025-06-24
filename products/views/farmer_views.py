# products/views/farmer_views.py

import base64
from io import BytesIO
from django.core.files.base import ContentFile
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product, FarmerProfile
from products.forms import ProductForm
from django.contrib.auth import get_user_model
User = get_user_model()

# Vue du tableau de bord du fermier
@login_required
def farmer_dashboard(request):
    if not request.user.is_farmer:
        return redirect('home')

    profile = getattr(request.user, 'profile', None)
    products = Product.objects.filter(farmer=request.user)
    return render(request, 'profil_farmer/farmer_dashboard.html', {
        'profile': profile,
        'products': products
    })

# Vue publique du profil d'un fermier

def farmer_profile(request, farmer_id):
    farmer = get_object_or_404(User, id=farmer_id, is_farmer=True)
    profile = getattr(farmer, 'profile', None)
    products = Product.objects.filter(farmer=farmer, is_active=True)
    return render(request, 'profil_farmer/farmer_profile.html', {
        'farmer': farmer,
        'profile': profile,
        'products': products
    })

# Vue pour éditer le profil du fermier
@login_required
def edit_profile(request):
    if not request.user.is_farmer:
        return redirect('home')
    profile = getattr(request.user, 'profile', None)
    if request.method == 'POST':
        # À adapter selon votre formulaire de profil
        # form = FarmerProfileForm(request.POST, instance=profile)
        # if form.is_valid():
        #     form.save()
        #     messages.success(request, "Profil mis à jour avec succès.")
        #     return redirect('farmer_dashboard')
        pass
    # else:
        # form = FarmerProfileForm(instance=profile)
    return render(request, 'profil_farmer/edit_profile.html', {
        'profile': profile,
        # 'form': form
    })

