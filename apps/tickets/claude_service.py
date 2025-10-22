"""
Claude AI Service for automatic ticket responses.
Handles simple technical support questions after 15:30.
"""
import os
import logging
from datetime import datetime
from anthropic import Anthropic
from django.conf import settings

logger = logging.getLogger(__name__)


class ClaudeTicketAssistant:
    """AI assistant for handling simple technical support tickets"""

    # Problem categories that Claude can handle
    SIMPLE_PROBLEMS = [
        'password_reset',
        'login_issues',
        'email_not_working',
        'connection_problem',
        'installation_help',
        'basic_setup',
        'documentation_question',
        'account_unlock',
        'license_activation',
        'software_restart',
    ]

    # Problems that require human support
    COMPLEX_PROBLEMS = [
        'hardware_failure',
        'data_loss',
        'security_breach',
        'system_crash',
        'database_corruption',
        'custom_development',
        'billing_dispute',
        'emergency_critical',
    ]

    SUPPORT_HOURS_START = 7  # 7:00 AM
    AUTO_RESPONSE_START = 15  # 15:30 (3:30 PM)
    AUTO_RESPONSE_START_MINUTE = 30

    def __init__(self):
        """Initialize Claude client with API key from settings"""
        self.api_key = getattr(settings, 'CLAUDE_API_KEY', None)
        if not self.api_key:
            # Try environment variable as fallback
            self.api_key = os.environ.get('CLAUDE_API_KEY')

        if self.api_key:
            self.client = Anthropic(api_key=self.api_key)
        else:
            logger.warning("Claude API key not configured")
            self.client = None

    def can_auto_respond(self) -> bool:
        """
        Check if it's within auto-response time window (15:30 - 23:59, all day)
        In production, you might want to also check day of week, holidays, etc.
        """
        now = datetime.now()

        # Convert to minutes for easier comparison
        current_time = now.hour * 60 + now.minute
        auto_response_time = self.AUTO_RESPONSE_START * 60 + self.AUTO_RESPONSE_START_MINUTE

        # Auto-respond from 15:30 onwards
        return current_time >= auto_response_time

    def classify_problem(self, title: str, description: str) -> tuple[str, bool]:
        """
        Classify problem as simple or complex.
        Returns: (category, is_simple)

        Simple problems: Claude can handle
        Complex problems: Requires human support
        """
        text_combined = f"{title} {description}".lower()

        # Check for complex problem keywords
        complex_keywords = [
            'hardware', 'crash', 'data loss', 'security', 'breach',
            'corrupted', 'emergency', 'critical', 'urgent',
            'custom', 'development', 'billing', 'server down'
        ]

        for keyword in complex_keywords:
            if keyword in text_combined:
                return ('complex', False)

        # Check for simple problem keywords
        simple_keywords = [
            'password', 'login', 'email', 'connection', 'install',
            'setup', 'restart', 'license', 'activation', 'unlock',
            'how to', 'how do i', 'can i', 'what is'
        ]

        for keyword in simple_keywords:
            if keyword in text_combined:
                return ('simple', True)

        # Default to complex (safer approach)
        return ('unknown', False)

    def generate_response(self, title: str, description: str, category: str) -> str:
        """
        Generate AI response for simple technical problems.
        Uses Claude API or free version depending on configuration.
        """
        if not self.client:
            return self._get_offline_response()

        try:
            # Create conversation with Claude
            conversation_history = [
                {
                    "role": "user",
                    "content": f"""
Du bist ein hilfreicher technischer Support-Agent für ein Helpdesk-System.
Antworte auf diese Supportanfrage in DEUTSCH und sei prägnant und hilfreich.

Ticket-Titel: {title}
Ticket-Beschreibung: {description}

Gib praktische Lösungsschritte oder Tipps. Halte deine Antwort auf 2-3 Absätze.
Wenn du nicht sicher bist, erwähne, dass ein Support-Agent sie überprüfen wird.
"""
                }
            ]

            # Call Claude API
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",  # Using best available model
                max_tokens=500,
                messages=conversation_history
            )

            response_text = message.content[0].text
            logger.info(f"Claude generated response for ticket: {title[:50]}")
            return response_text

        except Exception as e:
            logger.error(f"Claude API error: {str(e)}")
            return self._get_offline_response()

    def _get_offline_response(self) -> str:
        """
        Fallback response when API is not available.
        Returns a template response.
        """
        return """
Vielen Dank für Ihre Anfrage!

Wir haben Ihre Anfrage erhalten und werden diese so schnell wie möglich bearbeiten.
Unser Support-Team steht ab 07:00 Uhr zur Verfügung.

Falls Sie dringende Fragen haben, können Sie uns auch direkt kontaktieren.

Mit freundlichen Grüßen,
Ihr Support-Team
"""

    def get_support_message(self) -> str:
        """
        Get message for problems that require human support.
        """
        return """
Vielen Dank für Ihre Anfrage!

Diese Anfrage erfordert die Aufmerksamkeit unseres Support-Teams.
Unser Support ist täglich ab 07:00 Uhr erreichbar.

Ihr Ticket wird priorisiert bearbeitet.

Mit freundlichen Grüßen,
Ihr Support-Team
"""

    def process_ticket(self, ticket) -> bool:
        """
        Process a ticket and generate AI response if appropriate.
        Returns: True if response was generated, False otherwise
        """
        # Check if auto-response is enabled and within time window
        if not self.can_auto_respond():
            logger.debug("Auto-response not available outside 15:30")
            return False

        # Check if ticket already has a response
        if ticket.notes:
            logger.debug(f"Ticket {ticket.id} already has notes")
            return False

        # Classify the problem
        category, is_simple = self.classify_problem(
            ticket.title,
            ticket.description
        )

        # Generate appropriate response
        if is_simple:
            logger.info(f"Ticket {ticket.id} classified as simple: {category}")
            response = self.generate_response(
                ticket.title,
                ticket.description,
                category
            )
        else:
            logger.info(f"Ticket {ticket.id} classified as complex: {category}")
            response = self.get_support_message()

        # Add response as note
        if response:
            ticket.notes = response
            ticket.save(update_fields=['notes'])
            logger.info(f"Added AI response to ticket {ticket.id}")
            return True

        return False


# Initialize global instance
claude_assistant = ClaudeTicketAssistant()
