from django import forms

class RegisterForm(forms.Form):
    name = forms.CharField(label='Nombre', max_length=100, required=True)
    last_name = forms.CharField(label='Apellidos', max_length=100, required=True)
    document = forms.CharField(label='Documento', max_length=25, required=True)
    email = forms.EmailField(label='Correo electrónico', max_length=100, required=True)
    phone = forms.CharField(label='Celular', max_length=25, required=False)
    password = forms.CharField(label='Contraseña', max_length=100, widget=forms.PasswordInput, required=True)
    password_confirmation = forms.CharField(label='Confirmar contraseña', max_length=100, widget=forms.PasswordInput)
    
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirmation = cleaned_data.get('password_confirmation')
        
        if password != password_confirmation:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned_data
