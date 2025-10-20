# ML Gruppe Helpdesk - Django Quickstart

## Schnellstart-Anleitung

### 1. Virtuelle Umgebung erstellen und aktivieren

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows
```

### 2. Dependencies installieren

```bash
pip install -r requirements.txt
```

### 3. Umgebungsvariablen konfigurieren

Kopieren Sie `.env.example` nach `.env` und passen Sie die Werte an:

```bash
cp .env.example .env
nano .env
```

**Wichtige Einstellungen:**

```bash
DEBUG=True
SECRET_KEY=dein-sicherer-secret-key
DATABASE_URL=sqlite:///db.sqlite3  # oder MySQL/PostgreSQL
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 4. Datenbank initialisieren

```bash
# Migrations erstellen
python manage.py makemigrations

# Migrations ausführen
python manage.py migrate

# Superuser erstellen
python manage.py createsuperuser
```

### 5. Development Server starten

```bash
python manage.py runserver
```

Die Anwendung ist nun unter `http://localhost:8000/` erreichbar.

**Admin-Interface**: `http://localhost:8000/admin/`

### 6. Optional: Testdaten erstellen

```bash
python manage.py shell
```

```python
from apps.accounts.models import User
from apps.tickets.models import Ticket, Category

# Kategorie erstellen
cat = Category.objects.create(name="IT Support", description="IT-Probleme")

# Test-User erstellen
user = User.objects.create_user(
    email='test@example.com',
    username='testuser',
    password='test123',
    first_name='Test',
    last_name='User'
)

# Test-Ticket erstellen
ticket = Ticket.objects.create(
    title='Test Ticket',
    description='Dies ist ein Test-Ticket',
    created_by=user,
    category=cat,
    priority='high'
)
ticket.set_priority_based_sla()
ticket.save()
```

## Projektstruktur

```
mini-helpdesk/
├── manage.py                    # Django Management-Script
├── helpdesk/                    # Projekt-Konfiguration
│   ├── settings.py             # Django Settings
│   ├── urls.py                 # URL-Konfiguration
│   ├── wsgi.py                 # WSGI Entry Point
│   └── celery.py               # Celery-Konfiguration
├── apps/                        # Django Applications
│   ├── accounts/               # User & Auth
│   │   └── models.py
│   ├── tickets/                # Ticket-System
│   │   └── models.py
│   ├── knowledge/              # Wissensdatenbank
│   ├── api/                    # REST API
│   └── main/                   # Dashboard
├── templates/                   # HTML Templates
├── static/                      # CSS, JS, Images
├── media/                       # User Uploads
└── requirements.txt             # Dependencies
```

## Wichtige Django-Befehle

```bash
# Development
python manage.py runserver              # Server starten
python manage.py shell                  # Python Shell
python manage.py dbshell                # Datenbank Shell

# Datenbank
python manage.py makemigrations         # Migrations erstellen
python manage.py migrate                # Migrations ausführen
python manage.py showmigrations         # Migrations anzeigen

# User Management
python manage.py createsuperuser        # Admin erstellen
python manage.py changepassword USER    # Passwort ändern

# Static Files
python manage.py collectstatic          # Static Files sammeln

# Testing
python manage.py test                   # Tests ausführen

# Daten Import/Export
python manage.py loaddata data.json     # Daten importieren
python manage.py dumpdata > data.json   # Daten exportieren
```

## API-Endpoints

Die REST API ist unter `/api/v1/` verfügbar:

- `GET /api/v1/tickets/` - Alle Tickets
- `POST /api/v1/tickets/` - Neues Ticket erstellen
- `GET /api/v1/tickets/{id}/` - Ticket Details
- `PUT /api/v1/tickets/{id}/` - Ticket aktualisieren
- `DELETE /api/v1/tickets/{id}/` - Ticket löschen

## Celery (Background Tasks)

```bash
# Celery Worker starten
celery -A helpdesk worker -l info

# Celery Beat (Scheduled Tasks)
celery -A helpdesk beat -l info

# Beide zusammen
celery -A helpdesk worker -B -l info
```

## Production Deployment

Siehe `INSTALLATION_ISPCONFIG3.md` für detaillierte Deployment-Anweisungen.

**Wichtige Schritte:**

1. `DEBUG=False` setzen
2. `SECRET_KEY` ändern
3. `ALLOWED_HOSTS` konfigurieren
4. Static Files sammeln: `python manage.py collectstatic`
5. Gunicorn/uWSGI konfigurieren
6. Nginx/Apache konfigurieren

## Troubleshooting

### Problem: `ModuleNotFoundError`
```bash
# Virtual Environment aktiviert?
source venv/bin/activate

# Dependencies installiert?
pip install -r requirements.txt
```

### Problem: Datenbank-Fehler
```bash
# Migrations durchführen
python manage.py migrate

# Oder Datenbank zurücksetzen
rm db.sqlite3
python manage.py migrate
```

### Problem: Static Files werden nicht geladen
```bash
# In Development: DEBUG=True setzen
# In Production: collectstatic ausführen
python manage.py collectstatic
```

## Weitere Dokumentation

- `DJANGO_MIGRATION.md` - Detaillierte Django-Migration von Flask
- `INSTALLATION_ISPCONFIG3.md` - ISPConfig3 Deployment
- `README.md` - Projekt-Übersicht

## Support

Bei Fragen oder Problemen:
- E-Mail: it-support@mlgruppe.de
- Interne IT-Abteilung kontaktieren
