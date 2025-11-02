#!/usr/bin/env python
"""
Test script to generate widget embed codes
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpdesk.settings')
django.setup()

from django.conf import settings
from apps.admin_panel.models import SystemSettings
from apps.chat.models import ChatSettings

def generate_widget_codes():
    """Generate widget embed codes"""
    
    # Get settings
    system_settings = SystemSettings.get_settings()
    chat_settings = ChatSettings.get_settings()
    
    # Generate codes (same logic as in views.py)
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
    
    print("WIDGET EMBED CODES GENERIERT:")
    print("=" * 60)
    print(f"Widget URL: {widget_url}")
    print(f"Site URL: {site_url}")
    print(f"Chat enabled: {chat_settings.is_enabled}")
    print("=" * 60)
    
    print("\nHTML IFRAME CODE:")
    print("-" * 40)
    print(embed_code)
    
    print("\nJAVASCRIPT CODE:")
    print("-" * 40)
    print(js_embed_code)
    
    print("\nDie Codes sind bereit zur Verwendung!")
    print("Loggen Sie sich als Admin ein und besuchen Sie: http://localhost:8000/settings/")

if __name__ == "__main__":
    generate_widget_codes()