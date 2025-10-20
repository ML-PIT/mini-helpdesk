# ML Gruppe Helpdesk - Installation (Django)

## Windows Installation

### 1. Voraussetzungen

- Python 3.9 oder höher
- Git (optional)
- Redis (optional, für Celery)

### 2. Projekt klonen oder herunterladen

```bash
# Mit Git
git clone <repository-url>
cd mini-helpdesk

# Oder ZIP herunterladen und entpacken
```

### 3. Virtuelle Umgebung erstellen

```bash
# Virtuelle Umgebung erstellen
python -m venv venv

# Aktivieren (Windows)
venv\Scripts\activate

# Aktivieren (Linux/Mac)
source venv/bin/activate
```

### 4. Dependencies installieren

```bash
pip install -r requirements.txt
```

**Hinweis zu Datenbank-Treibern:**

- **SQLite**: Eingebaut in Python, keine Installation nötig
- **MySQL/MariaDB**: `PyMySQL` wird automatisch installiert
- **PostgreSQL**: Auskommentiert wegen Build-Problemen auf Windows
  - Falls benötigt: PostgreSQL installieren und dann `pip install psycopg2-binary`

### 5. Umgebungsvariablen konfigurieren

Kopieren Sie `.env.example` zu `.env`:

```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

Bearbeiten Sie `.env`:

```bash
# Django Settings
DEBUG=True
SECRET_KEY=ihr-geheimer-schluessel-hier
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (wählen Sie eine Option)
# Option 1: SQLite (für Development)
DATABASE_URL=sqlite:///db.sqlite3

# Option 2: MySQL/MariaDB (für Production)
DATABASE_URL=mysql://username:password@localhost:3306/helpdesk_db

# Option 3: PostgreSQL (falls installiert)
# DATABASE_URL=postgresql://username:password@localhost:5432/helpdesk_db
```

### 6. Datenbank initialisieren

```bash
# Migrations erstellen
python manage.py makemigrations

# Migrations ausführen
python manage.py migrate

# Superuser erstellen
python manage.py createsuperuser
```

Folgen Sie den Anweisungen und geben Sie ein:
- Email
- Username
- Password (mindestens 8 Zeichen)

### 7. Development Server starten

```bash
python manage.py runserver
```

Die Anwendung läuft jetzt unter:
- **Hauptseite**: http://localhost:8000/
- **Admin**: http://localhost:8000/admin/

### 8. Testdaten erstellen (optional)

```bash
python manage.py shell
```

```python
from apps.accounts.models import User
from apps.tickets.models import Ticket, Category

# Kategorie erstellen
cat = Category.objects.create(
    name="IT Support",
    description="IT-Probleme und Anfragen",
    color="#007bff"
)

# Test-User erstellen
user = User.objects.create_user(
    email='test@example.com',
    username='testuser',
    password='test123',
    first_name='Test',
    last_name='User',
    role='customer'
)

# Test-Ticket erstellen
ticket = Ticket.objects.create(
    title='Test Ticket',
    description='Dies ist ein Test-Ticket für das neue System',
    created_by=user,
    category=cat,
    priority='medium',
    status='open'
)
ticket.set_priority_based_sla()
ticket.save()

print(f"Ticket erstellt: {ticket.ticket_number}")
```

## Linux/Ubuntu Installation (für ISPConfig3)

### 1. System vorbereiten

```bash
# System aktualisieren
sudo apt update && sudo apt upgrade -y

# Python und Dependencies installieren
sudo apt install python3 python3-pip python3-venv -y

# MySQL Client installieren (für PyMySQL)
sudo apt install default-libmysqlclient-dev -y

# Redis installieren (für Celery)
sudo apt install redis-server -y
```

### 2. Projekt auf den Server übertragen

```bash
# Als web-user in ISPConfig3
cd ~/web/app1

# Git Repository klonen
git clone <repository-url> .

# Oder mit SCP/FTP hochladen
```

### 3. Virtuelle Umgebung und Dependencies

```bash
# Virtuelle Umgebung erstellen
python3 -m venv venv

# Aktivieren
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt
```

### 4. Datenbank in ISPConfig3 erstellen

1. ISPConfig3 öffnen
2. **Sites** → **Database**
3. Neue Datenbank erstellen:
   - Name: `helpdesk_db`
   - User: `helpdesk_user`
   - Password: Sicheres Passwort generieren

### 5. Umgebungsvariablen (.env)

```bash
nano .env
```

**WICHTIG: UTF-8 Encoding verwenden!** (keine Umlaute in Passwörtern)

```bash
DEBUG=False
SECRET_KEY=super-geheimer-production-key-mindestens-50-zeichen-lang
ALLOWED_HOSTS=helpdesk.ihredomain.de

DATABASE_URL=mysql://helpdesk_user:passwort@localhost:3306/helpdesk_db

# Microsoft OAuth2 (optional)
MICROSOFT_CLIENT_ID=ihre-client-id
MICROSOFT_CLIENT_SECRET=ihr-secret
MICROSOFT_TENANT_ID=ihre-tenant-id

