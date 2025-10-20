# Flask zu Django Migration - ML Gruppe Helpdesk

## Übersicht

Dieses Dokument beschreibt die vollständige Migration des ML Gruppe Helpdesk Systems von Flask nach Django.

## Projektstruktur

```
mini-helpdesk/
├── manage.py                  # Django Management Script
├── helpdesk/                  # Django Projekt-Konfiguration
│   ├── __init__.py
│   ├── settings.py           # Django Settings
│   ├── urls.py               # Haupt-URL-Konfiguration
│   ├── wsgi.py               # WSGI Entry Point
│   ├── asgi.py               # ASGI Entry Point
│   └── celery.py             # Celery-Konfiguration
├── apps/                      # Django Applications
│   ├── accounts/             # Benutzer & Authentifizierung
│   │   ├── models.py         # User-Model
│   │   ├── views.py          # Auth-Views
│   │   ├── forms.py          # Login/Register-Forms
│   │   ├── urls.py           # Auth-URLs
│   │   ├── admin.py          # Admin-Interface
│   │   ├── serializers.py    # API-Serializer
│   │   └── backends.py       # Microsoft OAuth Backend
│   ├── tickets/              # Ticket-System
│   │   ├── models.py         # Ticket, Comment, Attachment Models
│   │   ├── views.py          # Ticket-Views
│   │   ├── forms.py          # Ticket-Forms
│   │   ├── urls.py           # Ticket-URLs
│   │   ├── admin.py          # Admin-Interface
│   │   ├── serializers.py    # API-Serializer
│   │   └── tasks.py          # Celery Tasks (Email, SLA)
│   ├── knowledge/            # Wissensdatenbank
│   │   ├── models.py         # KnowledgeArticle Model
│   │   ├── views.py          # KB-Views
│   │   ├── forms.py          # KB-Forms
│   │   ├── urls.py           # KB-URLs
│   │   └── admin.py          # Admin-Interface
│   ├── api/                  # REST API
│   │   ├── views.py          # API ViewSets
│   │   ├── urls.py           # API-URLs
│   │   └── permissions.py    # Custom Permissions
│   └── main/                 # Dashboard & Haupt-Views
│       ├── views.py          # Dashboard-Views
│       └── urls.py           # Main-URLs
├── templates/                 # Django Templates
│   ├── base.html
│   ├── accounts/
│   ├── tickets/
│   ├── knowledge/
│   └── dashboard/
├── static/                    # Static Files (CSS, JS, Images)
├── media/                     # User Uploads
├── logs/                      # Log Files
├── requirements-django.txt    # Django Dependencies
└── .env                       # Environment Variables
```

## Migration Schritte

### 1. Installation & Setup

```bash
# Virtuelle Umgebung erstellen
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows

# Django Dependencies installieren
pip install -r requirements-django.txt

# Umgebungsvariablen einrichten
cp .env.example .env
nano .env
```

### 2. Datenbank-Migration

**WICHTIG**: Django verwendet ein anderes Migrations-System als Flask-Migrate.

```bash
# Initial migrations erstellen
python manage.py makemigrations accounts
python manage.py makemigrations tickets
python manage.py makemigrations knowledge

# Migrations ausführen
python manage.py migrate

# Superuser erstellen
python manage.py createsuperuser
```

**Daten von Flask nach Django migrieren**:

```bash
# Flask-Datenbank exportieren
# Option 1: SQLite
sqlite3 helpdesk.db .dump > flask_dump.sql

# Option 2: MySQL
mysqldump -u helpdesk_user -p helpdesk_db > flask_dump.sql

# Django-Datenbank vorbereiten und anpassen
# Siehe Abschnitt "Daten-Migration" weiter unten
```

### 3. Haupt-Unterschiede Flask vs Django

#### Models

**Flask (SQLAlchemy)**:
```python
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
```

**Django (ORM)**:
```python
from django.db import models

class User(models.Model):
    username = models.CharField(max_length=80, unique=True)
    # id wird automatisch erstellt
```

#### Views

**Flask**:
```python
from flask import render_template, request

@app.route('/tickets/')
def tickets():
    tickets = Ticket.query.all()
    return render_template('tickets.html', tickets=tickets)
```

**Django**:
```python
from django.shortcuts import render
from django.views.generic import ListView

class TicketListView(ListView):
    model = Ticket
    template_name = 'tickets/list.html'
    context_object_name = 'tickets'
```

#### Forms

**Flask-WTF**:
```python
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField

class TicketForm(FlaskForm):
    title = StringField('Title')
    description = TextAreaField('Description')
```

**Django Forms**:
```python
from django import forms

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description']
```

#### Templates

**Flask (Jinja2)** und **Django Templates** sind sehr ähnlich, aber mit kleinen Unterschieden:

