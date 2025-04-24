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

class OrderForm(forms.Form):
    shipping_address = forms.CharField(
        label="Adresse de livraison",
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adresse complète'})
    )
    shipping_city = forms.CharField(
        label="Ville",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ville'})
    )
    shipping_zip_code = forms.CharField(
        label="Code postal",
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Code postal'})
    )
    contact_email = forms.EmailField(
        label="Email de contact",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email pour le suivi de commande'})
    )
    contact_phone = forms.CharField(
        label="Téléphone",
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro de téléphone'})
    )
    notes = forms.CharField(
        label="Notes sur la commande",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Instructions spéciales pour la livraison ou autres informations',
            'rows': 3
        })
    )
    payment_method = forms.ChoiceField(
        label="Méthode de paiement",
        choices=[
            ('stripe', 'Carte de crédit'),
            ('paypal', 'PayPal'),
            ('bank_transfer', 'Virement bancaire')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    # Validations personnalisées
    def clean_shipping_zip_code(self):
        zip_code = self.cleaned_data.get('shipping_zip_code')
        # Validation pour les codes postaux belges (4 chiffres)
        if not zip_code.isdigit() or len(zip_code) != 4:
            raise forms.ValidationError("Le code postal belge doit comporter 4 chiffres.")
        return zip_code
    
    def clean_contact_phone(self):
        phone = self.cleaned_data.get('contact_phone')
        # Supprimer les espaces et caractères non numériques
        phone = ''.join(c for c in phone if c.isdigit() or c in '+-')
        # S'assurer que le numéro est valide
        if len(phone) < 9:
            raise forms.ValidationError("Veuillez entrer un numéro de téléphone valide.")
        return phone
