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
        fields = ['name', 'description', 'price', 'stock', 'category', 'image', 'image_url']
    
    image_url = forms.URLField(required=False, label="Image URL", widget=forms.URLInput(attrs={'placeholder': 'URL de l\'image'}))
