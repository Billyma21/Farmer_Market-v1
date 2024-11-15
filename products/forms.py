# # products/forms.py
# from django import forms
# from .models import Product

# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = ['name', 'description', 'price', 'stock', 'category', 'image', 'image_url']
        
#     def clean(self):
#         cleaned_data = super().clean()
#         image = cleaned_data.get('image')
#         image_url = cleaned_data.get('image_url')

#         if not image and not image_url:
#             raise forms.ValidationError("Vous devez fournir soit une image soit un lien d'image.")

#         return cleaned_data

from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image', 'image_url', 'category', 'stock']

    # Si tu veux vérifier et nettoyer les données pour éviter d'avoir les deux (image et image_url) remplis en même temps
    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        image_url = cleaned_data.get('image_url')

        if not image and not image_url:
            raise forms.ValidationError("Vous devez fournir une image ou un lien vers une image.")
        
        return cleaned_data
