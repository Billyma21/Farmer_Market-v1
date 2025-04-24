#products/models/farmeProfile.py

from django.db import models
from django.utils import timezone
from accounts.models import User

class FarmerProfile(models.Model):
    # Références à l'utilisateur
    farmer = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="profile", 
        limit_choices_to={'is_farmer': True}
    )
    
    # Informations de géolocalisation
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)

    # Informations sur la ferme
    farm_name = models.CharField(max_length=255, null=False, blank=False)  
    description = models.TextField(blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    agriculture_sector = models.CharField(max_length=255, blank=True)
    services = models.TextField(blank=True)
    website = models.URLField(blank=True, null=True)
    additional_info = models.TextField(blank=True)

    # Horaires d'ouverture pour chaque jour de la semaine
    opening_hours_json = models.JSONField(default=dict)

    # Fichiers multimédias
    farm_images = models.ImageField(
        upload_to='farm_images/', 
        blank=True, 
        null=True
    )

    # Métadonnées
    date_creation = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Profil du fermier {self.farmer.username}"







# #products/models/farmeProfile.py

# from django.db import models
# from django.utils import timezone
# from accounts.models import User

# class FarmerProfile(models.Model):
#     # Références à l'utilisateur
#     farmer = models.OneToOneField(
#         User, 
#         on_delete=models.CASCADE, 
#         related_name="profile", 
#         limit_choices_to={'is_farmer': True}
#     )
    
#     # Informations de géolocalisation
#     latitude = models.FloatField(null=True, blank=True)
#     longitude = models.FloatField(null=True, blank=True)
#     address = models.CharField(max_length=255, blank=True)

#     # Informations sur la ferme
#     farm_name = models.CharField(max_length=255, blank=True)  
#     description = models.TextField(blank=True)
#     phone_number = models.CharField(max_length=15, blank=True)
#     agriculture_sector = models.CharField(max_length=255, blank=True)
#     services = models.TextField(blank=True)
#     opening_hours = models.TextField(blank=True)
#     google_maps_link = models.URLField(max_length=255, blank=True)
#     website = models.URLField(blank=True, null=True)
#     additional_info = models.TextField(blank=True)

#     # Fichiers multimédias
#     farm_images = models.ImageField(
#         upload_to='farm_images/', 
#         blank=True, 
#         null=True
#     )

#     # Métadonnées
#     date_creation = models.DateTimeField(default=timezone.now)

#     def __str__(self):
#         return f"Profil du fermier {self.farmer.username}"





