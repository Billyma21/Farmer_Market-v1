
# products/forms/farmer_profile.py

import requests
from django import forms
from django.forms import inlineformset_factory
from products.models import FarmerProfile, OpeningHours
from products.forms.opening_hours import OpeningHoursForm

class FarmerProfileForm(forms.ModelForm):
    farm_images = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = FarmerProfile
        fields = [
            'farm_name', 'description', 'address', 'phone_number', 'agriculture_sector',
            'services', 'website', 'farm_images', 'latitude', 'longitude',
            'additional_info'
        ]
        widgets = {
            'farm_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'agriculture_sector': forms.TextInput(attrs={'class': 'form-control'}),
            'services': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'additional_info': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

    def clean_address(self):
        address = self.cleaned_data.get('address')
        if address:
            try:
                response = requests.get(
                    'https://nominatim.openstreetmap.org/search',
                    params={'q': address, 'format': 'json', 'addressdetails': 1},
                    headers={'User-Agent': 'MonSite/1.0'}
                )
                response.raise_for_status()
                data = response.json()
                if data:
                    self.cleaned_data['latitude'] = float(data[0]['lat'])
                    self.cleaned_data['longitude'] = float(data[0]['lon'])
                else:
                    raise forms.ValidationError("Adresse non trouvée. Veuillez vérifier et réessayer.")
            except requests.RequestException as e:
                raise forms.ValidationError(f"Erreur lors de la vérification de l'adresse : {e}")
        return address

# Formset pour les horaires
OpeningHoursFormSet = inlineformset_factory(
    FarmerProfile, OpeningHours,
    form=OpeningHoursForm,
    extra=7,  # Une ligne pour chaque jour de la semaine
    can_delete=True
)



# # products/forms/farmer_profile.py
# import requests
# from django import forms
# from products.models import FarmerProfile
# from datetime import time

# class FarmerProfileForm(forms.ModelForm):
#     farm_images = forms.ImageField(
#         required=False,
#         widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
#     )

#     opening_hours_start = forms.TimeField(
#         required=False,
#         widget=forms.TimeInput(attrs={'class': 'form-control', 'placeholder': '08:00'}),
#     )

#     opening_hours_end = forms.TimeField(
#         required=False,
#         widget=forms.TimeInput(attrs={'class': 'form-control', 'placeholder': '18:00'}),
#     )

#     class Meta:
#         model = FarmerProfile
#         fields = [
#             'farm_name', 'description', 'address', 'phone_number', 'agriculture_sector',
#             'services', 'opening_hours_start', 'opening_hours_end', 'website', 'farm_images', 
#             'latitude', 'longitude', 'google_maps_link', 'additional_info'
#         ]
#         widgets = {
#             'farm_name': forms.TextInput(attrs={'class': 'form-control'}),
#             'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
#             'address': forms.TextInput(attrs={'class': 'form-control'}),
#             'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
#             'agriculture_sector': forms.TextInput(attrs={'class': 'form-control'}),
#             'services': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
#             'website': forms.URLInput(attrs={'class': 'form-control'}),
#             'google_maps_link': forms.URLInput(attrs={'class': 'form-control'}),
#             'additional_info': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
#         }

#     def clean_opening_hours_start(self):
#         opening_hours_start = self.cleaned_data.get('opening_hours_start')
#         if not opening_hours_start:
#             raise forms.ValidationError("L'heure d'ouverture est obligatoire.")
#         return opening_hours_start

#     def clean_opening_hours_end(self):
#         opening_hours_end = self.cleaned_data.get('opening_hours_end')
#         if not opening_hours_end:
#             raise forms.ValidationError("L'heure de fermeture est obligatoire.")
#         return opening_hours_end

#     def clean_address(self):
#         address = self.cleaned_data.get('address')
#         if address:
#             try:
#                 response = requests.get(
#                     'https://nominatim.openstreetmap.org/search',
#                     params={'q': address, 'format': 'json', 'addressdetails': 1},
#                     headers={'User-Agent': 'MonSite/1.0'}
#                 )
#                 response.raise_for_status()
#                 data = response.json()
#                 if data:
#                     self.cleaned_data['latitude'] = float(data[0]['lat'])
#                     self.cleaned_data['longitude'] = float(data[0]['lon'])
#                 else:
#                     raise forms.ValidationError("Adresse non trouvée. Veuillez vérifier et réessayer.")
#             except requests.RequestException as e:
#                 raise forms.ValidationError(f"Erreur lors de la vérification de l'adresse : {e}")
#         return address


# # products/forms/farmer_profile.py

# from django import forms
# from products.models import FarmerProfile
# import re
# import requests

# class FarmerProfileForm(forms.ModelForm):
#     farm_images = forms.ImageField(
#         required=False,
#         widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
#     )

#     # Utilisation d'un champ DateTime pour simplifier la gestion des horaires
#     opening_hours_start = forms.TimeField(
#         required=False,
#         widget=forms.TimeInput(attrs={'class': 'form-control', 'placeholder': '08:00'}),
#     )

#     opening_hours_end = forms.TimeField(
#         required=False,
#         widget=forms.TimeInput(attrs={'class': 'form-control', 'placeholder': '18:00'}),
#     )

#     class Meta:
#         model = FarmerProfile
#         fields = [
#             'farm_name', 'description', 'address', 'phone_number', 'agriculture_sector',
#             'services', 'opening_hours_start', 'opening_hours_end', 'website', 'farm_images', 
#             'latitude', 'longitude', 'google_maps_link', 'additional_info'
#         ]
#         widgets = {
#             'farm_name': forms.TextInput(attrs={'class': 'form-control'}),
#             'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
#             'address': forms.TextInput(attrs={'class': 'form-control'}),
#             'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
#             'agriculture_sector': forms.TextInput(attrs={'class': 'form-control'}),
#             'services': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
#             'website': forms.URLInput(attrs={'class': 'form-control'}),
#             'google_maps_link': forms.URLInput(attrs={'class': 'form-control'}),
#             'additional_info': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
#         }

#     def clean_opening_hours_start(self):
#         opening_hours_start = self.cleaned_data.get('opening_hours_start')
#         if not opening_hours_start:
#             raise forms.ValidationError("L'heure d'ouverture est obligatoire.")
#         return opening_hours_start

#     def clean_opening_hours_end(self):
#         opening_hours_end = self.cleaned_data.get('opening_hours_end')
#         if not opening_hours_end:
#             raise forms.ValidationError("L'heure de fermeture est obligatoire.")
#         return opening_hours_end

#     def clean_address(self):
#         address = self.cleaned_data.get('address')
#         if address:
#             try:
#                 response = requests.get(
#                     'https://nominatim.openstreetmap.org/search',
#                     params={'q': address, 'format': 'json', 'addressdetails': 1},
#                     headers={'User-Agent': 'MonSite/1.0'}
#                 )
#                 response.raise_for_status()
#                 data = response.json()
#                 if data:
#                     self.cleaned_data['latitude'] = float(data[0]['lat'])
#                     self.cleaned_data['longitude'] = float(data[0]['lon'])
#                 else:
#                     raise forms.ValidationError("Adresse non trouvée. Veuillez vérifier et réessayer.")
#             except requests.RequestException as e:
#                 raise forms.ValidationError(f"Erreur lors de la vérification de l'adresse : {e}")
#         return address






#--------------------------------
# from django import forms
# from products.models import FarmerProfile
# import re
# import requests

# class FarmerProfileForm(forms.ModelForm):
#     farm_images = forms.ImageField(
#         required=False,
#         widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
#     )
    
#     opening_hours = forms.CharField(
#         required=True,
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '08:00 à 18:00'}),
#     )

