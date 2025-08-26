from datetime import datetime, timedelta
from flask import jsonify, request, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import check_password_hash
from app.api import bp
from app.models.user import User
from app.models.ticket import Ticket, TicketComment, Category
from app.models.knowledge import KnowledgeArticle, FAQ
from app.models.audit import AuditLog, SystemLog
from app import db
from app.utils.decorators import api_role_required, api_permission_required, api_ticket_access_required
from app.utils.sla import get_sla_metrics, get_agent_sla_performance
import base64

# Authentication endpoints
@bp.route('/auth/login', methods=['POST'])
def api_login():
    """API login endpoint"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']) or not user.is_active:
            SystemLog.warning('api', f'Failed login attempt for {data["email"]}',
                            details={'ip_address': request.remote_addr})
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Log successful login
        AuditLog.log_user_action(
            user_id=user.id,
            target_user=user,
            action='api_login',
            description='API login successful',
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict(),
            'expires_in': current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds()
        }), 200
        
    except Exception as e:
        SystemLog.error('api', f'Login error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def api_refresh():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'error': 'User not found or inactive'}), 401
        
        new_token = create_access_token(identity=current_user_id)
        
        return jsonify({
            'access_token': new_token,
            'expires_in': current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds()
        }), 200
        
    except Exception as e:
        SystemLog.error('api', f'Token refresh error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/auth/me', methods=['GET'])
@jwt_required()
def api_me():
    """Get current user info"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        SystemLog.error('api', f'Get user error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

# Ticket endpoints
@bp.route('/tickets', methods=['GET'])
@jwt_required()
def api_get_tickets(current_api_user=None):
    """Get tickets list with filtering"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 401
        
        # Base query with access control
        if user.role == 'customer':
            query = Ticket.query.filter_by(created_by=user.id)
        else:
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
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Sort
        sort_by = request.args.get('sort_by', 'updated_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        if hasattr(Ticket, sort_by):
            if sort_order == 'asc':
                query = query.order_by(getattr(Ticket, sort_by).asc())
            else:
                query = query.order_by(getattr(Ticket, sort_by).desc())
        
        tickets = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'tickets': [ticket.to_dict() for ticket in tickets.items],
            'pagination': {
                'page': tickets.page,
                'pages': tickets.pages,
                'per_page': tickets.per_page,
                'total': tickets.total,
                'has_next': tickets.has_next,
                'has_prev': tickets.has_prev
            }
        }), 200
        
    except Exception as e:
        SystemLog.error('api', f'Get tickets error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/tickets', methods=['POST'])
@jwt_required()
def api_create_ticket():
    """Create new ticket"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 401
        
        data = request.get_json()
        
        if not data or not data.get('title') or not data.get('description'):
            return jsonify({'error': 'Title and description are required'}), 400
        
        # Create ticket
        ticket = Ticket(
            title=data['title'][:200],
            description=data['description'],
            priority=data.get('priority', 'medium'),
            created_by=user.id,
            category_id=data.get('category_id')
        )
        
        # Set SLA
        ticket.set_priority_based_sla()
        
        # Auto-assign if category has auto-assignment
        if ticket.category and ticket.category.auto_assign_to:
            ticket.assigned_to = ticket.category.auto_assign_to
        
        db.session.add(ticket)
        db.session.commit()
        
        # Log creation
        AuditLog.log_ticket_action(
            user_id=user.id,
            ticket=ticket,
            action='create',
            new_values=ticket.to_dict(),
            description=f'Ticket {ticket.ticket_number} created via API',
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'message': 'Ticket created successfully',
            'ticket': ticket.to_dict(include_details=True)
        }), 201
        
    except Exception as e:
        SystemLog.error('api', f'Create ticket error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/tickets/<int:ticket_id>', methods=['GET'])
@api_ticket_access_required()
def api_get_ticket(ticket_id, current_api_user=None, ticket=None):
    """Get single ticket details"""
    try:
        # Check SLA status
        ticket.check_sla_breach()
        if ticket.sla_breached:
            db.session.commit()
        
        return jsonify({'ticket': ticket.to_dict(include_details=True)}), 200
        
    except Exception as e:
        SystemLog.error('api', f'Get ticket error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/tickets/<int:ticket_id>', methods=['PUT'])
