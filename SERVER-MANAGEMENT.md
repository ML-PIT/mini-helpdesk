# Server Management - Best Practices

## 🚨 WICHTIG: Development Server Management

### Problem: Mehrere laufende Server-Instanzen

**Was passiert ist:**
- Mehrere `manage.py runserver` Prozesse im Hintergrund
- Ports blockiert
- Unklarer Zustand
- **DARF IN PRODUCTION NIEMALS PASSIEREN!**

### ✅ Korrekte Vorgehensweise

#### Development (lokal):

```bash
# Server starten (Vordergrund)
python manage.py runserver

# Stoppen: Strg + C
```

**NIEMALS:**
- Server im Hintergrund mit `&` starten
- Mehrere Instanzen parallel laufen lassen
- Terminal einfach schließen ohne Server zu stoppen

#### Production (Server):

```bash
# Mit Systemd Service
sudo systemctl start helpdesk
sudo systemctl stop helpdesk
sudo systemctl restart helpdesk
sudo systemctl status helpdesk

# Logs prüfen
sudo journalctl -u helpdesk -f
```

## Server-Status prüfen

### Welche Server laufen?

**Windows:**
```bash
netstat -ano | findstr ":8000"
netstat -ano | findstr ":8080"

# Prozess beenden (mit PID aus netstat)
taskkill /PID [PID] /F
```

**Linux:**
```bash
# Ports prüfen
sudo lsof -i :8000
sudo lsof -i :8080

# Prozesse finden
ps aux | grep "manage.py runserver"

# Prozess beenden
kill [PID]
# Oder forciert
kill -9 [PID]
```

## Production Deployment - Systemd Service

### Warum Systemd?

- ✅ Kontrolliertes Starten/Stoppen
- ✅ Automatischer Neustart bei Crash
- ✅ Logging integriert
- ✅ Keine "vergessenen" Prozesse
- ✅ Status jederzeit prüfbar

### Service-Datei erstellen

`/etc/systemd/system/helpdesk.service`:

```ini
[Unit]
Description=ML Gruppe Helpdesk (Django)
After=network.target postgresql.service

[Service]
Type=notify
User=helpdesk
Group=helpdesk
WorkingDirectory=/var/www/helpdesk
Environment="PATH=/var/www/helpdesk/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=helpdesk.settings"

# Gunicorn (richtig!)
ExecStart=/var/www/helpdesk/venv/bin/gunicorn \
    helpdesk.wsgi:application \
    --bind unix:/var/www/helpdesk/helpdesk.sock \
    --workers 4 \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --access-logfile /var/log/helpdesk/gunicorn-access.log \
    --error-logfile /var/log/helpdesk/gunicorn-error.log \
    --log-level info

# Graceful Shutdown
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30

# Neustart bei Crash
Restart=always
RestartSec=5

# Sicherheit
PrivateTmp=true
NoNewPrivileges=true
ProtectSystem=full
ProtectHome=true

[Install]
WantedBy=multi-user.target
```

### Service aktivieren

```bash
# Service-Datei registrieren
sudo systemctl daemon-reload

# Service aktivieren (Start beim Booten)
sudo systemctl enable helpdesk

# Service starten
sudo systemctl start helpdesk

# Status prüfen
sudo systemctl status helpdesk

# Logs anschauen
sudo journalctl -u helpdesk -f
```

## Health Checks

### Automated Health Check Script

`/usr/local/bin/check-helpdesk.sh`:

```bash
#!/bin/bash

# Health Check für Helpdesk
URL="http://localhost:8000/admin/"
EXPECTED_STATUS=200

# HTTP Request
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $URL)

if [ $STATUS -eq $EXPECTED_STATUS ]; then
    echo "✅ Helpdesk is healthy (HTTP $STATUS)"
    exit 0
else
    echo "❌ Helpdesk is down (HTTP $STATUS)"

    # Optional: Service neustarten
    # sudo systemctl restart helpdesk

    # Optional: Alert senden
    # mail -s "Helpdesk Down" admin@example.com

    exit 1
fi
```

### Cron Job für regelmäßige Checks

```bash
# /etc/cron.d/helpdesk-health
*/5 * * * * root /usr/local/bin/check-helpdesk.sh >> /var/log/helpdesk-health.log 2>&1
```

## Deployment Workflow

### 1. Vorbereitung

```bash
# Backup!
sudo -u postgres pg_dump helpdesk_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Code aktualisieren
cd /var/www/helpdesk
git pull origin main
```

### 2. Dependencies & Migrations

```bash
# Virtual Environment aktivieren
source venv/bin/activate

# Dependencies aktualisieren
pip install -r requirements.txt

# Migrations prüfen
python manage.py showmigrations

# Migrations ausführen
python manage.py migrate

# Static Files sammeln
python manage.py collectstatic --no-input
```

### 3. Service neu starten

```bash
# Graceful Reload (Gunicorn)
sudo systemctl reload helpdesk

# Oder komplett neu starten
sudo systemctl restart helpdesk

# Status prüfen
sudo systemctl status helpdesk
```

### 4. Verification

```bash
# HTTP Status
curl -I http://localhost:8000/

# Logs prüfen
sudo journalctl -u helpdesk -n 50

# Fehler suchen
sudo journalctl -u helpdesk | grep ERROR
```

## Monitoring

### Essential Monitoring Points

1. **HTTP Verfügbarkeit**
   - Tool: Uptime Robot, Pingdom
   - Check: Alle 5 Minuten

2. **Response Time**
   - Tool: New Relic, DataDog
   - Threshold: < 500ms

3. **Error Rate**
   - Tool: Sentry
   - Alert bei > 1% Error Rate

4. **Server Resources**
   - CPU < 80%
   - RAM < 90%
   - Disk < 85%

5. **Database Performance**
   - Query Time < 100ms
   - Connection Pool < 80%

## Emergency Procedures

### Server reagiert nicht

```bash
# 1. Status prüfen
sudo systemctl status helpdesk

# 2. Logs anschauen
sudo journalctl -u helpdesk -n 100

# 3. Service neu starten
sudo systemctl restart helpdesk

# 4. Falls nicht hilft: Force Kill
sudo systemctl kill helpdesk
sudo systemctl start helpdesk
```

### Zu viele Worker

```bash
# Worker-Anzahl anpassen
# In /etc/systemd/system/helpdesk.service
--workers 2  # Reduzieren

# Service neu laden
sudo systemctl daemon-reload
sudo systemctl restart helpdesk
```

### Memory Leak

```bash
# Prozess neu starten
sudo systemctl restart helpdesk

# Worker regelmäßig neu starten (in gunicorn config)
--max-requests 1000 --max-requests-jitter 50
```

## Checkliste: Vor jedem Server-Start

- [ ] Nur EINE Instanz läuft
- [ ] Port ist frei
- [ ] Virtual Environment aktiviert
- [ ] `.env` korrekt konfiguriert
- [ ] Migrations ausgeführt
- [ ] Static Files gesammelt
- [ ] Logs-Ordner existiert
- [ ] Berechtigungen korrekt

## Checkliste: Server-Stopp

- [ ] Graceful Shutdown (kein `kill -9`)
- [ ] Aktive Requests abwarten
- [ ] Port freigegeben
- [ ] Keine Zombie-Prozesse
- [ ] Logs archiviert

---

**Merke:**
- Development: `python manage.py runserver` (nur lokal!)
- Production: **Systemd + Gunicorn** (niemals manage.py runserver!)

Ein professionelles Setup verhindert solche Probleme von Anfang an.