# Email
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
EMAIL_USERNAME=projekteit@mlgruppe.de
EMAIL_PASSWORD=email-passwort

# Redis (für Celery)
REDIS_URL=redis://localhost:6379/0

# Claude AI (optional)
CLAUDE_API_KEY=ihr-api-key
```

**UTF-8 Problem vermeiden:**
```bash
# Falls .env Umlaute enthält, konvertieren:
iconv -f ISO-8859-1 -t UTF-8 .env > .env.tmp && mv .env.tmp .env
```

### 6. Datenbank initialisieren

```bash
# Migrations
python manage.py makemigrations
python manage.py migrate

# Superuser erstellen
python manage.py createsuperuser

# Static Files sammeln
python manage.py collectstatic --no-input
```

### 7. Gunicorn Service einrichten

```bash
sudo nano /etc/systemd/system/helpdesk.service
```

```ini
[Unit]
Description=ML Gruppe Helpdesk (Django)
After=network.target

[Service]
User=web16
Group=client2
WorkingDirectory=/var/www/clients/client2/web16/web/app1
Environment="PATH=/var/www/clients/client2/web16/web/app1/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=helpdesk.settings"
ExecStart=/var/www/clients/client2/web16/web/app1/venv/bin/gunicorn \
    --workers 4 \
    --bind unix:/var/www/clients/client2/web16/web/app1/helpdesk.sock \
    --timeout 120 \
    --access-logfile /var/www/clients/client2/web16/web/app1/logs/gunicorn-access.log \
    --error-logfile /var/www/clients/client2/web16/web/app1/logs/gunicorn-error.log \
    helpdesk.wsgi:application

[Install]
WantedBy=multi-user.target
```

**Service starten:**

```bash
# Logs-Verzeichnis erstellen
mkdir -p ~/web/app1/logs

# Service aktivieren
sudo systemctl daemon-reload
sudo systemctl enable helpdesk
sudo systemctl start helpdesk

# Status prüfen
sudo systemctl status helpdesk
```

### 8. Nginx/Apache konfigurieren

Siehe `INSTALLATION_ISPCONFIG3.md` für Details.

**Nginx (empfohlen):**

In ISPConfig3 unter **Nginx Directives**:

```nginx
location / {
    proxy_pass http://unix:/var/www/clients/client2/web16/web/app1/helpdesk.sock;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

location /static/ {
    alias /var/www/clients/client2/web16/web/app1/staticfiles/;
}

location /media/ {
    alias /var/www/clients/client2/web16/web/app1/media/;
}
```

### 9. Celery Worker (optional)

```bash
sudo nano /etc/systemd/system/helpdesk-celery.service
```

```ini
[Unit]
Description=Helpdesk Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=web16
Group=client2
WorkingDirectory=/var/www/clients/client2/web16/web/app1
Environment=PATH=/var/www/clients/client2/web16/web/app1/venv/bin
ExecStart=/var/www/clients/client2/web16/web/app1/venv/bin/celery -A helpdesk worker --detach
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable helpdesk-celery
sudo systemctl start helpdesk-celery
```

## Troubleshooting

### Problem: "No module named 'pymysql'"

```bash
pip install PyMySQL
```

### Problem: Database Connection Error

```bash
# Datenbank-URL in .env prüfen
python manage.py check --database default

# Oder direkt testen
python manage.py dbshell
```

### Problem: Static Files werden nicht geladen

```bash
# In Production
python manage.py collectstatic --clear

# In Development
# DEBUG=True in .env setzen
```

### Problem: "OperationalError: no such table"

```bash
# Migrations durchführen
python manage.py migrate

# Oder komplett neu
python manage.py migrate --run-syncdb
```

### Problem: Permission Denied (Linux)

```bash
# Berechtigungen setzen
chmod -R 755 /var/www/clients/client2/web16/web/app1
chmod 600 /var/www/clients/client2/web16/web/app1/.env
```

### Problem: UnicodeDecodeError in .env

```bash
# .env in UTF-8 konvertieren
iconv -f ISO-8859-1 -t UTF-8 .env > .env.tmp && mv .env.tmp .env

# Oder Umlaute entfernen
```

## Nächste Schritte

1. ✅ Django installiert
2. ✅ Datenbank initialisiert
3. ✅ Admin-User erstellt
4. ⏳ Templates erstellen
5. ⏳ Frontend entwickeln
6. ⏳ Microsoft OAuth2 konfigurieren
7. ⏳ E-Mail-Integration einrichten
8. ⏳ Tests schreiben

## Weitere Hilfe

- **Quickstart**: `QUICKSTART.md`
- **Migration**: `DJANGO_MIGRATION.md`
- **ISPConfig3**: `INSTALLATION_ISPCONFIG3.md`
- **Django Docs**: https://docs.djangoproject.com/

Bei Problemen: it-support@mlgruppe.de
