# ML Gruppe Helpdesk - Installation für ISPConfig3

## Übersicht

Diese Anleitung beschreibt die Installation des ML Gruppe Helpdesk Systems auf einem ISPConfig3 Server. Das System ist eine Flask-basierte Webanwendung mit integrierter Microsoft 365 Authentifizierung und verschiedenen Helpdesk-Funktionalitäten.

## Systemanforderungen

### Server-Spezifikationen
- **CPU**: Minimum 2 Kerne, empfohlen 4+ Kerne
- **RAM**: Minimum 4GB, empfohlen 8GB+
- **Speicher**: Minimum 10GB freier Speicherplatz
- **OS**: Ubuntu 20.04+ oder Debian 10+ mit ISPConfig3

### Software-Voraussetzungen
- ISPConfig3 (bereits installiert)
- Python 3.8+
- MySQL/MariaDB
- Redis (optional, empfohlen)
- Nginx (über ISPConfig3 verwaltet)

## Installation

### 1. Website in ISPConfig3 erstellen

1. Melden Sie sich im ISPConfig3 Control Panel an
2. Navigieren Sie zu **Sites** → **Website**
3. Erstellen Sie eine neue Website:
   - **Domain**: `helpdesk.ihredomain.de`
   - **Document Root**: `/var/www/helpdesk.ihredomain.de/web`
   - **PHP**: Deaktiviert
   - **SSL**: Aktiviert (Let's Encrypt)

### 2. Datenbank einrichten

1. In ISPConfig3 unter **Sites** → **Database**:
   - **Database Name**: `helpdesk_db`
   - **Database User**: `helpdesk_user`
   - **Database Password**: Sicheres Passwort generieren

2. Notieren Sie sich die Verbindungsdaten für später

### 3. Anwendung installieren

```bash
# Als root oder sudo user
cd /var/www/helpdesk.ihredomain.de

# Repository klonen
git clone https://github.com/mlgruppe/helpdesk.git app
cd app

# Python Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt

# Berechtigungen setzen
chown -R web1:client1 /var/www/helpdesk.ihredomain.de/app
chmod -R 755 /var/www/helpdesk.ihredomain.de/app
```

### 4. Umgebungskonfiguration

```bash
# Umgebungsdatei erstellen
cp .env.example .env
nano .env
```

Bearbeiten Sie die `.env` Datei mit Ihren spezifischen Werten:

```bash
# Flask Konfiguration
SECRET_KEY=ihr-super-geheimer-schlüssel-hier
FLASK_ENV=production

# Datenbank (von ISPConfig3)
DATABASE_URL=mysql+pymysql://helpdesk_user:ihr_passwort@localhost/helpdesk_db

# Microsoft OAuth2 (Azure AD)
MICROSOFT_CLIENT_ID=ihre-azure-app-client-id
MICROSOFT_CLIENT_SECRET=ihr-azure-app-secret
MICROSOFT_TENANT_ID=ihre-azure-tenant-id

# E-Mail Konfiguration (Office 365)
EMAIL_USERNAME=projekteit@mlgruppe.de
EMAIL_PASSWORD=ihr-email-passwort
EMAIL_HOST=outlook.office365.com
EMAIL_PORT=993
SMTP_HOST=smtp.office365.com
SMTP_PORT=587

# Optional: Claude AI Integration
CLAUDE_API_KEY=ihr-claude-api-schlüssel

# Optional: Microsoft Teams Webhook
TEAMS_WEBHOOK_URL=ihr-teams-webhook-url

# Security
WTF_CSRF_ENABLED=True
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True

# Uploads
UPLOAD_FOLDER=/var/www/helpdesk.ihredomain.de/app/instance/uploads
MAX_CONTENT_LENGTH=16777216

# Optional: Redis für Caching
RATELIMIT_STORAGE_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 5. Datenbank initialisieren

```bash
# Virtual Environment aktivieren
source venv/bin/activate

# Flask-Umgebung setzen
export FLASK_APP=app.py

# Datenbank-Migration
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Initiale Daten laden (Admin-User, etc.)
flask deploy
```

### 6. WSGI-Konfiguration für ISPConfig3

Erstellen Sie eine WSGI-Datei für die Anwendung:

```bash
nano /var/www/helpdesk.ihredomain.de/web/app.wsgi
```

Inhalt der `app.wsgi` Datei:

```python
#!/usr/bin/python3
import sys
import os

# Pfad zur Anwendung
sys.path.insert(0, '/var/www/helpdesk.ihredomain.de/app/')

# Virtual Environment aktivieren
activate_this = '/var/www/helpdesk.ihredomain.de/app/venv/bin/activate_this.py'
exec(open(activate_this).read(), dict(__file__=activate_this))

# Umgebungsvariablen laden
from dotenv import load_dotenv
load_dotenv('/var/www/helpdesk.ihredomain.de/app/.env')

# Flask App importieren
from app import create_app
application = create_app('production')

if __name__ == "__main__":
    application.run()
```

### 7. Webserver-Konfiguration

#### Option A: Apache mit WSGI (Standard ISPConfig3)

In ISPConfig3 unter **Sites** → **Website** → **Options**:

```apache
# Apache Direktiven hinzufügen
DocumentRoot /var/www/helpdesk.ihredomain.de/web

# WSGI Konfiguration
WSGIDaemonProcess helpdesk python-path=/var/www/helpdesk.ihredomain.de/app python-home=/var/www/helpdesk.ihredomain.de/app/venv
WSGIProcessGroup helpdesk
WSGIScriptAlias / /var/www/helpdesk.ihredomain.de/web/app.wsgi

<Directory /var/www/helpdesk.ihredomain.de/web>
    WSGIApplicationGroup %{GLOBAL}
    Require all granted
</Directory>

# Statische Dateien
Alias /static /var/www/helpdesk.ihredomain.de/app/app/static
<Directory /var/www/helpdesk.ihredomain.de/app/app/static>
    Require all granted
</Directory>

# Upload-Verzeichnis
Alias /uploads /var/www/helpdesk.ihredomain.de/app/instance/uploads
<Directory /var/www/helpdesk.ihredomain.de/app/instance/uploads>
    Require all granted
</Directory>

# Sicherheits-Header
Header always set X-Frame-Options DENY
Header always set X-Content-Type-Options nosniff
Header always set X-XSS-Protection "1; mode=block"
Header always set Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"
```

#### Option B: Nginx als Reverse Proxy (Empfohlen für bessere Performance)

Wenn Sie Nginx anstatt Apache verwenden möchten:

**1. Gunicorn Service erstellen:**

```bash
sudo nano /etc/systemd/system/helpdesk-gunicorn.service
```

```ini
[Unit]
Description=Gunicorn instance to serve ML Gruppe Helpdesk
After=network.target

[Service]
User=web1
Group=client1
WorkingDirectory=/var/www/helpdesk.ihredomain.de/app
Environment="PATH=/var/www/helpdesk.ihredomain.de/app/venv/bin"
ExecStart=/var/www/helpdesk.ihredomain.de/app/venv/bin/gunicorn --workers 4 --bind unix:/var/www/helpdesk.ihredomain.de/helpdesk.sock -m 007 "app:create_app()"
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**2. Service aktivieren:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable helpdesk-gunicorn
sudo systemctl start helpdesk-gunicorn
sudo systemctl status helpdesk-gunicorn
```

**3. Nginx Konfiguration in ISPConfig3:**

In ISPConfig3 unter **Sites** → **Website** → **Options** → **Nginx Directives**:

```nginx
# Hauptkonfiguration für Flask App
location / {
    include proxy_params;
    proxy_pass http://unix:/var/www/helpdesk.ihredomain.de/helpdesk.sock;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;
}

# Statische Dateien direkt ausliefern
location /static/ {
    alias /var/www/helpdesk.ihredomain.de/app/app/static/;
    expires 1y;
    add_header Cache-Control "public, immutable";
    access_log off;
}

# Upload-Dateien
location /uploads/ {
    alias /var/www/helpdesk.ihredomain.de/app/instance/uploads/;
    expires 30d;
    add_header Cache-Control "public";
}

# Favicon
location = /favicon.ico {
    alias /var/www/helpdesk.ihredomain.de/app/app/static/favicon.ico;
    expires 1y;
    add_header Cache-Control "public, immutable";
    access_log off;
}

# Robots.txt
location = /robots.txt {
    alias /var/www/helpdesk.ihredomain.de/app/app/static/robots.txt;
    expires 1y;
    add_header Cache-Control "public, immutable";
    access_log off;
}

# Sicherheits-Header
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# Rate Limiting
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
limit_req_zone $binary_remote_addr zone=api:10m rate=30r/m;

location /auth/login {
    limit_req zone=login burst=3 nodelay;
    include proxy_params;
    proxy_pass http://unix:/var/www/helpdesk.ihredomain.de/helpdesk.sock;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

location /api/ {
    limit_req zone=api burst=10 nodelay;
    include proxy_params;
    proxy_pass http://unix:/var/www/helpdesk.ihredomain.de/helpdesk.sock;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_Set_header X-Forwarded-Proto $scheme;
}

# Maximale Upload-Größe
client_max_body_size 16M;
```

**4. Socket-Berechtigungen setzen:**

```bash
# Socket-Verzeichnis vorbereiten
sudo mkdir -p /var/www/helpdesk.ihredomain.de
sudo chown web1:client1 /var/www/helpdesk.ihredomain.de

# Nginx Benutzer zur Gruppe hinzufügen
sudo usermod -a -G client1 www-data
```

**5. Nginx testen:**

```bash
sudo nginx -t
sudo systemctl reload nginx
```

#### Option C: Nginx mit ISPConfig3 Auto-SSL

Für automatisches SSL-Management mit ISPConfig3 und Nginx:

**1. Website auf Nginx umstellen:**
- In ISPConfig3: **Sites** → **Website** → **Options**
- **Auto-Subdomain**: Aktiviert
- **SSL**: Let's Encrypt aktiviert  
- **Nginx Directives** wie in Option B konfigurieren

**2. ISPConfig3 Nginx Template anpassen:**
```bash
sudo cp /usr/local/ispconfig/server/conf/nginx_vhost.conf.master /usr/local/ispconfig/server/conf-custom/
sudo nano /usr/local/ispconfig/server/conf-custom/nginx_vhost.conf.master
```

**Empfehlung:** Option B (Nginx mit Gunicorn) bietet die beste Performance und Stabilität für Flask-Anwendungen.

### 8. Systemd Service erstellen (Optional für Background Tasks)

```bash
sudo nano /etc/systemd/system/helpdesk-celery.service
```

```ini
[Unit]
Description=Helpdesk Celery Worker
After=network.target mysql.service redis.service

[Service]
Type=forking
User=web1
Group=client1
WorkingDirectory=/var/www/helpdesk.ihredomain.de/app
Environment=PATH=/var/www/helpdesk.ihredomain.de/app/venv/bin
ExecStart=/var/www/helpdesk.ihredomain.de/app/venv/bin/celery -A app.celery worker --detach
ExecStop=/bin/kill -s TERM $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Service aktivieren und starten
sudo systemctl daemon-reload
sudo systemctl enable helpdesk-celery
sudo systemctl start helpdesk-celery
```

### 9. Berechtigungen und Sicherheit

```bash
# Ordnerstruktur und Berechtigungen
mkdir -p /var/www/helpdesk.ihredomain.de/app/instance/uploads
mkdir -p /var/www/helpdesk.ihredomain.de/app/logs

# Korrekte Berechtigungen setzen
chown -R web1:client1 /var/www/helpdesk.ihredomain.de/app
chmod -R 755 /var/www/helpdesk.ihredomain.de/app
chmod -R 775 /var/www/helpdesk.ihredomain.de/app/instance
chmod 600 /var/www/helpdesk.ihredomain.de/app/.env

# Log-Dateien
touch /var/www/helpdesk.ihredomain.de/app/logs/helpdesk.log
chown web1:client1 /var/www/helpdesk.ihredomain.de/app/logs/helpdesk.log
chmod 644 /var/www/helpdesk.ihredomain.de/app/logs/helpdesk.log
```

### 10. SSL-Zertifikat einrichten

1. In ISPConfig3 unter **Sites** → **Website**
2. **SSL** Tab aktivieren
3. **Let's Encrypt SSL** aktivieren
4. **SSL Domain**: `helpdesk.ihredomain.de`
5. Speichern und warten bis Zertifikat erstellt wird

## Microsoft Azure AD Konfiguration

### 1. App-Registrierung erstellen

1. Melden Sie sich im Azure Portal an
2. Navigieren Sie zu **Azure Active Directory** → **App registrations**
3. Klicken Sie auf **New registration**:
   - **Name**: ML Gruppe Helpdesk
   - **Redirect URI**: `https://helpdesk.ihredomain.de/auth/microsoft/callback`

### 2. API-Berechtigungen konfigurieren

Fügen Sie folgende Microsoft Graph Berechtigungen hinzu:
- `User.Read` (delegated)
- `Mail.Read` (delegated)
- `Mail.Send` (delegated)

### 3. Client Secret erstellen

1. Unter **Certificates & secrets**
2. **New client secret** erstellen
3. Wert notieren für die `.env` Datei

## Erste Schritte nach der Installation

### 1. Admin-Benutzer erstellen

```bash
cd /var/www/helpdesk.ihredomain.de/app
source venv/bin/activate
python3 -c "
from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app('production')
with app.app_context():
    admin = User(
        username='admin',
        email='admin@ihredomain.de',
        password_hash=generate_password_hash('AdminPasswort123!'),
        role='admin',
        is_active=True
    )
    db.session.add(admin)
    db.session.commit()
    print('Admin user created successfully!')
"
```

### 2. System-Tests durchführen

```bash
# Anwendung testen
curl -I https://helpdesk.ihredomain.de

# Log-Dateien überprüfen
tail -f /var/www/helpdesk.ihredomain.de/app/logs/helpdesk.log
tail -f /var/log/apache2/error.log
```

### 3. E-Mail-Integration testen

1. Melden Sie sich im Helpdesk an
2. Erstellen Sie ein Test-Ticket
3. Überprüfen Sie, ob E-Mail-Benachrichtigungen funktionieren

## Wartung und Updates

### Backup-Strategie

```bash
# Tägliches Backup-Script erstellen
nano /var/www/helpdesk.ihredomain.de/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/www/helpdesk.ihredomain.de/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Verzeichnis erstellen falls nicht vorhanden
mkdir -p $BACKUP_DIR

# Datenbank Backup
mysqldump -u helpdesk_user -p'ihr_passwort' helpdesk_db > $BACKUP_DIR/db_backup_$DATE.sql

# Anwendung Backup (ohne venv)
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    /var/www/helpdesk.ihredomain.de/app

# Alte Backups löschen (älter als 7 Tage)
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

```bash
# Script ausführbar machen
chmod +x /var/www/helpdesk.ihredomain.de/backup.sh

# Cronjob einrichten
crontab -e
# Hinzufügen: 0 2 * * * /var/www/helpdesk.ihredomain.de/backup.sh
```

### Update-Prozess

```bash
cd /var/www/helpdesk.ihredomain.de/app

# Backup vor Update
./backup.sh

# Repository aktualisieren
git pull origin main

# Abhängigkeiten aktualisieren
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Datenbank-Migration
flask db upgrade

# Apache neu starten
sudo systemctl reload apache2

# Services neu starten (falls vorhanden)
sudo systemctl restart helpdesk-celery
```

## Monitoring und Logging

### Log-Dateien

Wichtige Log-Dateien zur Überwachung:
- Anwendung: `/var/www/helpdesk.ihredomain.de/app/logs/helpdesk.log`
- Apache: `/var/log/apache2/error.log`
- MySQL: `/var/log/mysql/error.log`

### Performance-Monitoring

```bash
# System-Ressourcen überwachen
htop
df -h
free -h

# MySQL Performance
mysql -e "SHOW PROCESSLIST;"
mysql -e "SHOW STATUS LIKE 'Connections';"

# Apache Status
systemctl status apache2
```

## Troubleshooting

### Häufige Probleme

#### 1. Anwendung startet nicht
- Überprüfen Sie die `.env` Datei auf korrekte Werte
- Kontrollieren Sie die Datenbankverbindung
- Prüfen Sie Apache Error-Logs

#### 2. E-Mail Integration funktioniert nicht
- Verifizieren Sie Office 365 Zugangsdaten
- Prüfen Sie Firewall-Einstellungen für Ports 587/993
- Stellen Sie sicher, dass moderne Authentifizierung aktiviert ist

#### 3. OAuth Authentifizierung schlägt fehl
- Überprüfen Sie Azure AD App-Registrierung
- Kontrollieren Sie Redirect-URIs
- Verifizieren Sie Tenant-Konfiguration

#### 4. Upload-Probleme
- Überprüfen Sie Ordnerberechtigungen
- Kontrollieren Sie `MAX_CONTENT_LENGTH` Einstellung
- Prüfen Sie verfügbaren Speicherplatz

### Debug-Modus aktivieren

```bash
# In .env Datei temporär ändern
FLASK_ENV=development
FLASK_DEBUG=True

# Apache neu laden
sudo systemctl reload apache2
```

## Sicherheitsrichtlinien

### Sicherheits-Checkliste

- [ ] Starke Passwörter für alle Accounts verwenden
- [ ] SSL/TLS Verschlüsselung aktiviert
- [ ] Firewall konfiguriert
- [ ] Regelmäßige Sicherheitsupdates
- [ ] Audit-Logging aktiviert
- [ ] Rate-Limiting konfiguriert
- [ ] Backup-Verschlüsselung eingerichtet
- [ ] Zugriffsschlüssel-Rotation implementiert

### Firewall-Konfiguration

```bash
# UFW (Ubuntu Firewall) Regeln
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw allow from trusted_ip to any port 3306  # MySQL (nur von vertrauenswürdigen IPs)
sudo ufw --force enable
```

## Support und Kontakt

Für technischen Support und Fragen:
- **E-Mail**: it-support@mlgruppe.de
- **Dokumentation**: Diese Datei
- **Issues**: Interne IT-Abteilung kontaktieren

## Fazit

Diese Installationsanleitung stellt sicher, dass das ML Gruppe Helpdesk System ordnungsgemäß in einer ISPConfig3-Umgebung installiert und konfiguriert wird. Folgen Sie allen Schritten sorgfältig und testen Sie das System nach der Installation gründlich.

Bei Problemen oder Fragen wenden Sie sich an die IT-Abteilung der ML Gruppe.