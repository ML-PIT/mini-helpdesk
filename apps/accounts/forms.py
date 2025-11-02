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
    
    def save(self, commit=True):
        """Save the new password for the user"""
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            self.user.set_password(new_password)
            if commit:
                self.user.save()
        return self.user


class UserCreateForm(forms.ModelForm):
    """Form for creating new users"""
    
    password1 = forms.CharField(
        label='Passwort',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': True}),
        help_text='Das Passwort sollte mindestens 8 Zeichen lang sein.',
        min_length=8,
        required=True
    )
    password2 = forms.CharField(
        label='Passwort bestätigen',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'required': True}),
        help_text='Geben Sie das Passwort zur Bestätigung erneut ein.',
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        
        # Set form field attributes and make required fields required
        for field_name, field in self.fields.items():
            if field_name not in ['password1', 'password2']:
                field.widget.attrs.update({'class': 'form-control'})
        
        # Mark required fields
        required_fields = ['username', 'email', 'first_name', 'last_name', 'role']
        for field_name in required_fields:
            if field_name in self.fields:
                self.fields[field_name].required = True
                self.fields[field_name].widget.attrs.update({'required': True})
        
        # Restrict role choices based on current user permissions
        if self.current_user:
            if self.current_user.role == 'admin':
                # Admins can create all types
                self.fields['role'].choices = User.ROLE_CHOICES
                self.fields['support_level'].choices = User.SUPPORT_LEVEL_CHOICES
            elif self.current_user.role == 'support_agent' and self.current_user.support_level == 4:
                # Level 4 can create customers and support agents level 1-3
                self.fields['role'].choices = [
                    ('customer', 'Customer'),
                    ('support_agent', 'Support Agent')
                ]
                self.fields['support_level'].choices = [
                    (1, 'Level 1 - Basic Support'),
                    (2, 'Level 2 - Technical Support'),
                    (3, 'Level 3 - Expert Support')
                ]
            else:
                # Level 1-3 can only create customers
                self.fields['role'].choices = [('customer', 'Customer')]
                # Remove support_level field for customer-only creation
                if 'support_level' in self.fields:
                    del self.fields['support_level']
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'role', 'support_level',
            'phone', 'department', 'location', 'street', 'postal_code', 'city', 'country'
        ]
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
            'support_level': forms.Select(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'value': 'Deutschland'}),
        }
        labels = {
            'username': 'Benutzername',
            'email': 'E-Mail-Adresse',
            'first_name': 'Vorname',
            'last_name': 'Nachname',
            'role': 'Rolle',
            'support_level': 'Support Level',
            'phone': 'Telefonnummer',
            'department': 'Abteilung',
            'location': 'Standort',
            'street': 'Straße',
            'postal_code': 'Postleitzahl',
            'city': 'Stadt',
            'country': 'Land',
        }
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        
        if not password1:
            raise forms.ValidationError('Passwort ist erforderlich.')
        
        if len(password1) < 8:
            raise forms.ValidationError('Das Passwort muss mindestens 8 Zeichen lang sein.')
        
        # Additional password validation can be added here
        return password1
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if not password2:
            raise forms.ValidationError('Passwort-Bestätigung ist erforderlich.')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Die Passwörter stimmen nicht überein.')
        
        return password2
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        if not username:
            raise forms.ValidationError('Benutzername ist erforderlich.')
        
        # Check if username already exists
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Ein Benutzer mit diesem Benutzernamen existiert bereits.')
        
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        if not email:
            raise forms.ValidationError('E-Mail-Adresse ist erforderlich.')
        
        # Check if email already exists
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Ein Benutzer mit dieser E-Mail-Adresse existiert bereits.')
        
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        support_level = cleaned_data.get('support_level')
        
        # Validate support_level only for support_agent role
        if role == 'support_agent' and not support_level:
            raise forms.ValidationError('Support Level ist erforderlich für Support Agents.')
        elif role != 'support_agent' and support_level:
            cleaned_data['support_level'] = None
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')
        
        # Debug: Check if password is available
        if not password:
            raise ValueError('Passwort nicht verfügbar in cleaned_data')
        
        # Set password
        user.set_password(password)
        user.is_active = True
        
        # Set default role if not specified
        if not user.role:
            user.role = 'customer'
        
        # Ensure required fields are set
        if not user.first_name:
            raise ValueError('Vorname ist erforderlich')
        if not user.last_name:
            raise ValueError('Nachname ist erforderlich')
        if not user.email:
            raise ValueError('E-Mail ist erforderlich')
        if not user.username:
            raise ValueError('Benutzername ist erforderlich')
        
        if commit:
            try:
                user.save()
            except Exception as e:
                raise ValueError(f'Fehler beim Speichern in der Datenbank: {str(e)}')
        return user


class UserEditForm(forms.ModelForm):
    """Form for editing existing users"""
    
    def __init__(self, *args, **kwargs):
        self.current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        
        # Set form field attributes
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Restrict role choices based on current user permissions
        if self.current_user:
            if self.current_user.role == 'admin':
                # Admins can edit all types
                self.fields['role'].choices = User.ROLE_CHOICES
                self.fields['support_level'].choices = User.SUPPORT_LEVEL_CHOICES
            elif self.current_user.role == 'support_agent' and self.current_user.support_level == 4:
                # Level 4 can edit customers and support agents level 1-3
                self.fields['role'].choices = [
                    ('customer', 'Customer'),
                    ('support_agent', 'Support Agent')
                ]
                self.fields['support_level'].choices = [
                    (1, 'Level 1 - Basic Support'),
                    (2, 'Level 2 - Technical Support'),
                    (3, 'Level 3 - Expert Support')
                ]
            else:
                # Level 1-3 can only edit customers
                self.fields['role'].choices = [('customer', 'Customer')]
                # Remove support_level field for customer-only editing
                if 'support_level' in self.fields:
                    del self.fields['support_level']
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 'role', 'support_level',
            'phone', 'department', 'location', 'street', 'postal_code', 'city', 'country',
            'is_active', 'force_password_change'
        ]
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
            'support_level': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'force_password_change': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'username': 'Benutzername',
            'email': 'E-Mail-Adresse',
            'first_name': 'Vorname',
            'last_name': 'Nachname',
            'role': 'Rolle',
            'support_level': 'Support Level',
            'phone': 'Telefonnummer',
            'department': 'Abteilung',
            'location': 'Standort',
            'street': 'Straße',
            'postal_code': 'Postleitzahl',
            'city': 'Stadt',
            'country': 'Land',
            'is_active': 'Aktiv',
            'force_password_change': 'Passwort-Änderung erzwingen',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        support_level = cleaned_data.get('support_level')
        
        # Validate support_level only for support_agent role
        if role == 'support_agent' and not support_level:
            raise forms.ValidationError('Support Level ist erforderlich für Support Agents.')
        elif role != 'support_agent' and support_level:
            cleaned_data['support_level'] = None
        
        return cleaned_data
