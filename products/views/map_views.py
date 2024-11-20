# products/views/map_views.py

from django.shortcuts import render
from products.models import FarmerProfile

# Vue pour afficher la carte
def map_view(request):
    farmers = FarmerProfile.objects.select_related('farmer').all()
    return render(request, 'products/map_view.html', {'farmers': farmers})