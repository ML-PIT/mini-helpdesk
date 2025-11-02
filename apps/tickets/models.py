from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import random
import base64


# Mobile classroom models removed - not needed for this project


class Category(models.Model):
    """Ticket categories for organization"""

    name = models.CharField(_('name'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    color = models.CharField(_('color'), max_length=7, default='#2fb2bf',
                            help_text='Hex color code')
    is_active = models.BooleanField(_('active'), default=True)
    auto_assign_to = models.ForeignKey(settings.AUTH_USER_MODEL,
                                       on_delete=models.SET_NULL,
                                       null=True, blank=True,
                                       related_name='assigned_categories',
                                       verbose_name=_('auto assign to'))
    created_at = models.DateTimeField(_('created at'), default=timezone.now)

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ['name']

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'is_active': self.is_active,
            'auto_assign_to': self.auto_assign_to.to_dict() if self.auto_assign_to else None
        }


class Ticket(models.Model):
    """Main ticket model"""

    STATUS_CHOICES = [
        ('open', _('Open')),
        ('in_progress', _('In Progress')),
        ('pending', _('Pending')),
        ('resolved', _('Resolved')),
        ('closed', _('Closed')),
    ]

    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('critical', _('Critical')),
    ]

    SUPPORT_LEVEL_CHOICES = [
        ('level_1', _('Level 1 - First Line Support')),
        ('level_2', _('Level 2 - Technical Support')),
        ('level_3', _('Level 3 - Expert Support')),
        ('level_4', _('Level 4 - Senior Expert')),
    ]

    # Basic information
    ticket_number = models.CharField(_('ticket number'), max_length=20, unique=True,
                                    db_index=True, editable=False)
    title = models.CharField(_('title'), max_length=200)
    description = models.TextField(_('description'))

    # Relationships
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  on_delete=models.PROTECT,
                                  related_name='created_tickets',
                                  verbose_name=_('created by'),
                                  db_index=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.SET_NULL,
                                   null=True, blank=True,
                                   related_name='assigned_tickets',
                                   verbose_name=_('assigned to'),
                                   db_index=True)
    category = models.ForeignKey(Category,
                                on_delete=models.SET_NULL,
                                null=True, blank=True,
                                related_name='tickets',
                                verbose_name=_('category'),
                                db_index=True)
    # Mobile classroom field removed - not needed

    # Status and priority
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES,
                            default='open', db_index=True)
    priority = models.CharField(_('priority'), max_length=20, choices=PRIORITY_CHOICES,
                              default='medium', db_index=True)

    # Support Level (for escalation)
    support_level = models.CharField(_('support level'), max_length=10,
                                    choices=SUPPORT_LEVEL_CHOICES,
                                    default='level_1', db_index=True)

    # Time tracking for SLA
    created_at = models.DateTimeField(_('created at'), default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    first_response_at = models.DateTimeField(_('first response at'), null=True, blank=True)
    resolved_at = models.DateTimeField(_('resolved at'), null=True, blank=True)
    closed_at = models.DateTimeField(_('closed at'), null=True, blank=True)

    # SLA tracking
    sla_due_date = models.DateTimeField(_('SLA due date'), null=True, blank=True,
                                       db_index=True)
    sla_breached = models.BooleanField(_('SLA breached'), default=False, db_index=True)

    # Email integration
    email_thread_id = models.CharField(_('email thread ID'), max_length=255,
                                      null=True, blank=True)

    # Customer satisfaction
    rating = models.IntegerField(_('rating'), null=True, blank=True,
                                help_text='1-5 stars')
    feedback = models.TextField(_('feedback'), null=True, blank=True)

    class Meta:
        verbose_name = _('ticket')
        verbose_name_plural = _('tickets')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.ticket_number} - {self.title}'

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = self.generate_ticket_number()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_ticket_number():
        """Generate unique ticket number"""
        from datetime import datetime
        while True:
            number = f"TK-{datetime.now().year}-{random.randint(10000, 99999)}"
            if not Ticket.objects.filter(ticket_number=number).exists():
                return number

    def set_priority_based_sla(self):
        """Set SLA due date based on priority"""
        from datetime import timedelta

        sla_hours = {
            'critical': 4,
            'high': 24,
            'medium': 72,
            'low': 168  # 1 week
        }

        hours = sla_hours.get(self.priority, 72)
        self.sla_due_date = self.created_at + timedelta(hours=hours)

    def check_sla_breach(self):
        """Check if SLA has been breached"""
        if self.sla_due_date and self.status not in ['resolved', 'closed']:
            if timezone.now() > self.sla_due_date:
                self.sla_breached = True
                return True
        return False

    def get_response_time(self):
        """Get time to first response in hours"""
        if self.first_response_at:
            delta = self.first_response_at - self.created_at
            return delta.total_seconds() / 3600
        return None

    def get_resolution_time(self):
        """Get time to resolution in hours"""
        if self.resolved_at:
            delta = self.resolved_at - self.created_at
            return delta.total_seconds() / 3600
        return None

    def get_processing_time_hours(self):
        """Get total processing time in hours (from creation to closure/resolution)"""
        end_time = self.closed_at or self.resolved_at
        if end_time:
            delta = end_time - self.created_at
            return delta.total_seconds() / 3600
        return None

    def get_processing_time_display(self):
        """Get processing time in human-readable format (e.g., '2 days, 3 hours')"""
        processing_hours = self.get_processing_time_hours()
        if processing_hours is None:
            return 'N/A'

        days = int(processing_hours // 24)
        hours = int(processing_hours % 24)
        minutes = int((processing_hours % 1) * 60)

        parts = []
        if days > 0:
            parts.append(f"{days} {'Tag' if days == 1 else 'Tage'}")
        if hours > 0:
            parts.append(f"{hours} {'Stunde' if hours == 1 else 'Stunden'}")
        if minutes > 0 and days == 0:
            parts.append(f"{minutes} {'Minute' if minutes == 1 else 'Minuten'}")

        return ', '.join(parts) if parts else '< 1 Minute'

    def get_history_as_text(self):
        """Generate complete ticket history as formatted text for email export"""
        lines = []
        lines.append("=" * 70)
        lines.append(f"TICKET {self.ticket_number}")
        lines.append("=" * 70)
        lines.append(f"Titel: {self.title}")
        lines.append(f"Status: {self.get_status_display()}")
        lines.append(f"Priorität: {self.get_priority_display()}")
        lines.append(f"Support Level: {self.get_support_level_display()}")
        lines.append(f"Kategorie: {self.category.name if self.category else 'Keine'}")
        lines.append(f"Erstellt am: {self.created_at.strftime('%d.%m.%Y %H:%M')}")
        lines.append(f"Erstellt von: {self.created_by.full_name} ({self.created_by.email})")
        if self.assigned_to:
            lines.append(f"Zugewiesen an: {self.assigned_to.full_name}")
        if self.closed_at:
            lines.append(f"Geschlossen am: {self.closed_at.strftime('%d.%m.%Y %H:%M')}")
        lines.append("")
        lines.append("-" * 70)
        lines.append("BESCHREIBUNG")
        lines.append("-" * 70)
        lines.append(self.description)
        lines.append("")

        # Get all non-internal comments
        comments = self.comments.filter(is_internal=False).order_by('created_at')
        if comments.exists():
            lines.append("-" * 70)
            lines.append("VERLAUF")
            lines.append("-" * 70)
            for comment in comments:
                lines.append("")
                lines.append(f"[{comment.created_at.strftime('%d.%m.%Y %H:%M')}] {comment.author.full_name}:")
                lines.append(comment.content)

        lines.append("")
        lines.append("=" * 70)
        if self.rating:
            lines.append(f"Bewertung: {'⭐' * self.rating}")
            if self.feedback:
                lines.append(f"Feedback: {self.feedback}")
        lines.append("")
        lines.append("Vielen Dank für Ihre Anfrage!")
        lines.append("Mit freundlichen Grüßen")
        lines.append("Ihr Support-Team")

        return "\n".join(lines)

    def to_dict(self, include_details=False):
        """Convert ticket to dictionary for API responses"""
        data = {
            'id': self.id,
            'ticket_number': self.ticket_number,
            'title': self.title,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'creator': self.created_by.to_dict() if self.created_by else None,
            'assignee': self.assigned_to.to_dict() if self.assigned_to else None,
            'category': self.category.name if self.category else None,
            # Mobile classroom references removed
            'sla_due_date': self.sla_due_date.isoformat() if self.sla_due_date else None,
            'sla_breached': self.sla_breached
        }

        if include_details:
            data.update({
                'description': self.description,
                'first_response_at': self.first_response_at.isoformat() if self.first_response_at else None,
                'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
                'rating': self.rating,
                'feedback': self.feedback,
                'comments': [comment.to_dict() for comment in self.comments.all().order_by('created_at')],
                'attachments': [att.to_dict() for att in self.attachments.all()]
            })

        return data


class TicketComment(models.Model):
    """Comments on tickets"""

    ticket = models.ForeignKey(Ticket,
                              on_delete=models.CASCADE,
                              related_name='comments',
                              verbose_name=_('ticket'),
                              db_index=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.PROTECT,
                              related_name='ticket_comments',
                              verbose_name=_('author'),
                              db_index=True)
    content = models.TextField(_('content'))
    is_internal = models.BooleanField(_('internal note'), default=False,
                                     help_text='Internal notes are not visible to customers')
    email_message_id = models.CharField(_('email message ID'), max_length=255,
                                       null=True, blank=True)
    created_at = models.DateTimeField(_('created at'), default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('ticket comment')
        verbose_name_plural = _('ticket comments')
        ordering = ['created_at']

    def __str__(self):
        return f'Comment on {self.ticket.ticket_number} by {self.author.username}'

    def save(self, *args, **kwargs):
        # Set first response time if this is the first agent response
        if not self.ticket.first_response_at and not self.is_internal:
            if self.author.role in ['support_agent', 'admin']:
                self.ticket.first_response_at = timezone.now()
                self.ticket.save(update_fields=['first_response_at'])
        super().save(*args, **kwargs)

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'is_internal': self.is_internal,
            'author': self.author.to_dict(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class TicketAttachment(models.Model):
    """File attachments for tickets"""

    ticket = models.ForeignKey(Ticket,
                              on_delete=models.CASCADE,
                              related_name='attachments',
                              verbose_name=_('ticket'),
                              db_index=True)
    filename = models.CharField(_('filename'), max_length=255)
    file = models.FileField(_('file'), upload_to='ticket_attachments/%Y/%m/%d/')
    content_type = models.CharField(_('content type'), max_length=100)
    size = models.IntegerField(_('size'))
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.PROTECT,
                                   related_name='uploaded_attachments',
                                   verbose_name=_('uploaded by'))
    uploaded_at = models.DateTimeField(_('uploaded at'), default=timezone.now)

    class Meta:
        verbose_name = _('ticket attachment')
        verbose_name_plural = _('ticket attachments')
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.filename} on {self.ticket.ticket_number}'

    def to_dict(self, include_content=False):
        data = {
            'id': self.id,
            'filename': self.filename,
            'content_type': self.content_type,
            'size': self.size,
            'uploaded_by': self.uploaded_by.to_dict(),
            'uploaded_at': self.uploaded_at.isoformat(),
            'url': self.file.url if self.file else None
        }

        return data
