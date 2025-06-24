# # products/forms.py

from django import forms
from products.models import Product
from django.utils import timezone
import datetime
from .models import Order, Review, AvailabilityTimeSlot, PickupAppointment

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image', 'category', 'stock']

    image = forms.ImageField(required=False, label="Télécharger une image")

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')

        # Validation : Vérifier si une image a été téléchargée.
        if not image:
            raise forms.ValidationError("Vous devez télécharger une image pour votre produit.")
        
        return cleaned_data

class OrderForm(forms.ModelForm):
    # Pour les créneaux horaires de retrait
    TIME_SLOTS = [
        ('matin_8_10', '8h - 10h'),
        ('matin_10_12', '10h - 12h'),
        ('aprem_14_16', '14h - 16h'),
        ('aprem_16_18', '16h - 18h'),
        ('soir_18_20', '18h - 20h'),
    ]
    
    pickup_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Date de retrait",
        help_text="Choisissez une date de retrait (minimum 1 jour, maximum 14 jours)"
    )
    
    pickup_time_slot = forms.ChoiceField(
        choices=TIME_SLOTS,
        label="Créneau horaire",
        help_text="Choisissez un créneau horaire pour récupérer votre commande"
    )
    
    class Meta:
        model = Order
        fields = ['pickup_date', 'pickup_time_slot', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Instructions spéciales pour votre commande'}),
        }
    
    def clean_pickup_date(self):
        pickup_date = self.cleaned_data.get('pickup_date')
        today = timezone.now().date()
        min_date = today + datetime.timedelta(days=1)
        max_date = today + datetime.timedelta(days=14)
        
        if pickup_date < min_date:
            raise forms.ValidationError("La date de retrait doit être au minimum le jour suivant.")
        
        if pickup_date > max_date:
            raise forms.ValidationError("La date de retrait ne peut pas dépasser 14 jours à partir d'aujourd'hui.")
        
        return pickup_date

class OrderNoteForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Instructions spéciales pour votre commande'}),
        }

class TimeSlotForm(forms.ModelForm):
    """Formulaire pour créer/éditer un créneau horaire"""
    class Meta:
        model = AvailabilityTimeSlot
        fields = ['weekday', 'start_time', 'end_time', 'max_orders', 'location', 'active']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'location': forms.TextInput(attrs={'placeholder': 'Adresse de retrait'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError("L'heure de début doit être antérieure à l'heure de fin.")
            
        # Vérifier qu'un créneau ne chevauche pas un autre créneau existant
        weekday = cleaned_data.get('weekday')
        farmer = self.initial.get('farmer') if hasattr(self, 'initial') and 'farmer' in self.initial else None
        
        if weekday is not None and farmer:
            # Exclure l'instance actuelle en cas de mise à jour
            instance_id = self.instance.id if self.instance and self.instance.id else None
            
            overlapping_slots = AvailabilityTimeSlot.objects.filter(
                farmer=farmer,
                weekday=weekday
            )
            
            if instance_id:
                overlapping_slots = overlapping_slots.exclude(id=instance_id)
                
            for slot in overlapping_slots:
                if (start_time <= slot.end_time and end_time >= slot.start_time):
                    raise forms.ValidationError(f"Ce créneau chevauche un créneau existant: {slot}")
        
        return cleaned_data

class PickupAppointmentForm(forms.ModelForm):
    """Formulaire pour planifier un rendez-vous de retrait"""
    class Meta:
        model = PickupAppointment
        fields = ['availability_slot', 'pickup_date']
        widgets = {
            'pickup_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, order=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.order = order
        
        if order:
            # Filtrer les créneaux disponibles pour cette commande
            farmers_ids = order.items.values_list('product__farmer', flat=True).distinct()
            self.fields['availability_slot'].queryset = AvailabilityTimeSlot.objects.filter(
                farmer__in=farmers_ids,
                active=True
            )
    
    def clean(self):
        cleaned_data = super().clean()
        availability_slot = cleaned_data.get('availability_slot')
        pickup_date = cleaned_data.get('pickup_date')
        
        if availability_slot and pickup_date:
            # Vérifier que la date correspond au jour de la semaine du créneau
            if pickup_date.weekday() != availability_slot.weekday:
                raise forms.ValidationError(
                    f"La date sélectionnée ({pickup_date.strftime('%d/%m/%Y')}) ne correspond pas au jour du créneau ({availability_slot.get_weekday_display()})."
                )
            
            # Vérifier que la date n'est pas dans le passé
            if pickup_date < timezone.now().date():
                raise forms.ValidationError("La date de retrait ne peut pas être dans le passé.")
            
            # Vérifier que le créneau n'est pas complet pour cette date
            count = PickupAppointment.objects.filter(
                availability_slot=availability_slot,
                pickup_date=pickup_date
            ).count()
            
            # Exclure l'instance actuelle en cas de mise à jour
            if self.instance and self.instance.id:
                count = count - 1
                
            if count >= availability_slot.max_orders:
                raise forms.ValidationError("Ce créneau est complet pour la date sélectionnée.")
        
        return cleaned_data

class ReviewForm(forms.ModelForm):
    """Formulaire pour ajouter/modifier un avis"""
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre de votre avis'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Votre commentaire'}),
        }

# from django import forms
# from products.models import Product

# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = ['name', 'description', 'price', 'image', 'image_url', 'category', 'stock']

#     image = forms.ImageField(required=False, label="Télécharger une image")
#     image_url = forms.URLField(required=False, label="Ou entrer un lien d'image")

#     def clean(self):
#         cleaned_data = super().clean()
#         image = cleaned_data.get('image')
#         image_url = cleaned_data.get('image_url')

#         # Validation : au moins un des champs image ou image_url doit être renseigné
#         if not image and not image_url:
#             raise forms.ValidationError("Vous devez fournir une image ou un lien vers une image.")

#         # Validation supplémentaire : vérifier que l'URL est valide si fournie
#         if image_url and not image_url.startswith(('http://', 'https://')):
#             raise forms.ValidationError("L'URL de l'image doit commencer par 'http://' ou 'https://'.")

#         return cleaned_data
