# 🚀 Django Helpdesk - Schnellstart

## ✅ Migration abgeschlossen!

Das Projekt wurde erfolgreich von Flask zu Django migriert.

## Sofort loslegen:

### 1. Virtual Environment aktivieren

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Superuser erstellen

```bash
python manage.py createsuperuser
```

Folgen Sie den Anweisungen:
- **Email**: Ihre E-Mail-Adresse
- **Username**: admin (oder beliebig)
- **Password**: Mindestens 8 Zeichen
- **First name**: Ihr Vorname
- **Last name**: Ihr Nachname

### 3. Server starten

```bash
python manage.py runserver
```

### 4. Anwendung öffnen

**Admin-Interface:**
- URL: http://127.0.0.1:8000/admin/
- Login mit Superuser-Credentials

**Hauptseite:**
- URL: http://127.0.0.1:8000/

## Was ist bereits verfügbar?

### ✅ Django Admin-Interface

Das Admin-Interface ist vollständig konfiguriert:

- **Benutzer verwalten** (`/admin/accounts/user/`)
  - Benutzer erstellen/bearbeiten
  - Rollen zuweisen (admin, team_leader, support_agent, customer)
  - Microsoft OAuth Konfiguration

- **Tickets verwalten** (`/admin/tickets/ticket/`)
  - Tickets erstellen/bearbeiten
  - Kommentare hinzufügen (Inline)
  - Anhänge hochladen (Inline)
  - Status und Priorität ändern
  - SLA-Tracking

- **Kategorien** (`/admin/tickets/category/`)
  - Kategorien erstellen
  - Auto-Zuweisung konfigurieren

- **Wissensdatenbank** (`/admin/knowledge/knowledgearticle/`)
  - Artikel erstellen/bearbeiten
  - Veröffentlichen
  - View-Tracking

### 📊 Aktuelle Features:

**User Model:**
- ✅ Rollen-System (admin, team_leader, support_agent, customer)
- ✅ Microsoft OAuth2 Integration (vorbereitet)
- ✅ Berechtigungsprüfung
- ✅ Dashboard-Statistiken

**Ticket System:**
- ✅ Ticket mit SLA-Tracking
- ✅ Kommentare (intern/extern)
- ✅ Dateianhänge
- ✅ Kategorien
- ✅ Prioritäten
- ✅ Status-Tracking

**Wissensdatenbank:**
- ✅ Artikel mit Slug-URLs
- ✅ View-Counter
- ✅ Helpfulness-Voting
- ✅ SEO-Felder

## Nächste Schritte:

### Templates erstellen

```bash
# Verzeichnis erstellen
mkdir -p templates/dashboard
mkdir -p templates/tickets
mkdir -p templates/accounts
mkdir -p templates/knowledge
```

### Views implementieren

Die Views sind bereits vorbereitet in:
- `apps/main/views.py` - Dashboard
- `apps/tickets/views.py` - Tickets (TODO)
- `apps/accounts/views.py` - Auth (TODO)
- `apps/knowledge/views.py` - KB (TODO)

### REST API aktivieren

```bash
# Django REST Framework installieren
pip install djangorestframework django-cors-headers

# In settings.py aktivieren (auskommentieren):
# 'rest_framework',
# 'corsheaders',

# In urls.py aktivieren:
# path('api/v1/', include('apps.api.urls')),
```

### Celery für Background Tasks

```bash
# Celery installieren
pip install celery redis django-celery-beat django-celery-results

# In settings.py aktivieren
# Redis starten
redis-server

# Celery Worker starten
celery -A helpdesk worker -l info
```

## Testdaten erstellen

```bash
python manage.py shell
```

```python
from apps.accounts.models import User
from apps.tickets.models import Ticket, Category

# Kategorie erstellen
cat = Category.objects.create(
    name="IT Support",
    description="IT-Probleme",
    color="#007bff"
)

# Test-User
user = User.objects.create_user(
    email='kunde@example.com',
    username='kunde1',
    password='test123',
    first_name='Max',
    last_name='Mustermann',
    role='customer'
)

# Test-Ticket
ticket = Ticket.objects.create(
    title='Computer startet nicht',
    description='Mein Computer zeigt nur einen schwarzen Bildschirm.',
    created_by=user,
    category=cat,
    priority='high'
)
ticket.set_priority_based_sla()
ticket.save()

print(f"✅ Ticket erstellt: {ticket.ticket_number}")
```

## Häufige Befehle:

```bash
# Server starten
python manage.py runserver

# Server auf anderem Port
python manage.py runserver 8080

# Migrations
python manage.py makemigrations
python manage.py migrate

# Shell
python manage.py shell

# Tests
python manage.py test

# Static Files sammeln (für Production)
python manage.py collectstatic
```

## Troubleshooting:

### Problem: "ModuleNotFoundError: No module named 'django'"

```bash
# Virtual Environment aktivieren!
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Django installieren
pip install -r requirements.txt
```

### Problem: "no such table: accounts_user"

```bash
# Migrations ausführen
python manage.py migrate
```

### Problem: SSL-Fehler im Browser

- ✅ Bereits behoben!
- `.env` enthält jetzt `DEBUG=True`
- Server läuft auf http:// (nicht https://)

### Problem: "CSRF token missing"

- In Development ist CSRF automatisch konfiguriert
- Bei API-Requests: CSRF-Token in Header senden

## Dokumentation:

- **START.md** (diese Datei) - Schnellstart
- **SUCCESS.md** - Migrations-Zusammenfassung
- **QUICKSTART.md** - Ausführliche Anleitung
- **DJANGO_MIGRATION.md** - Technische Details
- **INSTALLATION.md** - Installation & Deployment
- **README-DJANGO.md** - Projekt-Übersicht

## Support:

- **Django Docs**: https://docs.djangoproject.com/
- **DRF Docs**: https://www.django-rest-framework.org/
- **E-Mail**: it-support@mlgruppe.de

---

## 🎉 Viel Erfolg mit Django!

Das Projekt ist bereit für die Weiterentwicklung.

**ML Gruppe Helpdesk - Powered by Django 5.0.6** 🚀
