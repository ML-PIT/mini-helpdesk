from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, jsonify, current_app, abort
from flask_login import current_user, login_required
from app.tickets import bp
from app.models.ticket import Ticket, TicketComment, TicketAttachment, Category
from app.models.user import User
from app.models.audit import AuditLog
from app import db
from app.tickets.forms import TicketForm, CommentForm, AssignTicketForm, CategoryForm
from app.utils.decorators import role_required, agent_or_admin_required, permission_required, ticket_access_required
from app.utils.sla import check_sla_breaches

@bp.route('/dashboard')
@login_required
def dashboard():
    """Ticket dashboard based on user role"""
    if current_user.role == 'customer':
        return redirect(url_for('customer.dashboard'))
    
    # Get statistics
    stats = {
        'total_tickets': Ticket.query.count(),
        'open_tickets': Ticket.query.filter_by(status='open').count(),
        'in_progress_tickets': Ticket.query.filter_by(status='in_progress').count(),
        'pending_tickets': Ticket.query.filter_by(status='pending').count(),
        'resolved_today': Ticket.query.filter(
            Ticket.resolved_at >= datetime.utcnow().date()
        ).count(),
        'sla_breached': Ticket.query.filter_by(sla_breached=True).count()
    }
    
    if current_user.role == 'support_agent':
        stats['my_assigned'] = Ticket.query.filter_by(assigned_to=current_user.id).count()
        stats['my_pending'] = Ticket.query.filter_by(
            assigned_to=current_user.id, 
            status='pending'
        ).count()
    
    # Recent tickets based on role
    if current_user.role == 'support_agent':
        recent_tickets = Ticket.query.filter_by(assigned_to=current_user.id)\
                              .order_by(Ticket.updated_at.desc()).limit(10).all()
    else:
        recent_tickets = Ticket.query.order_by(Ticket.updated_at.desc()).limit(10).all()
    
    # SLA alerts
    sla_alerts = Ticket.query.filter(
        Ticket.sla_due_date <= datetime.utcnow() + timedelta(hours=2),
        Ticket.status.notin_(['resolved', 'closed'])
    ).limit(5).all()
    
    return render_template('tickets/dashboard.html', 
                         stats=stats, 
                         recent_tickets=recent_tickets,
                         sla_alerts=sla_alerts)

