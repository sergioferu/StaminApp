from django import forms
from .models import Usuario, Producto


class UsuarioForm(forms.ModelForm):
    password = forms.CharField(required=False, widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'telefono', 'rol']

    def save(self, commit=True):
        user = super().save(commit=False)
        pwd = self.cleaned_data.get('password')
        if pwd:
            user.set_password(pwd)
        if commit:
            user.save()
        return user


try:
    from .models import Producto

    class ProductoForm(forms.ModelForm):
        class Meta:
            model = Producto
            fields = '__all__'
except ImportError:
    # models.Producto may not exist yet
    pass
