from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .models import User


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
