from datetime import datetime
from app import db
import json

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Who performed the action
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    
    # What was affected
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=True, index=True)
    entity_type = db.Column(db.String(50), nullable=False, index=True)  # ticket, user, knowledge_article, etc.
    entity_id = db.Column(db.Integer, nullable=True, index=True)
    
    # What action was performed
    action = db.Column(db.String(50), nullable=False, index=True)  # create, update, delete, assign, etc.
    
    # Details of the change
    old_values = db.Column(db.Text, nullable=True)  # JSON string of old values
    new_values = db.Column(db.Text, nullable=True)  # JSON string of new values
    
    # Additional context
    description = db.Column(db.String(500))
    ip_address = db.Column(db.String(45))  # IPv4 or IPv6
    user_agent = db.Column(db.String(500))
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<AuditLog {self.action} on {self.entity_type}>'
    
    @classmethod
    def log_action(cls, user_id, entity_type, entity_id, action, old_values=None, 
                   new_values=None, description=None, ip_address=None, user_agent=None, ticket_id=None):
        """Create an audit log entry"""
        audit_log = cls(
            user_id=user_id,
            ticket_id=ticket_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.add(audit_log)
        return audit_log
    
    @classmethod
    def log_ticket_action(cls, user_id, ticket, action, old_values=None, new_values=None, 
                         description=None, ip_address=None, user_agent=None):
        """Convenience method for logging ticket actions"""
        return cls.log_action(
            user_id=user_id,
            entity_type='ticket',
            entity_id=ticket.id,
            ticket_id=ticket.id,
            action=action,
            old_values=old_values,
            new_values=new_values,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @classmethod
    def log_user_action(cls, user_id, target_user, action, old_values=None, new_values=None,
                       description=None, ip_address=None, user_agent=None):
        """Convenience method for logging user actions"""
        return cls.log_action(
            user_id=user_id,
            entity_type='user',
            entity_id=target_user.id,
            action=action,
            old_values=old_values,
            new_values=new_values,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    def get_old_values(self):
        """Get old values as dictionary"""
        if self.old_values:
            return json.loads(self.old_values)
        return {}
    
    def get_new_values(self):
        """Get new values as dictionary"""
        if self.new_values:
            return json.loads(self.new_values)
        return {}
    
    def get_changes(self):
        """Get a summary of what changed"""
        old = self.get_old_values()
        new = self.get_new_values()
        
        changes = {}
        all_keys = set(old.keys()) | set(new.keys())
        
        for key in all_keys:
            old_val = old.get(key)
            new_val = new.get(key)
            if old_val != new_val:
                changes[key] = {
                    'from': old_val,
                    'to': new_val
                }
        
        return changes
    
    def to_dict(self):
        """Convert audit log to dictionary"""
        return {
            'id': self.id,
            'user': self.user.to_dict() if self.user else None,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'ticket_id': self.ticket_id,
            'action': self.action,
            'description': self.description,
            'old_values': self.get_old_values(),
            'new_values': self.get_new_values(),
            'changes': self.get_changes(),
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat()
        }

class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Log level and source
    level = db.Column(db.String(10), nullable=False, index=True)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    source = db.Column(db.String(50), nullable=False, index=True)  # email, auth, api, etc.
    
    # Message details
    message = db.Column(db.String(1000), nullable=False)
    details = db.Column(db.Text, nullable=True)  # Additional details as JSON
    
    # Context
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(100), nullable=True)
    ip_address = db.Column(db.String(45))
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    user = db.relationship('User', backref='system_logs')
    
    def __repr__(self):
        return f'<SystemLog {self.level}: {self.message[:50]}>'
    
    @classmethod
    def log(cls, level, source, message, details=None, user_id=None, session_id=None, ip_address=None):
        """Create a system log entry"""
        log_entry = cls(
            level=level.upper(),
            source=source,
            message=message,
            details=json.dumps(details) if details else None,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address
        )
        
        db.session.add(log_entry)
        return log_entry
    
    @classmethod
    def info(cls, source, message, **kwargs):
        return cls.log('INFO', source, message, **kwargs)
    
    @classmethod
    def warning(cls, source, message, **kwargs):
        return cls.log('WARNING', source, message, **kwargs)
    
    @classmethod
    def error(cls, source, message, **kwargs):
        return cls.log('ERROR', source, message, **kwargs)
    
    @classmethod
    def debug(cls, source, message, **kwargs):
        return cls.log('DEBUG', source, message, **kwargs)
    
    def get_details(self):
        """Get details as dictionary"""
        if self.details:
            return json.loads(self.details)
        return {}
    
    def to_dict(self):
        return {
            'id': self.id,
            'level': self.level,
            'source': self.source,
            'message': self.message,
            'details': self.get_details(),
            'user': self.user.to_dict() if self.user else None,
            'session_id': self.session_id,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat()
        }