# ML Gruppe Helpdesk System

Ein umfassendes Django-basiertes Helpdesk-System mit Support-Ticketing, FAQ/Wissensdatenbank und KI-gestützten Auto-Responses.

## 🚀 Features

### Ticket-System
- ✅ Multi-Level Support (Level 1-4)
- ✅ Ticket-Eskalation zwischen Levels
- ✅ Chat-ähnliche Kommunikation
- ✅ Interne Notizen für Support-Team
- ✅ Auto-Email beim Ticket-Schließen
- ✅ Email-Benachrichtigungen bei neuen Tickets
- ✅ SLA-Tracking
- ✅ Claude AI Auto-Response für einfache Fragen

### FAQ/Wissensdatenbank
- ✅ Öffentliche und interne Artikel
- ✅ Suchfunktion
- ✅ Kategorie-Filter
- ✅ Helpfulness-Voting
- ✅ Featured Articles

### Benutzerrollen
- **Admin**: Vollzugriff auf System und Django Admin
- **Support Agent (L1-L4)**: Ticket-Management, FAQ-Erstellung (ab L2)
- **Kunde**: Ticket-Erstellung, FAQ-Zugriff

### Authentifizierung
- ✅ Selbstregistrierung für Kunden
- ✅ Email-basierte Authentifizierung
- ✅ Passwort-Management

---

## 📋 Voraussetzungen

- Python 3.8+
- MySQL/PostgreSQL/SQLite
- SMTP Server für Email-Versand (optional)
- Anthropic API Key für Claude AI (optional)

---

## 🔧 Installation

### Methode 1: Standalone mit systemd (Linux)

#### 1. System vorbereiten
```bash
# Als root oder mit sudo
apt update
apt install python3 python3-pip python3-venv nginx supervisor git

# Benutzer für die Anwendung erstellen
useradd -m -s /bin/bash helpdesk
```

#### 2. Projekt clonen/kopieren
```bash
# Als helpdesk user
su - helpdesk
mkdir -p /home/helpdesk/app
cd /home/helpdesk/app

# Projekt-Dateien hierhin kopieren oder clonen
# git clone <your-repo> .
```

#### 3. Virtual Environment einrichten
```bash
cd /home/helpdesk/app
python3 -m venv venv
source venv/bin/activate

# Dependencies installieren
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Datenbank & Konfiguration
```bash
# .env Datei erstellen
cat > .env << 'EOF'
DEBUG=False
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
ALLOWED_HOSTS=ihre-domain.de,www.ihre-domain.de
DATABASE_URL=sqlite:///helpdesk.db

# Email-Konfiguration
EMAIL_USERNAME=support@ihre-domain.de
EMAIL_PASSWORD=ihr-password
SMTP_HOST=smtp.office365.com
SMTP_PORT=587

# Optional: Claude AI
CLAUDE_API_KEY=sk-ant-api03-...

# Optional: Sentry
SENTRY_DSN=
EOF

# Datenbank migrieren
python manage.py migrate
python manage.py collectstatic --noinput

# Admin-Benutzer erstellen
python manage.py createsuperuser
```

#### 5. Gunicorn konfigurieren
```bash
# gunicorn installieren
pip install gunicorn

# gunicorn_config.py erstellen
cat > gunicorn_config.py << 'EOF'
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
errorlog = "/home/helpdesk/app/logs/gunicorn-error.log"
accesslog = "/home/helpdesk/app/logs/gunicorn-access.log"
loglevel = "info"
EOF

# Log-Verzeichnis erstellen
mkdir -p logs
```

#### 6. systemd Service einrichten
```bash
# Als root
sudo cat > /etc/systemd/system/helpdesk.service << 'EOF'
[Unit]
Description=ML Gruppe Helpdesk
After=network.target

