from django import forms
from django.core.exceptions import ValidationError
from .models import SystemSettings
from apps.api.license_manager import LicenseManager
from datetime import datetime
import json


class SystemSettingsForm(forms.ModelForm):
    """Form for managing system settings"""

    # SMTP Fields
    smtp_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter SMTP password (leave blank to keep current)'
        })
    )

    # IMAP Fields
    imap_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter IMAP password (leave blank to keep current)'
        })
    )

    # Statistics Permissions
    can_admin_view_stats = forms.BooleanField(
        required=False,
        label='Admin - Can View All Statistics',
        initial=True
    )
    can_agent_view_stats = forms.BooleanField(
        required=False,
        label='Support Agent - Can View Statistics',
        initial=False
    )
    can_customer_view_stats = forms.BooleanField(
        required=False,
        label='Customer - Can View Own Statistics',
        initial=False
    )

    # File Types
    file_types_pdf = forms.BooleanField(required=False, label='PDF', initial=True)
    file_types_jpg = forms.BooleanField(required=False, label='JPG/JPEG', initial=True)
    file_types_png = forms.BooleanField(required=False, label='PNG', initial=True)
    file_types_gif = forms.BooleanField(required=False, label='GIF', initial=True)
    file_types_doc = forms.BooleanField(required=False, label='DOC/DOCX', initial=True)
    file_types_zip = forms.BooleanField(required=False, label='ZIP', initial=True)

    class Meta:
        model = SystemSettings
        fields = [
            'smtp_host', 'smtp_port', 'smtp_username', 'smtp_password', 'smtp_use_tls', 'smtp_use_ssl',
            'imap_enabled', 'imap_host', 'imap_port', 'imap_username', 'imap_password', 'imap_use_ssl', 'imap_folder',
            'logo', 'app_name', 'company_name', 'site_url',
            'text_editor',
            'max_upload_size_mb',
            'send_email_notifications', 'email_signature',
            'timezone', 'language'
        ]

        widgets = {
            'smtp_host': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., smtp.office365.com'}),
            'smtp_port': forms.NumberInput(attrs={'class': 'form-control'}),
            'smtp_username': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'SMTP account email'}),
            'smtp_use_tls': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'smtp_use_ssl': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

            'imap_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'imap_host': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., outlook.office365.com'}),
            'imap_port': forms.NumberInput(attrs={'class': 'form-control'}),
            'imap_username': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'IMAP account email'}),
            'imap_use_ssl': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'imap_folder': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'INBOX'}),

            'logo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'app_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'site_url': forms.URLInput(attrs={'class': 'form-control'}),

            'text_editor': forms.RadioSelect(attrs={'class': 'form-check-input'}),

            'max_upload_size_mb': forms.NumberInput(attrs={'class': 'form-control'}),

            'send_email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_signature': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Email signature text'
            }),

            'timezone': forms.TextInput(attrs={'class': 'form-control'}),
            'language': forms.RadioSelect(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Load existing permissions
        if self.instance and self.instance.pk:
            stats_perms = self.instance.get_stats_permissions()
            self.fields['can_admin_view_stats'].initial = stats_perms.get('admin', True)
            self.fields['can_agent_view_stats'].initial = stats_perms.get('support_agent', False)
            self.fields['can_customer_view_stats'].initial = stats_perms.get('customer', False)

            # Load file types
            allowed_types = self.instance.get_allowed_extensions()
            self.fields['file_types_pdf'].initial = 'pdf' in allowed_types
            self.fields['file_types_jpg'].initial = any(x in allowed_types for x in ['jpg', 'jpeg'])
            self.fields['file_types_png'].initial = 'png' in allowed_types
            self.fields['file_types_gif'].initial = 'gif' in allowed_types
            self.fields['file_types_doc'].initial = any(x in allowed_types for x in ['doc', 'docx'])
            self.fields['file_types_zip'].initial = 'zip' in allowed_types

        # Add CSS classes to all form fields
        for field in self.fields:
            if field not in ['smtp_use_tls', 'smtp_use_ssl', 'imap_enabled', 'imap_use_ssl',
                           'send_email_notifications', 'can_admin_view_stats', 'can_agent_view_stats',
                           'can_customer_view_stats', 'file_types_pdf', 'file_types_jpg',
                           'file_types_png', 'file_types_gif', 'file_types_doc', 'file_types_zip',
                           'text_editor', 'language']:
                if self.fields[field].widget.__class__.__name__ not in ['CheckboxInput', 'RadioSelect']:
                    self.fields[field].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()

        # Validate SMTP settings if they have values
        smtp_host = cleaned_data.get('smtp_host')
        smtp_port = cleaned_data.get('smtp_port')

        if smtp_host:
            if not (1 <= smtp_port <= 65535):
                raise ValidationError('SMTP Port must be between 1 and 65535')

        # Validate IMAP settings
        imap_enabled = cleaned_data.get('imap_enabled')
        if imap_enabled:
            imap_host = cleaned_data.get('imap_host')
            imap_port = cleaned_data.get('imap_port')

            if not imap_host:
                raise ValidationError('IMAP Host is required when IMAP is enabled')
            if not (1 <= imap_port <= 65535):
                raise ValidationError('IMAP Port must be between 1 and 65535')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Save statistics permissions
        stats_perms = {
            'admin': self.cleaned_data.get('can_admin_view_stats', True),
            'support_agent': self.cleaned_data.get('can_agent_view_stats', False),
            'customer': self.cleaned_data.get('can_customer_view_stats', False),
        }
        instance.set_stats_permissions(stats_perms)

        # Save allowed file types
        allowed_types = []
        if self.cleaned_data.get('file_types_pdf'):
            allowed_types.append('pdf')
        if self.cleaned_data.get('file_types_jpg'):
            allowed_types.extend(['jpg', 'jpeg'])
        if self.cleaned_data.get('file_types_png'):
            allowed_types.append('png')
        if self.cleaned_data.get('file_types_gif'):
            allowed_types.append('gif')
        if self.cleaned_data.get('file_types_doc'):
            allowed_types.extend(['doc', 'docx'])
        if self.cleaned_data.get('file_types_zip'):
            allowed_types.append('zip')
        instance.allowed_file_types = allowed_types

        if commit:
            instance.save()

        return instance


class TestEmailForm(forms.Form):
    """Form for testing email configuration"""

    test_email = forms.EmailField(
        label='Test Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'recipient@example.com'
        })
    )

    def clean_test_email(self):
        email = self.cleaned_data['test_email']
        if not email:
            raise ValidationError('Please provide a test email address')
        return email


class TestIMAPForm(forms.Form):
    """Form for testing IMAP configuration"""

    test_action = forms.ChoiceField(
        choices=[
            ('test_connection', 'Test Connection Only'),
            ('fetch_emails', 'Test Connection & Fetch Last 5 Emails'),
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='test_connection'
    )


class LicenseForm(forms.Form):
    """Form for managing license code"""

    license_code = forms.CharField(
        label='License Code',
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., STARTER-1-12-20261031-038357A3F9C143BA',
            'autocomplete': 'off'
        }),
        help_text='Enter your ABoro-Soft Helpdesk license code'
    )

    def clean_license_code(self):
        """Validate license code"""
        license_code = self.cleaned_data['license_code'].strip()

        if not license_code:
            raise ValidationError('License code is required')

        # Validate license using LicenseManager
        is_valid, error_msg = LicenseManager.validate_license(license_code)

        if not is_valid:
            raise ValidationError(f'Invalid license code: {error_msg}')

        return license_code

    def get_license_info(self):
        """Get license information"""
        if 'license_code' in self.cleaned_data:
            license_code = self.cleaned_data['license_code']
            return LicenseManager.get_license_info(license_code)
        return None
