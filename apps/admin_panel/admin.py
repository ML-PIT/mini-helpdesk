from django.contrib import admin
from .models import SystemSettings, AuditLog, CustomField, CustomFieldValue


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
        ('License Configuration', {
            'fields': ('license_code', 'license_product', 'license_expiry_date', 'license_max_agents', 'license_features', 'license_valid', 'license_last_validated')
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


@admin.register(CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    """Custom fields management"""
    
    list_display = ['label', 'field_type', 'target_model', 'is_required', 'is_active', 'display_order']
    list_filter = ['field_type', 'target_model', 'is_required', 'is_active']
    search_fields = ['name', 'label']
    ordering = ['target_model', 'display_order', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'label', 'field_type', 'target_model')
        }),
        ('Configuration', {
            'fields': ('is_required', 'default_value', 'help_text', 'choices')
        }),
        ('Display Options', {
            'fields': ('display_order', 'is_visible_in_list', 'is_searchable')
        }),
        ('Permissions', {
            'fields': ('visible_to_customers', 'editable_by_customers')
        }),
        ('Status', {
            'fields': ('is_active',)
        })
    )


@admin.register(CustomFieldValue)
class CustomFieldValueAdmin(admin.ModelAdmin):
    """Custom field values management"""
    
    list_display = ['field', 'object_id', 'value', 'updated_at']
    list_filter = ['field__target_model', 'field']
    search_fields = ['field__label', 'value']
    readonly_fields = ['created_at', 'updated_at']
    
    def has_add_permission(self, request):
        # Values are usually created automatically
        return request.user.is_superuser
