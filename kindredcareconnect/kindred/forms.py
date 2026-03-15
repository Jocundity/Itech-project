from django import forms
from .models import EmergencyContact


class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        fields = ['name', 'mobile', 'relationship']
        labels = {
            'name': 'Contact Name',
            'mobile': 'Mobile Number',
            'relationship': 'Relationship',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control rounded-pill bg-beige shadow-sm border p-1 me-2',
                'placeholder': 'Enter contact name'
            }),
            'mobile': forms.TextInput(attrs={
                'class': 'form-control rounded-pill bg-beige shadow-sm border p-1 me-2',
                'placeholder': 'Enter mobile number (e.g 07712345678)',
                'type': 'tel'
            }),
            'relationship': forms.TextInput(attrs={
                'class': 'form-control rounded-pill bg-beige shadow-sm border p-1 me-2',
                'placeholder': 'Enter relationship (e.g. Spouse, Daughter)'
            }),
        }