@api_ticket_access_required()
@api_role_required('admin', 'team_leader', 'support_agent')
def api_update_ticket(ticket_id, current_api_user=None, ticket=None):
    """Update ticket"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        old_values = {}
        new_values = {}
        
        # Update allowed fields
        updatable_fields = ['title', 'description', 'priority', 'status', 'assigned_to', 'category_id']
        
        for field in updatable_fields:
            if field in data:
                old_values[field] = getattr(ticket, field)
                setattr(ticket, field, data[field])
                new_values[field] = data[field]
        
        # Handle status changes
        if 'status' in data and data['status'] == 'resolved' and not ticket.resolved_at:
            ticket.resolved_at = datetime.utcnow()
        elif 'status' in data and data['status'] == 'closed' and not ticket.closed_at:
            ticket.closed_at = datetime.utcnow()
        
        # Recalculate SLA if priority changed
        if 'priority' in data:
            ticket.set_priority_based_sla()
        
        db.session.commit()
        
        # Log update
        AuditLog.log_ticket_action(
            user_id=current_api_user.id,
            ticket=ticket,
            action='update',
            old_values=old_values,
            new_values=new_values,
            description='Ticket updated via API',
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'message': 'Ticket updated successfully',
            'ticket': ticket.to_dict(include_details=True)
        }), 200
        
    except Exception as e:
        SystemLog.error('api', f'Update ticket error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/tickets/<int:ticket_id>/comments', methods=['GET'])
@api_ticket_access_required()
def api_get_ticket_comments(ticket_id, current_api_user=None, ticket=None):
    """Get ticket comments"""
    try:
        comments = ticket.comments.order_by(TicketComment.created_at.asc())
        
        # Filter internal comments for customers
        if current_api_user.role == 'customer':
            comments = comments.filter_by(is_internal=False)
        
        return jsonify({
            'comments': [comment.to_dict() for comment in comments.all()]
        }), 200
        
    except Exception as e:
        SystemLog.error('api', f'Get comments error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/tickets/<int:ticket_id>/comments', methods=['POST'])
@api_ticket_access_required()
def api_add_ticket_comment(ticket_id, current_api_user=None, ticket=None):
    """Add comment to ticket"""
    try:
        data = request.get_json()
        
        if not data or not data.get('content'):
            return jsonify({'error': 'Comment content is required'}), 400
        
        # Determine if comment is internal
        is_internal = False
        if current_api_user.role in ['support_agent', 'team_leader', 'admin']:
            is_internal = data.get('is_internal', False)
        
        # Add comment
        comment = ticket.add_comment(
            author_id=current_api_user.id,
            content=data['content'],
            is_internal=is_internal
        )
        
        # Update ticket status if needed
        if current_api_user.role in ['support_agent', 'team_leader', 'admin']:
            if ticket.status == 'open':
                ticket.status = 'in_progress'
        
        db.session.commit()
        
        # Log comment
        AuditLog.log_ticket_action(
            user_id=current_api_user.id,
            ticket=ticket,
            action='comment',
            new_values={'comment': comment.content, 'is_internal': is_internal},
            description='Comment added via API',
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'message': 'Comment added successfully',
            'comment': comment.to_dict()
        }), 201
        
    except Exception as e:
        SystemLog.error('api', f'Add comment error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/tickets/<int:ticket_id>/attachments', methods=['POST'])
@api_ticket_access_required()
def api_add_attachment(ticket_id, current_api_user=None, ticket=None):
    """Add attachment to ticket"""
    try:
        data = request.get_json()
        
        if not data or not data.get('filename') or not data.get('content'):
            return jsonify({'error': 'Filename and content are required'}), 400
        
        # Decode base64 content
        try:
            file_content = base64.b64decode(data['content'])
        except:
            return jsonify({'error': 'Invalid base64 content'}), 400
        
        # Check file size (16MB limit)
        if len(file_content) > 16 * 1024 * 1024:
            return jsonify({'error': 'File too large (max 16MB)'}), 400
        
        # Add attachment
        attachment = ticket.add_attachment(
            filename=data['filename'],
            content=file_content,
            content_type=data.get('content_type', 'application/octet-stream'),
            author_id=current_api_user.id
        )
        
        db.session.commit()
        
        return jsonify({
            'message': 'Attachment added successfully',
            'attachment': attachment.to_dict()
        }), 201
        
    except Exception as e:
        SystemLog.error('api', f'Add attachment error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

# Categories endpoints
@bp.route('/categories', methods=['GET'])
@jwt_required()
def api_get_categories():
    """Get categories list"""
    try:
        categories = Category.query.filter_by(is_active=True).order_by(Category.name).all()
        
        return jsonify({
            'categories': [category.to_dict() for category in categories]
        }), 200
        
    except Exception as e:
        SystemLog.error('api', f'Get categories error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

# Knowledge base endpoints
@bp.route('/kb/articles', methods=['GET'])
@jwt_required()
def api_get_articles():
    """Get knowledge base articles"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        query = KnowledgeArticle.query.filter_by(is_published=True)
        
        # Filter by visibility
        if user.role == 'customer':
            query = query.filter_by(is_public=True)
        
        # Search
        search = request.args.get('search')
        if search:
            query = query.filter(
                db.or_(
                    KnowledgeArticle.title.contains(search),
                    KnowledgeArticle.content.contains(search),
                    KnowledgeArticle.tags.contains(search)
                )
            )
        
        # Category filter
        category_id = request.args.get('category_id', type=int)
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        articles = query.order_by(
            KnowledgeArticle.is_featured.desc(),
            KnowledgeArticle.view_count.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'articles': [article.to_dict() for article in articles.items],
            'pagination': {
                'page': articles.page,
                'pages': articles.pages,
                'per_page': articles.per_page,
                'total': articles.total
            }
        }), 200
        
    except Exception as e:
        SystemLog.error('api', f'Get articles error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/kb/articles/<int:article_id>', methods=['GET'])
