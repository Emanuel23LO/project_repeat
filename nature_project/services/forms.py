from django import forms
from . models import Service

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = "__all__"
        exclude = ['status']
        labels = {
            'name': 'Nombre',
            'value': 'valor',  
            'image': 'Imagen',                       
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ingresa el nombre'}),
            'value': forms.NumberInput(attrs={'placeholder': 'Ingresa el valor'}),  
            'image': forms.FileInput(attrs={'placeholder': 'Ingresa la imagen'}),          
        }