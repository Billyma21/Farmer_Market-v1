# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import User
from django.core.exceptions import ValidationError

class RegisterFarmerForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email", widget=forms.EmailInput(attrs={'placeholder': 'Votre email'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        # Vérification si l'email est déjà utilisé
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Cet email est déjà utilisé.")
        return email

    def clean_username(self):
        # Vérification si le nom d'utilisateur est déjà pris
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Ce nom d'utilisateur est déjà pris.")
        return username


class RegisterCustomerForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email", widget=forms.EmailInput(attrs={'placeholder': 'Votre email'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Cet email est déjà utilisé.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Ce nom d'utilisateur est déjà pris.")
        return username


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Nom d\'utilisateur'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe'}))


# Profile du vendeur pour la map

from django import forms
from products.models.farmeProfile import FarmerProfile

class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = FarmerProfile
        fields = [
            'farm_name', 'description', 'street', 'city', 'zip_code', 'country',
            'location_instructions', 'phone_number', 'email', 'website', 'facebook',
            'instagram', 'twitter', 'agriculture_sector', 'services',
            'opening_hours', 'is_organic_certified', 'certification_details',
            'can_deliver', 'delivery_area', 'delivery_conditions', 'specialties',
            'seasonal_products', 'production_methods', 'farm_image', 'latitude', 'longitude'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Décrivez votre ferme...'}),
            'street': forms.TextInput(attrs={'placeholder': 'Rue et numéro'}),
            'city': forms.TextInput(attrs={'placeholder': 'Ville'}),
            'zip_code': forms.TextInput(attrs={'placeholder': 'Code postal'}),
            'country': forms.TextInput(attrs={'placeholder': 'Pays', 'value': 'Belgique'}),
            'location_instructions': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Instructions pour trouver la ferme...'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+32 xxx xx xx xx'}),
            'email': forms.EmailInput(attrs={'placeholder': 'contact@exemple.com'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://www.votresite.com'}),
            'facebook': forms.URLInput(attrs={'placeholder': 'https://www.facebook.com/votrepage'}),
            'instagram': forms.URLInput(attrs={'placeholder': 'https://www.instagram.com/votrepage'}),
            'twitter': forms.URLInput(attrs={'placeholder': 'https://twitter.com/votrepage'}),
            'agriculture_sector': forms.TextInput(attrs={'placeholder': 'Ex: Maraîchage, Élevage, Arboriculture...'}),
            'services': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Services proposés: vente directe, visites guidées...'}),
            'opening_hours': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Ex: Lun-Ven 9h-18h, Sam 9h-12h'}),
            'certification_details': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Détails des certifications (Bio, HVE, etc.)'}),
            'delivery_area': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Zone de livraison (codes postaux, villes)'}),
            'delivery_conditions': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Conditions de livraison (minimum de commande, délais)'}),
            'specialties': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Produits phares de votre ferme'}),
            'seasonal_products': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Produits disponibles selon les saisons'}),
            'production_methods': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Méthodes de production employées'}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }
        labels = {
            'farm_name': 'Nom de la ferme',
            'description': 'Description',
            'street': 'Rue et numéro',
            'city': 'Ville',
            'zip_code': 'Code postal',
            'country': 'Pays',
            'location_instructions': 'Comment trouver la ferme',
            'phone_number': 'Téléphone',
            'email': 'Email de contact',
            'website': 'Site web',
            'facebook': 'Page Facebook',
            'instagram': 'Compte Instagram',
            'twitter': 'Compte Twitter',
            'agriculture_sector': 'Secteur agricole',
            'services': 'Services proposés',
            'opening_hours': 'Horaires d\'ouverture',
            'is_organic_certified': 'Certifié biologique',
            'certification_details': 'Détails des certifications',
            'can_deliver': 'Propose des livraisons',
            'delivery_area': 'Zone de livraison',
            'delivery_conditions': 'Conditions de livraison',
            'specialties': 'Spécialités',
            'seasonal_products': 'Produits saisonniers',
            'production_methods': 'Méthodes de production',
            'farm_image': 'Image principale de la ferme',
        }