@jwt_required()
def api_get_article(article_id):
    """Get single knowledge base article"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        article = KnowledgeArticle.query.get_or_404(article_id)
        
        if not article.can_view(user):
            return jsonify({'error': 'Access denied'}), 403
        
        # Increment view count
        article.increment_view()
        
        return jsonify({
            'article': article.to_dict(include_content=True)
        }), 200
        
    except Exception as e:
        SystemLog.error('api', f'Get article error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

# Analytics endpoints
@bp.route('/analytics/sla', methods=['GET'])
@api_role_required('admin', 'team_leader')
def api_sla_metrics(current_api_user=None):
    """Get SLA metrics"""
    try:
        days = request.args.get('days', 30, type=int)
        metrics = get_sla_metrics(days)
        
        return jsonify({'metrics': metrics}), 200
        
    except Exception as e:
        SystemLog.error('api', f'SLA metrics error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/analytics/agent/<int:agent_id>/sla', methods=['GET'])
@api_role_required('admin', 'team_leader')
def api_agent_sla_performance(agent_id, current_api_user=None):
    """Get agent SLA performance"""
    try:
        days = request.args.get('days', 30, type=int)
        performance = get_agent_sla_performance(agent_id, days)
        
        if not performance:
            return jsonify({'error': 'No data found for this agent'}), 404
        
        return jsonify({'performance': performance}), 200
        
    except Exception as e:
        SystemLog.error('api', f'Agent SLA performance error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

# Dashboard endpoints
@bp.route('/dashboard/stats', methods=['GET'])
@jwt_required()
def api_dashboard_stats():
    """Get dashboard statistics"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        stats = user.get_dashboard_stats()
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        SystemLog.error('api', f'Dashboard stats error: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

# Error handlers
@bp.errorhandler(404)
def api_not_found(error):
    return jsonify({'error': 'Not found'}), 404

@bp.errorhandler(400)
def api_bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@bp.errorhandler(403)
def api_forbidden(error):
    return jsonify({'error': 'Forbidden'}), 403

@bp.errorhandler(500)
def api_internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500