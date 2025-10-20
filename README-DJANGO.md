# ML Gruppe Helpdesk - Django Version

## Migration von Flask zu Django abgeschlossen!

Dieses Projekt wurde erfolgreich von Flask nach Django migriert.

## Neue Projektstruktur

```
mini-helpdesk/
├── manage.py                          # Django Management Script
├── requirements.txt                    # Django Dependencies
├── .env                                # Environment Variables
│
├── helpdesk/                          # Django Projekt-Konfiguration
│   ├── __init__.py
│   ├── settings.py                    # Haupt-Settings
│   ├── urls.py                        # URL-Konfiguration
│   ├── wsgi.py                        # WSGI Entry Point
│   ├── asgi.py                        # ASGI Entry Point
│   └── celery.py                      # Celery-Konfiguration
│
├── apps/                              # Django Applications
│   ├── accounts/                      # Benutzer & Authentifizierung
│   │   ├── models.py                  # Custom User Model
│   │   ├── admin.py                   # Admin-Interface
│   │   └── urls.py                    # Auth URLs
│   │
│   ├── tickets/                       # Ticket-System
│   │   ├── models.py                  # Ticket, Comment, Attachment Models
│   │   ├── admin.py                   # Admin-Interface
│   │   └── urls.py                    # Ticket URLs
│   │
│   ├── knowledge/                     # Wissensdatenbank
│   │   ├── models.py                  # Knowledge Article Model
│   │   ├── admin.py                   # Admin-Interface
│   │   └── urls.py                    # KB URLs
│   │
│   ├── api/                           # REST API
│   │   ├── urls.py                    # API URLs
│   │   └── apps.py
│   │
│   └── main/                          # Dashboard & Haupt-Views
│       ├── views.py                   # Dashboard Views
│       └── urls.py                    # Main URLs
│
├── templates/                         # Django Templates (noch zu erstellen)
├── static/                            # Static Files
├── media/                             # User Uploads
└── logs/                              # Log Files
```

## Was wurde geändert?

### Gelöscht (Flask-spezifisch):
- `app/` (Flask Blueprint Ordner)
- `app.py` (Flask Application Factory)
- `config.py` (Flask Config)
- `migrations/` (Flask-Migrate)
- `instance/` (Flask Instance Folder)
- Alte `requirements.txt` (Flask Dependencies)
- Docker-Dateien
- Alte Tests

### Neu hinzugefügt (Django):
- `manage.py` - Django Management Script
- `helpdesk/` - Django Projekt-Konfiguration
- `apps/` - Django Applications (accounts, tickets, knowledge, api, main)
- Neue `requirements.txt` mit Django Dependencies
- Admin-Interfaces für alle Models
- Django URL-Konfiguration

## Schnellstart

### 1. Environment Setup

```bash
# Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Dependencies installieren
pip install -r requirements.txt
```

### 2. Datenbank initialisieren

```bash
# Migrations erstellen
python manage.py makemigrations

# Migrations ausführen
python manage.py migrate

# Superuser erstellen
python manage.py createsuperuser
```

### 3. Development Server starten

```bash
python manage.py runserver
```

Öffnen Sie: `http://localhost:8000/admin/`

## Hauptunterschiede Flask vs Django

| Feature | Flask | Django |
|---------|-------|--------|
| **Projekt-Setup** | `app = Flask(__name__)` | `django-admin startproject` |
| **Apps** | Blueprints | Django Apps |
| **Models** | SQLAlchemy | Django ORM |
| **Migrations** | Flask-Migrate | Django Migrations |
| **Forms** | Flask-WTF | Django Forms |
| **Templates** | Jinja2 | Django Templates (ähnlich) |
| **Admin** | Manuell | Eingebaut & Konfigurierbar |
| **Auth** | Flask-Login | Eingebaut |
| **API** | Flask-RESTful | Django REST Framework |
| **Static Files** | Flask Static | collectstatic |
| **Config** | Python-Klassen | settings.py |

## Models

### User Model (Custom)
- `apps/accounts/models.py`
- Ersetzt Flask-Login UserMixin
- Unterstützt Rollen: admin, team_leader, support_agent, customer
- Microsoft OAuth2 Integration

### Ticket Models
- `apps/tickets/models.py`
- Ticket, TicketComment, TicketAttachment, Category
- SLA-Tracking
- Email-Integration

### Knowledge Model
- `apps/knowledge/models.py`
- KnowledgeArticle mit Slug-basiertem Routing
- View-Tracking
- Helpfulness-Voting

## Admin-Interface

Django bietet ein mächtiges Admin-Interface:

```bash
# Server starten
python manage.py runserver

# Admin-Interface öffnen
http://localhost:8000/admin/
```

**Vorteile:**
- Sofort einsatzbereit
- Konfigurierbar über `admin.py`
- Inline-Editing (Comments, Attachments)
- Filter, Suche, Sortierung
- Bulk-Actions

## API (Django REST Framework)

Die API ist unter `/api/v1/` verfügbar:

```bash
# API Root
GET /api/v1/

# Tickets
GET /api/v1/tickets/
POST /api/v1/tickets/
GET /api/v1/tickets/{id}/
PUT /api/v1/tickets/{id}/
DELETE /api/v1/tickets/{id}/
```

## Environment Variables (.env)

