from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import User

class UserProfileUpdateForm(UserChangeForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        label="Lozinka"
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        label="Lozinka ponovo"
    )

    class Meta:
        model = User
        fields = ['ime_k', 'prz_k', 'mail_k', 'tip_k', 'password']
        widgets = {
            'ime_k': forms.TextInput(attrs={'class': 'form-control'}),
            'prz_k': forms.TextInput(attrs={'class': 'form-control'}),
            'mail_k': forms.EmailInput(attrs={'class': 'form-control'}),
            'tip_k': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'ime_k': 'Ime',
            'prz_k': 'Prezime',
            'mail_k': 'Email',
            'tip_k': 'Radno mesto',
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password != password_confirm:
            raise forms.ValidationError("Lozinke se ne poklapaju")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Ažuriraj password samo ako je unet novi
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        
        if commit:
            user.save()
        
        return user