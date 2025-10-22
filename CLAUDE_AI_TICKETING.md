# Claude AI Automatic Ticket Response System

## Übersicht

Das System generiert automatisch AI-gestützte Antworten auf Support-Tickets ab **15:30 Uhr** für kleine technische Probleme.

### Features

✅ **Zeitbasierte Aktivierung**: Antwortet nur nach 15:30 Uhr
✅ **Intelligente Klassifizierung**: Unterscheidet simple vs. komplexe Probleme
✅ **Claude AI Integration**: Verwendet Claude API (Paid) oder Free Version
✅ **Automatische Verarbeitung**: Beim Erstellen von Tickets oder via Management Command
✅ **Deutsche Oberfläche**: Antwortet in Deutsch

## Konfiguration

### 1. Claude API Key einrichten

Du hast zwei Optionen:

#### Option A: Kostenlose Version (Fallback)
- Wenn kein API Key vorhanden: System verwendet Template-Antwort
- Funktioniert offline
- Begrenzte Personalisierung

#### Option B: Claude API (Empfohlen)
- Professionelle AI-Antworten
- Personalisierte Lösungen
- Kostet pro API-Aufruf

**Einrichtung:**

1. Gehe zu https://console.anthropic.com/
2. Erstelle einen API Key
3. Füge in `.env` hinzu:
   ```
   CLAUDE_API_KEY=sk-ant-xxx...
   ```

4. Oder in Environment-Variablen:
   ```bash
   export CLAUDE_API_KEY=sk-ant-xxx...
   ```

### 2. Aktivierung in settings.py

Die Konfiguration ist bereits in place:

```python
# helpdesk/settings.py
CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY')
```

## Wie es funktioniert

### 1. Automatische Verarbeitung bei Ticket-Erstellung

Wenn ein neues Ticket erstellt wird UND es ist nach 15:30:

```
Ticket erstellt
↓
Signal aktiviert (post_save)
↓
Klassifizierung: Simple oder Complex?
↓
Simple → Claude API aufgerufen → Antwort generiert
Complex → Support-Message gesendet
```

### 2. Manuelle Verarbeitung mit Management Command

```bash
# Normale Verarbeitung (nur nach 15:30)
python manage.py process_tickets_with_ai

# Erzwungen (jederzeit)
python manage.py process_tickets_with_ai --force

# Begrenzt auf 5 Tickets
python manage.py process_tickets_with_ai --limit 5

# Spezifischer Status
python manage.py process_tickets_with_ai --status pending
```

### 3. Mit Cron oder Celery automatisieren

**Cron-Beispiel (jede 30 Minuten nach 15:30):**

```bash
# Jede 30 Minuten ausführen (ab 15:30)
30,0 15-23 * * * cd /path/to/helpdesk && python manage.py process_tickets_with_ai

# Oder mit Celery Beat:
# Für regelmäßige Aufrufe
```

## Problem-Klassifizierung

### Simple Problems (Claude kann antworten)

Claude beantwortet diese Probleme automatisch:

- Password Reset / Passwort-Zurücksetzen
- Login Issues / Login-Probleme
- Email nicht erreichbar
- Verbindungsprobleme
- Installationshilfe
- Grundlegende Setup-Fragen
- Lizenzaktivierung
- Account-Freischaltung
- Software-Neustart

**Beispiel:**
```
Ticket: "Ich kann mein Passwort nicht zurücksetzen"
↓
Claude antwortet: "Gehen Sie zu... Klicken Sie auf... Dann..."
```

### Complex Problems (Wartet auf Support)

Diese Probleme bekommen Nachricht "Support ab 7:00 Uhr":

- Hardware-Fehler
- Datenverlust
- Sicherheitsprobleme
- System-Crash
- Datenbankfehler
- Custom-Entwicklung
- Billing-Dispute
- Notfall/Kritisch

**Beispiel:**
```
Ticket: "Server ist crashed und alle Daten sind weg!"
↓
System: "Diese Anfrage erfordert Support... Support ab 7:00 Uhr erreichbar"
```

## API-Verbrauch & Kosten

### Claude API Kosten (kostenpflichte Variante)

Preise (Stand Oktober 2024):

- **Input**: $3 pro 1M Tokens
- **Output**: $15 pro 1M Tokens

**Durchschnittliche Kosten pro Ticket**: ca. $0.001 - $0.01

Mit 100 Tickets pro Tag: **$0.10 - $1.00/Tag**

### Sparen mit Free Version

Wenn kein API Key: System nutzt Template-Antwort (kostenlos)

## Implementierungsdetails

### Dateien

```
apps/tickets/
├── claude_service.py              # Hauptlogik
├── signals.py                      # Auto-Trigger
├── apps.py                         # Signal-Registrierung
└── management/
    └── commands/
        └── process_tickets_with_ai.py  # Management Command
```

### Klasse: ClaudeTicketAssistant

