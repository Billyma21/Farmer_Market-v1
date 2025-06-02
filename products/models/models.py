# from django.db import models
# from django.utils.text import slugify
# from accounts.models import User

# class Category(models.Model):
#     name = models.CharField(max_length=100)
#     slug = models.SlugField(unique=True, blank=True)  # Le champ 'slug' peut être vide au début

#     def save(self, *args, **kwargs):
#         if not self.slug:  # Si le slug n'est pas déjà défini
#             self.slug = slugify(self.name)  # Générer un slug à partir du nom
#         super().save(*args, **kwargs)  # Appeler la méthode save du modèle parent

#     def __str__(self):
#         return self.name

# class Product(models.Model):
#     name = models.CharField(max_length=255)
#     description = models.TextField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     image = models.ImageField(upload_to='products/', blank=True, null=True)
#     image_url = models.URLField(blank=True, null=True)
#     category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
#     farmer = models.ForeignKey(User, related_name='products', on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#     stock = models.IntegerField(default=0)  # Ajouter un champ stock
#     sales_count = models.IntegerField(default=0)  # Compte des ventes

#     def __str__(self):
#         return self.name

#     # Méthode pour obtenir l'URL de l'image
#     def get_image_url(self):
#         if self.image and hasattr(self.image, 'url'):
#             return self.image.url  # Utiliser l'image téléchargée
#         elif self.image_url:
#             return self.image_url  # Utiliser l'URL externe
#         return '/static/images/default-image.jpg'  # Image par défaut si aucune image n'est présente



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

from django.db import models
from accounts.models import User
from products.models import Product
from django.utils import timezone
import uuid

class Order(models.Model):
    STATUS_CHOICES = (
        ('created', 'Créée'),
        ('processing', 'En traitement'),
        ('shipped', 'Expédiée'),
        ('delivered', 'Livrée'),
        ('cancelled', 'Annulée'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
        ('refunded', 'Remboursé'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Informations de livraison
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_zip_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100, default='Belgique')
    
    # Informations de contact
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    
    # Informations de paiement
    payment_method = models.CharField(max_length=50, blank=True)
    payment_id = models.CharField(max_length=150, blank=True, null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Champs pour le suivi et la communication
    notes = models.TextField(blank=True, null=True)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'
    
    def __str__(self):
        return f"Commande {self.id} - {self.customer.username}"
    
    def get_total_price(self):
        return sum(item.get_cost() for item in self.items.all())
    
    def update_total_price(self):
        self.total_price = self.get_total_price()
        self.save()
    
    def cancel(self):
        self.status = 'cancelled'
        # Remettre les produits en stock
        for item in self.items.all():
            product = item.product
            product.stock += item.quantity
            product.save()
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.PROTECT)
    farmer = models.ForeignKey(User, on_delete=models.PROTECT, related_name='sold_items')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    def get_cost(self):
        return self.price * self.quantity