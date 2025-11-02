#!/usr/bin/env python
"""
Check if admin can access settings page and see widget integration
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpdesk.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model

def check_admin_access():
    User = get_user_model()
    admin = User.objects.filter(is_superuser=True).first()
    
    if not admin:
        print("FEHLER: Kein Admin-User gefunden!")
        return
    
    print(f"Admin gefunden: {admin.username}")
    print(f"Admin ist superuser: {admin.is_superuser}")
    print(f"Admin ist aktiv: {admin.is_active}")
    
    # Test mit Django Test Client
    client = Client()
    
    # Login admin
    login_success = client.force_login(admin)
    print(f"Login erfolgreich: {login_success}")
    
    # Teste Dashboard
    response = client.get('/')
    print(f"Dashboard Status: {response.status_code}")
    
    # Teste Settings
    response = client.get('/settings/')
    print(f"Settings Status: {response.status_code}")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8', errors='ignore')
        
        # Prüfe Widget Integration Sektion
        if 'Chat Widget Integration' in content:
            print("✓ Chat Widget Integration Sektion gefunden!")
        else:
            print("✗ Chat Widget Integration Sektion NICHT gefunden!")
            
        # Prüfe Widget URL
        if 'chat/widget/' in content:
            print("✓ Widget URL gefunden!")
        else:
            print("✗ Widget URL NICHT gefunden!")
            
        # Prüfe Embed Code
        if 'iframe src=' in content:
            print("✓ iframe Embed Code gefunden!")
        else:
            print("✗ iframe Embed Code NICHT gefunden!")
            
        # Prüfe aktuelle Einstellungen
        if 'System Settings' in content and 'Chat Settings' in content:
            print("✓ Aktuelle Einstellungen Formulare gefunden!")
        else:
            print("✗ Aktuelle Einstellungen Formulare NICHT gefunden!")
            
        # Speichere Debug-Ausgabe
        with open('debug_admin_settings.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Settings HTML gespeichert in: debug_admin_settings.html")
        
    elif response.status_code == 302:
        print("UMLEITUNG - möglicherweise nicht eingeloggt")
        print(f"Umleitung zu: {response.get('Location', 'unbekannt')}")
    elif response.status_code == 403:
        print("ZUGRIFF VERWEIGERT - keine Admin-Berechtigung")
    else:
        print(f"UNBEKANNTER FEHLER: Status {response.status_code}")

if __name__ == "__main__":
    check_admin_access()