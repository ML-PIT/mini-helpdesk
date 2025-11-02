from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class ChatSession(models.Model):
    """A chat session between a visitor and support"""
    
    # Visitor Information
    visitor_name = models.CharField(max_length=100)
    visitor_email = models.EmailField()
    visitor_ip = models.GenericIPAddressField()
    
    # Session details
    session_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # Assignment
    assigned_agent = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='chat_sessions'
    )
    
    # Status
    STATUS_CHOICES = [
        ('waiting', 'Waiting for Agent'),
        ('active', 'Active Chat'),
        ('escalated', 'Escalated to Agent'),
        ('ended', 'Chat Ended'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    
    # Additional info
    initial_message = models.TextField(help_text="Visitor's first message")
    visitor_page_url = models.URLField(null=True, blank=True, help_text="Page where chat was initiated")
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Chat {self.session_id} - {self.visitor_name}"
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    @property
    def duration(self):
        if self.ended_at:
            return self.ended_at - self.created_at
        return timezone.now() - self.created_at


class ChatMessage(models.Model):
    """Individual messages in a chat session"""
    
    session = models.ForeignKey(
        ChatSession, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    
    # Message content
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    
    # Sender information
    is_from_visitor = models.BooleanField(default=True)
    sender_name = models.CharField(max_length=100)
    agent = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="If message is from agent"
    )
    
    # Message type
    MESSAGE_TYPES = [
        ('text', 'Text Message'),
        ('system', 'System Message'),
        ('file', 'File Upload'),
    ]
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    
    class Meta:
        ordering = ['timestamp']
        
    def __str__(self):
        sender = self.sender_name if self.is_from_visitor else f"Agent: {self.sender_name}"
        return f"{sender}: {self.message[:50]}..."


class ChatSettings(models.Model):
    """Global chat settings"""
    
    # Widget appearance
    widget_color = models.CharField(max_length=7, default='#667eea', help_text="Hex color code")
    widget_position = models.CharField(
        max_length=20, 
        choices=[('bottom-right', 'Bottom Right'), ('bottom-left', 'Bottom Left')],
        default='bottom-right'
    )
    
    # Behavior
    auto_assign = models.BooleanField(default=True, help_text="Automatically assign chats to available agents")
    offline_message = models.TextField(
        default="Wir sind derzeit offline. Senden Sie uns eine E-Mail und wir melden uns so schnell wie möglich.",
        help_text="Message shown when no agents are available"
    )
    welcome_message = models.TextField(
        default="Hallo! Wie können wir Ihnen helfen?",
        help_text="First message shown to visitors"
    )
    
    # Availability
    is_enabled = models.BooleanField(default=True)
    business_hours_only = models.BooleanField(default=False)
    business_start = models.TimeField(default='09:00')
    business_end = models.TimeField(default='17:00')
    
    class Meta:
        verbose_name = "Chat Settings"
        verbose_name_plural = "Chat Settings"
    
    def save(self, *args, **kwargs):
        # Ensure only one settings object exists
        if not self.pk and ChatSettings.objects.exists():
            raise ValueError("Only one ChatSettings instance is allowed")
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        settings, created = cls.objects.get_or_create(pk=1)
        return settings