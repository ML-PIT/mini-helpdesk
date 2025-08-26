try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    
from flask import current_app
from app.models.audit import SystemLog
import json

class ClaudeIntegration:
    """Claude AI integration for helpdesk features"""
    
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Claude client if API key is available"""
        if not ANTHROPIC_AVAILABLE:
            SystemLog.info('claude', 'Anthropic library not installed - Claude features will be disabled')
            self.client = None
            return
            
        api_key = current_app.config.get('CLAUDE_API_KEY')
        if api_key:
            try:
                self.client = anthropic.Anthropic(api_key=api_key)
                SystemLog.info('claude', 'Claude client initialized successfully')
            except Exception as e:
                SystemLog.error('claude', f'Failed to initialize Claude client: {str(e)}')
                self.client = None
        else:
            SystemLog.info('claude', 'No Claude API key configured - Claude features will be disabled')
    
    def is_available(self):
        """Check if Claude integration is available"""
        return self.client is not None
    
    def get_response_suggestions(self, ticket):
        """Get AI-powered response suggestions for a ticket"""
        if not self.is_available():
            return None
        
        try:
            # Build context from ticket and comments
            context = self._build_ticket_context(ticket)
            
            prompt = f"""
You are a helpful IT support assistant. Based on the following ticket information, provide 3 professional response suggestions that a support agent could use. Each suggestion should be appropriate for the issue described.

Ticket Context:
{context}

Please provide responses in the following JSON format:
{{
    "suggestions": [
        {{
            "title": "Brief title for this response",
            "content": "Full response text that could be sent to the customer",
            "type": "acknowledgment|solution|request_info|escalation"
        }}
    ]
}}

Make the responses helpful, professional, and specific to the issue described.
"""
            
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse the response
            suggestions = json.loads(response.content[0].text)
            
            SystemLog.info('claude', f'Generated response suggestions for ticket {ticket.ticket_number}')
            
            return suggestions.get('suggestions', [])
            
        except Exception as e:
            SystemLog.error('claude', f'Error getting response suggestions: {str(e)}')
            return None
    
    def suggest_category(self, title, description):
        """Suggest appropriate category for a ticket"""
        if not self.is_available():
            return None
        
        try:
            # Import here to avoid circular imports
            from app.models.ticket import Category
            
            # Get available categories
            categories = Category.query.filter_by(is_active=True).all()
            if not categories:
                return None
            
            category_list = [f"- {cat.name}: {cat.description or 'No description'}" for cat in categories]
            category_text = "\n".join(category_list)
            
            prompt = f"""
Based on the following ticket information, suggest the most appropriate category from the available options.

Ticket Title: {title}
Ticket Description: {description}

Available Categories:
{category_text}

Please respond with only the exact category name that best fits this ticket. If none are appropriate, respond with "None".
"""
            
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                messages=[{"role": "user", "content": prompt}]
            )
            
            suggested_category_name = response.content[0].text.strip()
            
            # Find the category object
            category = Category.query.filter_by(name=suggested_category_name, is_active=True).first()
            
            if category:
                SystemLog.info('claude', f'Suggested category "{category.name}" for ticket')
                return category
            
            return None
            
        except Exception as e:
            SystemLog.error('claude', f'Error suggesting category: {str(e)}')
            return None
    
    def generate_knowledge_article(self, ticket):
        """Generate knowledge base article from resolved ticket"""
        if not self.is_available():
            return None
        
        try:
            if ticket.status not in ['resolved', 'closed']:
                return None
            
            context = self._build_ticket_context(ticket, include_resolution=True)
            
            prompt = f"""
Based on the following resolved support ticket, create a knowledge base article that could help other customers with similar issues.

Ticket Information:
{context}

Please create a knowledge base article in the following JSON format:
{{
    "title": "Clear, descriptive title for the article",
    "summary": "Brief summary of what this article covers (1-2 sentences)",
    "content": "Full article content in markdown format, including problem description, solution steps, and any relevant notes",
    "tags": ["tag1", "tag2", "tag3"]
}}

Make the article clear, step-by-step, and helpful for customers who might have similar issues.
"""
            
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            article_data = json.loads(response.content[0].text)
            
            SystemLog.info('claude', f'Generated knowledge article for ticket {ticket.ticket_number}')
            
            return article_data
            
        except Exception as e:
            SystemLog.error('claude', f'Error generating knowledge article: {str(e)}')
            return None
    
    def analyze_ticket_sentiment(self, ticket):
        """Analyze customer sentiment from ticket content"""
        if not self.is_available():
            return None
        
        try:
            # Get customer comments only
            customer_comments = []
            for comment in ticket.comments:
                if comment.author.role == 'customer':
                    customer_comments.append(comment.content)
            
            if not customer_comments:
                customer_content = ticket.description
            else:
                customer_content = f"{ticket.description}\n\n" + "\n\n".join(customer_comments)
            
            prompt = f"""
Analyze the sentiment of the following customer communication from a support ticket. Consider frustration level, urgency, and overall tone.