Flask:
```html
{% extends "base.html" %}
{% block content %}
    {{ user.username }}
{% endblock %}
```

Django (fast identisch):
```html
{% extends "base.html" %}
{% block content %}
    {{ user.username }}
{% endblock %}
```

**Unterschied**: Django hat `{% load static %}` für Static Files.

### 4. Authentifizierung

Django hat ein eingebautes Auth-System. Microsoft OAuth2 wird mit `django-allauth` oder `msal` implementiert.

**Microsoft OAuth Backend erstellen** (`apps/accounts/backends.py`):

```python
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
import msal

User = get_user_model()

class MicrosoftOAuthBackend(BaseBackend):
    def authenticate(self, request, token=None):
        # Microsoft Token validieren
        # User erstellen oder aktualisieren
        pass
```

**In settings.py**:
```python
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'apps.accounts.backends.MicrosoftOAuthBackend',
]
```

### 5. REST API

Django REST Framework wird für die API verwendet.

**Serializer erstellen** (`apps/tickets/serializers.py`):

```python
from rest_framework import serializers
from .models import Ticket

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'
```

**ViewSet erstellen** (`apps/api/views.py`):

```python
from rest_framework import viewsets
from apps.tickets.models import Ticket
from apps.tickets.serializers import TicketSerializer

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
```

**URLs konfigurieren** (`apps/api/urls.py`):

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TicketViewSet

