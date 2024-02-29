from django import forms
from . models import Cabin
from cabin_types.models import Cabin_type

class CabinForm(forms.ModelForm):
    cabin_type = forms.ModelChoiceField(queryset=Cabin_type.objects.filter(status=True).order_by('name'), label="Tipo de cabaña")
       
    class Meta:
        model = Cabin
        fields = "__all__"
        exclude = ['status']
        labels = {
            'name': 'Nombre',
            'capacity': 'Capacidad',  
            'description': 'Descripcion',  
            'value': 'Valor',
            'image': 'Imagen',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ingresa el nombre'}),
            'capacity': forms.NumberInput(attrs={'placeholder': 'Ingresa la disponibilidad'}),
            'description': forms.TextInput(attrs={'placeholder': 'Ingresa la description'}),    
            'value': forms.TextInput(attrs={'placeholder': 'Ingresa el valor'}),
            'image': forms.FileInput(attrs={'placeholder': 'Ingresa la imagen de la cabaña'}),   
        }