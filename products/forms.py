# # products/forms.py

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
