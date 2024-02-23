from django import forms
from .models import Food, Beverage

class FoodForm(forms.ModelForm):
    class Meta:
        model = Food
        fields = ['name', 'price', 'quantity', 'category']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.HiddenInput(attrs={'class': 'form-control'},),
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Set the initial value for the 'category' field to 'Food'
            self.initial['category'] = 'Food'

class BeverageForm(forms.ModelForm):
    class Meta:
        model = Beverage
        fields = ['name', 'price', 'quantity']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.HiddenInput(attrs={'class': 'form-control'}),
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Set the initial value for the 'category' field to 'Food'
            self.initial['category'] = 'Beverages' 