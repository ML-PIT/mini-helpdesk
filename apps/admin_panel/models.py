from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now as timezone_now
import json


class SystemSettings(models.Model):
    """System-wide settings managed through admin panel"""

    # Email Configuration (SMTP)
    smtp_host = models.CharField(_('SMTP Host'), max_length=255, default='smtp.office365.com',
                                help_text='e.g., smtp.office365.com, smtp.gmail.com')
    smtp_port = models.IntegerField(_('SMTP Port'), default=587)
    smtp_username = models.CharField(_('SMTP Username'), max_length=255, blank=True)
    smtp_password = models.CharField(_('SMTP Password'), max_length=255, blank=True)
    smtp_use_tls = models.BooleanField(_('Use TLS'), default=True)
    smtp_use_ssl = models.BooleanField(_('Use SSL'), default=False)

    # IMAP Configuration (for email import)
    imap_enabled = models.BooleanField(_('Enable IMAP'), default=False,
                                      help_text='Enable reading emails from mailbox')
    imap_host = models.CharField(_('IMAP Host'), max_length=255, default='outlook.office365.com',
                                blank=True)
    imap_port = models.IntegerField(_('IMAP Port'), default=993, blank=True)
    imap_username = models.CharField(_('IMAP Username'), max_length=255, blank=True)
    imap_password = models.CharField(_('IMAP Password'), max_length=255, blank=True)
    imap_use_ssl = models.BooleanField(_('Use SSL'), default=True)
    imap_folder = models.CharField(_('IMAP Folder'), max_length=255, default='INBOX',
                                  help_text='Mailbox folder to monitor')

    # Branding Configuration
    logo = models.ImageField(_('Logo'), upload_to='logos/', null=True, blank=True,
                            help_text='Company logo (max 2MB, recommended: 200x50px)')
    app_name = models.CharField(_('Application Name'), max_length=255, default='Helpdesk',
                               help_text='Name shown in navbar and browser tab')
    company_name = models.CharField(_('Company Name'), max_length=255, default='Company',
                                   help_text='Company name for branding')
    site_url = models.URLField(_('Site URL'), default='http://localhost:8000',
                              help_text='Base URL for email links and redirects')

    # Text Editor Configuration
    text_editor = models.CharField(
        _('Text Editor'),
        max_length=20,
        choices=[
            ('tinymce', 'TinyMCE'),
            ('ckeditor', 'CKEditor'),
        ],
        default='tinymce',
        help_text='Choose which rich text editor to use throughout the application'
    )

    # Statistics Access Permissions (JSON storage for flexibility)
    stats_permissions = models.JSONField(
        _('Statistics Permissions'),
        default=dict,
        help_text='Which user roles can access which statistics'
    )

    # File Upload Settings
    max_upload_size_mb = models.IntegerField(_('Max Upload Size (MB)'), default=16,
                                            help_text='Maximum file size allowed for uploads')
    allowed_file_types = models.JSONField(
        _('Allowed File Types'),
        default=list,
        help_text='List of allowed file extensions (e.g., ["pdf", "jpg", "png"])'
    )

    # Email Notification Settings
    send_email_notifications = models.BooleanField(_('Send Email Notifications'), default=True)
    email_signature = models.TextField(_('Email Signature'), blank=True,
                                      help_text='Signature added to all outgoing emails')

    # License Configuration
    license_code = models.CharField(
        _('License Code'),
        max_length=255,
        blank=True,
        null=True,
        help_text='ABoro-Soft Helpdesk License Code (format: PRODUCT-VERSION-DURATION-EXPIRY-SIGNATURE)'
    )
    license_product = models.CharField(
        _('License Product'),
        max_length=50,
        choices=[
            ('STARTER', 'Starter (€199/month - 5 agents)'),
            ('PROFESSIONAL', 'Professional (€499/month - 20 agents)'),
            ('ENTERPRISE', 'Enterprise (€1,299/month - unlimited)'),
            ('ON_PREMISE', 'On-Premise (€10,000 one-time)'),
            ('TRIAL', 'Free Trial (30 days)'),
        ],
        default='TRIAL',
        help_text='Current license type'
    )
    license_expiry_date = models.DateField(
        _('License Expiry Date'),
        null=True,
        blank=True,
        help_text='When the current license expires'
    )
    license_max_agents = models.IntegerField(
        _('License Max Agents'),
        default=5,
        help_text='Maximum number of support agents allowed by license'
    )
    license_features = models.JSONField(
        _('License Features'),
        default=list,
        help_text='List of enabled features for current license'
    )
    license_valid = models.BooleanField(
        _('License Valid'),
        default=False,
        help_text='Indicates if the current license is valid'
    )
    license_last_validated = models.DateTimeField(
        _('License Last Validated'),
        null=True,
        blank=True,
        help_text='When the license was last validated'
    )

    # AI Settings
    ai_enabled = models.BooleanField(
        _('AI Chat Support aktiviert'),
        default=False,
        help_text='KI-gestützte Antworten im Live Chat aktivieren'
    )
    ai_provider = models.CharField(
        _('AI Provider'),
        max_length=20,
        choices=[
            ('chatgpt', 'ChatGPT (OpenAI)'),
            ('claude', 'Claude (Anthropic)'),
        ],
        default='claude',
        help_text='Welche KI für automatische Antworten verwenden'
    )
    openai_api_key = models.CharField(
        _('OpenAI API Key'),
        max_length=255,
        blank=True,
        null=True,
        help_text='API Key für ChatGPT Integration'
    )
    anthropic_api_key = models.CharField(
        _('Anthropic API Key'),
        max_length=255,
        blank=True,
        null=True,
        help_text='API Key für Claude Integration (optional, nutzt sonst Free-Version)'
    )
    ai_response_delay = models.IntegerField(
        _('AI Antwort Verzögerung (Sekunden)'),
        default=3,
        help_text='Wartezeit bevor KI antwortet (um natürlicher zu wirken)'
    )
    ai_max_tokens = models.IntegerField(
        _('AI Max Tokens'),
        default=500,
        help_text='Maximale Länge der KI-Antworten'
    )

    # System Settings
    timezone = models.CharField(_('Timezone'), max_length=100, default='Europe/Berlin')
    language = models.CharField(
        _('Language'),
        max_length=10,
        choices=[
            ('de', 'Deutsch'),
            ('en', 'English'),
        ],
        default='de'
    )

    # Metadata
    created_at = models.DateTimeField(_('Created At'), default=timezone_now)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_settings',
        verbose_name=_('Updated By')
    )

    class Meta:
        verbose_name = _('System Settings')
        verbose_name_plural = _('System Settings')

    def __str__(self):
        return 'System Settings'

    @classmethod
    def get_settings(cls):
        """Get or create default settings"""
        settings_obj, created = cls.objects.get_or_create(id=1)
        return settings_obj

    def get_stats_permissions(self):
        """Get parsed statistics permissions"""
        if isinstance(self.stats_permissions, dict):
            return self.stats_permissions
        try:
            return json.loads(self.stats_permissions) if isinstance(self.stats_permissions, str) else {}
        except:
            return {}

    def set_stats_permissions(self, permissions_dict):
        """Set statistics permissions"""
        self.stats_permissions = permissions_dict

    def get_allowed_extensions(self):
        """Get allowed file extensions"""
        if isinstance(self.allowed_file_types, list):
            return self.allowed_file_types
        try:
            return json.loads(self.allowed_file_types) if isinstance(self.allowed_file_types, str) else []
        except:
            return []