@bp.route('/list')
@login_required
@agent_or_admin_required
def list_tickets():
    """List all tickets with filtering and pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Base query
    query = Ticket.query
    
    # Apply filters
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)
    
    priority = request.args.get('priority')
    if priority:
        query = query.filter_by(priority=priority)
    
    category_id = request.args.get('category_id', type=int)
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    assigned_to = request.args.get('assigned_to', type=int)
    if assigned_to:
        query = query.filter_by(assigned_to=assigned_to)
    elif request.args.get('unassigned'):
        query = query.filter(Ticket.assigned_to.is_(None))
    
    # Search
    search = request.args.get('search')
    if search:
        query = query.filter(
            db.or_(
                Ticket.title.contains(search),
                Ticket.description.contains(search),
                Ticket.ticket_number.contains(search)
            )
        )
    
    # For agents, show only their assigned tickets by default unless they request all
    if current_user.role == 'support_agent' and not request.args.get('show_all'):
        query = query.filter_by(assigned_to=current_user.id)
    
    # Sort
    sort_by = request.args.get('sort_by', 'updated_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    if sort_order == 'asc':
        query = query.order_by(getattr(Ticket, sort_by).asc())
    else:
        query = query.order_by(getattr(Ticket, sort_by).desc())
    
    tickets = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get filter options
    categories = Category.query.filter_by(is_active=True).all()
    agents = User.query.filter(User.role.in_(['support_agent', 'team_leader'])).all()
    
    return render_template('tickets/list.html',
                         tickets=tickets,
                         categories=categories,
                         agents=agents)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_ticket():
    """Create new ticket"""
    form = TicketForm()
    
    # Populate category choices
    form.category_id.choices = [(0, 'Select Category')] + [
        (c.id, c.name) for c in Category.query.filter_by(is_active=True).all()
    ]
    
    if form.validate_on_submit():
        # Create ticket
        ticket = Ticket(
            title=form.title.data,
            description=form.description.data,
            priority=form.priority.data,
            created_by=current_user.id,
            category_id=form.category_id.data if form.category_id.data != 0 else None
        )
        
        # Set SLA due date based on priority
        ticket.set_priority_based_sla()
        
        # Auto-assign if category has auto-assignment
        if ticket.category and ticket.category.auto_assign_to:
            ticket.assigned_to = ticket.category.auto_assign_to
        
        # AI-powered category suggestion if no category selected and Claude available
        if not ticket.category_id and current_app.config.get('CLAUDE_API_KEY'):
            try:
                from app.utils.claude import get_category_suggestion
                suggested_category = get_category_suggestion(ticket.title, ticket.description)
                if suggested_category:
                    ticket.category_id = suggested_category.id
                    if suggested_category.auto_assign_to:
                        ticket.assigned_to = suggested_category.auto_assign_to
            except Exception as e:
                current_app.logger.warning(f"Claude category suggestion failed: {e}")
        
        db.session.add(ticket)
        db.session.commit()
        
        # Handle file attachments
        for file in form.attachments.data:
            if file and file.filename:
                ticket.add_attachment(
                    filename=file.filename,
                    content=file.read(),
                    content_type=file.content_type,
                    author_id=current_user.id
                )
        
        db.session.commit()
        
        # Log ticket creation
        AuditLog.log_ticket_action(
            user_id=current_user.id,
            ticket=ticket,
            action='create',
            new_values=ticket.to_dict(),
            description=f'Ticket {ticket.ticket_number} created',
            ip_address=request.remote_addr
        )
        
        # Send notifications
        try:
            from app.utils.email import send_ticket_notification
            send_ticket_notification(ticket, 'created')
        except Exception as e:
            current_app.logger.warning(f"Failed to send notification: {e}")
        
        flash(f'Ticket {ticket.ticket_number} created successfully!', 'success')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket.id))
    
    return render_template('tickets/create.html', form=form)

@bp.route('/<int:ticket_id>')
@login_required
@ticket_access_required()
def view_ticket(ticket_id):
    """View ticket details"""
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # Check SLA status
    ticket.check_sla_breach()
    if ticket.sla_breached:
        db.session.commit()
    
    # Forms for various actions
    comment_form = CommentForm()
    assign_form = AssignTicketForm()
    
    # Populate assign form choices
    if current_user.role in ['admin', 'team_leader']:
        agents = User.query.filter(User.role.in_(['support_agent', 'team_leader'])).all()
        assign_form.assigned_to.choices = [(0, 'Unassigned')] + [
            (u.id, u.full_name) for u in agents
        ]
    
    # Get AI suggestions if available
    claude_suggestions = None
    if current_app.config.get('CLAUDE_API_KEY') and current_user.role in ['support_agent', 'team_leader', 'admin']:
        try:
            from app.utils.claude import get_claude_suggestions
            claude_suggestions = get_claude_suggestions(ticket)
        except Exception as e:
            current_app.logger.warning(f"Claude suggestions failed: {e}")
    
    # Get comments (filtered by visibility)
    comments = ticket.comments.order_by(TicketComment.created_at.asc())
    if current_user.role == 'customer':
        comments = comments.filter_by(is_internal=False)
    
    return render_template('tickets/view.html',
                         ticket=ticket,
                         comments=comments.all(),
                         comment_form=comment_form,
                         assign_form=assign_form,
                         claude_suggestions=claude_suggestions)

@bp.route('/<int:ticket_id>/comment', methods=['POST'])
@login_required
@ticket_access_required()
def add_comment(ticket_id):
    """Add comment to ticket"""
    ticket = Ticket.query.get_or_404(ticket_id)
    form = CommentForm()
    
    if form.validate_on_submit():
        # Determine if comment is internal
        is_internal = False
        if current_user.role in ['support_agent', 'team_leader', 'admin']:
            is_internal = form.is_internal.data
        
        # Add comment
        comment = ticket.add_comment(
            author_id=current_user.id,
            content=form.content.data,
            is_internal=is_internal
        )
        
        # Update ticket status if needed
        if current_user.role in ['support_agent', 'team_leader', 'admin']:
            if ticket.status == 'open':
                old_status = ticket.status
                ticket.status = 'in_progress'
                
                # Log status change
                AuditLog.log_ticket_action(
                    user_id=current_user.id,
                    ticket=ticket,
                    action='status_change',
                    old_values={'status': old_status},
                    new_values={'status': ticket.status},
                    description=f'Status changed from {old_status} to {ticket.status}',
                    ip_address=request.remote_addr
                )
        
        db.session.commit()
        
        # Log comment addition
        AuditLog.log_ticket_action(
            user_id=current_user.id,
            ticket=ticket,
            action='comment',
            new_values={'comment': comment.content, 'is_internal': is_internal},
            description='Comment added to ticket',
            ip_address=request.remote_addr
        )
        
        # Send notifications
        try:
            from app.utils.email import send_ticket_notification
            send_ticket_notification(ticket, 'commented', comment)
        except Exception as e:
            current_app.logger.warning(f"Failed to send notification: {e}")
        
        flash('Comment added successfully!', 'success')
    else:
        flash('Error adding comment. Please try again.', 'error')
    
    return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))

@bp.route('/<int:ticket_id>/assign', methods=['POST'])
@login_required
@role_required('admin', 'team_leader')
def assign_ticket(ticket_id):
    """Assign ticket to agent"""
    ticket = Ticket.query.get_or_404(ticket_id)
    form = AssignTicketForm()
    
    # Populate choices
    agents = User.query.filter(User.role.in_(['support_agent', 'team_leader'])).all()
    form.assigned_to.choices = [(0, 'Unassigned')] + [(u.id, u.full_name) for u in agents]
    
    if form.validate_on_submit():
        old_assigned_to = ticket.assigned_to
        new_assigned_to = form.assigned_to.data if form.assigned_to.data != 0 else None
        
        if old_assigned_to != new_assigned_to:
            ticket.assigned_to = new_assigned_to
            db.session.commit()
            
            # Log assignment change
            AuditLog.log_ticket_action(
                user_id=current_user.id,
                ticket=ticket,
                action='assign',
                old_values={'assigned_to': old_assigned_to},
                new_values={'assigned_to': new_assigned_to},
                description=f'Ticket assigned to {ticket.assignee.full_name if ticket.assignee else "unassigned"}',
                ip_address=request.remote_addr
            )
            
            # Send notification
            try:
                from app.utils.email import send_ticket_notification
                send_ticket_notification(ticket, 'assigned')
            except Exception as e:
                current_app.logger.warning(f"Failed to send notification: {e}")
            
            flash('Ticket assigned successfully!', 'success')
        else:
            flash('No assignment change made.', 'info')
    
    return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))

@bp.route('/<int:ticket_id>/self_assign', methods=['POST'])
@login_required
@role_required('support_agent', 'team_leader')
def self_assign_ticket(ticket_id):
    """Allow agents to self-assign available tickets"""
    ticket = Ticket.query.get_or_404(ticket_id)
    
    if ticket.assigned_to and ticket.assigned_to != current_user.id:
        flash('Ticket is already assigned to another agent.', 'error')
    else:
        old_assigned_to = ticket.assigned_to
        ticket.assigned_to = current_user.id
        db.session.commit()
        
        # Log self-assignment
        AuditLog.log_ticket_action(
            user_id=current_user.id,
            ticket=ticket,
            action='self_assign',
            old_values={'assigned_to': old_assigned_to},
            new_values={'assigned_to': current_user.id},
            description=f'Agent self-assigned ticket',
            ip_address=request.remote_addr
        )
        
        try:
            from app.utils.email import send_ticket_notification
            send_ticket_notification(ticket, 'assigned')
        except Exception as e:
            current_app.logger.warning(f"Failed to send notification: {e}")
        flash('Ticket assigned to you successfully!', 'success')
    
    return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))

@bp.route('/<int:ticket_id>/status/<status>')
@login_required
@agent_or_admin_required
def change_status(ticket_id, status):
    """Change ticket status"""
    ticket = Ticket.query.get_or_404(ticket_id)
    
    valid_statuses = ['open', 'in_progress', 'pending', 'resolved', 'closed']
    if status not in valid_statuses:
        flash('Invalid status.', 'error')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))
    
    old_status = ticket.status
    if old_status != status:
        ticket.status = status
        
        # Set timestamps
        if status == 'resolved' and not ticket.resolved_at:
            ticket.resolved_at = datetime.utcnow()
        elif status == 'closed' and not ticket.closed_at:
            ticket.closed_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log status change
        AuditLog.log_ticket_action(
            user_id=current_user.id,
            ticket=ticket,
            action='status_change',
            old_values={'status': old_status},
            new_values={'status': status},
            description=f'Status changed from {old_status} to {status}',
            ip_address=request.remote_addr
        )
        
        # Send notification
        try:
            from app.utils.email import send_ticket_notification
            send_ticket_notification(ticket, 'status_changed')
        except Exception as e:
            current_app.logger.warning(f"Failed to send notification: {e}")
        
        flash(f'Ticket status changed to {status.replace("_", " ").title()}!', 'success')
    
    return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))

@bp.route('/<int:ticket_id>/priority/<priority>')
@login_required
@agent_or_admin_required
def change_priority(ticket_id, priority):
    """Change ticket priority"""
    ticket = Ticket.query.get_or_404(ticket_id)
    
    valid_priorities = ['low', 'medium', 'high', 'critical']
    if priority not in valid_priorities:
        flash('Invalid priority.', 'error')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))
    
    old_priority = ticket.priority
    if old_priority != priority:
        ticket.priority = priority
        ticket.set_priority_based_sla()  # Recalculate SLA
        db.session.commit()
        
        # Log priority change
        AuditLog.log_ticket_action(
            user_id=current_user.id,
            ticket=ticket,
            action='priority_change',
            old_values={'priority': old_priority},
            new_values={'priority': priority},
            description=f'Priority changed from {old_priority} to {priority}',
            ip_address=request.remote_addr
        )
        
        try:
            from app.utils.email import send_ticket_notification
            send_ticket_notification(ticket, 'priority_changed')
        except Exception as e:
            current_app.logger.warning(f"Failed to send notification: {e}")
        
        flash(f'Ticket priority changed to {priority.title()}!', 'success')
    
    return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))

@bp.route('/<int:ticket_id>/rate', methods=['POST'])
@login_required
def rate_ticket(ticket_id):
    """Rate ticket satisfaction (customers only)"""
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # Only ticket creator can rate
    if ticket.created_by != current_user.id:
        abort(403)
    
    # Only resolved/closed tickets can be rated
    if ticket.status not in ['resolved', 'closed']:
        flash('Only resolved or closed tickets can be rated.', 'error')
        return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))
    
    rating = request.form.get('rating', type=int)
    feedback = request.form.get('feedback', '')
    
    if rating and 1 <= rating <= 5:
        old_rating = ticket.rating
        ticket.rating = rating
        ticket.feedback = feedback if feedback.strip() else None
        db.session.commit()
        
        # Log rating
        AuditLog.log_ticket_action(
            user_id=current_user.id,
            ticket=ticket,
            action='rate',
            old_values={'rating': old_rating},
            new_values={'rating': rating, 'feedback': feedback},
            description=f'Ticket rated {rating} stars',
            ip_address=request.remote_addr
        )
        
        flash('Thank you for your feedback!', 'success')
    else:
        flash('Please provide a valid rating (1-5 stars).', 'error')
    
    return redirect(url_for('tickets.view_ticket', ticket_id=ticket_id))

@bp.route('/categories')
@login_required
@role_required('admin', 'team_leader')
def manage_categories():
    """Manage ticket categories"""
    categories = Category.query.order_by(Category.name).all()
    return render_template('tickets/categories.html', categories=categories)

@bp.route('/categories/create', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'team_leader')
def create_category():
    """Create new category"""
    form = CategoryForm()
    
    # Populate assignee choices
    agents = User.query.filter(User.role.in_(['support_agent', 'team_leader'])).all()
    form.auto_assign_to.choices = [(0, 'No Auto-Assignment')] + [
        (u.id, u.full_name) for u in agents
    ]
    
    if form.validate_on_submit():
        category = Category(
            name=form.name.data,
            description=form.description.data,
            color=form.color.data,
            auto_assign_to=form.auto_assign_to.data if form.auto_assign_to.data != 0 else None
        )
        
        db.session.add(category)
        db.session.commit()
        
        flash('Category created successfully!', 'success')
        return redirect(url_for('tickets.manage_categories'))
    
    return render_template('tickets/create_category.html', form=form)

@bp.route('/sla_check')
@login_required
@role_required('admin', 'team_leader')
def sla_check():
    """Manual SLA breach check"""
    breached_count = check_sla_breaches()
    
    flash(f'SLA check completed. {breached_count} tickets marked as breached.', 'info')
    return redirect(url_for('tickets.dashboard'))