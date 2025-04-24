#products/views/profil_famer.py

import json
import base64
import requests
from django.http import JsonResponse
from io import BytesIO
from django.core.files.base import ContentFile
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from products.models import FarmerProfile, OpeningHours
from products.forms.products import ProductForm
from products.forms.farmer_profile import FarmerProfileForm
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_time
from products.models import OpeningHours



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
    farmer, created = FarmerProfile.objects.get_or_create(farmer=request.user)

    if request.method == 'POST':
        form = FarmerProfileForm(request.POST, request.FILES, instance=farmer)
        if form.is_valid():
            farmer = form.save()

            # Récupérer les horaires d'ouverture depuis le formulaire
            opening_hours_data = json.loads(request.POST.get('opening_hours', '[]'))
            for day, entry in opening_hours_data.items():
                is_closed = entry.get('is_closed', False)
                opening_time = entry.get('opening_time')
                closing_time = entry.get('closing_time')

                # Gérer les horaires fermés
                ot = parse_time(opening_time) if opening_time and not is_closed else None
                ct = parse_time(closing_time) if closing_time and not is_closed else None

                # Mettre à jour ou créer les horaires pour le jour donné
                OpeningHours.objects.update_or_create(
                    farmer_profile=farmer,
                    day_of_week=day,
                    defaults={
                        'is_closed': is_closed,
                        'opening_time': ot,
                        'closing_time': ct,
                    }
                )

            messages.success(request, "Profil et horaires mis à jour avec succès.")
            return redirect('edit_profile')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = FarmerProfileForm(instance=farmer)

    context = {
        'form': form,
        'farmer': farmer,
        'opening_hours': farmer.hours_of_operation.all(),
    }
    return render(request, 'profil_farmer/edit_profile.html', context)


 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from products.models import OpeningHours  # Importez le modèle OpeningHours

@csrf_exempt
def save_opening_hours(request):
    if request.method == "POST":
        data = json.loads(request.body)
        opening_hours = data.get("opening_hours", [])

        for entry in opening_hours:
            day_of_week = entry["day_of_week"]
            is_closed = entry["is_closed"]
            opening_time = entry["opening_time"]
            closing_time = entry["closing_time"]

            OpeningHours.objects.update_or_create(
                farmer_profile=request.user.farmerprofile,
                day_of_week=day_of_week,
                defaults={
                    "is_closed": is_closed,
                    "opening_time": opening_time if not is_closed else None,
                    "closing_time": closing_time if not is_closed else None,
                },
            )
        return JsonResponse({"success": True})
    return JsonResponse({"error": "Invalid request"})



# Vue pour prévisualiser le profil
@login_required
def preview_profile(request, farmer_id):
    # Récupérer le profil fermier par son ID
    farmer = get_object_or_404(FarmerProfile, id=farmer_id)
    
    # formulaire basé sur l'instance de profil fermier
    form = FarmerProfileForm(instance=farmer)
    
    context = {
        'form': form,
        'farmer': farmer,
        'preview': True,  # aperçu
    }

    return render(request, 'profil_farmer/preview_profile.html', context)




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

