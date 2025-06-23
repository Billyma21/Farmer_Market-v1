#products/models/farmeProfile.py

from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from accounts.models import User
from django.utils.text import slugify
import json

class FarmerProfile(models.Model):
    # Champs supplémentaires pour mieux identifier le fermier
    farmer = models.OneToOneField(User, on_delete=models.CASCADE, related_name="farmerprofile", 
                                 limit_choices_to={'is_farmer': True}, verbose_name="Utilisateur")
    
    # Informations de base
    farm_name = models.CharField(max_length=255, blank=True, verbose_name="Nom de la ferme")
    slug = models.SlugField(max_length=255, blank=True, unique=True)
    
    # Localisation du fermier
    latitude = models.FloatField(null=True, blank=True, 
                                help_text="Latitude pour la localisation sur la carte",
                                verbose_name="Latitude")
    longitude = models.FloatField(null=True, blank=True, 
                                 help_text="Longitude pour la localisation sur la carte",
                                 verbose_name="Longitude")
    
    # Détails du fermier
    description = models.TextField(blank=True, 
                                  help_text="Brève description du fermier et de sa ferme",
                                  verbose_name="Description")
    
    # Adresse complète
    street = models.CharField(max_length=255, blank=True, 
                             help_text="Rue et numéro",
                             verbose_name="Rue")
    city = models.CharField(max_length=100, blank=True, 
                           help_text="Ville du fermier",
                           verbose_name="Ville")
    zip_code = models.CharField(max_length=10, blank=True, 
                               help_text="Code postal du fermier",
                               verbose_name="Code postal")
    country = models.CharField(max_length=100, blank=True, default="Belgique",
                              help_text="Pays du fermier",
                              verbose_name="Pays")
    location_instructions = models.TextField(blank=True,
                                           help_text="Instructions pour trouver la ferme plus facilement",
                                           verbose_name="Comment trouver la ferme")
    
    # Contact et communication
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Le numéro de téléphone doit être au format: '+999999999'. 10-15 chiffres autorisés."
    )
    phone_number = models.CharField(max_length=15, blank=True, 
                                   validators=[phone_regex],
                                   help_text="Numéro de téléphone du fermier",
                                   verbose_name="Téléphone")
    email = models.EmailField(blank=True, null=True,
                             help_text="Email de contact pour la ferme",
                             verbose_name="Email de contact")
    website = models.URLField(blank=True, null=True, 
                             help_text="Site web de la ferme",
                             verbose_name="Site web")
    
    # Réseaux sociaux
    facebook = models.URLField(blank=True, null=True, 
                              help_text="Lien vers la page Facebook",
                              verbose_name="Facebook")
    instagram = models.URLField(blank=True, null=True, 
                               help_text="Lien vers le compte Instagram",
                               verbose_name="Instagram")
    twitter = models.URLField(blank=True, null=True, 
                             help_text="Lien vers le compte Twitter",
                             verbose_name="Twitter")
    
    # Secteur agricole et informations supplémentaires
    agriculture_sector = models.CharField(max_length=255, blank=True, 
                                         help_text="Secteur ou branche agricole de la ferme (ex: culture, élevage, etc.)",
                                         verbose_name="Secteur agricole")
    services = models.TextField(blank=True, 
                               help_text="Services supplémentaires fournis par la ferme (ex: visites, produits locaux, etc.)",
                               verbose_name="Services")
    opening_hours = models.TextField(blank=True, 
                                    help_text="Horaires d'ouverture de la ferme",
                                    verbose_name="Horaires d'ouverture")
    
    # Options et services
    is_organic_certified = models.BooleanField(default=False, 
                                             help_text="La ferme est-elle certifiée biologique?",
                                             verbose_name="Certifié biologique")
    certification_details = models.TextField(blank=True, 
                                           help_text="Détails des certifications (Bio, HVE, etc.)",
                                           verbose_name="Détails des certifications")
    can_deliver = models.BooleanField(default=False,
                                     help_text="Le fermier propose-t-il des livraisons?",
                                     verbose_name="Propose des livraisons")
    delivery_area = models.TextField(blank=True,
                                    help_text="Zone de livraison (codes postaux, villes, etc.)",
                                    verbose_name="Zone de livraison")
    delivery_conditions = models.TextField(blank=True,
                                          help_text="Conditions de livraison (minimum de commande, délais, etc.)",
                                          verbose_name="Conditions de livraison")
    
    # Spécialités et produits phares
    specialties = models.TextField(blank=True,
                                  help_text="Spécialités et produits phares de la ferme",
                                  verbose_name="Spécialités")
    seasonal_products = models.TextField(blank=True,
                                        help_text="Produits disponibles selon les saisons",
                                        verbose_name="Produits saisonniers")
    
    # Méthodes de production
    production_methods = models.TextField(blank=True,
                                         help_text="Description des méthodes de production",
                                         verbose_name="Méthodes de production")
    
    # Date de création du profil
    date_creation = models.DateTimeField(default=timezone.now, 
                                        verbose_name="Date de création")
    last_updated = models.DateTimeField(auto_now=True,
                                       verbose_name="Dernière mise à jour")

    # Images
    farm_image = models.ImageField(upload_to='farm_images/', blank=True, null=True, 
                                   help_text="Image principale représentant la ferme",
                                   verbose_name="Image principale")
    
    # Stockage JSON pour les images supplémentaires
    additional_images_json = models.TextField(blank=True, null=True,
                                            help_text="Stockage JSON pour les images supplémentaires",
                                            verbose_name="Images supplémentaires (JSON)")
    
    def __str__(self):
        if self.farm_name:
            return f"{self.farm_name} ({self.farmer.username})"
        return f"Profil du fermier {self.farmer.username}"
        
    def save(self, *args, **kwargs):
        if not self.slug:
            if self.farm_name:
                self.slug = slugify(self.farm_name)
            else:
                self.slug = slugify(f"ferme-{self.farmer.username}")
        super().save(*args, **kwargs)
        
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('farmer_profile', kwargs={'farmer_id': self.farmer.id})
        
    def get_full_address(self):
        parts = []
        if self.street:
            parts.append(self.street)
        if self.zip_code and self.city:
            parts.append(f"{self.zip_code} {self.city}")
        elif self.city:
            parts.append(self.city)
        if self.country and self.country.lower() != "belgique":
            parts.append(self.country)
        return ", ".join(parts) if parts else "Adresse non spécifiée"
        
    def get_farm_image_url(self):
        if self.farm_image and hasattr(self.farm_image, 'url'):
            return self.farm_image.url
        return '/static/images/default-farm.jpg'
    
    def set_additional_images(self, images_list):
        """Stocke une liste d'images sous forme de JSON"""
        self.additional_images_json = json.dumps(images_list)
        
    def get_additional_images(self):
        """Récupère la liste des images supplémentaires"""
        if not self.additional_images_json:
            return []
        try:
            return json.loads(self.additional_images_json)
        except json.JSONDecodeError:
            return []
    
    @property
    def product_count(self):
        """Retourne le nombre de produits proposés par ce fermier"""
        return self.farmer.products.filter(is_active=True).count()
    
    @property
    def avg_rating(self):
        """Calcule la note moyenne des produits du fermier"""
        from django.db.models import Avg
        products = self.farmer.products.all()
        reviews = []
        for product in products:
            reviews.extend(list(product.reviews.all()))
        
        if not reviews:
            return 0
        
        avg = sum(review.rating for review in reviews) / len(reviews)
        return round(avg, 1)
    
    class Meta:
        verbose_name = "Profil de fermier"
        verbose_name_plural = "Profils de fermiers"
        ordering = ['farm_name', 'farmer__username']