# ML Gruppe Helpdesk System

[![CI/CD Pipeline](https://github.com/mlgruppe/helpdesk/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/mlgruppe/helpdesk/actions)
[![Coverage](https://codecov.io/gh/mlgruppe/helpdesk/branch/main/graph/badge.svg)](https://codecov.io/gh/mlgruppe/helpdesk)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Ein umfassendes, produktionsreifes Helpdesk-System für die ML Gruppe mit modernen Technologien und KI-Integration.

## 🌟 Features

### Kern-Funktionen
- **🎫 Intelligentes Ticket-System** mit SLA-Tracking und automatischer Priorisierung
- **👤 Rollenbasierte Zugriffskontrolle** (Admin, Team Leader, Support Agent, Kunde)
- **🔐 Microsoft Office 365 OAuth2/MSAL Integration** für nahtlose Authentifizierung
- **📧 Vollständige Email-Integration** (IMAP/SMTP) mit automatischer Ticket-Erstellung
- **🤖 Claude AI Integration** mit Fallback-Optionen für intelligente Unterstützung
- **📱 RESTful API** mit JWT-Authentifizierung für mobile Apps
- **🔗 Microsoft Teams Integration** für Team-Benachrichtigungen
- **📊 Monitoring & Analytics Dashboard** mit Echtzeit-Metriken
- **🎯 Kunden-Portal** mit Self-Service-Funktionen
- **📚 Knowledge Base & FAQ System** mit Volltext-Suche
- **🐳 Docker-Unterstützung** für einfache Bereitstellung

### Technische Highlights
- **Multi-Database Support**: SQLite (Dev), MySQL (Prod), MongoDB (Advanced)
- **Horizontale Skalierung**: Load Balancer ready
- **Security First**: CSRF-Schutz, XSS-Prävention, SQL-Injection-Schutz
- **DSGVO-konform**: Sichere Datenhaltung und Audit-Logs
- **Performance optimiert**: Redis-Caching, Background-Tasks mit Celery
- **Monitoring**: Sentry-Integration, strukturiertes Logging

## 🏗️ Architektur

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Client    │    │   Mobile App    │    │  Teams/Email    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
              ┌─────────────────────────────────┐
              │        Nginx (Reverse Proxy)    │
              └─────────────────────────────────┘
                                 │
              ┌─────────────────────────────────┐
              │     Flask Application           │
              │  ┌─────────────────────────┐    │
              │  │     Auth Blueprint      │    │
              │  │   Tickets Blueprint     │    │
              │  │     API Blueprint       │    │
              │  │    Admin Blueprint      │    │
              │  │  Customer Blueprint     │    │
              │  │ Knowledge Blueprint     │    │
              │  └─────────────────────────┘    │
              └─────────────────────────────────┘
                                 │
    ┌────────────────────────────┼────────────────────────────┐
    │                            │                            │
┌───▼────┐              ┌───────▼────┐              ┌────────▼───┐
│ MySQL  │              │   Redis    │              │  Celery    │
│   DB   │              │  (Cache)   │              │ (Workers)  │
└────────┘              └────────────┘              └────────────┘
```

## 🚀 Quick Start

### Mit Docker (Empfohlen)

```bash
# Repository klonen
git clone https://github.com/mlgruppe/helpdesk.git
cd helpdesk

# Umgebung konfigurieren
cp .env.example .env
# .env bearbeiten mit Ihren Konfigurationen

# Entwicklungsumgebung starten
./deploy.sh dev deploy

# Oder manuell:
docker-compose -f docker-compose.dev.yml up -d
```

### Ohne Docker

```bash
# Abhängigkeiten installieren
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Datenbank initialisieren
export FLASK_APP=app.py
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
flask deploy

# Server starten
python app.py
```

## 📋 Systemanforderungen

### Mindestanforderungen
- **CPU**: 2 Kerne
- **RAM**: 4GB
- **Storage**: 20GB
- **OS**: Ubuntu 20.04+, CentOS 8+, Windows Server 2019+

### Produktionsumgebung
- **CPU**: 4+ Kerne
- **RAM**: 8GB+
- **Storage**: 50GB+ (SSD empfohlen)
- **Network**: 1Gbps
- **Backup**: Automatisierte tägliche Backups

## ⚙️ Konfiguration

### Umgebungsvariablen

```bash
# Flask-Konfiguration
SECRET_KEY=ihr-super-geheimer-schlüssel
FLASK_ENV=production

# Microsoft Office 365
MICROSOFT_CLIENT_ID=ihre-azure-app-client-id
MICROSOFT_CLIENT_SECRET=ihr-azure-app-secret
MICROSOFT_TENANT_ID=ihre-azure-tenant-id

# Email-Konfiguration
EMAIL_USERNAME=projekteit@mlgruppe.de
EMAIL_PASSWORD=ihr-email-passwort

# Datenbank
DATABASE_URL=mysql+pymysql://user:password@localhost/helpdesk_db

# Optional: Claude AI
CLAUDE_API_KEY=ihr-claude-api-schlüssel

# Optional: Teams Integration
TEAMS_WEBHOOK_URL=ihr-teams-webhook-url
```

### Office 365 App-Registrierung

1. **Azure Portal** öffnen → App-Registrierungen
2. **Neue Registrierung** erstellen:
   - Name: "ML Gruppe Helpdesk"
   - Unterstützte Kontotypen: Nur Konten in diesem Organisationsverzeichnis
   - Redirect URI: `https://helpdesk.mlgruppe.de/auth/oauth_callback`

3. **API-Berechtigungen** hinzufügen:
   - Microsoft Graph: `User.Read`, `Mail.Read`, `Mail.Send`

4. **Client Secret** erstellen und notieren

## 🔧 Bereitstellung

### Produktionsbereitstellung

```bash
# SSL-Zertifikate einrichten
./deploy.sh production ssl

# Produktionsumgebung deployen
./deploy.sh production deploy

# Backup erstellen
./deploy.sh production backup

# Logs überwachen
./deploy.sh production logs
```

### Detaillierte Bereitstellungsanleitung

Siehe [DEPLOYMENT.md](DEPLOYMENT.md) für:
- Docker-Bereitstellung
- Traditionelle Server-Installation
- SSL-Konfiguration
- Datenbank-Setup
- Monitoring & Wartung
- Fehlerbehebung

## 📊 Benutzerrollen & Berechtigungen

| Rolle | Beschreibung | Berechtigungen |
|-------|-------------|---------------|
| **Admin** | Systemadministrator | Alle Berechtigungen, API-Key-Verwaltung, Systemkonfiguration |
| **Team Leader** | Team-Leiter | Ticket-Zuweisung, Agent-Verwaltung, volle Ticket-Berechtigungen, Analytics |
| **Support Agent** | Support-Mitarbeiter | Ticket-Selbstzuweisung, Erstellung, Bearbeitung, Beantwortung |
| **Kunde/Endnutzer** | Endbenutzer | Ticket-Erstellung, eigene Tickets einsehen, Kommentare, Status verfolgen |

## 🎯 SLA-Management

### Prioritäten & SLA-Zeiten

| Priorität | SLA-Zeit | Beschreibung |
|-----------|----------|-------------|
| **Kritisch** | 4 Stunden | System ausgefallen, schwerwiegende Geschäftsauswirkungen |
| **Hoch** | 24 Stunden | Geschäftsauswirkungen, benötigt dringende Aufmerksamkeit |
| **Mittel** | 72 Stunden | Standard-Support-Anfrage |
| **Niedrig** | 1 Woche | Allgemeine Fragen oder kleinere Probleme |

### SLA-Tracking Features
- ⏰ Automatische SLA-Berechnung basierend auf Priorität
- 🚨 SLA-Verletzungswarnungen
- 📈 SLA-Compliance-Berichte
- 📊 Erste-Antwort-Zeit-Tracking
- ⭐ Kundenzufriedenheitsbewertungen

## 🤖 Claude AI Integration

### Verfügbare Features (mit API-Key)
- 💡 Automatische Antwortvorschläge für Agents
- 🏷️ Intelligente Ticket-Kategorisierung
- 📝 Knowledge Base Artikel-Generierung
- 🎯 FAQ-Antworten basierend auf gelösten Tickets
- 😊 Sentiment-Analyse für Kundenkommunikation

### Fallback-Optionen (ohne API-Key)
- 🔗 "Mit Claude öffnen" Button für manuellen Chat
- 📋 Vorformulierte Prompts für häufige Support-Anfragen
- 💾 Ticket-Kontext in Zwischenablage für externe Nutzung

## 📱 API & Mobile Support

### REST API Features
- 🔑 JWT-Authentifizierung
- 📄 Vollständige CRUD-Operationen für Tickets
- 📊 Dashboard-Statistiken
- 📚 Knowledge Base Zugriff
- 📈 Analytics-Endpoints (Admin/Team Leader)
- 🔍 Erweiterte Filterung und Suche

### API-Dokumentation
- 📖 Interaktive Swagger-Dokumentation: `/api/docs`
- 📋 Postman-Collection verfügbar
- 🛠️ SDK-Beispiele für JavaScript/Python
- 📱 Mobile App ready

Siehe [API.md](API.md) für detaillierte API-Dokumentation.

## 📧 Email-Integration

### IMAP-Features
- 📥 Automatische Ticket-Erstellung aus eingehenden Emails
- 🔗 Email-Threading für Ticket-Kommunikation
- 📎 Automatische Anhangserkennung
- 👤 Automatische Benutzer-Erstellung

### SMTP-Features
- 📤 Automatische Benachrichtigungen
- 🤖 Auto-Reply mit Ticket-Nummer
- 📊 Status-Update-Benachrichtigungen
- 🎯 Rollenbasierte Benachrichtigungen

## 📊 Monitoring & Analytics

### Dashboard-Metriken
- 🎫 Ticket-Statistiken (Gesamt, Offen, In Bearbeitung, Gelöst)
- ⏱️ Durchschnittliche Antwort- und Lösungszeiten
- 📈 SLA-Compliance-Raten
- 👨‍💼 Agent-Performance-Metriken
- 😊 Kundenzufriedenheitstrends

### Monitoring-Tools
- 🔍 Sentry-Integration für Fehler-Tracking
- 📋 Strukturiertes Logging
- 🏥 Health-Check-Endpoints
- 📊 Echtzeit-Performance-Metriken

## 🧪 Testing

### Test-Suite ausführen

```bash
# Alle Tests
pytest

# Mit Coverage-Report
pytest --cov=app --cov-report=html

# Nur API-Tests
pytest tests/test_api.py -v

# Nur Model-Tests
pytest tests/test_models.py -v
```

### Test-Kategorien
- ✅ **Unit Tests**: Model-Tests, Utility-Funktionen
- 🔗 **Integration Tests**: API-Endpoints, Datenbankinteraktionen
- 🌐 **End-to-End Tests**: Vollständige User-Workflows
- 🔒 **Security Tests**: Authentifizierung, Autorisierung

## 🔒 Sicherheit

### Implementierte Schutzmaßnahmen
- 🛡️ **CSRF-Schutz**: Schutz vor Cross-Site Request Forgery
- 🚫 **XSS-Prävention**: Input-Validation und Output-Escaping
- 💉 **SQL-Injection-Schutz**: Parametrisierte Abfragen
- 🔐 **Sichere Passwort-Hashing**: bcrypt mit Salt
- 📊 **Audit-Logging**: Vollständige Aktionsprotokolle
- ⏱️ **Rate-Limiting**: Schutz vor Brute-Force-Angriffen
- 🔒 **Sichere Sessions**: HTTPOnly, Secure, SameSite Cookies

### DSGVO-Compliance
- 📝 **Datenminimierung**: Nur notwendige Daten sammeln
- 🗂️ **Strukturierte Datenhaltung**: Klare Datenorganisation
- 🔍 **Audit-Trail**: Nachvollziehbare Datenverarbeitung
- 🗑️ **Löschfunktionen**: Benutzer- und Daten-Löschung
- 📋 **Datenschutz-Dokumentation**: Verarbeitungsverzeichnis

## 🛠️ Entwicklung

### Development Setup

```bash
# Repository forken und klonen
git clone https://github.com/ihrusername/helpdesk.git
cd helpdesk

# Development-Umgebung
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Pre-commit hooks installieren
pre-commit install

# Tests ausführen
pytest

# Code-Qualität prüfen
black app tests
flake8 app tests
mypy app
```

### Code-Qualität
- 🐍 **Black**: Code-Formatierung
- 📏 **Flake8**: Linting
- 🔍 **MyPy**: Type-Checking
- 🔒 **Bandit**: Security-Scanning
- 📊 **Coverage**: Test-Abdeckung >80%

## 🤝 Beitragen

1. **Fork** das Repository
2. **Branch** erstellen (`git checkout -b feature/AmazingFeature`)
3. **Änderungen** committen (`git commit -m 'Add: Amazing Feature'`)
4. **Branch** pushen (`git push origin feature/AmazingFeature`)
5. **Pull Request** erstellen

### Contribution Guidelines
- ✅ Tests für neue Features schreiben
- 📝 Dokumentation aktualisieren
- 🎨 Code-Style-Guidelines befolgen
- 🔒 Security-Best-Practices einhalten

## 📜 Changelog

### Version 1.0.0 (2024-01-15)
- 🎉 Initial Release
- ✨ Vollständiges Ticket-System
- 🔐 Office 365 Integration
- 🤖 Claude AI Integration
- 📧 Email-Integration
- 📱 REST API
- 🐳 Docker-Support

Siehe [CHANGELOG.md](CHANGELOG.md) für detaillierte Versionshistorie.

## 📞 Support & Kontakt

### Technischer Support
- 📧 **Email**: it-support@mlgruppe.de
- 💬 **Teams**: ML Gruppe IT-Support
- 🐛 **Issues**: [GitHub Issues](https://github.com/mlgruppe/helpdesk/issues)
- 📚 **Dokumentation**: https://docs.mlgruppe.de/helpdesk

### Notfall-Support
- 📱 **24/7 Hotline**: +49 (0) XXX XXXXXXX
- 🚨 **Kritische Systeme**: Sofortige Benachrichtigung über Teams

## 📄 Lizenz

Dieses Projekt ist lizenziert unter der MIT License - siehe [LICENSE](LICENSE) Datei für Details.

## 🙏 Danksagungen

- **Flask Community** für das hervorragende Web-Framework
- **Anthropic** für die Claude AI API
- **Microsoft** für die umfassende Graph API
- **ML Gruppe Team** für Feedback und Testing
- **Open Source Community** für die verwendeten Bibliotheken

---

<div align="center">

**[🏠 Homepage](https://mlgruppe.de)** • 
**[📚 Dokumentation](https://docs.mlgruppe.de/helpdesk)** • 
**[🐛 Issues](https://github.com/mlgruppe/helpdesk/issues)** • 
**[💬 Discussions](https://github.com/mlgruppe/helpdesk/discussions)**

Entwickelt mit ❤️ von der ML Gruppe für die ML Gruppe

</div>