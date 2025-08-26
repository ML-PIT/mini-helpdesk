from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255))
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    
    # Role: admin, team_leader, support_agent, customer
    role = db.Column(db.String(20), nullable=False, default='customer', index=True)
    
    # Microsoft OAuth2 integration
    microsoft_id = db.Column(db.String(100), unique=True, nullable=True)
    microsoft_token = db.Column(db.Text, nullable=True)
    
    # Profile information
    phone = db.Column(db.String(20))
    department = db.Column(db.String(100))
    location = db.Column(db.String(100))
    
    # Status and metadata
    is_active = db.Column(db.Boolean, default=True, index=True)
    email_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_tickets = db.relationship('Ticket', foreign_keys='Ticket.created_by', backref='creator', lazy='dynamic')
    assigned_tickets = db.relationship('Ticket', foreign_keys='Ticket.assigned_to', backref='assignee', lazy='dynamic')
    comments = db.relationship('TicketComment', backref='author', lazy='dynamic')
    audit_logs = db.relationship('AuditLog', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def has_permission(self, permission):
        """Check if user has specific permission based on role"""
        permissions = {
            'admin': ['all'],
            'team_leader': ['manage_agents', 'assign_tickets', 'view_all_tickets', 'manage_categories'],
            'support_agent': ['view_assigned_tickets', 'update_tickets', 'create_tickets', 'self_assign'],
            'customer': ['view_own_tickets', 'create_tickets', 'comment_own_tickets']
        }
        
        role_permissions = permissions.get(self.role, [])
        return 'all' in role_permissions or permission in role_permissions
    
    def can_access_ticket(self, ticket):
        """Check if user can access a specific ticket"""
        if self.role == 'admin':
            return True
        elif self.role in ['team_leader', 'support_agent']:
            return True  # Can access all tickets
        elif self.role == 'customer':
            return ticket.created_by == self.id
        return False
    
    def get_dashboard_stats(self):
        """Get dashboard statistics for the user"""
        if self.role == 'customer':
            return {
                'my_tickets': self.created_tickets.count(),
                'open_tickets': self.created_tickets.filter_by(status='open').count(),
                'resolved_tickets': self.created_tickets.filter_by(status='resolved').count()
            }
        else:
            from app.models.ticket import Ticket
            return {
                'total_tickets': Ticket.query.count(),
                'open_tickets': Ticket.query.filter_by(status='open').count(),
                'my_assigned': self.assigned_tickets.count() if self.role == 'support_agent' else 0
            }
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary for API responses"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'role': self.role,
            'phone': self.phone,
            'department': self.department,
            'location': self.location,
            'is_active': self.is_active,
            'email_verified': self.email_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat()
        }
        
        if include_sensitive and self.role in ['admin', 'team_leader']:
            data['microsoft_id'] = self.microsoft_id
            
        return data