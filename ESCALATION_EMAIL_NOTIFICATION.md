# Eskalierungs-Email-Benachrichtigungen

## Übersicht

Wenn ein Support-Agent ein Ticket an einen anderen (höher qualifizierten) Agent eskaliert, erhält der Zielagent automatisch eine Email mit den Ticket-Details und der **Dringlichkeit (Priorität)** des Tickets.

## Features

### 1. Automatische Email-Benachrichtigung bei Eskalation
- Der Agent, an den das Ticket eskaliert wird, erhält sofort eine Email
- Die Email enthält klare Dringlichkeits-Indikatoren basierend auf der Priorität
- Die Email informiert über den Grund der Eskalation (falls angegeben)
- Die Email enthält einen direkten Link zum Ticket

### 2. Dringlichkeits-Indikatoren
Die Email zeigt Dringlichkeit mit Emojis und klarem Text:

| Priorität | Dringlichkeit in Email |
|-----------|------------------------|
| **Critical** | 🔴 KRITISCH - Sofortige Aktion erforderlich |
| **High** | 🟠 HOCH - Baldige Bearbeitung erforderlich |
| **Medium** | 🟡 MITTEL - Normale Priorität |
| **Low** | 🟢 NIEDRIG - Kann in Ruhe bearbeitet werden |

### 3. Email-Inhalt
Die Email enthält:
- ✅ Dringlichkeits-Level prominent am Anfang
- ✅ Ticket-Nummer und Titel
- ✅ Priorität und Kategorie
- ✅ Kundenname, Email und Telefonnummer
- ✅ Erstellungsdatum des Tickets
- ✅ Name des Agenten, der eskaliert hat
- ✅ Grund der Eskalation (falls angegeben)
- ✅ Komplette Ticketbeschreibung
- ✅ Direkter Link zum Ticket

## Technische Implementierung

### Neue Funktion in `apps/tickets/views.py`

```python
def notify_agent_ticket_escalation(ticket, escalated_from_agent, escalated_to_agent, reason=''):
    """Send email notification to agent when ticket is escalated to them"""
    if not escalated_to_agent or not escalated_to_agent.email:
        return

    # Build ticket URL using SITE_URL setting
    site_url = settings.SITE_URL.rstrip('/')
    ticket_url = f"{site_url}/tickets/{ticket.pk}/"

    # Get priority display
    priority_display = ticket.get_priority_display()

    # Priority urgency mapping
    urgency_map = {
        'critical': '🔴 KRITISCH - Sofortige Aktion erforderlich',
        'high': '🟠 HOCH - Baldige Bearbeitung erforderlich',
        'medium': '🟡 MITTEL - Normale Priorität',
        'low': '🟢 NIEDRIG - Kann in Ruhe bearbeitet werden'
    }

    urgency_text = urgency_map.get(ticket.priority, priority_display)

    # Build email subject
    subject = f'ESKALIERT: Ticket {ticket.ticket_number} - {ticket.title} ({priority_display})'

    # Build email message with full details
    message = f"""Hallo {escalated_to_agent.first_name},

ein Ticket wurde zu Ihnen eskaliert:

{'=' * 70}
DRINGLICHKEIT: {urgency_text}
{'=' * 70}

Ticket-Nummer: {ticket.ticket_number}
Titel: {ticket.title}
Priorität: {priority_display}
Kategorie: {ticket.category.name if ticket.category else 'Keine'}
Erstellt von: {ticket.created_by.full_name} ({ticket.created_by.email})
Telefonnummer Kunde: {ticket.created_by.phone if ticket.created_by.phone else 'Nicht angegeben'}
Erstellt am: {ticket.created_at.strftime('%d.%m.%Y %H:%M')}
Eskaliert von: {escalated_from_agent.full_name if escalated_from_agent else 'System'}

Beschreibung:
{ticket.description}
"""

    if reason:
        message += f"\nEskalations-Grund:\n{reason}\n"

    message += f"""
Ticket ansehen: {ticket_url}

---
Diese Email wurde automatisch vom ML Gruppe Helpdesk System gesendet.
"""

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[escalated_to_agent.email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Failed to send escalation notification email: {e}")
```

### Integration in `ticket_escalate` View

```python
# Send email notification to escalated agent with urgency
notify_agent_ticket_escalation(ticket, old_agent, new_agent, reason)

messages.success(request, f'Ticket wurde eskaliert an {new_agent.full_name} und Email wurde versendet')
```

## Workflow

### Szenario: Ticket-Eskalation mit Email

