from django.contrib import admin
from .models import SystemSettings, AuditLog


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    """Admin interface for System Settings"""
    list_display = ['app_name', 'company_name', 'text_editor', 'updated_at']
    readonly_fields = ['created_at', 'updated_at', 'updated_by']

    fieldsets = (
        ('Branding', {
            'fields': ('logo', 'app_name', 'company_name', 'site_url')
        }),
        ('SMTP Configuration', {
            'fields': ('smtp_host', 'smtp_port', 'smtp_username', 'smtp_password', 'smtp_use_tls', 'smtp_use_ssl')
        }),
        ('IMAP Configuration', {
            'fields': ('imap_enabled', 'imap_host', 'imap_port', 'imap_username', 'imap_password', 'imap_use_ssl', 'imap_folder')
        }),
        ('Text Editor', {
            'fields': ('text_editor',)
        }),
        ('Email Notifications', {
            'fields': ('send_email_notifications', 'email_signature')
        }),
        ('File Upload Settings', {
            'fields': ('max_upload_size_mb', 'allowed_file_types')
        }),
        ('System', {
            'fields': ('timezone', 'language')
        }),
        ('Statistics Permissions', {
            'fields': ('stats_permissions',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'updated_by'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        """Set the updated_by field"""
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin interface for Audit Logs"""
    list_display = ['action', 'user', 'content_type', 'created_at']
    list_filter = ['action', 'created_at', 'user']
    search_fields = ['description', 'user__username', 'ip_address']
    readonly_fields = ['action', 'user', 'content_type', 'object_id', 'description', 'old_values', 'new_values', 'ip_address', 'created_at']
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        """Disable adding audit logs manually"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disable deleting audit logs"""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable editing audit logs"""
        return False
