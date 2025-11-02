#!/usr/bin/env python
"""
Debug script to test admin settings view
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpdesk.settings')
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth import get_user_model
from apps.main.views import admin_settings
from apps.admin_panel.models import SystemSettings
from apps.chat.models import ChatSettings

def test_admin_settings():
    User = get_user_model()
    admin = User.objects.filter(is_superuser=True).first()
    
    if not admin:
        print("ERROR: Kein Admin-User gefunden!")
        return
    
    print(f"Admin user: {admin.username}")
    
    # Test with RequestFactory
    factory = RequestFactory()
    request = factory.get('/settings/')
    request.user = admin
    
    try:
        # Test if settings objects exist
        system_settings = SystemSettings.get_settings()
        chat_settings = ChatSettings.get_settings()
        print(f"SystemSettings ID: {system_settings.id}")
        print(f"ChatSettings ID: {chat_settings.id}")
        
        # Test the view
        response = admin_settings(request)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode()
            if 'Chat Widget Integration' in content:
                print("SUCCESS: Chat Widget Integration section found!")
                
                # Check for embed code
                if 'embed_code' in content:
                    print("SUCCESS: embed_code variable found in template!")
                else:
                    print("WARNING: embed_code variable not found in template")
                    
                # Check for widget_url
                if 'widget_url' in content:
                    print("SUCCESS: widget_url variable found in template!")
                else:
                    print("WARNING: widget_url variable not found in template")
            else:
                print("ERROR: Chat Widget Integration section not found!")
        else:
            print(f"ERROR: Response status {response.status_code}")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_admin_settings()