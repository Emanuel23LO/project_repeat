from django import forms
from . models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = "__all__"
        exclude = ['status']
        labels = {
            'full_name': 'Nombre',
            'document': 'Documento',
            'phone': 'Celular',    
            'email': 'Email',                       
        }
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Ingresa el nombre'}),
            'document': forms.TextInput(attrs={'placeholder': 'Ingresa el documento'}),
            'phone': forms.NumberInput(attrs={'placeholder': 'Ingresa el numero'}),  
            'email': forms.EmailInput(attrs={'placeholder': 'Ingresa el email'}),    

        }