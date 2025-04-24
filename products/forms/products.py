# products/forms/products.py

from django import forms
from products.models import Product

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



