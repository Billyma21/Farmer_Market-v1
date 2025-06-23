#products/views/profil_famer.py

import base64
import requests
from io import BytesIO
from django.core.files.base import ContentFile
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product, FarmerProfile
from products.forms import ProductForm


# Vue pour afficher le profil fermier
@login_required
def farmer_profile(request, farmer_id):
    # Vérifier que l'ID correspond bien à l'utilisateur connecté
    if request.user.id != farmer_id:
        return redirect('farmer_dashboard')  # Redirige vers le tableau de bord si l'utilisateur n'est pas celui du profil demandé
    
    # Essayer de récupérer le profil fermier en fonction de l'ID
    try:
        farmer = FarmerProfile.objects.get(farmer__id=farmer_id)
    except FarmerProfile.DoesNotExist:
        messages.info(request, "Veuillez créer un profil fermier.")
        return redirect('edit_profile')
    
    # Vérifier si le profil est complet (ajustez selon vos champs nécessaires)
    if not farmer.description or not farmer.address:
        messages.info(request, "Veuillez compléter votre profil.")
        return redirect('edit_profile')

    return render(request, 'profil_farmer/farmer_profile.html', {'farmer': farmer})





# Vue pour modifier le profil fermier
@login_required
def edit_profile(request):
    # Récupère ou crée le profil fermier lié à l'utilisateur
    profile, created = FarmerProfile.objects.get_or_create(farmer=request.user)
    from accounts.forms import UpdateProfileForm

    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès!")
            return redirect('farmer_profile', farmer_id=profile.farmer.id)
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = UpdateProfileForm(instance=profile)

    return render(request, 'products/edit_profile.html', {'form': form, 'profile': profile})




# @login_required
# def edit_profile(request):
#     farmer = request.user.profile

#     if request.method == 'POST':
#         description = request.POST.get('description', '')
#         address = request.POST.get('address', '')
#         phone_number = request.POST.get('phone_number', '')
#         agriculture_sector = request.POST.get('agriculture_sector', '')
#         latitude = request.POST.get('latitude', '')
#         longitude = request.POST.get('longitude', '')
#         google_maps_link = request.POST.get('google_maps_link', '')
#         additional_info = request.POST.get('additional_info', '')
#         opening_hours = request.POST.get('opening_hours', '')
#         services = request.POST.get('services', '')

#         # Validation des champs
#         if not description:
#             messages.error(request, "La description est requise.")
#             return redirect('edit_profile')

#         if not address:
#             messages.error(request, "L'adresse est requise.")
#             return redirect('edit_profile')

#         farmer.description = description
#         farmer.address = address
#         farmer.phone_number = phone_number
#         farmer.agriculture_sector = agriculture_sector
#         farmer.opening_hours = opening_hours
#         farmer.services = services
#         farmer.additional_info = additional_info
#         farmer.google_maps_link = google_maps_link

#         # Mise à jour des coordonnées géographiques
#         if latitude and latitude != 'None':
#             try:
#                 farmer.latitude = float(latitude)
#             except ValueError:
#                 farmer.latitude = None

#         if longitude and longitude != 'None':
#             try:
#                 farmer.longitude = float(longitude)
#             except ValueError:
#                 farmer.longitude = None

#         farmer.save()
#         messages.success(request, "Votre profil a été mis à jour avec succès.")
#         return redirect('farmer_dashboard')

#     return render(request, 'profil_farmer/edit_profile.html', {'farmer': farmer})




# 
# 
# 
# Vue pour modifier le profil du fermier
# @login_required
# def edit_profile(request):
#     farmer = request.user.profile

#     if request.method == 'POST':
#         description = request.POST.get('description', '')
#         address = request.POST.get('address', '')
#         phone_number = request.POST.get('phone_number', '')
#         website = request.POST.get('website', '')
#         latitude = request.POST.get('latitude', '')
#         longitude = request.POST.get('longitude', '')

#         if not description:
#             messages.error(request, "La description est requise.")
#             return redirect('edit_profile')

#         if not address:
#             messages.error(request, "L'adresse est requise.")
#             return redirect('edit_profile')

#         farmer.description = description
#         farmer.address = address
#         farmer.phone_number = phone_number
#         farmer.website = website

#         # Mise à jour des coordonnées géographiques
#         if latitude and latitude != 'None':
#             try:
#                 farmer.latitude = float(latitude)
#             except ValueError:
#                 farmer.latitude = None

#         if longitude and longitude != 'None':
#             try:
#                 farmer.longitude = float(longitude)
#             except ValueError:
#                 farmer.longitude = None

#         farmer.save()
#         messages.success(request, "Votre profil a été mis à jour avec succès.")
#         return redirect('farmer_dashboard')

#     return render(request, 'profil_farmer/edit_profile.html', {'farmer': farmer})



# # Vue pour afficher le profil du fermier
# @login_required
# def farmer_profile(request, farmer_id):
#     farmer = get_object_or_404(FarmerProfile, farmer__id=farmer_id)

#     # Redirigez l'utilisateur vers la page d'édition si le profil est incomplet
#     if not farmer.description or not farmer.address:
#         messages.info(request, "Veuillez compléter votre profil.")
#         return redirect('edit_profile')

#     if request.user.id != farmer.farmer.id:
#         return HttpResponseForbidden("Accès non autorisé.")
#     return render(request, 'profil_farmer/farmer_profile.html', {'farmer': farmer})



# # Vue pour modifier le profil du fermier
# @login_required
# def edit_profile(request):
#     farmer = request.user.profile

#     if request.method == 'POST':
#         description = request.POST.get('description', '')
#         address = request.POST.get('address', '')
#         phone_number = request.POST.get('phone_number', '')
#         website = request.POST.get('website', '')
#         latitude = request.POST.get('latitude', '')
#         longitude = request.POST.get('longitude', '')

#         if not description:
#             messages.error(request, "La description est requise.")
#             return redirect('edit_profile')

#         if not address:
#             messages.error(request, "L'adresse est requise.")
#             return redirect('edit_profile')

#         farmer.description = description
#         farmer.address = address
#         farmer.phone_number = phone_number
#         farmer.website = website

#         # Mise à jour des coordonnées géographiques
#         if latitude and latitude != 'None':
#             try:
#                 farmer.latitude = float(latitude)
#             except ValueError:
#                 farmer.latitude = None

#         if longitude and longitude != 'None':
#             try:
#                 farmer.longitude = float(longitude)
#             except ValueError:
#                 farmer.longitude = None

#         farmer.save()
#         messages.success(request, "Votre profil a été mis à jour avec succès.")
#         return redirect('farmer_dashboard')

#     return render(request, 'profil_farmer/edit_profile.html', {'farmer': farmer})

