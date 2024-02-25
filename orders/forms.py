from django import forms
from .models import Order, OrderTable, OrderItem


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['table']
        widgets = {
            'table': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['table'].queryset = OrderTable.objects.all()

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['food', 'beverage', 'quantity','price']

        widgets = {
            'food': forms.Select(attrs={'class': 'form-control'}),
            'beverage': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super(OrderItemForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            # Wenn ein Objekt vorhanden ist (d. h. das Formular wird für eine vorhandene Bestellung bearbeitet),
            # setzt das Preisfeld auf den bereits gespeicherten Preis
            self.fields['price'].widget.attrs['value'] = instance.price

