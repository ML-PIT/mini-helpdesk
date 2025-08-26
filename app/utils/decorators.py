from functools import wraps
from flask import abort, request, jsonify, current_app
from flask_login import current_user
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.audit import SystemLog

def role_required(*allowed_roles):
    """
    Decorator to require specific user roles
    Usage: @role_required('admin', 'team_leader')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)  # Unauthorized
            
            if current_user.role not in allowed_roles:
                # Log unauthorized access attempt
                SystemLog.warning('security', 
                    f'Unauthorized access attempt by user {current_user.email} to {request.endpoint}',
                    user_id=current_user.id,
                    details={
                        'required_roles': list(allowed_roles),
                        'user_role': current_user.role,
                        'endpoint': request.endpoint,
                        'ip_address': request.remote_addr
                    }
                )
                abort(403)  # Forbidden
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def permission_required(permission):
    """
    Decorator to require specific permission
    Usage: @permission_required('manage_users')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            
            if not current_user.has_permission(permission):
                SystemLog.warning('security',
                    f'Permission denied for user {current_user.email} accessing {request.endpoint}',
                    user_id=current_user.id,
                    details={
                        'required_permission': permission,
                        'user_role': current_user.role,
                        'endpoint': request.endpoint,
                        'ip_address': request.remote_addr
                    }
                )
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator to require admin role"""
    return role_required('admin')(f)

def agent_or_admin_required(f):
    """Decorator to require agent, team leader or admin role"""
    return role_required('admin', 'team_leader', 'support_agent')(f)

def api_role_required(*allowed_roles):
    """
    API version of role_required that returns JSON responses
    Usage: @api_role_required('admin', 'team_leader')
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or not user.is_active:
                return jsonify({'error': 'User not found or inactive'}), 401
            
            if user.role not in allowed_roles:
                SystemLog.warning('security',
                    f'API unauthorized access attempt by user {user.email} to {request.endpoint}',
                    user_id=user.id,
                    details={
                        'required_roles': list(allowed_roles),
                        'user_role': user.role,
                        'endpoint': request.endpoint,
                        'ip_address': request.remote_addr
                    }
                )
                return jsonify({
                    'error': 'Insufficient permissions',
                    'required_roles': list(allowed_roles)
                }), 403
            
            # Add user to kwargs so it can be used in the route
            kwargs['current_api_user'] = user
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def api_permission_required(permission):
    """
    API version of permission_required
    Usage: @api_permission_required('manage_users')
    """
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or not user.is_active:
                return jsonify({'error': 'User not found or inactive'}), 401
            
            if not user.has_permission(permission):
                SystemLog.warning('security',
                    f'API permission denied for user {user.email} accessing {request.endpoint}',
                    user_id=user.id,
                    details={
                        'required_permission': permission,
                        'user_role': user.role,
                        'endpoint': request.endpoint,
                        'ip_address': request.remote_addr
                    }
                )
                return jsonify({
                    'error': 'Insufficient permissions',
                    'required_permission': permission
                }), 403
            
            kwargs['current_api_user'] = user
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def ticket_access_required(get_ticket_func=None):
    """
    Decorator to check if user can access a specific ticket
    Usage: @ticket_access_required() - ticket will be passed as first argument
           @ticket_access_required(lambda: get_ticket_by_id(ticket_id)) - custom function to get ticket
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            
            # Get ticket from arguments or custom function
            if get_ticket_func:
                ticket = get_ticket_func()
            else:
                # Assume ticket is the first argument
                ticket = args[0] if args else None
            
            if not ticket:
                abort(404)
            
            if not current_user.can_access_ticket(ticket):
                SystemLog.warning('security',
                    f'Ticket access denied for user {current_user.email} to ticket {ticket.ticket_number}',
                    user_id=current_user.id,
                    details={
                        'ticket_id': ticket.id,
                        'ticket_number': ticket.ticket_number,
                        'user_role': current_user.role,
                        'ip_address': request.remote_addr
                    }
                )
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def api_ticket_access_required(get_ticket_func=None):
    """API version of ticket_access_required"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or not user.is_active:
                return jsonify({'error': 'User not found or inactive'}), 401
            
            # Get ticket from arguments or custom function
            if get_ticket_func:
                ticket = get_ticket_func()
            else:
                # Try to get ticket_id from URL parameters
                ticket_id = kwargs.get('ticket_id') or request.view_args.get('ticket_id')
                if ticket_id:
                    from app.models.ticket import Ticket
                    ticket = Ticket.query.get(ticket_id)
                else:
                    return jsonify({'error': 'Ticket not specified'}), 400
            
            if not ticket:
                return jsonify({'error': 'Ticket not found'}), 404
            
            if not user.can_access_ticket(ticket):
                SystemLog.warning('security',
                    f'API ticket access denied for user {user.email} to ticket {ticket.ticket_number}',
                    user_id=user.id,
                    details={
                        'ticket_id': ticket.id,
                        'ticket_number': ticket.ticket_number,
                        'user_role': user.role,
                        'ip_address': request.remote_addr
                    }
                )
                return jsonify({
                    'error': 'Access denied',
                    'message': 'You do not have permission to access this ticket'
                }), 403
            
            kwargs['current_api_user'] = user
            kwargs['ticket'] = ticket
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def rate_limit_by_role():
    """Apply different rate limits based on user role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated:
                if current_user.role == 'customer':
                    # Apply customer rate limit
                    from flask_limiter import Limiter
                    # This would be configured in the app factory
                    pass
                # Agents and admins get higher limits
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_action(action_type, entity_type=None):
    """
    Decorator to automatically log actions
    Usage: @log_action('create', 'ticket')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            result = f(*args, **kwargs)
            
            if current_user.is_authenticated:
                from app.models.audit import AuditLog
                
                # Extract entity info from result if it's a model instance
                entity_id = None
                if hasattr(result, 'id'):
                    entity_id = result.id
                elif isinstance(result, dict) and 'id' in result:
                    entity_id = result['id']
                
                AuditLog.log_action(
                    user_id=current_user.id,
                    entity_type=entity_type or 'unknown',
                    entity_id=entity_id,
                    action=action_type,
                    description=f'{action_type.title()} {entity_type or "entity"}',
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent')
                )
            
            return result
        return decorated_function
    return decorator