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

