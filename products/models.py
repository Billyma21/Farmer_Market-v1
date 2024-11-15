from django.db import models
from accounts.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)  # Pour télécharger l'image
    image_url = models.URLField(blank=True, null=True)  # Pour l'URL d'une image externe
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    farmer = models.ForeignKey(User, related_name='products', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    stock = models.IntegerField(default=0)  # Ajouter un champ stock
    sales_count = models.IntegerField(default=0)  # Compte des ventes

    def __str__(self):
        return self.name

def get_image_url(self):
    """
    Retourne l'URL de l'image :
    - Utilise d'abord l'image téléchargée (ImageField).
    - Utilise ensuite l'URL externe si fournie.
    - Enfin, utilise une image par défaut.
    """
    if self.image and hasattr(self.image, 'url'):
        return self.image.url  # Utiliser l'URL de l'image téléchargée
    elif self.image_url:
        return self.image_url  # Utiliser l'URL externe
    return '/static/images/default-image.jpg'  # Image par défaut