"""
Context processors for admin app
"""
from .models import SystemSettings


def admin_settings_context(request):
    """
    Add admin settings to context for all templates
    """
    try:
        settings = SystemSettings.get_settings()
        return {
            'system_settings': settings,
            'text_editor': settings.text_editor,
            'admin_app_name': settings.app_name,
            'admin_company_name': settings.company_name,
            'admin_logo': settings.logo,
            'stats_permissions': settings.get_stats_permissions(),
        }
    except:
        return {
            'text_editor': 'tinymce',
            'admin_app_name': 'Helpdesk',
            'admin_company_name': 'Company',
            'admin_logo': None,
            'stats_permissions': {'admin': True, 'support_agent': False, 'customer': False},
        }
