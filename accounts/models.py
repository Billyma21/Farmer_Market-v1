# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Champs pour distinguer les fermiers des clients
    is_farmer = models.BooleanField(default=False, help_text="Indicates if the user is a farmer")
    is_customer = models.BooleanField(default=False, help_text="Indicates if the user is a customer")

    def __str__(self):
        return self.username
