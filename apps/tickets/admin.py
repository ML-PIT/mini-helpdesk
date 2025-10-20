from django.contrib import admin
from .models import Ticket, TicketComment, TicketAttachment, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Category admin"""
    list_display = ['name', 'color', 'is_active', 'auto_assign_to', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']


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
    """Ticket admin"""
    list_display = ['ticket_number', 'title', 'status', 'priority', 'created_by',
                   'assigned_to', 'category', 'sla_breached', 'created_at']
    list_filter = ['status', 'priority', 'category', 'sla_breached', 'created_at']
    search_fields = ['ticket_number', 'title', 'description']
    date_hierarchy = 'created_at'
    inlines = [TicketCommentInline, TicketAttachmentInline]

    fieldsets = (
        ('Ticket Information', {
            'fields': ('ticket_number', 'title', 'description')
        }),
        ('Assignment', {
            'fields': ('created_by', 'assigned_to', 'category')
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


@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    """Ticket comment admin"""
    list_display = ['ticket', 'author', 'is_internal', 'created_at']
    list_filter = ['is_internal', 'created_at']
    search_fields = ['content', 'ticket__ticket_number']
    date_hierarchy = 'created_at'
