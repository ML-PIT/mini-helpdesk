from django.contrib import admin
from .models import Ticket, TicketComment, TicketAttachment, Category, MobileClassroom, MobileClassroomLocation


@admin.register(MobileClassroomLocation)
class MobileClassroomLocationAdmin(admin.ModelAdmin):
    """Mobile Classroom Location admin"""
    list_display = ['name', 'city', 'created_at']
    list_filter = ['created_at', 'city']
    search_fields = ['name', 'address', 'city']

    def has_module_permission(self, request):
        """Only admins can access location management"""
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role == 'admin')


@admin.register(MobileClassroom)
class MobileClassroomAdmin(admin.ModelAdmin):
    """Mobile Classroom admin"""
    list_display = ['name', 'location', 'equipment_type', 'is_active', 'created_at']
    list_filter = ['is_active', 'location', 'equipment_type', 'created_at']
    search_fields = ['name', 'serial_number', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'equipment_type')
        }),
        ('Location', {
            'fields': ('location', 'serial_number')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_module_permission(self, request):
        """Only admins can access classroom management"""
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role == 'admin')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Category admin - Only accessible to Admins"""
    list_display = ['name', 'color', 'is_active', 'auto_assign_to', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']

    def has_module_permission(self, request):
        """Only admins can access category management"""
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role == 'admin')


class TicketCommentInline(admin.TabularInline):
    """Inline comments for tickets"""
    model = TicketComment
    extra = 0
    fields = ['author', 'content', 'is_internal', 'created_at']
    readonly_fields = ['created_at']


class TicketAttachmentInline(admin.TabularInline):
    """Inline attachments for tickets"""
    model = TicketAttachment
    extra = 0
    fields = ['filename', 'file', 'uploaded_by', 'uploaded_at']
    readonly_fields = ['uploaded_at']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    """Ticket admin - Only accessible to Admins"""
    list_display = ['ticket_number', 'title', 'status', 'priority', 'support_level', 'created_by',
                   'assigned_to', 'category', 'mobile_classroom', 'sla_breached', 'created_at']
    list_filter = ['status', 'priority', 'support_level', 'category', 'mobile_classroom', 'sla_breached', 'created_at']
    search_fields = ['ticket_number', 'title', 'description']
    date_hierarchy = 'created_at'
    inlines = [TicketCommentInline, TicketAttachmentInline]

    fieldsets = (
        ('Ticket Information', {
            'fields': ('ticket_number', 'title', 'description')
        }),
        ('Assignment', {
            'fields': ('created_by', 'assigned_to', 'category', 'support_level', 'mobile_classroom')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority')
        }),
        ('SLA', {
            'fields': ('sla_due_date', 'sla_breached')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'first_response_at', 'resolved_at', 'closed_at')
        }),
        ('Customer Satisfaction', {
            'fields': ('rating', 'feedback'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['ticket_number', 'created_at', 'updated_at']

    def has_module_permission(self, request):
        """Only admins can access ticket management in admin"""
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role == 'admin')


@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    """Ticket comment admin - Only accessible to Admins"""
    list_display = ['ticket', 'author', 'is_internal', 'created_at']
    list_filter = ['is_internal', 'created_at']
    search_fields = ['content', 'ticket__ticket_number']
    date_hierarchy = 'created_at'

    def has_module_permission(self, request):
        """Only admins can access comment management in admin"""
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role == 'admin')
