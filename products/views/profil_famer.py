#products/views/profil_famer.py

import base64
import requests
from io import BytesIO
from django.core.files.base import ContentFile
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from products.models import Product, FarmerProfile
from products.forms.products import ProductForm
from products.forms.farmer_profile import FarmerProfileForm
from django.core.exceptions import ValidationError


# Vue pour afficher le profil fermier
@login_required
def farmer_profile(request, farmer_id):
    # Vérifier que l'ID correspond à l'utilisateur connecté
    if request.user.id != farmer_id:
        return redirect('farmer_dashboard')  # Redirige vers le tableau de bord si l'utilisateur n'est pas celui du profil demandé
    
    try:
        # Récupérer le profil fermier avec l'ID
        farmer = FarmerProfile.objects.get(farmer__id=farmer_id)
    except FarmerProfile.DoesNotExist:
        messages.info(request, "Veuillez créer un profil fermier.")
        return redirect('edit_profile')
    
    # Vérifier que le profil est complet
    if not farmer.description or not farmer.address:
        messages.info(request, "Veuillez compléter votre profil.")
        return redirect('edit_profile')
    
    # Passer les coordonnées au template
    context = {
        'farmer': farmer,
        'latitude': farmer.latitude,
        'longitude': farmer.longitude,
    }
    
    return render(request, 'profil_farmer/farmer_profile.html', context)



# Vue pour modifier le profil fermier

@login_required
def edit_profile(request):
    # Récupère le profil fermier de l'utilisateur connecté ou crée un profil vide si inexistant
    farmer, created = FarmerProfile.objects.get_or_create(farmer=request.user)

    if request.method == 'POST':
        # Formulaire avec données POST et fichiers si présents
        form = FarmerProfileForm(request.POST, request.FILES, instance=farmer)
        
        if form.is_valid():
            # Sauvegarde les données uniquement si le formulaire est valide
            form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('farmer_dashboard')  # Redirection vers le tableau de bord du fermier
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        # Affichage du formulaire avec les données actuelles du fermier
        form = FarmerProfileForm(instance=farmer)

    # Passage du formulaire à la vue
    return render(request, 'profil_farmer/edit_profile.html', {'form': form, 'farmer': farmer})




# Vue pour modifier le profil fermier


# @login_required
# def edit_profile(request):
#     farmer, created = FarmerProfile.objects.get_or_create(farmer=request.user)

#     if request.method == 'POST':
#         form = FarmerProfileForm(request.POST, request.FILES, instance=farmer)
#         if form.is_valid():
#             try:
#                 form.save()
#                 messages.success(request, "Profil mis à jour avec succès.")
#                 return redirect('farmer_dashboard')
#             except Exception as e:
#                 messages.error(request, f"Erreur lors de la sauvegarde: {e}")
#         else:
#             messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
#     else:
#         form = FarmerProfileForm(instance=farmer)

#     return render(request, 'profil_farmer/edit_profile.html', {'form': form, 'farmer': farmer}) 





#V_1.00

# @login_required
# def edit_profile(request):
#     farmer, created = FarmerProfile.objects.get_or_create(farmer=request.user)

#     if request.method == 'POST':
#         form = FarmerProfileForm(request.POST, request.FILES, instance=farmer)
#         if form.is_valid():
#             try:
#                 form.save()
#                 messages.success(request, "Profil mis à jour avec succès.")
#                 return redirect('farmer_dashboard')
#             except Exception as e:
#                 messages.error(request, f"Erreur lors de la sauvegarde: {e}")
#         else:
#             messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
#     else:
#         form = FarmerProfileForm(instance=farmer)

#     return render(request, 'profil_farmer/edit_profile.html', {'form': form, 'farmer': farmer})

# @login_required
# def edit_profile(request):
#     farmer, created = FarmerProfile.objects.get_or_create(farmer=request.user)
    
#     if request.method == 'POST':
#         form = FarmerProfileForm(request.POST, request.FILES, instance=farmer)
        
#         if form.is_valid():
#             profile = form.save(commit=False)

#             # Vérifier et compléter les données de géolocalisation
#             if not profile.latitude or not profile.longitude:
#                 try:
#                     response = requests.get(
#                         'https://nominatim.openstreetmap.org/search',
#                         params={'q': profile.address, 'format': 'json', 'addressdetails': 1}
#                     )
#                     response.raise_for_status()  # Vérifie les codes HTTP
#                     data = response.json()
#                     if data:
#                         profile.latitude = float(data[0].get('lat'))
#                         profile.longitude = float(data[0].get('lon'))
#                     else:
#                         messages.error(request, "Adresse non trouvée.")
#                         return redirect('edit_profile')
#                 except requests.exceptions.RequestException as e:
#                     messages.error(request, f"Erreur lors de la recherche d'adresse : {e}")
#                     return redirect('edit_profile')

#             profile.save()
#             messages.success(request, "Votre profil a été mis à jour avec succès.")
#             return redirect('farmer_dashboard')
#         else:
#             messages.error(request, "Erreur dans le formulaire. Veuillez corriger les erreurs.")
#     else:
#         form = FarmerProfileForm(instance=farmer)
    
#     return render(request, 'profil_farmer/edit_profile.html', {'form': form, 'farmer': farmer})





# Vue pour prévisualiser le profil
@login_required
def preview_profile(request, farmer_id):
    # Récupérer le profil fermier par son ID
    farmer = get_object_or_404(FarmerProfile, id=farmer_id)
    
    # Ne pas valider à nouveau le formulaire ici, juste afficher l'aperçu
    form = FarmerProfileForm(instance=farmer)

    context = {
        'form': form,
        'farmer': farmer,
        'preview': True
    }

    return render(request, 'profil_farmer/preview_profile.html', context)







# Liste des fermiers sur la carte
def farmer_map(request):
    farmers = FarmerProfile.objects.all()
    return render(request, 'profil_farmer/farmer_map.html', {'farmers': farmers})



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

