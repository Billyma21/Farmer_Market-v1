# products/forms/opening_hours.py

from django import forms
from products.models import OpeningHours

class OpeningHoursForm(forms.ModelForm):
    class Meta:
        model = OpeningHours
        fields = ['day_of_week', 'opening_time', 'closing_time', 'is_closed']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
            'opening_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_closed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        opening_time = cleaned_data.get('opening_time')
        closing_time = cleaned_data.get('closing_time')
        is_closed = cleaned_data.get('is_closed')

        if not is_closed:
            if not opening_time or not closing_time:
                raise forms.ValidationError("Veuillez fournir les horaires d'ouverture et de fermeture.")
            if opening_time >= closing_time:
                raise forms.ValidationError("L'heure d'ouverture doit précéder l'heure de fermeture.")
        return cleaned_data