#     class Meta:
#         model = FarmerProfile
#         fields = [
#             'farm_name', 'description', 'address', 'phone_number', 'agriculture_sector',
#             'services', 'opening_hours', 'website', 'farm_images', 
#             'latitude', 'longitude', 'google_maps_link', 'additional_info'
#         ]
#         widgets = {
#             'farm_name': forms.TextInput(attrs={'class': 'form-control'}),
#             'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
#             'address': forms.TextInput(attrs={'class': 'form-control'}),
#             'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
#             'agriculture_sector': forms.TextInput(attrs={'class': 'form-control'}),
#             'services': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
#             'website': forms.URLInput(attrs={'class': 'form-control'}),
#             'google_maps_link': forms.URLInput(attrs={'class': 'form-control'}),
#             'additional_info': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
#         }

#     def clean_opening_hours(self):
#         opening_hours = self.cleaned_data.get('opening_hours')
#         pattern = r'\d{2}:\d{2} à \d{2}:\d{2}'
#         if not re.match(pattern, opening_hours):
#             raise forms.ValidationError("Le format des horaires doit être 'HH:MM à HH:MM'.")
#         return opening_hours

#     def clean_address(self):
#         address = self.cleaned_data.get('address')
#         if address:
#             try:
#                 response = requests.get(
#                     'https://nominatim.openstreetmap.org/search',
#                     params={'q': address, 'format': 'json', 'addressdetails': 1},
#                     headers={'User-Agent': 'MonSite/1.0'}
#                 )
#                 response.raise_for_status()
#                 data = response.json()
#                 if data:
#                     self.cleaned_data['latitude'] = float(data[0]['lat'])
#                     self.cleaned_data['longitude'] = float(data[0]['lon'])
#                 else:
#                     raise forms.ValidationError("Adresse non trouvée. Veuillez vérifier et réessayer.")
#             except requests.RequestException as e:
#                 raise forms.ValidationError(f"Erreur lors de la vérification de l'adresse : {e}")
#         return address

