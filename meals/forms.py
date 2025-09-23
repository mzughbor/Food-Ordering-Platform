from django import forms
from .models import Meal
from restaurants.models import Restaurant


class MealForm(forms.ModelForm):
    """Form for creating and editing meals"""
    
    class Meta:
        model = Meal
        fields = ['name', 'description', 'price', 'image', 'is_available']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter meal name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter meal description'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.restaurant = kwargs.pop('restaurant', None)
        super().__init__(*args, **kwargs)
        
        # Make image field optional
        self.fields['image'].required = False
        
        # Add help text
        self.fields['price'].help_text = 'Enter price in dollars (e.g., 12.99)'
        self.fields['image'].help_text = 'Upload an image for your meal (optional)'
        self.fields['is_available'].help_text = 'Check if this meal is currently available for ordering'


class MealSearchForm(forms.Form):
    """Form for searching and filtering meals"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search meals...'
        })
    )
    is_available = forms.ChoiceField(
        choices=[('', 'All'), ('true', 'Available'), ('false', 'Unavailable')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
