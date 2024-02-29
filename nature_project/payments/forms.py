from django import forms
from . models import Payment
from bookings.models import Booking


class PaymentForm(forms.ModelForm):
    booking = forms.ModelChoiceField(queryset=Booking.objects.all().order_by('date_booking'))
    class Meta:
        model = Payment
        fields = "__all__"
        exclude = ['status']
        labels = {
            'payment_method': 'Metodo de pago',
            'date': 'Fecha ',
            'value': 'valor',   
            'booking.id': 'Reserva' 
        }
        widgets = {
            'payment_method': forms.TextInput(attrs={'placeholder': 'Ingresa metodo de pago'}),      
            'date': forms.DateInput(attrs={'type': 'date'}),   
            'value': forms.TextInput(attrs={'placeholder': 'Ingresa el valor'}),             
        }