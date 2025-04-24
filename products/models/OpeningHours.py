# products/models/OpeningHours.py
from django.db import models
from django.utils import timezone
from products.models import FarmerProfile

class OpeningHours(models.Model):
    DAYS_OF_WEEK = [
        ('lundi', 'Lundi'),
        ('mardi', 'Mardi'),
        ('mercredi', 'Mercredi'),
        ('jeudi', 'Jeudi'),
        ('vendredi', 'Vendredi'),
        ('samedi', 'Samedi'),
        ('dimanche', 'Dimanche'),
    ]

    farmer_profile = models.ForeignKey(FarmerProfile, related_name="hours_of_operation", on_delete=models.CASCADE)
    day_of_week = models.CharField(choices=DAYS_OF_WEEK, max_length=10)
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)  

    def __str__(self):
        return f"{self.day_of_week}: {self.opening_time} - {self.closing_time}"
