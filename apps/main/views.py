from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.conf import settings


@login_required
def dashboard(request):
    """Main dashboard view"""
    context = {
        'stats': request.user.get_dashboard_stats() if hasattr(request.user, 'get_dashboard_stats') else {}
    }
    return render(request, 'dashboard/index.html', context)


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard class-based view"""
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stats'] = self.request.user.get_dashboard_stats()
        return context


@login_required
def admin_settings(request):
    """Admin settings view - combines System Settings and Chat Settings"""
    
    # Check if user is admin
    if not (request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role == 'admin')):
        return HttpResponseForbidden('Sie haben keine Berechtigung, diese Seite zu sehen.')
    
    from apps.admin_panel.models import SystemSettings
    from apps.chat.models import ChatSettings
    from apps.main.forms import AdminSettingsForm
    
    # Get or create settings objects
    system_settings = SystemSettings.get_settings()
    chat_settings = ChatSettings.get_settings()
    
    if request.method == 'POST':
        form = AdminSettingsForm(request.POST, request.FILES, 
                                system_settings=system_settings, 
                                chat_settings=chat_settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Einstellungen wurden erfolgreich gespeichert!')
            return redirect('main:admin_settings')
    else:
        form = AdminSettingsForm(system_settings=system_settings, chat_settings=chat_settings)
    
    # Generate chat widget embed code
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
    widget_url = f"{site_url}/chat/widget/"
    
    embed_code = f'''<!-- Aboro-IT Helpdesk Live Chat Widget -->
<iframe src="{widget_url}" 
        width="400" 
        height="600" 
        frameborder="0" 
        style="position: fixed; bottom: 20px; right: 20px; z-index: 9999; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
</iframe>'''

    # Alternative: JavaScript embed code
    js_embed_code = f'''<!-- Aboro-IT Helpdesk Live Chat Widget (JavaScript) -->
<script>
(function() {{
    var iframe = document.createElement('iframe');
    iframe.src = '{widget_url}';
    iframe.width = '400';
    iframe.height = '600';
    iframe.frameBorder = '0';
    iframe.style.cssText = 'position: fixed; bottom: 20px; right: 20px; z-index: 9999; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);';
    
    // Auto-open chat when loaded in iframe
    iframe.onload = function() {{
        try {{
            iframe.contentWindow.postMessage({{'action': 'openChat'}}, '{site_url}');
        }} catch(e) {{
            console.log('Chat widget loaded');
        }}
    }};
    
    document.body.appendChild(iframe);
}})();
</script>'''

    context = {
        'form': form,
        'system_settings': system_settings,
        'chat_settings': chat_settings,
        'site_url': site_url,
        'widget_url': widget_url,
        'embed_code': embed_code,
        'js_embed_code': js_embed_code,
    }
    
    return render(request, 'main/admin_settings.html', context)


def debug_widget_codes(request):
    """Debug view to show widget codes without login requirement"""
    from apps.admin_panel.models import SystemSettings
    from apps.chat.models import ChatSettings
    
    # Get settings
    system_settings = SystemSettings.get_settings()
    chat_settings = ChatSettings.get_settings()
    
    # Generate widget codes
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
    widget_url = f"{site_url}/chat/widget/"
    
    embed_code = f'''<!-- Aboro-IT Helpdesk Live Chat Widget -->
<iframe src="{widget_url}" 
        width="400" 
        height="600" 
        frameborder="0" 
        style="position: fixed; bottom: 20px; right: 20px; z-index: 9999; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
</iframe>'''

    js_embed_code = f'''<!-- Aboro-IT Helpdesk Live Chat Widget (JavaScript) -->
<script>
(function() {{
    var iframe = document.createElement('iframe');
    iframe.src = '{widget_url}';
    iframe.width = '400';
    iframe.height = '600';
    iframe.frameBorder = '0';
    iframe.style.cssText = 'position: fixed; bottom: 20px; right: 20px; z-index: 9999; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);';
    document.body.appendChild(iframe);
}})();
</script>'''
    
    context = {
        'site_url': site_url,
        'widget_url': widget_url,
        'embed_code': embed_code,
        'js_embed_code': js_embed_code,
        'system_settings': system_settings,
        'chat_settings': chat_settings,
    }
    
    return render(request, 'main/debug_widget.html', context)
