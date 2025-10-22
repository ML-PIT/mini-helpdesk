"""
Django signals for Ticket model.
Automatically processes new tickets with Claude AI if conditions are met.
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Ticket
from .claude_service import claude_assistant

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Ticket)
def process_ticket_with_ai(sender, instance, created, **kwargs):
    """
    Signal handler to process new tickets with Claude AI.
    Only processes if:
    1. It's after 15:30
    2. Ticket is created (not updated)
    3. Ticket has no notes yet
    """
    if not created:
        # Only process newly created tickets
        return

    try:
        # Process ticket asynchronously would be better,
        # but for now we process synchronously
        if claude_assistant.can_auto_respond() and not instance.notes:
            logger.info(f"Processing new ticket #{instance.id} with Claude AI")
            claude_assistant.process_ticket(instance)
    except Exception as e:
        logger.error(f"Error processing ticket {instance.id} with Claude: {str(e)}")
        # Don't raise exception - let ticket creation continue


def ready(self):
    """
    App config ready method to register signals.
    Called from apps.py
    """
    import apps.tickets.signals  # noqa
