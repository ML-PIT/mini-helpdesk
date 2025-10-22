"""
Middleware to enforce password change on first login
"""
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required


class ForcePasswordChangeMiddleware:
    """
    Middleware that redirects users who need to change their password
    to the password change page
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Paths where password change is not required
        self.exempt_paths = [
            reverse('accounts:change_password'),
            '/api/',
            '/admin/',
            '/logout/',
            '/static/',
            '/media/',
        ]

    def __call__(self, request):
        # Check if user is authenticated and needs to change password
        if request.user.is_authenticated and request.user.force_password_change:
            # Allow access to password change view and exempt paths
            is_exempt = any(
                request.path.startswith(path) or request.path == path
                for path in self.exempt_paths
            )

            if not is_exempt:
                # Redirect to password change page
                return redirect('accounts:change_password')

        response = self.get_response(request)
        return response