router = DefaultRouter()
router.register(r'tickets', TicketViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

### 6. Celery Tasks

**Task definieren** (`apps/tickets/tasks.py`):

```python
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_ticket_notification(ticket_id):
    from .models import Ticket
    ticket = Ticket.objects.get(id=ticket_id)
    send_mail(
        f'Neues Ticket: {ticket.title}',
        ticket.description,
        'noreply@mlgruppe.de',
        [ticket.assignee.email],
    )
```

**Task aufrufen**:

```python
from apps.tickets.tasks import send_ticket_notification

# Asynchron ausführen
send_ticket_notification.delay(ticket.id)
```

### 7. Admin-Interface

Django hat ein sehr mächtiges Admin-Interface eingebaut.

**Admin registrieren** (`apps/tickets/admin.py`):

```python
from django.contrib import admin
from .models import Ticket, TicketComment

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'title', 'status', 'priority', 'created_by', 'created_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['ticket_number', 'title', 'description']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Ticket Information', {
            'fields': ('ticket_number', 'title', 'description')
        }),
        ('Assignment', {
            'fields': ('created_by', 'assigned_to', 'category')
        }),
        ('Status', {
            'fields': ('status', 'priority', 'sla_due_date', 'sla_breached')
        }),
    )
```

### 8. Static Files & Media

**settings.py**:

```python
# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files (User uploads)
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

**Static Files sammeln**:

```bash
python manage.py collectstatic
```

**In Templates verwenden**:

```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/style.css' %}">
<img src="{{ ticket.attachment.file.url }}" alt="Attachment">
```

### 9. Environment Variables (.env)

```bash
# Django Settings
DEBUG=False
SECRET_KEY=ihr-super-geheimer-django-schluessel
ALLOWED_HOSTS=helpdesk.ihredomain.de,localhost

# Database
DATABASE_URL=mysql://helpdesk_user:password@localhost/helpdesk_db

# Microsoft OAuth2
MICROSOFT_CLIENT_ID=ihre-azure-app-client-id
MICROSOFT_CLIENT_SECRET=ihr-azure-app-secret
MICROSOFT_TENANT_ID=ihre-azure-tenant-id
MICROSOFT_REDIRECT_URI=https://helpdesk.ihredomain.de/auth/microsoft/callback

# Email Configuration
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
EMAIL_USERNAME=projekteit@mlgruppe.de
EMAIL_PASSWORD=ihr-email-passwort
EMAIL_HOST=outlook.office365.com
EMAIL_PORT=993

# Claude AI
CLAUDE_API_KEY=ihr-claude-api-schluessel

# Celery & Redis
REDIS_URL=redis://localhost:6379/0

# Sentry
SENTRY_DSN=ihr-sentry-dsn

# CORS
CORS_ALLOWED_ORIGINS=https://helpdesk.ihredomain.de
```

### 10. Entwicklung starten

```bash
# Development Server
python manage.py runserver

# Mit spezifischem Port
python manage.py runserver 0.0.0.0:8000

# Celery Worker starten
celery -A helpdesk worker -l info

# Celery Beat (für geplante Tasks)
celery -A helpdesk beat -l info
```

### 11. Django Management Commands

Django hat viele nützliche Commands:

```bash
# Datenbank
python manage.py makemigrations  # Migrations erstellen
python manage.py migrate         # Migrations ausführen
python manage.py showmigrations  # Migrations anzeigen
python manage.py sqlmigrate accounts 0001  # SQL einer Migration anzeigen

# Benutzer
python manage.py createsuperuser  # Admin-User erstellen
python manage.py changepassword username  # Passwort ändern

# Daten
python manage.py loaddata fixture.json  # Daten importieren
python manage.py dumpdata > backup.json  # Daten exportieren

# Entwicklung
python manage.py shell  # Python Shell mit Django-Context
python manage.py dbshell  # Datenbank Shell
python manage.py check  # System-Check

# Testing
python manage.py test  # Tests ausführen
python manage.py test apps.tickets  # Tests für eine App
```

### 12. Production Deployment

**WSGI für ISPConfig3** (Apache + mod_wsgi):

Erstellen Sie `/var/www/helpdesk.ihredomain.de/web/django.wsgi`:

```python
#!/usr/bin/python3
import os
import sys

# Pfad zur Django-Anwendung
sys.path.insert(0, '/var/www/helpdesk.ihredomain.de/app/')

# Virtual Environment aktivieren
activate_this = '/var/www/helpdesk.ihredomain.de/app/venv/bin/activate_this.py'
exec(open(activate_this).read(), {'__file__': activate_this})

# Django Settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpdesk.settings')

# Django WSGI Application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Oder mit Gunicorn** (empfohlen):

`/etc/systemd/system/helpdesk-gunicorn.service`:

```ini
[Unit]
Description=Gunicorn instance for ML Gruppe Helpdesk (Django)
After=network.target

[Service]
User=web1
Group=client1
WorkingDirectory=/var/www/helpdesk.ihredomain.de/app
Environment="PATH=/var/www/helpdesk.ihredomain.de/app/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=helpdesk.settings"
ExecStart=/var/www/helpdesk.ihredomain.de/app/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/var/www/helpdesk.ihredomain.de/helpdesk.sock \
    --timeout 120 \
    --access-logfile /var/www/helpdesk.ihredomain.de/app/logs/gunicorn-access.log \
    --error-logfile /var/www/helpdesk.ihredomain.de/app/logs/gunicorn-error.log \
    helpdesk.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 13. Daten-Migration von Flask zu Django

**Script zur Daten-Migration** (`migrate_data.py`):

```python
#!/usr/bin/env python
"""
Migrate data from Flask SQLAlchemy to Django ORM
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helpdesk.settings')
django.setup()

from apps.accounts.models import User
from apps.tickets.models import Ticket, Category
# Import Flask models here if needed

def migrate_users():
    """Migrate users from Flask to Django"""
    # Read from Flask database and create Django users
    pass

def migrate_tickets():
    """Migrate tickets from Flask to Django"""
    pass

if __name__ == '__main__':
    print("Starting data migration...")
    migrate_users()
    migrate_tickets()
    print("Migration completed!")
```

## Vorteile von Django gegenüber Flask

1. **Admin-Interface**: Eingebautes, konfigurierbares Admin-Panel
2. **ORM**: Mächtigeres ORM mit besserer Query-Performance
3. **Authentifizierung**: Robustes, eingebautes Auth-System
4. **Forms**: Integriertes Form-System mit Validierung
5. **Security**: Eingebaute CSRF, XSS, SQL-Injection Protection
6. **Migrations**: Besseres Migrations-System
7. **Testing**: Umfangreiches Test-Framework
8. **Skalierbarkeit**: Besser für große Anwendungen

## Support & Dokumentation

- **Django Dokumentation**: https://docs.djangoproject.com/
- **Django REST Framework**: https://www.django-rest-framework.org/
- **Django Allauth**: https://django-allauth.readthedocs.io/
- **Celery**: https://docs.celeryproject.org/

## Nächste Schritte

1. Vollständige App-Implementierung (tickets, knowledge, api)
2. Templates von Flask nach Django konvertieren
3. Static Files organisieren
4. Tests schreiben
5. Deployment auf ISPConfig3 Server
6. Performance-Optimierung
7. Monitoring einrichten

## Troubleshooting

### Problem: Migrations funktionieren nicht

```bash
# Migrations zurücksetzen
python manage.py migrate APP_NAME zero

# Neu erstellen
python manage.py makemigrations
python manage.py migrate
```

### Problem: Static Files werden nicht geladen

```bash
# Static Files sammeln
python manage.py collectstatic --clear

# In Development DEBUG=True setzen
```

### Problem: Database Connection Error

```bash
# Database-URL prüfen
python manage.py dbshell

# Verbindung testen
python manage.py check --database default
```

## Fazit

Die Migration von Flask zu Django bringt viele Vorteile, insbesondere für ein strukturiertes Helpdesk-System. Django bietet mehr eingebaute Funktionen, bessere Skalierbarkeit und ein professionelles Admin-Interface.

Die Migration erfordert zwar initialen Aufwand, zahlt sich aber langfristig durch bessere Wartbarkeit und Erweiterbarkeit aus.
