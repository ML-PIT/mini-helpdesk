"""
Context processors to make settings available to all templates.
"""
from django.conf import settings


def branding_context(request):
    """
    Add customizable branding settings to template context.

    Makes the following variables available in all templates:
    - app_name: Application name (navbar brand)
    - company_name: Company name for branding
    - logo_url: URL to company logo
    - app_title: Application title for HTML title tags
    """
    return {
        'app_name': settings.APP_NAME,
        'company_name': settings.COMPANY_NAME,
        'logo_url': settings.LOGO_URL,
        'app_title': settings.APP_TITLE,
    }