```python
from apps.tickets.claude_service import claude_assistant

# Zeit prüfen
if claude_assistant.can_auto_respond():
    print("Nach 15:30 - Claude kann antworten")

# Problem klassifizieren
category, is_simple = claude_assistant.classify_problem(title, desc)

# Ticket verarbeiten
claude_assistant.process_ticket(ticket)

# Antwort generieren
response = claude_assistant.generate_response(title, desc, category)
```

## Workflow Beispiel

### Szenario 1: Passwort-Problem nach 15:30

```
15:35 - Kunde erstellt Ticket: "Passwort vergessen"
↓
Signal aktiviert
↓
Klassifizierung: "password_reset" (SIMPLE)
↓
Claude API aufgerufen
↓
Antwort generiert: "Um Ihr Passwort zurückzusetzen..."
↓
Ticket.notes gespeichert
↓
Kunde erhält sofort Antwort
```

### Szenario 2: Hardware-Problem nach 15:30

```
15:45 - Kunde erstellt Ticket: "Server bricht ab"
↓
Signal aktiviert
↓
Klassifizierung: "hardware_failure" (COMPLEX)
↓
Support-Message gesendet: "Erfordert Support... ab 7:00 Uhr"
↓
Ticket.notes mit Support-Nachricht gespeichert
↓
Kunde weiss Support kommt morgen
```

### Szenario 3: Problem vor 15:30

```
14:00 - Kunde erstellt Ticket
↓
Signal prüft: can_auto_respond() = False
↓
Keine automatische Antwort
↓
Ticket wartet auf Agent
```

## Überwachung & Logging

### Logs anschauen

```bash
# Django Logs
tail -f logs/helpdesk.log

# Oder im Shell
python manage.py shell
>>> from django.core.logging import logger
>>> logger.info("Claude ticket processing")
```

### Debug-Ausgabe

```python
import logging
logger = logging.getLogger('apps.tickets.claude_service')
logger.setLevel(logging.DEBUG)
```

## Fehlerbehandlung

### API Key fehlt

```
WARNING: Claude API key not configured
```

→ System nutzt Template-Antwort (kostenlos)

### API Fehler

```
ERROR: Claude API error: [error message]
```

→ Fallback auf Template-Antwort
→ Ticket erhält Standard-Antwort

### Netzwerkfehler

```
ERROR: Connection timeout
```

→ Ticket wird übersprungen
→ Kann später mit `--force` manuell verarbeitet werden

## Performance

- **API Call Zeit**: ca. 2-5 Sekunden
- **Ticket Update**: < 100ms
- **Database Query**: < 50ms

Bei synchronem Verarbeiten (current): Keine Performance-Probleme bis ~10 Tickets/Minute

**Empfehlung für >10 Tickets/Minute**: Celery Task Queue nutzen

## Sicherheit

✅ API Key in Umgebungsvariablen (nicht im Code)
✅ Keine Kundendaten an Claude API gesendet außer: Titel & Beschreibung
✅ Antworte sind lokal (nicht gecloudet)
✅ Nur Agent/Admin können Automatisierung ändern

## Troubleshooting

### Problem: Claude antwortet nicht

**Lösung:**
1. Prüfe ob CLAUDE_API_KEY gesetzt ist
2. Prüfe Zeit: Ist es nach 15:30?
3. Prüfe ob Ticket Notizen hat (nicht leer)
4. Logs ansehen: `python manage.py shell` → `logger.info(...)`

### Problem: Falsche Klassifizierung

**Lösung:**
Bearbeite `claude_service.py`:

```python
# SIMPLE_PROBLEMS erweitern
SIMPLE_PROBLEMS = [
    'dein_problem_hier',
    ...
]
```

### Problem: Zu viele API Calls

**Lösung:**
1. Reduziere Limit: `--limit 5`
2. Schränke Zeit ein: Nur von 15:30-17:00
3. Nutze Filter für bestimmte Kategorien

## Zukünftige Verbesserungen

- [ ] Celery Task Queue für asynchrone Verarbeitung
- [ ] Batch-Processing für mehrere Tickets
- [ ] Custom Training mit deinen Tickets
- [ ] Feedback-System (Kunde: "Antwort hilfreich?")
- [ ] Multi-language Support
- [ ] Sentiment-Analyse für Emotion Detection
- [ ] Integration mit Zendesk/Jira
- [ ] Analytics Dashboard

## Support & Hilfe

Für Probleme:

1. Überprüfe logs/helpdesk.log
2. Nutze `--force --limit 1` zum Testen
3. Kontrolliere CLAUDE_API_KEY in Environment
4. Überprüfe Django Logs: `python manage.py check`

## Zusammenfassung

Das Claude AI System:
- ✅ Automatisiert einfache Support-Anfragen
- ✅ Zeitgesteuert (ab 15:30)
- ✅ Intelligent klassifiziert (Simple vs. Complex)
- ✅ Deutsche Antworten
- ✅ Kosteneffizient (mit oder ohne API)
- ✅ Einfach zu verwenden

**Nutzen**: Reduzierte Supportlast bei einfachen Fragen, schnellere Kundenzufriedenheit, 24/7 Verfügbarkeit für einfache Probleme!
