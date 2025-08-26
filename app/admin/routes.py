from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from app.admin import bp
from app.models.user import User
from app.models.ticket import Ticket, Category
from app.models.audit import AuditLog, SystemLog
from app.models.knowledge import KnowledgeArticle
from app import db
from app.utils.decorators import admin_required, role_required
from app.utils.sla import get_sla_metrics

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard"""
    stats = {
        'total_users': User.query.count(),
        'total_tickets': Ticket.query.count(),
        'total_articles': KnowledgeArticle.query.count(),
        'active_agents': User.query.filter_by(is_active=True, role='support_agent').count(),
        'recent_logs': AuditLog.query.order_by(AuditLog.created_at.desc()).limit(10).all()
    }
    
    return render_template('admin/dashboard.html', stats=stats)

@bp.route('/users')
@login_required
@admin_required  
def manage_users():
    """Manage users"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@bp.route('/settings')
@login_required
@admin_required
def settings():
    """System settings"""
    return render_template('admin/settings.html')

@bp.route('/logs')
@login_required
@admin_required
def system_logs():
    """View system logs"""
    page = request.args.get('page', 1, type=int)
    logs = SystemLog.query.order_by(SystemLog.created_at.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    return render_template('admin/logs.html', logs=logs)