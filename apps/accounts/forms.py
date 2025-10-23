from django import forms
from django.contrib.auth import authenticate
from .models import User


class ProfileForm(forms.ModelForm):
    """Form for updating user profile information"""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'department', 'location']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Vorname',
                'required': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nachname',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'E-Mail-Adresse',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Telefonnummer (z.B. +49 30 12345678)',
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Abteilung (optional)',
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Standort (optional)',
            }),
        }
        labels = {
            'first_name': 'Vorname',
            'last_name': 'Nachname',
            'email': 'E-Mail-Adresse',
            'phone': 'Telefonnummer',
            'department': 'Abteilung',
            'location': 'Standort',
        }

    def clean_email(self):
        """Validate that email is unique (except for current user)"""
        email = self.cleaned_data.get('email')
        # Get the current user instance
        user_id = self.instance.id

        # Check if email already exists for another user
        if User.objects.filter(email=email).exclude(id=user_id).exists():
            raise forms.ValidationError('Eine Benutzer mit dieser Email-Adresse existiert bereits.')

        return email


class PasswordChangeForm(forms.Form):
    """Form for changing user password with current password validation"""

    current_password = forms.CharField(
        label='Aktuelles Passwort',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Geben Sie Ihr aktuelles Passwort ein',
            'required': True
        }),
        help_text='Für Sicherheitsgründe müssen Sie Ihr aktuelles Passwort bestätigen'
    )

    new_password = forms.CharField(
        label='Neues Passwort',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Geben Sie Ihr neues Passwort ein',
            'required': True
        }),
        min_length=8,
        help_text='Mindestens 8 Zeichen lang'
    )

    new_password_confirm = forms.CharField(
        label='Neues Passwort wiederholen',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Wiederholen Sie Ihr neues Passwort',
            'required': True
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        """Validate that current password is correct"""
        current_password = self.cleaned_data.get('current_password')

        if not self.user.check_password(current_password):
            raise forms.ValidationError('Das aktuelle Passwort ist incorrect.')

        return current_password

    def clean(self):
        """Validate that new passwords match"""
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        new_password_confirm = cleaned_data.get('new_password_confirm')

        if new_password and new_password_confirm:
            if new_password != new_password_confirm:
                raise forms.ValidationError('Die neuen Passwörter stimmen nicht überein.')

        # Check if new password is different from current password
        if new_password and self.user.check_password(new_password):
            raise forms.ValidationError('Das neue Passwort muss sich vom aktuellen Passwort unterscheiden.')

        return cleaned_data
