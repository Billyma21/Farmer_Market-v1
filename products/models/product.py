# # products/models/product.py

from django.db import models
from django.utils.text import slugify
from accounts.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
        
    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['name']

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nom")
    description = models.TextField(verbose_name="Description")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Image")
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, verbose_name="Catégorie")
    farmer = models.ForeignKey(User, related_name='products', on_delete=models.CASCADE, verbose_name="Fermier")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")
    stock = models.IntegerField(default=0, verbose_name="Stock disponible")
    sales_count = models.IntegerField(default=0, verbose_name="Nombre de ventes")
    is_organic = models.BooleanField(default=False, verbose_name="Produit bio")
    unit = models.CharField(max_length=20, default="kg", verbose_name="Unité de mesure", 
                           choices=(
                               ('kg', 'Kilogramme'),
                               ('g', 'Gramme'),
                               ('l', 'Litre'),
                               ('cl', 'Centilitre'),
                               ('unit', 'Unité'),
                               ('box', 'Panier'),
                           ))
    slug = models.SlugField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Actif")

    def __str__(self):
        return self.name
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return '/static/images/default-image.jpg'
        
    def get_average_rating(self):
        """Calcule la note moyenne du produit"""
        reviews = self.reviews.all()
        if not reviews:
            return 0
        return round(sum(review.rating for review in reviews) / reviews.count(), 1)
    
    def get_review_count(self):
        """Retourne le nombre d'avis pour ce produit"""
        return self.reviews.count()
        
    def update_stock(self, quantity, action='decrease'):
        """Met à jour le stock du produit"""
        if action == 'decrease':
            if self.stock >= quantity:
                self.stock -= quantity
                self.sales_count += quantity
                self.save()
                return True
            return False
        elif action == 'increase':
            self.stock += quantity
            self.save()
            return True
        return False
        
    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['-created_at']





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