import uuid
import requests
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlencode, urlparse as url_parse
import msal
from app.auth import bp
from app.models.user import User
from app.models.audit import AuditLog, SystemLog
from app import db
from app.auth.forms import LoginForm, RegisterForm
from app.utils.decorators import role_required

def _build_msal_app(cache=None, authority=None):
    """Build MSAL application"""
    return msal.ConfidentialClientApplication(
        current_app.config['MICROSOFT_CLIENT_ID'],
        authority=authority or current_app.config['MICROSOFT_AUTHORITY'],
        client_credential=current_app.config['MICROSOFT_CLIENT_SECRET'],
        token_cache=cache)

def _build_auth_code_flow(authority=None, scopes=None):
    """Build auth code flow"""
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or current_app.config['MICROSOFT_SCOPE'],
        redirect_uri=url_for('auth.oauth_callback', _external=True))

def _get_token_from_cache(scope=None):
    """Get token from cache"""
    cache = _load_cache()
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result

def _load_cache():
    """Load MSAL token cache from session"""
    cache = msal.SerializableTokenCache()
    if session.get('token_cache'):
        cache.deserialize(session['token_cache'])
    return cache

def _save_cache(cache):
    """Save MSAL token cache to session"""
    if cache.has_state_changed:
        session['token_cache'] = cache.serialize()

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with both local and OAuth options"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    # Handle local login form submission
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data) and user.is_active:
            login_user(user, remember=form.remember_me.data)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Log successful login
            AuditLog.log_user_action(
                user_id=user.id,
                target_user=user,
                action='login',
                description='Local login successful',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('main.index')
            return redirect(next_page)
        
        # Log failed login attempt
        SystemLog.warning('auth', f'Failed login attempt for {form.email.data}', 
                         details={'ip_address': request.remote_addr})
        
        flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/oauth_login')
def oauth_login():
    """Initiate OAuth2 login with Microsoft"""
    # Generate state parameter for CSRF protection
    session['flow'] = _build_auth_code_flow(scopes=current_app.config['MICROSOFT_SCOPE'])
    
    # Log OAuth attempt
    SystemLog.info('auth', 'OAuth login initiated', 
                  details={'ip_address': request.remote_addr})
    
    return redirect(session['flow']['auth_uri'])

@bp.route('/oauth_callback')
def oauth_callback():
    """Handle OAuth2 callback from Microsoft"""
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get('flow', {}), request.args)
        
        if 'error' in result:
            SystemLog.error('auth', f"OAuth error: {result.get('error_description')}")
            flash('Authentication failed. Please try again.', 'error')
            return redirect(url_for('auth.login'))
        
        _save_cache(cache)
        
        # Get user info from Microsoft Graph
        user_info = _get_user_profile(result['access_token'])
        
        if not user_info:
            flash('Failed to retrieve user information.', 'error')
            return redirect(url_for('auth.login'))
        
        # Find or create user
        user = User.query.filter_by(microsoft_id=user_info['id']).first()
        
        if not user:
            # Check if user exists by email
            user = User.query.filter_by(email=user_info['mail'] or user_info['userPrincipalName']).first()
            
            if user:
                # Link existing account to Microsoft
                user.microsoft_id = user_info['id']
            else:
                # Create new user
                user = User(
                    username=user_info['mailNickname'] or user_info['userPrincipalName'].split('@')[0],
                    email=user_info['mail'] or user_info['userPrincipalName'],
                    first_name=user_info['givenName'] or '',
                    last_name=user_info['surname'] or '',
                    microsoft_id=user_info['id'],
                    role='customer',  # Default role
                    email_verified=True,
                    is_active=True
                )
                db.session.add(user)
        
        # Update Microsoft token and user info
        user.microsoft_token = result.get('access_token')
        user.last_login = datetime.utcnow()
        
        # Update profile information from Microsoft
        if user_info.get('givenName'):
            user.first_name = user_info['givenName']
        if user_info.get('surname'):
            user.last_name = user_info['surname']
        
        db.session.commit()
        
        login_user(user, remember=True)
        
        # Log successful OAuth login
        AuditLog.log_user_action(
            user_id=user.id,
            target_user=user,
            action='oauth_login',
            description='Microsoft OAuth login successful',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        flash(f'Welcome {user.full_name}!', 'success')
        return redirect(url_for('main.index'))
        
    except Exception as e:
        SystemLog.error('auth', f'OAuth callback error: {str(e)}', 
                       details={'error': str(e), 'ip_address': request.remote_addr})
        
        flash('Authentication failed. Please try again.', 'error')
        return redirect(url_for('auth.login'))

def _get_user_profile(access_token):
    """Get user profile from Microsoft Graph API"""
    try:
        graph_url = 'https://graph.microsoft.com/v1.0/me'
        headers = {'Authorization': f'Bearer {access_token}'}
        
        response = requests.get(graph_url, headers=headers)
        response.raise_for_status()
        
        return response.json()
        
    except requests.RequestException as e:
        SystemLog.error('auth', f'Failed to get user profile: {str(e)}')
        return None

@bp.route('/logout')
@login_required
def logout():
    """Logout user"""
    user_id = current_user.id
    
    # Log logout
    AuditLog.log_user_action(
        user_id=user_id,
        target_user=current_user,
        action='logout',
        description='User logged out',
        ip_address=request.remote_addr
    )
    
    logout_user()
    
    # Clear session
    session.clear()
    
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration (for local accounts only)"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Check if registration is enabled
    if not current_app.config.get('ALLOW_REGISTRATION', False):
        flash('Registration is currently disabled. Please contact an administrator.', 'error')
        return redirect(url_for('auth.login'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        # Check if user already exists
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already taken.', 'error')
            return redirect(url_for('auth.register'))
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role='customer',
            is_active=True,
            email_verified=False  # Require email verification
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        # Log user registration
        AuditLog.log_user_action(
            user_id=user.id,
            target_user=user,
            action='register',
            description='User registered locally',
            ip_address=request.remote_addr
        )
        
        SystemLog.info('auth', f'New user registered: {user.email}', user_id=user.id)
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('auth/profile.html', title='Profile')

@bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    from app.auth.forms import EditProfileForm
    
    form = EditProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        old_values = {
            'first_name': current_user.first_name,
            'last_name': current_user.last_name,
            'phone': current_user.phone,
            'department': current_user.department,
            'location': current_user.location
        }
        
        # Update user
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.phone = form.phone.data
        current_user.department = form.department.data
        current_user.location = form.location.data
        
        db.session.commit()
        
        new_values = {
            'first_name': current_user.first_name,
            'last_name': current_user.last_name,
            'phone': current_user.phone,
            'department': current_user.department,
            'location': current_user.location
        }
        
        # Log profile update
        AuditLog.log_user_action(
            user_id=current_user.id,
            target_user=current_user,
            action='update_profile',
            old_values=old_values,
            new_values=new_values,
            description='Profile updated',
            ip_address=request.remote_addr
        )
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/edit_profile.html', title='Edit Profile', form=form)

@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password (local accounts only)"""
    if current_user.microsoft_id:
        flash('Password changes are not available for Microsoft accounts.', 'info')
        return redirect(url_for('auth.profile'))
    
    from app.auth.forms import ChangePasswordForm
    
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'error')
            return render_template('auth/change_password.html', form=form)
        
        current_user.set_password(form.new_password.data)
        db.session.commit()
        
        # Log password change
        AuditLog.log_user_action(
            user_id=current_user.id,
            target_user=current_user,
            action='change_password',
            description='Password changed',
            ip_address=request.remote_addr
        )
        
        flash('Password changed successfully!', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/change_password.html', title='Change Password', form=form)