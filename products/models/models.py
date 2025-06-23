from django.db import models
from django.utils import timezone
from accounts.models import User
from .product import Product
from .farmeProfile import FarmerProfile

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('ready', 'Prête à être récupérée'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée'),
    )
    
    customer = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    pickup_date = models.DateTimeField(null=True, blank=True)
    pickup_time_slot = models.CharField(max_length=50, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    reference_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    payment_status = models.CharField(max_length=20, default='unpaid', choices=(
        ('unpaid', 'Non payée'),
        ('processing', 'En cours de paiement'),
        ('paid', 'Payée'),
        ('refunded', 'Remboursée'),
    ))
    payment_method = models.CharField(max_length=20, blank=True, null=True, choices=(
        ('card', 'Carte de crédit'),
        ('cash', 'Espèces'),
        ('transfer', 'Virement bancaire'),
    ))
    payment_date = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Commande #{self.id} - {self.customer.username}"
    
    def calculate_total(self):
        total = sum(item.get_cost() for item in self.items.all())
        self.total_amount = total
        self.save()
        return total
        
    def clean(self):
        """Validation supplémentaire pour les commandes"""
        from django.core.exceptions import ValidationError
        
        # Vérifier que la date de retrait est dans le futur
        if self.pickup_date and self.pickup_date < timezone.now():
            raise ValidationError("La date de retrait ne peut pas être dans le passé.")
        
        # Vérifier que la commande a au moins un article
        if self.id and not self.items.exists():
            raise ValidationError("Une commande doit contenir au moins un article.")

    def save(self, *args, **kwargs):
        # Générer un numéro de référence unique s'il n'existe pas
        if not self.reference_number:
            import uuid
            self.reference_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} dans la commande #{self.order.id}"
    
    def get_cost(self):
        return self.price * self.quantity
    
    def clean(self):
        """Validation supplémentaire pour les articles de commande"""
        from django.core.exceptions import ValidationError
        
        # Vérifier que la quantité est positive
        if self.quantity <= 0:
            raise ValidationError("La quantité doit être positive.")
            
        # Vérifier la disponibilité du stock
        if self.product.stock < self.quantity:
            raise ValidationError(f"{self.product.name} n'est pas disponible en quantité suffisante. Stock disponible: {self.product.stock}")
    
    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.product.price
            
        # Nettoyer avant de sauvegarder
        self.full_clean()
        super().save(*args, **kwargs)
        
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Panier de {self.user.username}"
    
    def clear(self):
        self.items.all().delete()
    
    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())
    
    def item_count(self):
        return self.items.count()

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='cart_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
    def get_cost(self):
        return self.product.price * self.quantity

class Review(models.Model):
    RATING_CHOICES = (
        (1, '1 étoile'),
        (2, '2 étoiles'),
        (3, '3 étoiles'),
        (4, '4 étoiles'),
        (5, '5 étoiles'),
    )
    
    product = models.ForeignKey('products.Product', related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.User', related_name='reviews', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=100)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # Ensure a user can only review a product once
        unique_together = ('product', 'user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Avis de {self.user.username} sur {self.product.name}"

class Notification(models.Model):
    """Modèle pour les notifications aux utilisateurs"""
    NOTIFICATION_TYPES = (
        ('email', 'Email'),
        ('in_app', 'Dans l\'application'),
        ('both', 'Les deux'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('sent', 'Envoyée'),
        ('failed', 'Échec'),
        ('read', 'Lue'),
    )
    
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='email')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    order = models.ForeignKey(Order, related_name='notifications', on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"Notification: {self.title} pour {self.user.username}"
    
    def mark_as_sent(self):
        """Marquer la notification comme envoyée"""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save()
        return self
        
    def mark_as_failed(self):
        """Marquer la notification comme échouée"""
        self.status = 'failed'
        self.save()
        return self
        
    def mark_as_read(self):
        """Marquer la notification comme lue"""
        self.status = 'read'
        self.read_at = timezone.now()
        self.save()
        return self

class AvailabilityTimeSlot(models.Model):
    """Créneaux horaires disponibles pour les retraits de commande"""
    WEEKDAY_CHOICES = (
        (0, 'Lundi'),
        (1, 'Mardi'),
        (2, 'Mercredi'),
        (3, 'Jeudi'),
        (4, 'Vendredi'),
        (5, 'Samedi'),
        (6, 'Dimanche'),
    )
    
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availability_slots')
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_orders = models.PositiveIntegerField(default=5, help_text="Nombre maximum de commandes pour ce créneau")
    location = models.CharField(max_length=255, help_text="Lieu de retrait des commandes")
    active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['weekday', 'start_time']
        unique_together = ('farmer', 'weekday', 'start_time')
    
    def __str__(self):
        return f"{self.get_weekday_display()} de {self.start_time.strftime('%H:%M')} à {self.end_time.strftime('%H:%M')}"
    
    def is_available_for_date(self, date):
        """Vérifie si ce créneau est disponible pour une date donnée"""
        # Vérifier si la date correspond au jour de la semaine de ce créneau
        if date.weekday() != self.weekday:
            return False
            
        # Vérifier si le créneau est actif
        if not self.active:
            return False
            
        # Vérifier si la date n'est pas déjà passée
        if date < timezone.now().date():
            return False
            
        # Vérifier le nombre de rendez-vous déjà pris pour ce créneau à cette date
        appointments_count = PickupAppointment.objects.filter(
            availability_slot=self,
            pickup_date=date
        ).count()
        
        # Vérifier si le nombre maximum de commandes n'est pas atteint
        if appointments_count >= self.max_orders:
            return False
            
        return True
    
    def get_available_dates(self, weeks_ahead=4):
        """Retourne une liste de dates disponibles pour ce créneau"""
        available_dates = []
        
        # Date du jour
        today = timezone.now().date()
        
        # Calcul de la date de fin (aujourd'hui + nombre de semaines en avant)
        end_date = today + timezone.timedelta(weeks=weeks_ahead)
        
        # Pour chaque jour entre aujourd'hui et la date de fin
        current_date = today
        while current_date <= end_date:
            # Si le jour de la semaine correspond à ce créneau
            if current_date.weekday() == self.weekday:
                # Vérifier si ce créneau est disponible pour cette date
                if self.is_available_for_date(current_date):
                    available_dates.append(current_date)
            
            # Passer au jour suivant
            current_date += timezone.timedelta(days=1)
            
        return available_dates

class PickupAppointment(models.Model):
    """Rendez-vous pour le retrait d'une commande"""
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='pickup_appointment')
    availability_slot = models.ForeignKey(AvailabilityTimeSlot, on_delete=models.PROTECT, related_name='appointments')
    pickup_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['pickup_date', 'availability_slot__start_time']
        unique_together = ('availability_slot', 'pickup_date', 'order')
    
    def __str__(self):
        return f"Rendez-vous pour la commande #{self.order.id} le {self.pickup_date} à {self.availability_slot.start_time}"
    
    def save(self, *args, **kwargs):
        # Mettre à jour les informations de retrait sur la commande
        self.order.pickup_date = timezone.datetime.combine(
            self.pickup_date, 
            self.availability_slot.start_time
        )
        self.order.pickup_time_slot = f"{self.availability_slot.start_time.strftime('%H:%M')} - {self.availability_slot.end_time.strftime('%H:%M')}"
        self.order.save(update_fields=['pickup_date', 'pickup_time_slot'])
        
        super().save(*args, **kwargs)