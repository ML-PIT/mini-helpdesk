# Ticket-Erstellung durch Agenten mit automatischer Kundenerstellung

## Übersicht

Support-Agenten können nun Tickets im Namen von Kunden erstellen. Falls der Kunde noch nicht im System registriert ist, können Agenten den Kunden automatisch erstellen, indem sie E-Mail und Namen angeben.

## Funktionalität

### Szenarien

#### 1. Existing Customer (Bereits registrierter Kunde)
- Agent gibt die E-Mail des Kunden ein
- Vor- und Nachname sind optional
- System findet den Kunden und erstellt das Ticket im Namen des Kunden

#### 2. Neuer Customer (Noch nicht registrierter Kunde)
- Agent gibt die E-Mail ein
- Agent gibt Vor- und Nachname ein
- System erstellt automatisch einen neuen Kundenkonto
- Ticket wird im Namen des neuen Kunden erstellt

### Automatische Nutzererstellung

Wenn ein Kunde noch nicht existiert und der Agent Vor- und Nachname angibt:

1. **Username-Generierung**: Der Username wird aus der E-Mail generiert (z.B. `max.mueller@example.com` → `max.mueller`)
2. **Username-Eindeutigkeit**: Falls der Username bereits existiert, wird ein Zähler angehängt (z.B. `max.mueller1`)
3. **Rolle**: Der neue Benutzer erhält automatisch die Rolle "customer"
4. **Passwort**: Kein Passwort wird initial gesetzt (Kunde muss via "Passwort vergessen" einen setzen oder Admin vergibt manuell)

### Fehlerbehandlung

**Fehlerszenario**: Kunde existiert nicht, aber Vor-/Nachname fehlen
- Fehlermeldung: `"Kunde mit Email X existiert nicht. Bitte geben Sie Vor- und Nachname ein, um einen neuen Kunden zu erstellen."`
- Form bleibt angezeigt für erneute Eingabe

## Code-Änderungen

### 1. Forms (`apps/tickets/forms.py`)

**AgentTicketCreateForm** erweitert um:
- `customer_first_name`: Optional, erforderlich für neue Kunden
- `customer_last_name`: Optional, erforderlich für neue Kunden

```python
customer_first_name = forms.CharField(
    label='Vorname des Kunden',
    max_length=100,
    required=False,
    widget=forms.TextInput(attrs={...}),
    help_text='Nur erforderlich, wenn der Kunde noch nicht im System existiert'
)
```

### 2. Views (`apps/tickets/views.py`)

**ticket_create()** Funktion angepasst:

1. Extrahiere `customer_first_name` und `customer_last_name` aus Form
2. Versuche, Kunden mit der angegebenen E-Mail zu finden
3. Falls nicht gefunden:
   - Prüfe, ob Vor- und Nachname angegeben wurden
   - Falls nicht: Zeige Fehlermeldung
   - Falls ja: Erstelle neuen Kunden mit eindeutigem Username
4. Erstelle Ticket für den Kunden (existierend oder neu)
5. Setze SLA basierend auf Priorität
6. Erstelle interne Notiz
7. Sende Benachrichtigungen

### 3. Template (`templates/tickets/create_agent.html`)

**Neue Form-Felder**:
- Vorname und Nachname in Grid-Layout (2 Spalten)
- Help-Text erklärt, wann diese Felder erforderlich sind
- Info-Box aktualisiert

## Workflow-Beispiel

### Existierender Kunde
```
1. Agent navigiert zu /tickets/create/
2. Wählt "Ticket für Kunde erstellen"
3. Gibt E-Mail ein: max.mueller@example.com
4. Füllt Ticket-Details aus (Titel, Beschreibung, etc.)
5. Klickt "Ticket erstellen"
6. System findet Kunden und erstellt Ticket
7. Kunde erhält Benachrichtigung
```

### Neuer Kunde
```
1. Agent navigiert zu /tickets/create/
2. Wählt "Ticket für Kunde erstellen"
3. Gibt E-Mail ein: newcustomer@example.com
4. Gibt Vorname ein: Max
5. Gibt Nachname ein: Mueller
6. Füllt Ticket-Details aus
7. Klickt "Ticket erstellen"
8. System erstellt neuen Kundenkonto (email: newcustomer@example.com, username: newcustomer)
9. System erstellt Ticket im Namen des Kunden
10. Kunde erhält Benachrichtigung
```

## Interne Notiz

Für beide Szenarien wird automatisch eine interne Notiz erstellt:
```
"Ticket wurde von [Agent Name] für Kunde [Kundenname] erstellt (telefonische Anfrage)."
```

## Validierung

- Django System Check: ✅ No issues
- Template Syntax: ✅ Valid
- Form Validation: ✅ ClientEmail ist erforderlich, Name nur wenn Kunde nicht existiert

## Sicherheit

- Username wird eindeutig gemacht durch Zählervergabe
- E-Mail und Username müssen eindeutig sein
- Neuer Kunde kann sich selbst registrieren oder Admin setzt Passwort
- Interne Notiz dokumentiert, dass Agent das Ticket erstellt hat
