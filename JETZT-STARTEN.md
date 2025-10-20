# 🚀 Django Helpdesk - Sofort starten!

## ✅ Alles ist bereit!

Der Django Server läuft bereits auf **Port 8080**.

## Schritt 1: Superuser erstellen

Öffnen Sie ein **neues Terminal** und führen Sie aus:

```bash
cd C:\Users\aborowczak\PycharmProjects\FlaskProject\mini-helpdesk
venv\Scripts\activate
python manage.py createsuperuser
```

Geben Sie ein:
- **Email**: Ihre E-Mail (z.B. admin@mlgruppe.de)
- **Username**: admin
- **Password**: Mindestens 8 Zeichen
- **First name**: Ihr Vorname
- **Last name**: Ihr Nachname

## Schritt 2: Anwendung öffnen

### Option A: Admin-Interface (empfohlen)

```
http://127.0.0.1:8080/admin/
```

Hier können Sie:
- ✅ Benutzer verwalten
- ✅ Tickets erstellen und verwalten
- ✅ Kategorien anlegen
- ✅ Wissensdatenbank-Artikel erstellen
- ✅ Alle Models bearbeiten

### Option B: Dashboard

```
http://127.0.0.1:8080/
```

Schönes Dashboard mit Statistiken und Schnellzugriff.

### Option C: Login-Seite

```
http://127.0.0.1:8080/auth/login/
```

Professionelle Login-Seite mit ML Gruppe Design.

## Was ist verfügbar?

### ✅ Komplett funktionsfähig:

1. **Admin-Interface** (`/admin/`)
   - User Management mit Rollen
   - Ticket Management mit Kommentaren & Anhängen
   - Kategorie Management
   - Knowledge Base
   - Voll konfiguriert mit Inlines, Filtern, Suche

2. **Login-System** (`/auth/login/`)
   - Schönes Login-Template
   - Django Auth
   - Session Management

3. **Dashboard** (`/`)
   - Übersicht mit Statistiken
   - Schnellzugriff zu Admin-Bereichen
   - User-Info anzeigen

4. **Models**
   - User (mit Rollen: admin, team_leader, support_agent, customer)
   - Ticket (mit SLA, Priorität, Status)
   - TicketComment (intern/extern)
   - TicketAttachment (File-Upload)
   - Category (mit Auto-Zuweisung)
   - KnowledgeArticle (mit Views, Voting)

5. **Datenbank**
   - SQLite (db.sqlite3)
   - Alle Migrations ausgeführt
   - Bereit für MySQL/PostgreSQL

## Tipps für den Start:

### 1. Testdaten erstellen

Im Admin-Interface:
1. **Kategorie erstellen** (`/admin/tickets/category/add/`)
   - Name: "IT Support"
   - Farbe: #007bff

2. **Testuser erstellen** (`/admin/accounts/user/add/`)
   - Email: kunde@example.com
   - Username: kunde1
   - Rolle: Customer

3. **Test-Ticket erstellen** (`/admin/tickets/ticket/add/`)
   - Titel: "Computer Problem"
   - Beschreibung: "Mein PC startet nicht"
   - Priorität: High

### 2. Features testen

**Im Admin:**
- Ticket öffnen → Kommentar hinzufügen
- Ticket → Datei hochladen
- User → Rolle ändern
- KB-Artikel erstellen

### 3. API vorbereiten (optional)

```bash
pip install djangorestframework django-cors-headers

# In settings.py auskommentieren:
# 'rest_framework',
# 'corsheaders',

# In urls.py auskommentieren:
# path('api/v1/', include('apps.api.urls')),
```

## Häufige URLs:

```
Admin:          http://127.0.0.1:8080/admin/
Dashboard:      http://127.0.0.1:8080/
Login:          http://127.0.0.1:8080/auth/login/
Logout:         http://127.0.0.1:8080/auth/logout/

Admin-Bereiche:
Users:          http://127.0.0.1:8080/admin/accounts/user/
Tickets:        http://127.0.0.1:8080/admin/tickets/ticket/
Categories:     http://127.0.0.1:8080/admin/tickets/category/
Knowledge:      http://127.0.0.1:8080/admin/knowledge/knowledgearticle/
```

## Server starten/stoppen:

### Server läuft bereits auf Port 8080!

Falls Sie neu starten möchten:

```bash
# Terminal öffnen
cd C:\Users\aborowczak\PycharmProjects\FlaskProject\mini-helpdesk
venv\Scripts\activate

# Server starten
python manage.py runserver 0.0.0.0:8080
```

Stoppen: `Strg + C`

## Nächste Schritte:

1. ✅ **Jetzt**: Superuser erstellen und Admin öffnen
2. ⏳ **Später**: Templates für Tickets/KB anpassen
3. ⏳ **Bald**: REST API implementieren
4. ⏳ **Dann**: Microsoft OAuth2 einrichten
5. ⏳ **Zuletzt**: E-Mail-Integration aktivieren

## Support:

- **Dokumentation**: Siehe START.md, QUICKSTART.md
- **Django Docs**: https://docs.djangoproject.com/
- **E-Mail**: it-support@mlgruppe.de

---

## 🎉 Viel Erfolg!

**ML Gruppe Helpdesk - Django Version läuft!** 🚀

Server: http://127.0.0.1:8080/admin/
