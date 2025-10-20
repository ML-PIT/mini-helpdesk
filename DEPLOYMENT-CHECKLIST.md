# Production Deployment Checklist

## ⚠️ KRITISCH - Vor jedem Deployment prüfen!

### 1. Sicherheit

- [ ] `DEBUG=False` in `.env` gesetzt
- [ ] `SECRET_KEY` auf sicheren, zufälligen Wert geändert (min. 50 Zeichen)
- [ ] `ALLOWED_HOSTS` korrekt konfiguriert (nur Production-Domains)
- [ ] Keine Debug-Informationen in Templates
- [ ] Keine hardcoded Passwörter oder API-Keys im Code
- [ ] `.env` Datei in UTF-8 ohne Umlaute
- [ ] `.env` nicht in Git committed (in .gitignore)

### 2. Datenbank

- [ ] Production-Datenbank konfiguriert (MySQL/PostgreSQL, nicht SQLite)
- [ ] Database-Backups eingerichtet
- [ ] Migrations getestet und ausgeführt
- [ ] Database-User hat minimale Rechte (nur nötige Permissions)
- [ ] Database-Passwort ist sicher

### 3. Server-Konfiguration

- [ ] Gunicorn/uWSGI als WSGI-Server (nicht Django's runserver!)
- [ ] Nginx/Apache als Reverse Proxy
- [ ] SSL/TLS Zertifikat installiert
- [ ] Firewall konfiguriert
- [ ] Nur notwendige Ports offen (80, 443, ggf. SSH)
- [ ] Server-User ohne Root-Rechte
- [ ] Logs rotieren automatisch

### 4. Django Settings

- [ ] `SECURE_SSL_REDIRECT=True`
- [ ] `SESSION_COOKIE_SECURE=True`
- [ ] `CSRF_COOKIE_SECURE=True`
- [ ] `SECURE_HSTS_SECONDS` gesetzt
- [ ] `X_FRAME_OPTIONS='DENY'`
- [ ] Static Files mit `collectstatic` gesammelt
- [ ] Media Files Ordner existiert mit korrekten Permissions

### 5. Performance

- [ ] Redis für Caching konfiguriert
- [ ] Celery für Background Tasks
- [ ] Database-Indizes optimiert
- [ ] Static Files Caching aktiviert
- [ ] Gunicorn Worker-Anzahl korrekt (2-4 x CPU cores)

### 6. Monitoring & Logging

- [ ] Sentry oder alternatives Error-Tracking konfiguriert
- [ ] Logging in Production-Mode
- [ ] Log-Rotation eingerichtet
- [ ] Server-Monitoring (CPU, RAM, Disk)
- [ ] Uptime-Monitoring

### 7. Backup

- [ ] Automatische Datenbank-Backups (täglich)
- [ ] Media-Files Backup
- [ ] Backup-Restore getestet
- [ ] Off-site Backup-Speicherung

### 8. Testing vor Deployment

- [ ] Alle Tests erfolgreich (`python manage.py test`)
- [ ] Migrations in Test-Umgebung getestet
- [ ] Security-Check: `python manage.py check --deploy`
- [ ] Performance-Tests durchgeführt
- [ ] Browser-Testing (verschiedene Browser)

### 9. Deployment-Prozess

- [ ] Deployment-Dokumentation aktuell
- [ ] Rollback-Plan vorhanden
- [ ] Wartungsfenster kommuniziert
- [ ] Backup vor Deployment
- [ ] Schritt-für-Schritt Deployment befolgen

### 10. Nach dem Deployment

- [ ] Admin-Interface erreichbar und funktional
- [ ] Login funktioniert
- [ ] Alle URLs erreichbar
- [ ] Static Files werden geladen
- [ ] Email-Versand funktioniert
- [ ] Celery Tasks laufen
- [ ] Logs auf Errors prüfen

## 🚨 Was NIEMALS in Production:

- ❌ `DEBUG=True`
- ❌ `python manage.py runserver` als Production-Server
- ❌ SQLite als Production-Datenbank (außer sehr kleine Apps)
- ❌ Hardcoded Secrets im Code
- ❌ Default `SECRET_KEY`
- ❌ Port 8000/8080 öffentlich erreichbar
- ❌ Root-User für Django-Prozess
- ❌ Fehlende SSL-Zertifikate
- ❌ Unverschlüsselte Passwörter in `.env`
- ❌ Keine Backups

## Server-Start Commands (Production)

### ❌ FALSCH (Development):
```bash
python manage.py runserver
```

### ✅ RICHTIG (Production):
```bash
# Mit Gunicorn
gunicorn helpdesk.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile /var/log/gunicorn-access.log \
    --error-logfile /var/log/gunicorn-error.log \
    --daemon

# Oder als Systemd Service
sudo systemctl start helpdesk
sudo systemctl status helpdesk
```

## Security Check ausführen

```bash
# IMMER vor Production-Deployment!
python manage.py check --deploy

# Erwartete Warnungen beheben:
# - SECURE_HSTS_SECONDS
# - SECURE_SSL_REDIRECT
# - SESSION_COOKIE_SECURE
# - CSRF_COOKIE_SECURE
```

## Rollback-Plan

Falls Deployment fehlschlägt:

1. Datenbank aus Backup wiederherstellen
2. Alte Code-Version deployen
3. Server neu starten
4. Tests durchführen
5. Fehleranalyse im Log

## Support-Kontakte

- **System-Admin**: [Name/E-Mail]
- **DevOps**: [Name/E-Mail]
- **Notfall-Hotline**: [Telefon]

---

**Datum**: ______________________

**Deployment von**: ______________________

**Geprüft von**: ______________________

**Unterschrift**: ______________________
