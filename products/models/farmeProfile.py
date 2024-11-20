#products/models/farmeProfile.py

from django.db import models
from django.utils import timezone
from accounts.models import User

class FarmerProfile(models.Model):
    # Champs supplémentaires pour mieux identifier le fermier
    farmer = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", limit_choices_to={'is_farmer': True})
    
    # Localisation du fermier
    latitude = models.FloatField(null=True, blank=True, help_text="Latitude pour la localisation sur la carte")
    longitude = models.FloatField(null=True, blank=True, help_text="Longitude pour la localisation sur la carte")
    
    # Détails du fermier
    description = models.TextField(blank=True, help_text="Brève description du fermier et de sa ferme")
    address = models.CharField(max_length=255, blank=True, help_text="Adresse complète du fermier")
    phone_number = models.CharField(max_length=15, blank=True, help_text="Numéro de téléphone du fermier")
    
    # Secteur agricole et informations supplémentaires
    agriculture_sector = models.CharField(max_length=255, blank=True, help_text="Secteur ou branche agricole de la ferme (ex: culture, élevage, etc.)")
    services = models.TextField(blank=True, help_text="Services supplémentaires fournis par la ferme (ex: visites, produits locaux, etc.)")
    opening_hours = models.TextField(blank=True, help_text="Horaires d'ouverture de la ferme")
    
    # Lien vers Google Maps et informations supplémentaires
    google_maps_link = models.CharField(max_length=255, blank=True, help_text="Lien vers Google Maps pour localisation")
    additional_info = models.TextField(blank=True, help_text="Informations supplémentaires sur la ferme (ex: histoire, méthode de culture, etc.)")
    website = models.URLField(blank=True, null=True, help_text="Site web de la ferme")

    # Date de création du profil
    date_creation = models.DateTimeField(default=timezone.now)

    # Image représentant la ferme
    farm_images = models.ImageField(upload_to='farm_images/', blank=True, null=True, help_text="Téléchargez une image représentant la ferme")

    def __str__(self):
        return f"Profil du fermier {self.farmer.username}"


# from django.db import models
# from accounts.models import User

# class FarmerProfile(models.Model):
#     farmer = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", limit_choices_to={'is_farmer': True})
#     latitude = models.FloatField(null=True, blank=True, help_text="Latitude pour la localisation sur la carte")
#     longitude = models.FloatField(null=True, blank=True, help_text="Longitude pour la localisation sur la carte")
#     description = models.TextField(blank=True, help_text="Brève description du fermier et de sa ferme")
#     address = models.CharField(max_length=255, blank=True, help_text="Adresse complète du fermier")
#     phone_number = models.CharField(max_length=15, blank=True, help_text="Numéro de téléphone du fermier")
#     website = models.URLField(blank=True, help_text="URL du site web du fermier")
#     farm_images = models.ImageField(upload_to='farm_images/', blank=True, null=True, help_text="Téléchargez une image représentant la ferme")
#     opening_hours = models.TextField(blank=True, help_text="Horaires d'ouverture de la ferme")
#     services = models.TextField(blank=True, help_text="Services supplémentaires fournis par la ferme (ex : visites, produits locaux, etc.)")

#     def __str__(self):
#         return f"Profil du fermier {self.farmer.username}"