```bash
# Django Settings
DEBUG=False
SECRET_KEY=ihr-super-geheimer-django-schluessel
ALLOWED_HOSTS=helpdesk.ihredomain.de,localhost

# Database
DATABASE_URL=mysql://helpdesk_user:password@localhost/helpdesk_db
# oder
DATABASE_URL=sqlite:///db.sqlite3

# Microsoft OAuth2
MICROSOFT_CLIENT_ID=ihre-client-id
MICROSOFT_CLIENT_SECRET=ihr-client-secret
MICROSOFT_TENANT_ID=ihre-tenant-id

# Email
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
EMAIL_USERNAME=projekteit@mlgruppe.de
EMAIL_PASSWORD=ihr-passwort

# Celery & Redis
REDIS_URL=redis://localhost:6379/0

# Claude AI
CLAUDE_API_KEY=ihr-api-key

# Sentry
SENTRY_DSN=ihr-sentry-dsn
```

## Django Management Commands

```bash
# Datenbank
python manage.py makemigrations      # Migrations erstellen
python manage.py migrate             # Migrations ausführen
python manage.py showmigrations      # Migrations anzeigen

# User Management
python manage.py createsuperuser     # Admin erstellen
python manage.py changepassword user # Passwort ändern

# Development
python manage.py runserver          # Dev Server starten
python manage.py shell              # Python Shell
python manage.py dbshell            # Datenbank Shell

# Static Files
python manage.py collectstatic      # Static Files sammeln

# Testing
python manage.py test               # Tests ausführen

# Custom Commands
python manage.py help               # Alle Commands anzeigen
```

## Deployment

### ISPConfig3 mit Gunicorn

1. **Gunicorn Service erstellen** (`/etc/systemd/system/helpdesk.service`):

```ini
[Unit]
Description=ML Gruppe Helpdesk Django
After=network.target

[Service]
User=web1
Group=client1
WorkingDirectory=/var/www/helpdesk.ihredomain.de/app
Environment="PATH=/var/www/helpdesk.ihredomain.de/app/venv/bin"
ExecStart=/var/www/helpdesk.ihredomain.de/app/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/var/www/helpdesk.ihredomain.de/helpdesk.sock \
    helpdesk.wsgi:application

[Install]
WantedBy=multi-user.target
```

2. **Service aktivieren**:

```bash
sudo systemctl daemon-reload
sudo systemctl enable helpdesk
sudo systemctl start helpdesk
```

3. **Nginx konfigurieren** (in ISPConfig3):

```nginx
location / {
    proxy_pass http://unix:/var/www/helpdesk.ihredomain.de/helpdesk.sock;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

location /static/ {
    alias /var/www/helpdesk.ihredomain.de/app/staticfiles/;
}

location /media/ {
    alias /var/www/helpdesk.ihredomain.de/app/media/;
}
```

4. **Static Files sammeln**:

```bash
python manage.py collectstatic --no-input
```

## Celery (Background Tasks)

```bash
# Celery Worker starten
celery -A helpdesk worker -l info

# Celery Beat (Scheduled Tasks)
celery -A helpdesk beat -l info

# Beide zusammen
celery -A helpdesk worker -B -l info
```

## Nächste Schritte

1. ✅ Django-Projekt erstellt
2. ✅ Models migriert
3. ✅ Admin-Interfaces konfiguriert
4. ✅ URLs konfiguriert
5. ⏳ Templates erstellen
6. ⏳ Views implementieren
7. ⏳ Forms erstellen
8. ⏳ API ViewSets implementieren
9. ⏳ Microsoft OAuth2 Backend implementieren
10. ⏳ Celery Tasks migrieren
11. ⏳ Tests schreiben
12. ⏳ Frontend (CSS, JS) migrieren

## Dokumentation

- **QUICKSTART.md** - Schnellstart-Anleitung
- **DJANGO_MIGRATION.md** - Detaillierte Migrations-Dokumentation
- **INSTALLATION_ISPCONFIG3.md** - ISPConfig3 Deployment
- **README-DJANGO.md** (diese Datei) - Überblick

## Vorteile der Django-Migration

### 1. Admin-Interface
- Professionelles Admin-Panel ohne zusätzlichen Code
- Konfigurierbar und erweiterbar
- Inline-Editing, Filter, Suche

### 2. ORM
- Mächtigeres Query-System
- Bessere Performance-Optimierung
- Migrations-System

### 3. Security
- Eingebauter CSRF-Schutz
- XSS-Protection
- SQL-Injection-Schutz
- Sichere Password-Hashing

### 4. Dokumentation
- Umfangreiche offizielle Dokumentation
- Große Community
- Viele Third-Party-Packages

### 5. Skalierbarkeit
- Besser für große Anwendungen
- Bessere Code-Organisation
- Wiederverwendbare Apps

## Troubleshooting

### ImportError: No module named 'apps'
```bash
# PYTHONPATH setzen
export PYTHONPATH="${PYTHONPATH}:/pfad/zum/projekt"
```

### Migrations-Fehler
```bash
# Migrations zurücksetzen
python manage.py migrate app_name zero

# Neu erstellen
python manage.py makemigrations
python manage.py migrate
```

### Static Files werden nicht geladen
```bash
# In Development: DEBUG=True
# In Production:
python manage.py collectstatic
```

## Support

Bei Fragen oder Problemen:
- **E-Mail**: it-support@mlgruppe.de
- **Dokumentation**: Siehe Markdown-Dateien im Projekt
- **Django Docs**: https://docs.djangoproject.com/

## Changelog

### v2.0.0 - Django Migration (2025-10-20)
- ✅ Komplette Migration von Flask zu Django
- ✅ Alle Flask-Dateien entfernt
- ✅ Django-Projektstruktur erstellt
- ✅ Models migriert (User, Ticket, Knowledge)
- ✅ Admin-Interfaces konfiguriert
- ✅ URL-Routing eingerichtet
- ✅ Requirements aktualisiert
- ✅ Dokumentation erstellt

---

**ML Gruppe Helpdesk - Jetzt mit Django!** 🚀