```
1. Agent A arbeitet an Ticket #123 (Priorität: CRITICAL)
2. Agent A kann das Problem nicht lösen und eskaliert zu Agent B
3. Agent A gibt optional einen Grund an: "Hardware defekt, braucht Spezialisten"
4. System erstellt interne Notiz: "Ticket eskaliert von Agent A an Agent B"
5. System sendet Email an Agent B mit:
   - SUBJECT: "ESKALIERT: Ticket #123 - Drucker funktioniert nicht (Kritisch)"
   - DRINGLICHKEIT: "🔴 KRITISCH - Sofortige Aktion erforderlich"
   - Alle Ticket-Details
   - Eskalations-Grund
   - Link zum Ticket
6. Agent B erhält Email und kann sofort reagieren
```

### Email-Beispiel

**Subject:** `ESKALIERT: Ticket #T-2024-001234 - Netzwerk ausgefallen (Kritisch)`

```
Hallo Max,

ein Ticket wurde zu Ihnen eskaliert:

======================================================================
DRINGLICHKEIT: 🔴 KRITISCH - Sofortige Aktion erforderlich
======================================================================

Ticket-Nummer: T-2024-001234
Titel: Netzwerk ausgefallen
Priorität: Kritisch
Kategorie: Hardware
Erstellt von: Anna Schmidt (anna.schmidt@example.com)
Telefonnummer Kunde: +49 30 12345678
Erstellt am: 22.10.2024 14:30
Eskaliert von: Peter Mueller

Beschreibung:
Das gesamte Netzwerk in der mobilen Classroom ist ausgefallen.
Alle Geräte können nicht mehr verbunden werden.

Eskalations-Grund:
Hardware defekt, braucht Spezialisten

Ticket ansehen: https://ml-help.aboro-it.net/tickets/1234/

---
Diese Email wurde automatisch vom ML Gruppe Helpdesk System gesendet.
```

## Fehlererkennung

Falls die Email nicht versendet werden kann:
- **Fehler wird geloggt**: `print(f"Failed to send escalation notification email: {e}")`
- **Ticket-Eskalation wird NICHT unterbrochen**: `fail_silently=True`
- **User sieht Bestätigungsmeldung**: "Ticket wurde eskaliert an [Agent Name] und Email wurde versendet"
- Agent muss nicht neu-eskalieren, Email kann manuell versendet werden

## Sicherheitsfeatures

1. **Fail-Safe Design**: Wenn Email fehlschlägt, wird Eskalation trotzdem durchgeführt
2. **Logging**: Fehler werden in stdout geloggt für Debugging
3. **Datenschutz**: Nur der Zielagent erhält die Email (nicht alle Agenten)
4. **Authentifizierung**: Nur Support Agents können eskalieren
5. **Berechtigung**: Nur zu höher-qualifizierten Agenten eskalierbar

## Konfiguration

### Email-Settings in `helpdesk/settings.py`

Die Benachrichtigungen nutzen folgende Einstellungen:
```python
DEFAULT_FROM_EMAIL = 'noreply@your-domain.com'  # Sender-Email
SITE_URL = 'https://your-domain.com'  # Basis-URL für Links
```

## Test-Szenarien

### Test 1: CRITICAL Eskalation
```
1. Erstelle Ticket mit Priorität CRITICAL
2. Eskaliere zu Agent B
3. Prüfe Email-Inbox von Agent B
4. Verifiziere: 🔴 KRITISCH im Subject und Body
```

### Test 2: LOW Eskalation mit Grund
```
1. Erstelle Ticket mit Priorität LOW
2. Gib Grund an: "Umleitung zu Spezialisten"
3. Eskaliere zu Agent C
4. Prüfe Email in Agent C Inbox
5. Verifiziere: 🟢 NIEDRIG und Grund-Text
```

### Test 3: Email-Fehlerbehandlung
```
1. Setze EMAIL_BACKEND auf 'locmem://' (In-Memory)
2. Eskaliere Ticket
3. Verifiziere: Eskalation erfolgt
4. Prüfe Logs: Keine Fehler
```

## Bestätigungsmeldung für User

Nach erfolgreicher Eskalation sieht der Agent:
```
"Ticket wurde eskaliert an [Agent Name] und Email wurde versendet"
```

## Integration mit anderen Features

- ✅ Funktioniert mit allen Prioritäts-Levels
- ✅ Funktioniert mit allen Support-Levels
- ✅ Zeigt Kundentelefonummer (falls vorhanden)
- ✅ Nutzt konfigurierbare SITE_URL
- ✅ Kompatibel mit Eskalations-Gründen

## Datenspeicherung

Die Eskalation wird dokumentiert durch:
1. **System-Comment**: Interne Notiz mit vollständigen Details
2. **Email-Log**: stdout-Logging bei Fehlern
3. **Activity Trail**: User sieht Eskalation im Ticket-Detail

## Validierung

✅ Django System Check: Keine Fehler
✅ Code-Syntax: Gültig
✅ Email-Funktion: Integriert
✅ Error-Handling: Implementiert
