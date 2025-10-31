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
