from datetime import datetime
from app import db
import base64
import uuid

class Ticket(db.Model):
    __tablename__ = 'tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Relationships
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True, index=True)
    
    # Status and priority
    status = db.Column(db.String(20), nullable=False, default='open', index=True)  # open, in_progress, pending, resolved, closed
    priority = db.Column(db.String(20), nullable=False, default='medium', index=True)  # low, medium, high, critical
    
    # Time tracking for SLA
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    first_response_at = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    closed_at = db.Column(db.DateTime, nullable=True)
    
    # SLA tracking
    sla_due_date = db.Column(db.DateTime, nullable=True, index=True)
    sla_breached = db.Column(db.Boolean, default=False, index=True)
    
    # Email integration
    email_thread_id = db.Column(db.String(255), nullable=True)
    
    # Customer satisfaction
    rating = db.Column(db.Integer, nullable=True)  # 1-5 stars
    feedback = db.Column(db.Text, nullable=True)
    
    # Relationships
    category = db.relationship('Category', backref='tickets')
    comments = db.relationship('TicketComment', backref='ticket', lazy='dynamic', cascade='all, delete-orphan')
    attachments = db.relationship('TicketAttachment', backref='ticket', lazy='dynamic', cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='ticket', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.ticket_number:
            self.ticket_number = self.generate_ticket_number()
    
    def __repr__(self):
        return f'<Ticket {self.ticket_number}>'
    
    @staticmethod
    def generate_ticket_number():
        """Generate unique ticket number"""
        import random
        import string
        while True:
            number = f"TK-{datetime.now().year}-{random.randint(10000, 99999)}"
            if not Ticket.query.filter_by(ticket_number=number).first():
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
            if datetime.utcnow() > self.sla_due_date:
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
    
    def add_comment(self, author_id, content, is_internal=False, email_message_id=None):
        """Add a comment to the ticket"""
        comment = TicketComment(
            ticket_id=self.id,
            author_id=author_id,
            content=content,
            is_internal=is_internal,
            email_message_id=email_message_id
        )
        
        # Set first response time if this is the first agent response
        if not self.first_response_at and not is_internal:
            from app.models.user import User
            author = User.query.get(author_id)
            if author and author.role in ['support_agent', 'team_leader', 'admin']:
                self.first_response_at = datetime.utcnow()
        
        db.session.add(comment)
        return comment
    
    def add_attachment(self, filename, content, content_type, author_id):
        """Add an attachment to the ticket"""
        attachment = TicketAttachment(
            ticket_id=self.id,
            filename=filename,
            content=base64.b64encode(content).decode('utf-8'),
            content_type=content_type,
            size=len(content),
            uploaded_by=author_id
        )
        db.session.add(attachment)
        return attachment
    
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
            'creator': self.creator.to_dict() if self.creator else None,
            'assignee': self.assignee.to_dict() if self.assignee else None,
            'category': self.category.name if self.category else None,
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
                'comments': [comment.to_dict() for comment in self.comments.order_by(TicketComment.created_at)],
                'attachments': [att.to_dict() for att in self.attachments]
            })
        
        return data

class TicketComment(db.Model):
    __tablename__ = 'ticket_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    is_internal = db.Column(db.Boolean, default=False)  # Internal notes vs customer-visible comments
    email_message_id = db.Column(db.String(255), nullable=True)  # For email threading
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<TicketComment {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'is_internal': self.is_internal,
            'author': self.author.to_dict(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class TicketAttachment(db.Model):
    __tablename__ = 'ticket_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)  # Base64 encoded content
    content_type = db.Column(db.String(100), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    uploader = db.relationship('User', backref='uploaded_attachments')
    
    def __repr__(self):
        return f'<TicketAttachment {self.filename}>'
    
    def get_content(self):
        """Get decoded file content"""
        return base64.b64decode(self.content.encode('utf-8'))
    
    def to_dict(self, include_content=False):
        data = {
            'id': self.id,
            'filename': self.filename,
            'content_type': self.content_type,
            'size': self.size,
            'uploaded_by': self.uploader.to_dict(),
            'uploaded_at': self.uploaded_at.isoformat()
        }
        
        if include_content:
            data['content'] = self.content
            
        return data

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#2fb2bf')  # Hex color for UI
    is_active = db.Column(db.Boolean, default=True)
    
    # Auto-assignment
    auto_assign_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    assignee = db.relationship('User', backref='assigned_categories')
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'is_active': self.is_active,
            'auto_assign_to': self.assignee.to_dict() if self.assignee else None
        }