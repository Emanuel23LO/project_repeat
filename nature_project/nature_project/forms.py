from django import forms

class RegisterForm(forms.Form):
    name = forms.CharField(label='Nombre', max_length=100, required=True)
    last_name = forms.CharField(label='Apellidos', max_length=100, required=True)
    document = forms.CharField(label='Documento', max_length=25, required=True)
    email = forms.EmailField(label='Correo electrónico', max_length=100, required=True)
    phone = forms.CharField(label='Celular', max_length=25, required=False)
    password = forms.CharField(label='Contraseña', max_length=100, widget=forms.PasswordInput, required=True)
    

    def clean(self):
        cleaned_data = super().clean()
        # Validaciones adicionales si son necesarias
        return cleaned_data
