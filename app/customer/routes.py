from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from app.customer import bp
from app.models.ticket import Ticket
from app.models.knowledge import KnowledgeArticle, FAQ
from app.utils.decorators import role_required
from app.utils.claude import get_fallback_claude_url, is_claude_available

@bp.route('/dashboard')
@login_required
@role_required('customer')
def dashboard():
    """Customer dashboard"""
    stats = current_user.get_dashboard_stats()
    
    # Recent tickets
    recent_tickets = current_user.created_tickets.order_by(
        Ticket.updated_at.desc()
    ).limit(5).all()
    
    # Featured knowledge articles
    featured_articles = KnowledgeArticle.query.filter_by(
        is_published=True,
        is_public=True,
        is_featured=True
    ).limit(5).all()
    
    return render_template('customer/dashboard.html',
                         stats=stats,
                         recent_tickets=recent_tickets,
                         featured_articles=featured_articles)

@bp.route('/tickets')
@login_required
@role_required('customer')
def my_tickets():
    """Customer's tickets list"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get tickets with filtering
    query = current_user.created_tickets
    
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)
    
    search = request.args.get('search')
    if search:
        query = query.filter(
            db.or_(
                Ticket.title.contains(search),
                Ticket.description.contains(search),
                Ticket.ticket_number.contains(search)
            )
        )
    
    tickets = query.order_by(Ticket.updated_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('customer/tickets.html', tickets=tickets)

@bp.route('/knowledge')
@login_required
@role_required('customer')
def knowledge_base():
    """Knowledge base for customers"""
    search = request.args.get('search')
    category_id = request.args.get('category_id', type=int)
    
    query = KnowledgeArticle.query.filter_by(is_published=True, is_public=True)
    
    if search:
        query = query.filter(
            db.or_(
                KnowledgeArticle.title.contains(search),
                KnowledgeArticle.content.contains(search),
                KnowledgeArticle.tags.contains(search)
            )
        )
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    articles = query.order_by(
        KnowledgeArticle.is_featured.desc(),
        KnowledgeArticle.view_count.desc()
    ).limit(20).all()
    
    # Featured FAQs
    faqs = FAQ.query.filter_by(is_published=True, is_featured=True).limit(10).all()
    
    return render_template('customer/knowledge.html', 
                         articles=articles, faqs=faqs)

@bp.route('/claude-help/<int:ticket_id>')
@login_required
@role_required('customer')
def claude_help(ticket_id):
    """Generate Claude help URL for customer"""
    ticket = Ticket.query.get_or_404(ticket_id)
    
    # Ensure customer can only access their own tickets
    if ticket.created_by != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('customer.my_tickets'))
    
    if is_claude_available():
        # If Claude API is available, show suggestions on the page
        return render_template('customer/claude_help.html', ticket=ticket)
    else:
        # Generate fallback URL for manual Claude chat
        claude_url = get_fallback_claude_url(ticket)
        return render_template('customer/claude_fallback.html', 
                             ticket=ticket, claude_url=claude_url)