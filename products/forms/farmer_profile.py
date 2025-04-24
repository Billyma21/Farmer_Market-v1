# products/forms/farmer_profile.py

from django import forms
from products.models import FarmerProfile
import re
import requests

class FarmerProfileForm(forms.ModelForm):
    # Champ pour l'upload d'images
    farm_images = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
    )
    
    opening_hours = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '08:00 à 18:00'}),
    )

    class Meta:
        model = FarmerProfile
        fields = [
            'description', 'address', 'phone_number', 'agriculture_sector',
            'services', 'opening_hours', 'website', 'farm_images', 
            'latitude', 'longitude', 'google_maps_link', 'additional_info'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'agriculture_sector': forms.TextInput(attrs={'class': 'form-control'}),
            'services': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'additional_info': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

    def clean_opening_hours(self):
        opening_hours = self.cleaned_data.get('opening_hours')
        pattern = r'\d{2}:\d{2} à \d{2}:\d{2}'
        if not re.match(pattern, opening_hours):
            raise forms.ValidationError("Le format des horaires doit être 'HH:MM à HH:MM'.")
        return opening_hours

    def clean_address(self):
        address = self.cleaned_data.get('address')
        if address:
            # Validation de l'adresse avec API Nominatim
            try:
                response = requests.get(
                    'https://nominatim.openstreetmap.org/search',
                    params={'q': address, 'format': 'json', 'addressdetails': 1},
                )
                response.raise_for_status()
                data = response.json()
                if data:
                    self.cleaned_data['latitude'] = float(data[0]['lat'])
                    self.cleaned_data['longitude'] = float(data[0]['lon'])
                else:
                    raise forms.ValidationError("Adresse non trouvée.")
            except Exception as e:
                raise forms.ValidationError(f"Erreur API: {e}")
        return address




# from django import forms
# from products.models import FarmerProfile
# import requests
# import re

# class FarmerProfileForm(forms.ModelForm):
#     farm_images = forms.ImageField(
#         required=False,
#         label="Image représentant la ferme",
#         widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
#     )
#     address = forms.CharField(
#         max_length=255,
#         required=True,
#         label="Adresse",
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rechercher une adresse...'}),
#     )
#     latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
#     longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)

#     opening_hours = forms.CharField(
#         required=True,
#         label="Horaires d'ouverture",
#         widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '08:00 à 18:00'}),
#     )

#     class Meta:
#         model = FarmerProfile
#         fields = [
#             'description', 'address', 'phone_number', 'agriculture_sector',
#             'services', 'opening_hours', 'website', 'farm_images', 'latitude',
#             'longitude', 'google_maps_link', 'additional_info'
#         ]
#         widgets = {
#             'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
#             'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
#             'agriculture_sector': forms.TextInput(attrs={'class': 'form-control'}),
#             'services': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
#             'website': forms.URLInput(attrs={'class': 'form-control'}),
#             'additional_info': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
#         }

#     def clean(self):
#         cleaned_data = super().clean()
#         address = cleaned_data.get('address')

#         # Géolocalisation basée sur l'adresse
#         if address:
#             try:
#                 response = requests.get(
#                     'https://nominatim.openstreetmap.org/search',
#                     params={'q': address, 'format': 'json', 'addressdetails': 1},
#                 )
#                 response.raise_for_status()
#                 data = response.json()
#                 if data:
#                     cleaned_data['latitude'] = float(data[0]['lat'])
#                     cleaned_data['longitude'] = float(data[0]['lon'])
#                 else:
#                     raise forms.ValidationError("Adresse non trouvée.")
#             except Exception as e:
#                 raise forms.ValidationError(f"Erreur avec l'API d'adresse : {e}")

#         # Validation des horaires d'ouverture
#         opening_hours = cleaned_data.get('opening_hours')
#         pattern = r'\d{2}:\d{2} à \d{2}:\d{2}'
#         if opening_hours and not re.match(pattern, opening_hours):
#             raise forms.ValidationError("Le format des horaires doit être 'HH:MM à HH:MM'.")
        
#         return cleaned_data

