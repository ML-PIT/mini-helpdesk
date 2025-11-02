from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from django.views.decorators.http import require_http_methods
from .models import User
from .forms import ProfileForm, PasswordChangeForm as ProfilePasswordChangeForm


def register(request):
    """Customer/Trainer self-registration"""
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        department = request.POST.get('department', '')
        location = request.POST.get('location', '')

        # Validate
        if not all([username, email, password, first_name, last_name, phone]):
            messages.error(request, 'Bitte füllen Sie alle Pflichtfelder aus.')
            return render(request, 'accounts/register.html')

        if password != password_confirm:
            messages.error(request, 'Passwörter stimmen nicht überein.')
            return render(request, 'accounts/register.html')

        if len(password) < 8:
            messages.error(request, 'Passwort muss mindestens 8 Zeichen lang sein.')
            return render(request, 'accounts/register.html')

        # Check if user exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Ein Benutzer mit dieser Email existiert bereits.')
            return render(request, 'accounts/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Dieser Benutzername ist bereits vergeben.')
            return render(request, 'accounts/register.html')

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            department=department,
            location=location,
            role='customer'
        )

        # Auto-login after registration
        login(request, user)

        messages.success(request, f'Willkommen {user.first_name}! Ihr Account wurde erfolgreich erstellt.')
        return redirect('main:dashboard')

    return render(request, 'accounts/register.html')


@login_required
def profile_edit(request):
    """
    User profile edit view - allows users to change their personal data and password
    """
    if request.method == 'POST':
        action = request.POST.get('action')  # 'profile' or 'password'

        if action == 'profile':
            # Handle profile updates
            profile_form = ProfileForm(request.POST, instance=request.user)
            password_form = ProfilePasswordChangeForm(request.user)

            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Ihr Profil wurde erfolgreich aktualisiert!')
                return redirect('accounts:profile_edit')
            else:
                for field, errors in profile_form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')

        elif action == 'password':
            # Handle password change
            profile_form = ProfileForm(instance=request.user)
            password_form = ProfilePasswordChangeForm(request.user, request.POST)

            if password_form.is_valid():
                # Update password
                request.user.set_password(password_form.cleaned_data['new_password'])
                request.user.save()

                # Keep the user logged in after password change
                update_session_auth_hash(request, request.user)

                messages.success(request, 'Ihr Passwort wurde erfolgreich geändert!')
                return redirect('accounts:profile_edit')
            else:
                for field, errors in password_form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
    else:
        profile_form = ProfileForm(instance=request.user)
        password_form = ProfilePasswordChangeForm(request.user)

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'user': request.user,
    }
    return render(request, 'accounts/profile_edit.html', context)


@login_required
def change_password(request):
    """
    Change password view - especially for users who must change password on first login
    """
    force_change = request.user.force_password_change

    if request.method == 'POST':
        form = ProfilePasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            # Save the new password
            user = form.save()
            
            # If this was a forced password change, clear the flag
            if force_change:
                user.force_password_change = False
                user.save()

            # Keep the user logged in after password change
            update_session_auth_hash(request, request.user)

            messages.success(request, 'Ihr Passwort wurde erfolgreich geändert!')
            return redirect('main:dashboard')
        else:
            # Show form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ProfilePasswordChangeForm(request.user)

    context = {
        'form': form,
        'force_change': force_change,
    }
    return render(request, 'accounts/change_password.html', context)