Customer Communication:
{customer_content}

Please respond in JSON format:
{{
    "sentiment": "positive|neutral|negative|frustrated",
    "urgency_level": "low|medium|high|critical",
    "key_concerns": ["concern1", "concern2"],
    "suggested_approach": "Brief suggestion for how support should approach this customer"
}}
"""
            
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            analysis = json.loads(response.content[0].text)
            
            SystemLog.info('claude', f'Analyzed sentiment for ticket {ticket.ticket_number}')
            
            return analysis
            
        except Exception as e:
            SystemLog.error('claude', f'Error analyzing sentiment: {str(e)}')
            return None
    
    def generate_sla_excuse(self, ticket):
        """Generate professional response for SLA breach"""
        if not self.is_available():
            return None
        
        try:
            prompt = f"""
Generate a professional, empathetic response for a support ticket that has breached its SLA deadline.

Ticket Details:
- Ticket Number: {ticket.ticket_number}
- Title: {ticket.title}
- Priority: {ticket.priority}
- Created: {ticket.created_at.strftime('%Y-%m-%d %H:%M')}
- SLA Due: {ticket.sla_due_date.strftime('%Y-%m-%d %H:%M') if ticket.sla_due_date else 'N/A'}

Create a sincere apology that:
1. Acknowledges the delay
2. Takes responsibility
3. Provides assurance about resolution
4. Maintains professional tone

Keep it concise and customer-focused.
"""
            
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            SystemLog.error('claude', f'Error generating SLA excuse: {str(e)}')
            return None
    
    def _build_ticket_context(self, ticket, include_resolution=False):
        """Build context string from ticket information"""
        context = f"""
Ticket Number: {ticket.ticket_number}
Title: {ticket.title}
Description: {ticket.description}
Priority: {ticket.priority}
Status: {ticket.status}
Category: {ticket.category.name if ticket.category else 'None'}
Created by: {ticket.creator.full_name if ticket.creator else 'Unknown'}
Created at: {ticket.created_at.strftime('%Y-%m-%d %H:%M')}
"""
        
        # Add comments
        if ticket.comments.count() > 0:
            context += "\n\nComments:\n"
            for comment in ticket.comments.order_by('created_at'):
                author_role = comment.author.role if comment.author else 'Unknown'
                context += f"[{comment.created_at.strftime('%Y-%m-%d %H:%M')} - {author_role}]: {comment.content}\n"
        
        # Add resolution information if requested
        if include_resolution and ticket.status in ['resolved', 'closed']:
            context += f"\nResolution Date: {ticket.resolved_at.strftime('%Y-%m-%d %H:%M') if ticket.resolved_at else 'Unknown'}"
            if ticket.rating:
                context += f"\nCustomer Rating: {ticket.rating}/5 stars"
            if ticket.feedback:
                context += f"\nCustomer Feedback: {ticket.feedback}"
        
        return context

# Global Claude integration instance (will be initialized in app context)
claude_integration = None

def init_claude_integration(app):
    """Initialize Claude integration with app context"""
    global claude_integration
    with app.app_context():
        claude_integration = ClaudeIntegration()
    return claude_integration

# Convenience functions for use in routes
def get_claude_suggestions(ticket):
    """Get Claude response suggestions for a ticket"""
    if claude_integration is None:
        return None
    return claude_integration.get_response_suggestions(ticket)

def get_category_suggestion(title, description):
    """Get Claude category suggestion"""
    if claude_integration is None:
        return None
    return claude_integration.suggest_category(title, description)

def generate_kb_article(ticket):
    """Generate knowledge base article from ticket"""
    if claude_integration is None:
        return None
    return claude_integration.generate_knowledge_article(ticket)

def analyze_sentiment(ticket):
    """Analyze ticket sentiment"""
    if claude_integration is None:
        return None
    return claude_integration.analyze_ticket_sentiment(ticket)

def get_fallback_claude_url(ticket):
    """Generate Claude chat URL with ticket context for manual use"""
    if claude_integration is None:
        # Create a basic context without the integration
        context = f"""
Ticket Number: {ticket.ticket_number}
Title: {ticket.title}
Description: {ticket.description}
Priority: {ticket.priority}
Status: {ticket.status}
Created by: {ticket.creator.full_name if ticket.creator else 'Unknown'}
Created at: {ticket.created_at.strftime('%Y-%m-%d %H:%M')}
"""
    else:
        context = claude_integration._build_ticket_context(ticket)
    
    prompt = f"""I have a support ticket that needs attention. Here are the details:

{context}

Please help me:
1. Understand the customer's issue
2. Suggest appropriate responses
3. Recommend next steps

What would be the best way to handle this ticket?"""
    
    # URL encode the prompt for Claude web interface
    import urllib.parse
    encoded_prompt = urllib.parse.quote(prompt)
    
    return f"https://claude.ai/chat?q={encoded_prompt}"

def is_claude_available():
    """Check if Claude integration is available"""
    return claude_integration is not None and claude_integration.is_available()