[Service]
Type=notify
User=helpdesk
Group=helpdesk
WorkingDirectory=/home/helpdesk/app
Environment="PATH=/home/helpdesk/app/venv/bin"
ExecStart=/home/helpdesk/app/venv/bin/gunicorn helpdesk.wsgi:application -c gunicorn_config.py
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Service aktivieren und starten
sudo systemctl daemon-reload
sudo systemctl enable helpdesk
sudo systemctl start helpdesk
sudo systemctl status helpdesk
```

#### 7. Nginx konfigurieren
```bash
# Als root
sudo cat > /etc/nginx/sites-available/helpdesk << 'EOF'
server {
    listen 80;
    server_name ihre-domain.de www.ihre-domain.de;

    client_max_body_size 16M;

    location /static/ {
        alias /home/helpdesk/app/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /home/helpdesk/app/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
EOF

# Site aktivieren
sudo ln -s /etc/nginx/sites-available/helpdesk /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 8. SSL mit Let's Encrypt (optional)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d ihre-domain.de -d www.ihre-domain.de
```

---

### Methode 2: ISPConfig mit Nginx

#### 1. Website in ISPConfig anlegen
1. Login in ISPConfig
2. **Websites** → **Website** → **Add new website**
3. Domain: `ihre-domain.de`
4. Auto-Subdomain: `www`
5. **Save**

#### 2. Python Virtual Environment einrichten
```bash
# Per SSH auf Server verbinden
ssh username@ihre-domain.de

# Ins Web-Verzeichnis wechseln
cd /var/www/clients/client1/web1

# Projekt-Ordner erstellen
mkdir -p helpdesk
cd helpdesk

# Virtual Environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

#### 3. Projekt deployen
```bash
# Projekt-Dateien hochladen (z.B. via SFTP/SCP)
# Oder direkt clonen falls Git verfügbar

# Dependencies installieren
pip install -r requirements.txt

# .env konfigurieren (siehe oben)
nano .env

# Datenbank migrieren
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

#### 4. Gunicorn als Systemd Service
```bash
# gunicorn installieren
pip install gunicorn

# Service-Datei erstellen (als root)
sudo nano /etc/systemd/system/helpdesk-web1.service
```

Inhalt:
```ini
[Unit]
Description=Helpdesk Web1
After=network.target

[Service]
User=web1
Group=client1
WorkingDirectory=/var/www/clients/client1/web1/helpdesk
Environment="PATH=/var/www/clients/client1/web1/helpdesk/venv/bin"
ExecStart=/var/www/clients/client1/web1/helpdesk/venv/bin/gunicorn helpdesk.wsgi:application -b 127.0.0.1:8001 -w 4
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Service starten
sudo systemctl daemon-reload
sudo systemctl enable helpdesk-web1
sudo systemctl start helpdesk-web1
```

#### 5. Nginx in ISPConfig konfigurieren
1. **Websites** → Ihre Website bearbeiten
2. **Options** → **Nginx Directives**

```nginx
location /static/ {
    alias /var/www/clients/client1/web1/helpdesk/staticfiles/;
    expires 30d;
}

location /media/ {
    alias /var/www/clients/client1/web1/helpdesk/media/;
    expires 7d;
}

location / {
    proxy_pass http://127.0.0.1:8001;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

3. **Save**
4. SSL-Zertifikat über ISPConfig aktivieren (Let's Encrypt)

---

### Methode 3: Apache mit mod_wsgi

#### 1. Apache & mod_wsgi installieren
```bash
sudo apt install apache2 libapache2-mod-wsgi-py3
```

#### 2. Projekt einrichten
```bash
# Projekt-Verzeichnis
sudo mkdir -p /var/www/helpdesk
sudo chown $USER:$USER /var/www/helpdesk
cd /var/www/helpdesk

# Virtual Environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Konfiguration (siehe oben)
nano .env

# Datenbank
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

# Berechtigungen für Apache
sudo chown -R www-data:www-data /var/www/helpdesk
sudo chmod -R 755 /var/www/helpdesk
```

#### 3. Apache VirtualHost konfigurieren
```bash
sudo nano /etc/apache2/sites-available/helpdesk.conf
```

Inhalt:
```apache
<VirtualHost *:80>
    ServerName ihre-domain.de
    ServerAlias www.ihre-domain.de
    ServerAdmin admin@ihre-domain.de

    DocumentRoot /var/www/helpdesk

    # Python Path
    WSGIDaemonProcess helpdesk python-home=/var/www/helpdesk/venv python-path=/var/www/helpdesk
    WSGIProcessGroup helpdesk
    WSGIScriptAlias / /var/www/helpdesk/helpdesk/wsgi.py

    <Directory /var/www/helpdesk/helpdesk>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

    # Static files
    Alias /static /var/www/helpdesk/staticfiles
    <Directory /var/www/helpdesk/staticfiles>
        Require all granted
    </Directory>

    # Media files
    Alias /media /var/www/helpdesk/media
    <Directory /var/www/helpdesk/media>
        Require all granted
    </Directory>

    # Logging
    ErrorLog ${APACHE_LOG_DIR}/helpdesk-error.log
    CustomLog ${APACHE_LOG_DIR}/helpdesk-access.log combined
</VirtualHost>
```

#### 4. Site aktivieren
```bash
# Site aktivieren
sudo a2ensite helpdesk.conf
sudo a2enmod wsgi
sudo systemctl restart apache2

# SSL mit Certbot (optional)
sudo apt install certbot python3-certbot-apache
sudo certbot --apache -d ihre-domain.de -d www.ihre-domain.de
```

---

## 🔐 Sicherheit

### Production Checklist
- [ ] `DEBUG=False` in `.env`
- [ ] Starken `SECRET_KEY` generieren
- [ ] `ALLOWED_HOSTS` auf Ihre Domain setzen
- [ ] SSL-Zertifikat installiert
- [ ] Firewall konfiguriert (nur Port 80/443 offen)
- [ ] Regelmäßige Backups einrichten
- [ ] Database-Credentials sicher verwahren
- [ ] Email-Credentials verschlüsselt speichern

### Backup-Strategie
```bash
# Datenbank Backup
python manage.py dumpdata > backup_$(date +%Y%m%d).json

# Oder für SQLite
cp helpdesk.db helpdesk_backup_$(date +%Y%m%d).db

# Media-Dateien
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/
```

---

## 📊 Monitoring

### Service-Status prüfen
```bash
# systemd Service
sudo systemctl status helpdesk

# Logs ansehen
sudo journalctl -u helpdesk -f

# Nginx Logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Gunicorn Logs
tail -f /home/helpdesk/app/logs/gunicorn-error.log
```

---

## 🔄 Updates durchführen

```bash
# Als helpdesk user
cd /home/helpdesk/app
source venv/bin/activate

# Code aktualisieren
git pull  # oder Dateien kopieren

# Dependencies aktualisieren
pip install -r requirements.txt --upgrade

# Datenbank migrieren
python manage.py migrate

# Static files sammeln
python manage.py collectstatic --noinput

# Service neustarten
sudo systemctl restart helpdesk
```

---

## 🐛 Troubleshooting

### Service startet nicht
```bash
# Status und Fehler prüfen
sudo systemctl status helpdesk
sudo journalctl -u helpdesk -n 50

# Manuell testen
cd /home/helpdesk/app
source venv/bin/activate
python manage.py runserver
```

### Datenbank-Fehler
```bash
# Migrationen prüfen
python manage.py showmigrations

# Fehlende Migrationen
python manage.py migrate
```

### Static Files nicht gefunden
```bash
# Neu sammeln
python manage.py collectstatic --clear --noinput

# Berechtigungen prüfen
sudo chown -R helpdesk:helpdesk /home/helpdesk/app/staticfiles
sudo chmod -R 755 /home/helpdesk/app/staticfiles
```

### Email-Versand funktioniert nicht
```bash
# SMTP-Verbindung testen
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
```

---

## 📝 Konfiguration

### Wichtige Einstellungen in `.env`

| Variable | Beschreibung | Beispiel |
|----------|--------------|----------|
| `DEBUG` | Debug-Modus (nur Development!) | `False` |
| `SECRET_KEY` | Django Secret Key | Generierter String |
| `ALLOWED_HOSTS` | Erlaubte Domains | `domain.de,www.domain.de` |
| `DATABASE_URL` | Datenbank-URL | `sqlite:///db.sqlite3` |
| `EMAIL_USERNAME` | SMTP Email | `support@domain.de` |
| `EMAIL_PASSWORD` | SMTP Passwort | `***` |
| `SMTP_HOST` | SMTP Server | `smtp.office365.com` |
| `SMTP_PORT` | SMTP Port | `587` |
| `CLAUDE_API_KEY` | Claude AI API Key (optional) | `sk-ant-api03-...` |

---

## 👥 Support

Bei Fragen oder Problemen:
- Email: support@ml-gruppe.de
- Dokumentation: [BENUTZERHANDBUCH.md](BENUTZERHANDBUCH.md)

---

## 📄 Lizenz

© 2025 ML Gruppe - Alle Rechte vorbehalten
