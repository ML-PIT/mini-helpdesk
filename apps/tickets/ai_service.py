"""
Claude AI Service for automatic ticket responses
"""
import anthropic
from django.conf import settings
from .models import Ticket, TicketComment
from apps.knowledge.models import KnowledgeArticle


class ClaudeAIService:
    """Service to interact with Claude AI for auto-responses"""

    def __init__(self):
        self.client = None
        if settings.CLAUDE_API_KEY:
            self.client = anthropic.Anthropic(api_key=settings.CLAUDE_API_KEY)

    def is_available(self):
        """Check if Claude AI is configured and available"""
        return self.client is not None

    def get_relevant_knowledge(self, query, limit=3):
        """Search knowledge base for relevant articles"""
        from django.db.models import Q

        articles = KnowledgeArticle.objects.filter(
            status='published',
            is_public=True
        ).filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(keywords__icontains=query)
        )[:limit]

        return articles

    def should_auto_respond(self, ticket):
        """Determine if ticket should get auto-response"""
        # Only auto-respond to new tickets
        if ticket.status != 'open':
            return False

        # Don't auto-respond if already assigned
        if ticket.assigned_to:
            return False

        # Don't auto-respond if already has comments
        if ticket.comments.exists():
            return False

        # Only auto-respond to low/medium priority
        if ticket.priority in ['high', 'critical']:
            return False

        return True

    def generate_auto_response(self, ticket):
        """Generate an automatic response using Claude AI"""
        if not self.is_available():
            return None

        # Get relevant knowledge articles
        kb_articles = self.get_relevant_knowledge(ticket.title + ' ' + ticket.description)

        # Build context from knowledge base
        kb_context = ""
        if kb_articles:
            kb_context = "\n\nRelevante Wissensdatenbank-Artikel:\n"
            for article in kb_articles:
                kb_context += f"\n- {article.title}:\n{article.content[:500]}...\n"

        # Build prompt for Claude
        prompt = f"""Du bist ein hilfsbereiter Support-Agent für das ABoro-Soft Helpdesk-System.

Ein Kunde hat folgendes Ticket erstellt:

Titel: {ticket.title}
Beschreibung: {ticket.description}
Priorität: {ticket.get_priority_display()}
Kategorie: {ticket.category.name if ticket.category else 'Keine'}

{kb_context}

Aufgabe:
- Analysiere das Problem des Kunden
- Wenn das Problem einfach ist und du eine Lösung aus den Wissensdatenbank-Artikeln ableiten kannst, gib eine hilfreiche Antwort
- Wenn das Problem komplex ist oder keine passende Lösung in der Wissensdatenbank ist, sage dem Kunden freundlich, dass ein Support-Agent sich um sein Anliegen kümmern wird
- Schreibe auf Deutsch
- Sei freundlich und professionell
- Halte dich kurz (max. 200 Wörter)

Antworte NICHT mit einer Lösung wenn:
- Das Problem technisch komplex ist
- Es um sensible Daten geht
- Es um Abrechnungen oder Verträge geht
- Du dir nicht sicher bist

Beginne mit "Hallo {ticket.created_by.first_name}," und ende mit einer freundlichen Grußformel."""

        try:
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text

            # Determine if this is a helpful answer or a "wait for agent" message
            is_solution = any(word in response_text.lower() for word in [
                'lösung', 'können sie', 'versuchen sie', 'folgende schritte', 'hier ist'
            ])

            return {
                'text': response_text,
                'is_solution': is_solution,
                'kb_articles': list(kb_articles)
            }

        except Exception as e:
            print(f"Claude AI Error: {e}")
            return None

    def create_auto_comment(self, ticket):
        """Create an automatic comment on a ticket if appropriate"""
        if not self.should_auto_respond(ticket):
            return None

        response_data = self.generate_auto_response(ticket)

        if not response_data:
            return None

        # Create the comment
        comment = TicketComment.objects.create(
            ticket=ticket,
            author=ticket.created_by,  # System acts as customer
            content=response_data['text'] + "\n\n---\n🤖 Diese Antwort wurde automatisch von unserer KI generiert. Ein Support-Agent wird sich bei Bedarf zusätzlich um Ihr Anliegen kümmern.",
            is_internal=False
        )

        # If it's a potential solution, update ticket status
        if response_data['is_solution']:
            ticket.status = 'pending'  # Waiting for customer confirmation
            ticket.save()

        return comment


# Create a global instance
ai_service = ClaudeAIService()
