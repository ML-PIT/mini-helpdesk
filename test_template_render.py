#!/usr/bin/env python
"""
Test template rendering
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpdesk.settings')
django.setup()

from django.template.loader import render_to_string
from django.conf import settings
from apps.admin_panel.models import SystemSettings
from apps.chat.models import ChatSettings
from apps.main.forms import AdminSettingsForm

def test_template():
    # Get settings
    system_settings = SystemSettings.get_settings()
    chat_settings = ChatSettings.get_settings()
    form = AdminSettingsForm(system_settings=system_settings, chat_settings=chat_settings)
    
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
        'form': form,
        'system_settings': system_settings,
        'chat_settings': chat_settings,
        'site_url': site_url,
        'widget_url': widget_url,
        'embed_code': embed_code,
        'js_embed_code': js_embed_code,
    }
    
    try:
        # Render template
        html = render_to_string('main/admin_settings.html', context)
        
        print("Template rendered successfully!")
        print(f"HTML length: {len(html)}")
        
        # Check for widget integration section
        if 'Chat Widget Integration' in html:
            print("SUCCESS: Chat Widget Integration section found")
        else:
            print("ERROR: Chat Widget Integration section NOT found")
            
        if widget_url in html:
            print(f"SUCCESS: widget_url found: {widget_url}")
        else:
            print("ERROR: widget_url NOT found in rendered HTML")
            
        if 'iframe src=' in html:
            print("SUCCESS: iframe code found in HTML")
        else:
            print("ERROR: iframe code NOT found in HTML")
            
        # Save rendered HTML for inspection
        with open('debug_rendered.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("Rendered HTML saved to debug_rendered.html")
            
    except Exception as e:
        print(f"Template rendering failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_template()