class AuditLog(models.Model):
    """Audit log for settings changes"""

    ACTION_CHOICES = [
        ('created', _('Created')),
        ('updated', _('Updated')),
        ('deleted', _('Deleted')),
        ('email_sent', _('Email Sent')),
        ('file_uploaded', _('File Uploaded')),
    ]

    action = models.CharField(_('Action'), max_length=20, choices=ACTION_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                            null=True, blank=True, related_name='audit_logs')
    content_type = models.CharField(_('Content Type'), max_length=255)
    object_id = models.IntegerField(_('Object ID'), null=True, blank=True)
    description = models.TextField(_('Description'))
    old_values = models.JSONField(_('Old Values'), default=dict, blank=True)
    new_values = models.JSONField(_('New Values'), default=dict, blank=True)
    ip_address = models.GenericIPAddressField(_('IP Address'), null=True, blank=True)
    created_at = models.DateTimeField(_('Created At'), default=timezone_now, db_index=True)

    class Meta:
        verbose_name = _('Audit Log')
        verbose_name_plural = _('Audit Logs')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
        ]

    def __str__(self):
        return f"{self.action} - {self.created_at}"


class CustomField(models.Model):
    """Dynamic custom fields that can be added to models"""
    
    FIELD_TYPES = [
        ('text', _('Text Field')),
        ('textarea', _('Text Area')),
        ('number', _('Number')),
        ('email', _('Email')),
        ('url', _('URL')),
        ('date', _('Date')),
        ('datetime', _('Date & Time')),
        ('boolean', _('Yes/No')),
        ('select', _('Dropdown')),
        ('multiselect', _('Multiple Selection')),
    ]
    
    TARGET_MODELS = [
        ('user', _('User/Customer')),
        ('ticket', _('Ticket')),
        ('company', _('Company/Organization')),
    ]
    
    name = models.CharField(_('Field Name'), max_length=100)
    label = models.CharField(_('Display Label'), max_length=200)
    field_type = models.CharField(_('Field Type'), max_length=20, choices=FIELD_TYPES)
    target_model = models.CharField(_('Target Model'), max_length=20, choices=TARGET_MODELS)
    
    # Field configuration
    is_required = models.BooleanField(_('Required'), default=False)
    default_value = models.TextField(_('Default Value'), blank=True, null=True)
    help_text = models.TextField(_('Help Text'), blank=True, null=True)
    choices = models.TextField(_('Choices (one per line)'), blank=True, null=True,
                              help_text='For dropdown/multiselect fields, enter one option per line')
    
    # Display options
    is_visible_in_list = models.BooleanField(_('Visible in List View'), default=False)
    is_searchable = models.BooleanField(_('Searchable'), default=False)
    display_order = models.IntegerField(_('Display Order'), default=0)
    
    # Permissions
    visible_to_customers = models.BooleanField(_('Visible to Customers'), default=True)
    editable_by_customers = models.BooleanField(_('Editable by Customers'), default=True)
    
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('created at'), default=timezone_now)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Custom Field')
        verbose_name_plural = _('Custom Fields')
        ordering = ['target_model', 'display_order', 'name']
        unique_together = ['name', 'target_model']
    
    def __str__(self):
        return f"{self.get_target_model_display()}: {self.label}"
    
    def get_choices_list(self):
        """Get choices as a list"""
        if self.choices:
            return [choice.strip() for choice in self.choices.split('\n') if choice.strip()]
        return []
    
    def get_form_field(self):
        """Generate Django form field for this custom field"""
        from django import forms
        
        field_kwargs = {
            'label': self.label,
            'required': self.is_required,
            'help_text': self.help_text,
        }
        
        if self.default_value:
            field_kwargs['initial'] = self.default_value
        
        if self.field_type == 'text':
            return forms.CharField(max_length=255, **field_kwargs)
        elif self.field_type == 'textarea':
            return forms.CharField(widget=forms.Textarea, **field_kwargs)
        elif self.field_type == 'number':
            return forms.IntegerField(**field_kwargs)
        elif self.field_type == 'email':
            return forms.EmailField(**field_kwargs)
        elif self.field_type == 'url':
            return forms.URLField(**field_kwargs)
        elif self.field_type == 'date':
            return forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), **field_kwargs)
        elif self.field_type == 'datetime':
            return forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}), **field_kwargs)
        elif self.field_type == 'boolean':
            return forms.BooleanField(**field_kwargs)
        elif self.field_type == 'select':
            choices = [(choice, choice) for choice in self.get_choices_list()]
            return forms.ChoiceField(choices=choices, **field_kwargs)
        elif self.field_type == 'multiselect':
            choices = [(choice, choice) for choice in self.get_choices_list()]
            return forms.MultipleChoiceField(choices=choices, widget=forms.CheckboxSelectMultiple, **field_kwargs)
        
        return forms.CharField(**field_kwargs)


class CustomFieldValue(models.Model):
    """Values for custom fields"""
    
    field = models.ForeignKey(CustomField, on_delete=models.CASCADE, related_name='values')
    object_id = models.PositiveIntegerField(_('Object ID'))  # ID of the target object (user, ticket, etc.)
    value = models.TextField(_('Value'), blank=True, null=True)
    
    created_at = models.DateTimeField(_('created at'), default=timezone_now)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Custom Field Value')
        verbose_name_plural = _('Custom Field Values')
        unique_together = ['field', 'object_id']
    
    def __str__(self):
        return f"{self.field.label}: {self.value}"
    
    def get_formatted_value(self):
        """Get value formatted according to field type"""
        if not self.value:
            return None
        
        if self.field.field_type == 'boolean':
            return self.value.lower() in ['true', '1', 'yes', 'on']
        elif self.field.field_type == 'number':
            try:
                return int(self.value)
            except ValueError:
                return None
        elif self.field.field_type == 'multiselect':
            try:
                return json.loads(self.value) if self.value.startswith('[') else [self.value]
            except (json.JSONDecodeError, AttributeError):
                return [self.value]
        
        return self.value
