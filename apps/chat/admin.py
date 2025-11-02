from django.contrib import admin
from .models import ChatSession, ChatMessage, ChatSettings


@admin.register(ChatSettings)
class ChatSettingsAdmin(admin.ModelAdmin):
    list_display = ('is_enabled', 'widget_color', 'widget_position', 'auto_assign')
    fieldsets = (
        ('Widget Appearance', {
            'fields': ('widget_color', 'widget_position')
        }),
        ('Messages', {
            'fields': ('welcome_message', 'offline_message')
        }),
        ('Behavior', {
            'fields': ('is_enabled', 'auto_assign')
        }),
        ('Business Hours', {
            'fields': ('business_hours_only', 'business_start', 'business_end')
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one settings object
        return not ChatSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('timestamp', 'sender_name', 'is_from_visitor')
    fields = ('timestamp', 'sender_name', 'message', 'is_from_visitor', 'message_type')


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'visitor_name', 'visitor_email', 'status', 'assigned_agent', 'created_at')
    list_filter = ('status', 'created_at', 'assigned_agent')
    search_fields = ('visitor_name', 'visitor_email', 'session_id')
    readonly_fields = ('session_id', 'visitor_ip', 'created_at', 'duration')
    
    fieldsets = (
        ('Visitor Information', {
            'fields': ('visitor_name', 'visitor_email', 'visitor_ip', 'visitor_page_url')
        }),
        ('Session Details', {
            'fields': ('session_id', 'status', 'assigned_agent', 'created_at', 'ended_at')
        }),
        ('Initial Request', {
            'fields': ('initial_message',)
        }),
    )
    
    inlines = [ChatMessageInline]
    
    def duration(self, obj):
        return obj.duration
    duration.short_description = 'Duration'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'sender_name', 'timestamp', 'is_from_visitor', 'message_type')
    list_filter = ('is_from_visitor', 'message_type', 'timestamp')
    search_fields = ('message', 'sender_name', 'session__visitor_name')
    readonly_fields = ('timestamp',)