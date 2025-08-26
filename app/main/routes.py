from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user
from app.main import bp
from app.models.ticket import Ticket
from app.models.user import User

@bp.route('/')
def index():
    """Main dashboard route - redirect based on user role"""
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role in ['team_leader', 'support_agent']:
            return redirect(url_for('tickets.dashboard'))
        elif current_user.role == 'customer':
            return redirect(url_for('customer.dashboard'))
    return redirect(url_for('auth.login'))

@bp.route('/dashboard')
def dashboard():
    """Main dashboard with role-based content"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    
    # Get basic statistics
    stats = {}
    if current_user.role in ['admin', 'team_leader', 'support_agent']:
        stats = {
            'total_tickets': Ticket.query.count(),
            'open_tickets': Ticket.query.filter_by(status='open').count(),
            'pending_tickets': Ticket.query.filter_by(status='pending').count(),
            'resolved_tickets': Ticket.query.filter_by(status='resolved').count(),
            'my_tickets': Ticket.query.filter_by(assigned_to=current_user.id).count() if current_user.role == 'support_agent' else 0
        }
    elif current_user.role == 'customer':
        stats = {
            'my_tickets': Ticket.query.filter_by(created_by=current_user.id).count(),
            'open_tickets': Ticket.query.filter_by(created_by=current_user.id, status='open').count(),
            'resolved_tickets': Ticket.query.filter_by(created_by=current_user.id, status='resolved').count()
        }
    
    return render_template('dashboard.html', stats=stats)

@bp.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return {'status': 'healthy', 'version': '1.0.0'}, 200