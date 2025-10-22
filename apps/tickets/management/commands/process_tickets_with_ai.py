"""
Management command to process open tickets with Claude AI assistant.
Run with: python manage.py process_tickets_with_ai

Can be scheduled with cron or celery to run periodically (e.g., every 30 minutes after 15:30)
"""
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.tickets.models import Ticket
from apps.tickets.claude_service import claude_assistant

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Django management command for processing tickets with Claude AI"""

    help = 'Process open tickets with Claude AI and generate automatic responses for simple problems'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force processing even outside of 15:30-23:59 window',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Limit number of tickets to process (default: 10)',
        )
        parser.add_argument(
            '--status',
            type=str,
            default='open',
            help='Ticket status to process (default: open)',
        )

    def handle(self, *args, **options):
        """Execute the command"""
        force = options['force']
        limit = options['limit']
        status = options['status']

        self.stdout.write(
            self.style.SUCCESS(
                f'Processing up to {limit} {status} tickets with Claude AI...'
            )
        )

        # Check if auto-response is enabled
        if not force and not claude_assistant.can_auto_respond():
            self.stdout.write(
                self.style.WARNING(
                    'Auto-response is only available after 15:30. Use --force to override.'
                )
            )
            if not force:
                return

        # Get open tickets without AI responses
        tickets = Ticket.objects.filter(
            status=status,
            notes__exact=''  # No notes yet
        ).order_by('-created_at')[:limit]

        if not tickets.exists():
            self.stdout.write(
                self.style.WARNING('No open tickets without responses found.')
            )
            return

        processed = 0
        skipped = 0
        errors = 0

        for ticket in tickets:
            try:
                success = claude_assistant.process_ticket(ticket)

                if success:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Ticket #{ticket.id} ({ticket.title[:40]}) processed successfully'
                        )
                    )
                    processed += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⊘ Ticket #{ticket.id} ({ticket.title[:40]}) skipped (complex issue)'
                        )
                    )
                    skipped += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Error processing ticket #{ticket.id}: {str(e)}'
                    )
                )
                logger.exception(f"Error processing ticket {ticket.id}")
                errors += 1

        # Summary
        self.stdout.write(
            self.style.SUCCESS('\n' + '=' * 60)
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Summary: {processed} processed, {skipped} skipped, {errors} errors'
            )
        )

        if processed > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Customers notified: {processed} automatic responses sent'
                )
            )
