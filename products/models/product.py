# # products/models/product.py

from django.db import models
from django.utils.text import slugify
from accounts.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    farmer = models.ForeignKey(User, related_name='products', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    stock = models.IntegerField(default=0)
    sales_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def get_image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return '/static/images/default-image.jpg'





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
#         # Si une image est présente, retourner l'URL de l'image
#         if self.image and hasattr(self.image, 'url'):
#             return self.image.url
#         # Sinon, retourner l'URL de l'image externe si disponible
#         elif self.image_url:
#             return self.image_url
#         # Retourner l'image par défaut si aucune image n'est présente
#         return '/static/images/default-image.jpg'