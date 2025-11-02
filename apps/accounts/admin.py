from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom user admin - Only accessible to Admins"""

    list_display = ['username', 'email', 'full_name', 'role', 'support_level', 'is_active', 'created_at']
    list_filter = ['role', 'support_level', 'is_active', 'is_staff', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone', 'department', 'location')}),
        (_('Address'), {'fields': ('street', 'postal_code', 'city', 'country')}),
        (_('Permissions'), {
            'fields': ('role', 'support_level', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Microsoft OAuth'), {'fields': ('microsoft_id', 'microsoft_token')}),
        (_('Important dates'), {'fields': ('last_login', 'created_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'role', 'support_level'),
        }),
    )

    readonly_fields = ['created_at', 'last_login']

    def has_module_permission(self, request):
        """Only admins can access user management"""
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role == 'admin')

    def has_view_permission(self, request, obj=None):
        """Only admins can view users"""
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role == 'admin')

    def has_change_permission(self, request, obj=None):
        """Only admins can change users"""
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role == 'admin')

    def has_add_permission(self, request):
        """Only admins can add users"""
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role == 'admin')

    def has_delete_permission(self, request, obj=None):
        """Only admins can delete users"""
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role == 'admin')
