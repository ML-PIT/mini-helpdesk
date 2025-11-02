from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth import get_user_model
from .forms import UserCreateForm, UserEditForm
from django.views.decorators.http import require_http_methods
import json

User = get_user_model()


def can_manage_users(user, target_role=None):
    """
    Check if user can manage other users based on role hierarchy:
    - Admins: Can manage everyone
    - Support Agents Level 4: Can manage Support Agents (Level 1-3) and Customers
    - Support Agents Level 1-3: Can manage Customers only
    - Customers: Cannot manage anyone
    """
    if not user.is_authenticated:
        return False
    
    if user.role == 'admin':
        return True
    
    if user.role == 'support_agent':
        if user.support_level == 4:
            # Level 4 can manage customers and support agents level 1-3
            return target_role in ['customer', 'support_agent'] if target_role else True
        else:
            # Level 1-3 can only manage customers
            return target_role == 'customer' if target_role else True
    
    # Customers cannot manage anyone
    return False


def can_edit_user(current_user, target_user):
    """Check if current user can edit target user"""
    if not can_manage_users(current_user):
        return False
    
    # Admin can edit everyone
    if current_user.role == 'admin':
        return True
    
    # Support agents can edit based on rules
    if current_user.role == 'support_agent':
        if current_user.support_level == 4:
            # Level 4 can edit customers and support agents level 1-3
            if target_user.role == 'customer':
                return True
            if target_user.role == 'support_agent' and target_user.support_level < 4:
                return True
            return False
        else:
            # Level 1-3 can only edit customers
            return target_user.role == 'customer'
    
    return False


@login_required
def user_list(request):
    """List all users with filtering based on permissions"""
    if not can_manage_users(request.user):
        return HttpResponseForbidden('Sie haben keine Berechtigung zur Benutzerverwaltung.')
    
    # Base queryset
    users = User.objects.all().order_by('-created_at')
    
    # Filter based on permissions
    if request.user.role == 'support_agent' and request.user.support_level != 4:
        # Level 1-3 can only see customers
        users = users.filter(role='customer')
    elif request.user.role == 'support_agent' and request.user.support_level == 4:
        # Level 4 can see customers and support agents level 1-3
        users = users.filter(
            Q(role='customer') | 
            (Q(role='support_agent') & Q(support_level__lt=4))
        )
    # Admins can see everyone (no additional filter)
    
    # Search functionality
    search = request.GET.get('search', '')
    if search:
        users = users.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(username__icontains=search)
        )
    
    # Role filter
    role_filter = request.GET.get('role', '')
    if role_filter:
        users = users.filter(role=role_filter)
    
    # Status filter
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    # Pagination
    paginator = Paginator(users, 20)  # 20 users per page
    page_number = request.GET.get('page')
    users_page = paginator.get_page(page_number)
    
    # Available roles for filter dropdown
    available_roles = []
    if request.user.role == 'admin':
        available_roles = User.ROLE_CHOICES
    elif request.user.role == 'support_agent':
        if request.user.support_level == 4:
            available_roles = [('customer', 'Customer'), ('support_agent', 'Support Agent')]
        else:
            available_roles = [('customer', 'Customer')]
    
    context = {
        'users': users_page,
        'search': search,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'available_roles': available_roles,
        'can_create_users': can_manage_users(request.user),
    }
    
    return render(request, 'accounts/user_management/user_list.html', context)


@login_required
def user_create(request):
    """Create a new user"""
    if not can_manage_users(request.user):
        return HttpResponseForbidden('Sie haben keine Berechtigung neue Benutzer zu erstellen.')
    
    if request.method == 'POST':
        form = UserCreateForm(request.POST, current_user=request.user)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f'Benutzer "{user.full_name}" wurde erfolgreich erstellt.')
                return redirect('accounts:user_list')
            except Exception as e:
                messages.error(request, f'Fehler beim Speichern des Benutzers: {str(e)}')
        else:
            # Debug: Show form errors with details
            messages.error(request, 'Das Formular enthält Fehler:')
            for field, errors in form.errors.items():
                for error in errors:
                    field_label = form.fields.get(field, {}).label if hasattr(form.fields.get(field, {}), 'label') else field
                    messages.error(request, f'{field_label or field}: {error}')
            
            # Additional debug info
            if form.non_field_errors():
                for error in form.non_field_errors():
                    messages.error(request, f'Allgemeiner Fehler: {error}')
    else:
        form = UserCreateForm(current_user=request.user)
    
    context = {
        'form': form,
        'action': 'create',
    }
    
    return render(request, 'accounts/user_management/user_form.html', context)


@login_required
def user_edit(request, user_id):
    """Edit an existing user"""
    target_user = get_object_or_404(User, id=user_id)
    
    if not can_edit_user(request.user, target_user):
        return HttpResponseForbidden('Sie haben keine Berechtigung diesen Benutzer zu bearbeiten.')
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=target_user, current_user=request.user)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Benutzer "{user.full_name}" wurde erfolgreich aktualisiert.')
            return redirect('accounts:user_list')
    else:
        form = UserEditForm(instance=target_user, current_user=request.user)
    
    context = {
        'form': form,
        'action': 'edit',
        'target_user': target_user,
    }
    
    return render(request, 'accounts/user_management/user_form.html', context)


@login_required
def user_detail(request, user_id):
    """View user details"""
    target_user = get_object_or_404(User, id=user_id)
    
    if not can_edit_user(request.user, target_user):
        return HttpResponseForbidden('Sie haben keine Berechtigung diesen Benutzer zu sehen.')
    
    context = {
        'target_user': target_user,
        'can_edit': can_edit_user(request.user, target_user),
    }
    
    return render(request, 'accounts/user_management/user_detail.html', context)


@login_required
@require_http_methods(["POST"])
def user_toggle_status(request, user_id):
    """Toggle user active status (AJAX endpoint)"""
    target_user = get_object_or_404(User, id=user_id)
    
    if not can_edit_user(request.user, target_user):
        return JsonResponse({'success': False, 'error': 'Keine Berechtigung'})
    
    # Prevent disabling self
    if target_user == request.user:
        return JsonResponse({'success': False, 'error': 'Sie können sich nicht selbst deaktivieren'})
    
    target_user.is_active = not target_user.is_active
    target_user.save()
    
    status_text = "aktiviert" if target_user.is_active else "deaktiviert"
    
    return JsonResponse({
        'success': True,
        'is_active': target_user.is_active,
        'message': f'Benutzer wurde {status_text}.'
    })


@login_required
@require_http_methods(["POST"])
def user_reset_password(request, user_id):
    """Reset user password (AJAX endpoint)"""
    target_user = get_object_or_404(User, id=user_id)
    
    if not can_edit_user(request.user, target_user):
        return JsonResponse({'success': False, 'error': 'Keine Berechtigung'})
    
    # Generate temporary password
    import string
    import random
    temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    
    target_user.set_password(temp_password)
    target_user.force_password_change = True
    target_user.save()
    
    return JsonResponse({
        'success': True,
        'temp_password': temp_password,
        'message': 'Temporäres Passwort wurde generiert. Der Benutzer muss es beim nächsten Login ändern.'
    })