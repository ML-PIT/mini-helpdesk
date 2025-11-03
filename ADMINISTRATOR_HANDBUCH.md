# 👑 Administrator Handbuch
## Aboro-IT Helpdesk System - Vollständige Systemverwaltung

![Aboro-IT Logo](https://via.placeholder.com/400x150/FF4444/FFFFFF?text=ABORO-IT)

---

## 📋 Inhaltsverzeichnis

1. [Systemübersicht](#systemübersicht)
2. [Erste Einrichtung](#erste-einrichtung)
3. [Benutzerverwaltung](#benutzerverwaltung)
4. [Live-Chat System](#live-chat-system)
5. [KI-Integration & Claude/ChatGPT](#ki-integration--claudechatgpt)
6. [Ticket-System Administration](#ticket-system-administration)
7. [Wissensdatenbank Management](#wissensdatenbank-management)
8. [System-Einstellungen](#system-einstellungen)
9. [Lizenz-Management](#lizenz-management)
10. [Backup & Wartung](#backup--wartung)
11. [Monitoring & Logs](#monitoring--logs)
12. [Troubleshooting](#troubleshooting)

---

## 🏗️ Systemübersicht

### Architektur
- **Framework**: Django 5.0+ mit Python 3.13+
- **Datenbank**: SQLite (Standard) / PostgreSQL (Produktion)
- **Frontend**: Bootstrap 5 + Vanilla JavaScript
- **KI-Integration**: Claude API + OpenAI ChatGPT
- **Live-Chat**: WebSocket-basiert mit Polling Fallback

### Benutzerrollen
| Rolle | Beschreibung | Berechtigung |
|-------|--------------|--------------|
| **Admin** | Vollzugriff | Alles |
| **Support Agent L4** | Senior Expert + Team Lead | Alle Benutzer verwalten außer Admins |
| **Support Agent L3** | Expert Support | Kunden + L1-L2 Agents verwalten |
| **Support Agent L2** | Technical Support | Kunden verwalten |
| **Support Agent L1** | Basic Support | Nur Kunden verwalten |
| **Kunde** | Endbenutzer | Tickets erstellen/verwalten |

---

## 🚀 Erste Einrichtung

### 1. Admin-Benutzer erstellen
```bash
cd /path/to/mini-helpdesk
python manage.py createsuperuser
```

### 2. Grundkonfiguration
1. Öffnen Sie `/admin/`
2. Gehen Sie zu **System Settings**
3. Konfigurieren Sie:
   - **Firmenname**: Aboro-IT
   - **E-Mail-Einstellungen**: SMTP-Server
   - **App-Name & Logo**: Anpassung
   - **KI-Einstellungen**: Claude/ChatGPT APIs

### 3. Chat-Einstellungen
1. Gehen Sie zu **Chat Settings**
2. Konfigurieren Sie:
   - **Widget-Farbe**: Standard #667eea
   - **Willkommensnachricht**
   - **Offline-Nachricht**
   - **Auto-Zuweisung**: Aktiviert

### 4. Lizenz-System aktivieren
1. Generieren Sie Lizenz mit `tools/license_generator.py`
2. Installieren Sie Lizenz im Admin-Panel
3. Überprüfen Sie Gültigkeit

---

## 👥 Benutzerverwaltung

### Über die Web-Oberfläche

#### Benutzer erstellen
1. **Navigation**: Benutzerverwaltung
2. **Button**: "Neuen Benutzer erstellen"
3. **Ausfüllen**:
   ```
   ✅ Grunddaten: Name, E-Mail, Passwort
   ✅ Rolle & Level: Admin/Support Agent/Kunde
   ✅ Support Level: 1-4 (nur bei Agents)
   ✅ Kontaktdaten: Telefon, Adresse
   ✅ Status: Aktiv/Inaktiv
   ```

#### Benutzer bearbeiten
1. **Listen-Ansicht**: Alle Benutzer
2. **Klick auf Benutzer** → Detail-Ansicht
3. **"Bearbeiten"** → Alle Felder änderbar
4. **Aktionen**:
   - ⚡ Status aktivieren/deaktivieren
   - 🔑 Passwort zurücksetzen
   - 📧 Willkommens-E-Mail senden

#### Berechtigungsmatrix

| Aktion | Admin | L4 | L3 | L2 | L1 |
|--------|-------|----|----|----|----|
| Admins verwalten | ✅ | ❌ | ❌ | ❌ | ❌ |
| Support L4 verwalten | ✅ | ✅ | ❌ | ❌ | ❌ |
| Support L3 verwalten | ✅ | ✅ | ✅ | ❌ | ❌ |
| Support L2 verwalten | ✅ | ✅ | ✅ | ✅ | ❌ |
| Support L1 verwalten | ✅ | ✅ | ✅ | ✅ | ✅ |
| Kunden verwalten | ✅ | ✅ | ✅ | ✅ | ✅ |

### Django Admin Interface
Für erweiterte Benutzerverwaltung:
- URL: `/admin/accounts/user/`
- Bulk-Aktionen
- Erweiterte Filter
- CSV-Export

---

## 💬 Live-Chat System

### Chat-Widget Konfiguration

#### 1. Grundeinstellungen
```python
# Admin → Chat Settings
Widget-Farbe: #667eea
Position: Bottom Right
Willkommensnachricht: "Hallo! Wie können wir Ihnen helfen?"
Offline-Nachricht: "Wir sind offline. Schreiben Sie uns eine E-Mail."
```

#### 2. Widget in Website einbinden
```html
<!-- Standard Integration -->
<iframe src="https://your-domain.com/chat/widget/" 
        width="350" height="450" 
        style="position:fixed;bottom:20px;right:20px;border:none;border-radius:10px;">
</iframe>

<!-- Direktes Embedding (für eingeloggte Kunden) -->
<script>
fetch('/chat/widget-data/?customer=true&user_name=Max&user_email=max@example.com')
.then(response => response.json())
.then(data => {
    if (data.success) {
        renderChatWidget(data.widget_data);
    }
});
</script>
```

### Agent Dashboard
- **URL**: `/chat/dashboard/`
- **Zugriff**: Support Agents + Admins
- **Funktionen**:
  - 📊 Wartende Chats
  - 🚨 Eskalierte Chats
  - 💻 Aktive Chats
  - 🤖 KI-verwaltete Chats

### Chat-Status Management
| Status | Bedeutung | Wer kann zuweisen |
|--------|-----------|-------------------|
| **waiting** | Wartet auf Agent | Automatisch |
| **active** | Agent/KI bearbeitet | Agent übernimmt |
| **escalated** | Automatisch eskaliert | KI-System |
| **ended** | Chat beendet | Agent |

---

## 🤖 KI-Integration & Claude/ChatGPT

### System-Einstellungen
```python
# Admin → System Settings → KI-Konfiguration
AI Enabled: ✅ Aktiviert
AI Provider: Claude / ChatGPT
AI Response Delay: 3 Sekunden
AI Max Tokens: 1000
```

### API-Konfiguration

#### Claude (Anthropic)
```python
Anthropic API Key: sk-ant-api03-...
Model: claude-3-haiku-20240307
```

#### ChatGPT (OpenAI)
```python
OpenAI API Key: sk-...
Model: gpt-3.5-turbo
```

### KI-Funktionalitäten

#### 1. Intelligente Problem-Kategorisierung
```python
Kategorien:
- Login-Probleme
- E-Mail-Probleme  
- Performance-Probleme
- Netzwerk-Probleme
- Software-Probleme
- Hardware-Probleme
```

#### 2. User Expertise Detection
```python
Levels:
- Beginner: Einfache Sprache
- Intermediate: Technische Details
- Advanced: Vollständige technische Informationen
```

#### 3. Auto-Eskalation Trigger
```python
Eskalation bei:
- ≥4 User-Nachrichten ohne Lösung
- Frustrations-Keywords
- Kritische Sicherheitsprobleme
- Spezielle Eskalations-Wörter
```

#### 4. Fallback-Mechanismen
```python
Reihenfolge:
1. Primary Provider (Claude/ChatGPT)
2. Secondary Provider (ChatGPT/Claude)
3. Free AI Response
4. Emergency Response
```

### KI-Antwort-Qualität

#### Prompting-System
```python
System Prompt Includes:
✅ Problemlösungsstrategie
✅ Adaptive Kommunikation
✅ Kontextuelle Lösungsstrategien
✅ Proaktive Unterstützung
✅ Smart Escalation Criteria
✅ Qualitätsindikatoren
✅ Kommunikationsrichtlinien
```

#### Conversation Memory
```python
Kontext speichert:
- User-Expertise-Level
- Problem-Typ & Schweregrad
- Bisherige Lösungsversuche
- Konversations-Stage
- User-Antworten (letzte 3)
```

---

## 🎫 Ticket-System Administration

### Ticket-Kategorien verwalten
1. **Admin → Tickets → Categories**
2. **Erstellen**: Name, Beschreibung, Farbe
3. **Zuweisen**: Standard-Support-Level

### Prioritäten & SLA
| Priorität | SLA (Response Time) | Farbe |
|-----------|-------------------|-------|
| **Critical** | 4 Stunden | 🔴 Rot |
| **High** | 24 Stunden | 🟠 Orange |
| **Medium** | 72 Stunden | 🟡 Gelb |
| **Low** | 1 Woche | 🟢 Grün |

### Status-Workflow
```
Neu (Offen) 
    ↓
In Bearbeitung (Agent zugewiesen)
    ↓
Wartet auf Kunde (Agent wartet auf Antwort)
    ↓
Gelöst (Problem behoben)
    ↓
Geschlossen (Final abgeschlossen)
```

### Auto-Assignment Regeln
1. **Aktiviert**: Automatische Zuweisung an verfügbare Agents
2. **Level-basiert**: Tickets werden nach Schwierigkeit zugewiesen
3. **Load Balancing**: Gleichmäßige Verteilung

---

## 📚 Wissensdatenbank Management

### FAQ-Kategorien
1. **Admin → Knowledge → Categories**
2. **Hierarchie**: Haupt- und Unterkategorien
3. **Sichtbarkeit**: Öffentlich/Intern

### Artikel-Management
```python
Artikel-Status:
- Entwurf: Nicht sichtbar
- Veröffentlicht: Sichtbar
- Archiviert: Versteckt

Berechtigungen:
- Erstellen: Support L2+
- Bearbeiten: Autor + L2+
- Löschen: Admin + L3+
```

### SEO & Suchoptimierung
- **Slug-URLs**: Automatisch generiert
- **Meta-Beschreibungen**: Für Suchmaschinen
- **Suchbegriffe**: Komma-getrennt
- **Volltext-Suche**: Titel + Inhalt + Tags

---

## ⚙️ System-Einstellungen

### Grundkonfiguration
```python
# Admin → System Settings
Firma: Aboro-IT
App Name: ML Helpdesk
Logo URL: /static/images/logo.png
Admin Email: admin@aboro-it.net
Support Phone: +49 XXX XXXXXXX
```

### E-Mail-Konfiguration
```python
# SMTP Settings
EMAIL_HOST: smtp.gmail.com
EMAIL_PORT: 587
EMAIL_USE_TLS: True
EMAIL_HOST_USER: noreply@aboro-it.net
EMAIL_HOST_PASSWORD: [App Password]

# Template Settings
FROM_EMAIL: Aboro-IT Support <noreply@aboro-it.net>
REPLY_TO: support@aboro-it.net
```

### Benachrichtigungen
```python
Email Notifications:
✅ Neues Ticket → Alle Agents
✅ Ticket-Antwort → Zugewiesener Agent
✅ Eskalation → Ziel-Agent
✅ Ticket geschlossen → Kunde
✅ Agent-Benachrichtigungen → Bei Zuweisung
```

### Design-Anpassungen
```python
# CSS Variables (base.html)
Primary Color: #667eea
Success Color: #51cf66
Danger Color: #ff6b6b
Warning Color: #ffd43b
Info Color: #74c0fc
```

---

## 🔐 Lizenz-Management

### Lizenz-Generator Tools
```bash
# Standalone Generator
cd tools/
python license_generator.py

# GUI Generator
python license_generator_gui.py

# EXE Generator
license_generator.exe
```

### Lizenz-Installation
1. **Admin Panel → License Management**
2. **Upload .lic file**
3. **Verification**: Automatische Überprüfung
4. **Activation**: Sofortige Aktivierung

### Lizenz-Typer
```python
License Types:
- trial: 30 Tage Testversion
- standard: 1 Jahr Standard-Funktionen
- professional: 1 Jahr alle Funktionen
- enterprise: 1 Jahr + Premium Support
- unlimited: Unbegrenzt
```

### Lizenz-Überwachung
```python
Status-Check:
✅ Gültigkeitsdatum
✅ Feature-Berechtigung
✅ Benutzer-Limits
✅ Manipulations-Schutz
```

---

## 💾 Backup & Wartung

### Automatische Backups
```bash
# Tägliche Datenbank-Backups
python manage.py dbbackup

# Media-Files Backup
python manage.py mediabackup

# Cron Job (Linux)
0 2 * * * cd /path/to/helpdesk && python manage.py dbbackup
```

### Manuelle Wartung
```bash
# Cache leeren
python manage.py clear_cache

# Logs rotieren
python manage.py rotate_logs

# Alte Tickets archivieren
python manage.py archive_old_tickets --days 365

# Statistiken neu berechnen
python manage.py recalculate_stats
```

### Update-Prozess
```bash
# 1. Backup erstellen
python manage.py dbbackup

# 2. Code aktualisieren
git pull origin main

# 3. Dependencies installieren
pip install -r requirements.txt

# 4. Migrationen ausführen
python manage.py migrate

# 5. Static Files sammeln
python manage.py collectstatic --noinput

# 6. Server neu starten
systemctl restart helpdesk
```

---

## 📊 Monitoring & Logs

### Log-Dateien
```python
Log-Locations:
/var/log/helpdesk/django.log     # Django Logs
/var/log/helpdesk/email.log      # E-Mail Logs
/var/log/helpdesk/chat.log       # Chat Logs
/var/log/helpdesk/ai.log         # KI-Service Logs
/var/log/helpdesk/error.log      # Error Logs
```

### Performance Monitoring
```python
Metrics:
- Response Times
- Active Users
- Chat Sessions
- Ticket Volume
- AI Response Rate
- Error Rate
```

### System Health Check
```bash
# Health Check Endpoint
curl https://your-domain.com/health/

# Response:
{
  "status": "healthy",
  "database": "ok",
  "ai_service": "ok",
  "chat_service": "ok",
  "email_service": "ok"
}
```

---

## 🔧 Troubleshooting

### Häufige Probleme

#### 1. KI antwortet nicht
```python
Problem: Keine KI-Antworten im Chat

Lösung:
1. System Settings → AI Enabled: ✅
2. API Keys korrekt konfiguriert
3. Logs prüfen: /var/log/helpdesk/ai.log
4. Fallback-System testt

Debug:
python manage.py shell
>>> from apps.chat.ai_service import AIService
>>> ai = AIService()
>>> ai.is_ai_enabled()
>>> ai.get_ai_response("Test", None)
```

#### 2. Chat-Widget lädt nicht
```python
Problem: Widget zeigt nicht an

Lösung:
1. Chat Settings → Is Enabled: ✅
2. CSP Headers prüfen
3. JavaScript Errors in Browser Console
4. CORS-Einstellungen prüfen

Debug:
fetch('/chat/widget-data/')
.then(r => r.json())
.then(console.log)
```

#### 3. E-Mails kommen nicht an
```python
Problem: Keine E-Mail-Benachrichtigungen

Lösung:
1. SMTP-Einstellungen prüfen
2. App-Passwort (Gmail)
3. Firewall/Port 587 offen
4. E-Mail-Queue prüfen

Debug:
python manage.py send_test_email admin@example.com
```

#### 4. Lizenz-Probleme
```python
Problem: "Lizenz ungültig" Meldung

Lösung:
1. Lizenz-Datei neu hochladen
2. Systemzeit/Datum prüfen
3. Lizenz-Generator neu verwenden
4. Admin kontaktieren

Debug:
python manage.py check_license
```

### Log-Level Konfiguration
```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',  # DEBUG/INFO/WARNING/ERROR
            'class': 'logging.FileHandler',
            'filename': '/var/log/helpdesk/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

---

## 📞 Support-Kontakte

### Technischer Support
- **E-Mail**: admin@aboro-it.net
- **Telefon**: +49 XXX XXXXXXX
- **Notfall**: 24/7 Hotline

### Lizenz-Support
- **E-Mail**: lizenz@aboro-it.net
- **Portal**: https://licenses.aboro-it.net

### Entwickler-Support
- **GitHub**: https://github.com/ml-gruppe/helpdesk
- **Dokumentation**: /docs/
- **API-Docs**: /api/docs/

---

## 📝 Changelog

### Version 2.0 - November 2025
- ✅ Live-Chat System mit KI-Integration
- ✅ Claude/ChatGPT API Integration
- ✅ Auto-Escalation System
- ✅ Erweiterte Benutzerverwaltung
- ✅ Conversation Memory
- ✅ Smart Problem Categorization

### Version 1.0 - Januar 2025
- ✅ Grundlegendes Ticket-System
- ✅ Benutzer-Rollen & Permissions
- ✅ FAQ/Wissensdatenbank
- ✅ E-Mail-Benachrichtigungen
- ✅ Lizenz-System

---

---

**© 2025 Aboro-IT - Vertrauliches Administrator-Handbuch**  
*Version 2.0 - November 2025*  
*Professionelle IT-Lösungen für Ihr Unternehmen*  
*https://aboro-it.net*