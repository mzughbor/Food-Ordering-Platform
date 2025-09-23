from django import forms
from .models import Restaurant


class RestaurantForm(forms.ModelForm):
    """Form for editing restaurant details"""
    
    class Meta:
        model = Restaurant
        fields = ['name', 'description', 'location']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter restaurant name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter restaurant description'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter restaurant address'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help text
        self.fields['name'].help_text = 'The name of your restaurant'
        self.fields['description'].help_text = 'Describe your restaurant, cuisine type, and specialties'
        self.fields['location'].help_text = 'Full address where your restaurant is located'
