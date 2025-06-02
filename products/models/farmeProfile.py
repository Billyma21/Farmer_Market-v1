#products/models/farmeProfile.py

from django.db import models
from django.utils import timezone
from accounts.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from products.utils import geocode_address
import math

class FarmerProfile(models.Model):
    # Champs supplémentaires pour mieux identifier le fermier
    farmer = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", limit_choices_to={'is_farmer': True})
    
    # Localisation du fermier
    latitude = models.FloatField(null=True, blank=True, help_text="Latitude pour la localisation sur la carte")
    longitude = models.FloatField(null=True, blank=True, help_text="Longitude pour la localisation sur la carte")
    
    # Champ pour stocker l'adresse complète (utile pour la géolocalisation)
    full_address = models.CharField(max_length=500, blank=True, help_text="Adresse complète pour la géolocalisation automatique")
    
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

    # Méthodes de production (bio, conventionnel, etc.)
    PRODUCTION_METHODS = (
        ('conventional', 'Conventionnelle'),
        ('organic', 'Agriculture biologique'),
        ('biodynamic', 'Biodynamique'),
        ('permaculture', 'Permaculture'),
        ('agroecology', 'Agroécologie'),
        ('other', 'Autre'),
    )
    production_method = models.CharField(max_length=50, choices=PRODUCTION_METHODS, blank=True, default='conventional')
    
    # Certifications (Label Bio, etc.)
    certifications = models.TextField(blank=True, help_text="Liste des certifications (Label Bio, etc.)")
    
    # Disponibilité pour les visites
    visits_allowed = models.BooleanField(default=False, help_text="Autorise les visites à la ferme")

    # Date de création du profil
    date_creation = models.DateTimeField(default=timezone.now)

    # Image représentant la ferme
    farm_images = models.ImageField(upload_to='farm_images/', blank=True, null=True, help_text="Téléchargez une image représentant la ferme")

    def __str__(self):
        return f"Profil du fermier {self.farmer.username}"
    
    def save(self, *args, **kwargs):
        # Si l'adresse complète est fournie et que les coordonnées sont manquantes, tenter de les calculer
        if self.full_address and (self.latitude is None or self.longitude is None):
            self.geocode_address()
        
        # Si les coordonnées sont fournies et que le lien Google Maps est vide, le générer
        if self.latitude and self.longitude and not self.google_maps_link:
            self.google_maps_link = f"https://www.google.com/maps/search/?api=1&query={self.latitude},{self.longitude}"
        
        super(FarmerProfile, self).save(*args, **kwargs)
    
    def geocode_address(self):
        """Utilise l'API Nominatim pour obtenir les coordonnées géographiques à partir de l'adresse."""
        lat, lon = geocode_address(self.full_address)
        if lat and lon:
            self.latitude = lat
            self.longitude = lon
            return True
        return False

# Création automatique d'un profil fermier lors de la création d'un utilisateur fermier
@receiver(post_save, sender=User)
def create_farmer_profile(sender, instance, created, **kwargs):
    if created and instance.is_farmer:
        FarmerProfile.objects.create(farmer=instance)


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