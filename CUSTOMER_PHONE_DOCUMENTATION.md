# Telefonnummern-Erfassung für Kunden bei Ticket-Erstellung

## Übersicht

Wenn Support-Agenten telefonisch Tickets erstellen, können sie die Telefonnummer des Kunden eintragen und speichern. Diese Telefonnummer wird dann im Ticket-Detail angezeigt.

## Features

### 1. Telefonnummer bei Ticket-Erstellung durch Agenten
- **Form-Feld**: `customer_phone` in `AgentTicketCreateForm`
- **Optionalität**: Optional, aber empfohlen
- **Placeholder**: `z.B. +49 30 12345678 oder 030/12345678`
- **Max-Länge**: 20 Zeichen

### 2. Speicherung
**Für neue Kunden:**
- Telefonnummer wird direkt beim Kundenerstellung mitgespeichert
- Nutzt das User-Modell Feld `phone`

**Für existierende Kunden:**
- Falls Kunde noch keine Telefonnummer hat und Agent gibt eine ein → wird gespeichert
- Falls Kunde bereits Telefonnummer hat → wird nicht überschrieben

### 3. Anzeige im Ticket-Detail
- **Position**: Neben "Erstellt von" in den Ticket-Informationen
- **Verhalten**:
  - Wenn Nummer vorhanden: Klickbar als `tel:` Link
  - Wenn nicht vorhanden: "Nicht angegeben" in grau
- **Link-Funktion**: Ermöglicht direktes Anrufen auf Mobilgeräten

## Implementierung

### Form (`apps/tickets/forms.py`)

**Neues Feld in AgentTicketCreateForm:**
```python
customer_phone = forms.CharField(
    label='Telefonnummer des Kunden',
    max_length=20,
    required=False,
    widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'z.B. +49 30 12345678 oder 030/12345678'
    }),
    help_text='Telefonnummer des Kunden (optional, aber empfohlen)'
)
```

### View (`apps/tickets/views.py`)

**Extraktion und Speicherung:**
```python
customer_phone = form.cleaned_data.get('customer_phone', '').strip()

# Für existierende Kunden - nur updaten wenn leer
if customer_phone and not customer.phone:
    customer.phone = customer_phone
    customer.save()

# Für neue Kunden - mitgeben bei Erstellung
customer = User.objects.create_user(
    email=customer_email,
    username=username,
    password=INITIAL_PASSWORD,
    first_name=customer_first_name,
    last_name=customer_last_name,
    phone=customer_phone,  # Add phone number
    role='customer',
    force_password_change=True
)
```

### Template - Ticket-Erstellungsform (`templates/tickets/create_agent.html`)

**Telefonnummernfeld anzeigen:**
```html
<div class="form-group">
    {{ form.customer_phone.label_tag }}
    {{ form.customer_phone }}
    {% if form.customer_phone.errors %}
        <div style="color: #c92a2a; font-size: 13px; margin-top: 5px;">
            {{ form.customer_phone.errors }}
        </div>
    {% endif %}
    <small style="color: #868e96;">{{ form.customer_phone.help_text }}</small>
</div>
```

### Template - Ticket-Detail (`templates/tickets/detail.html`)

**Telefonnummer anzeigen mit Link:**
```html
<div>
    <p style="color: #868e96; font-size: 13px; margin-bottom: 5px;">Telefonnummer</p>
    <p style="font-weight: 500;">
        {% if ticket.created_by.phone %}
            <a href="tel:{{ ticket.created_by.phone }}" style="color: #667eea; text-decoration: none;">
                {{ ticket.created_by.phone }}
            </a>
        {% else %}
            <span style="color: #868e96;">Nicht angegeben</span>
        {% endif %}
    </p>
</div>
```

## Workflow

### Szenario 1: Neuer Kunde mit Telefonnummer

```
1. Agent: /tickets/create/ (Agent-Formular)
2. Agent gibt folgendes ein:
   - E-Mail: max.mueller@example.com
   - Vorname: Max
   - Nachname: Mueller
   - Telefonnummer: +49 30 12345678
   - Ticket-Details (Titel, Beschreibung, etc.)
3. Klick "Ticket für Kunde erstellen"
4. System erstellt neuen Kunden mit Telefonnummer
5. Meldung: "Neuer Kunde 'Max Mueller' wurde im System erstellt. Initial-Passwort: P@ssw0rd123"
6. Ticket wird erstellt
7. Ticket-Detail zeigt: "Telefonnummer: +49 30 12345678" (klickbar)
```

### Szenario 2: Existierender Kunde ohne Telefonnummer

```
1. Agent: /tickets/create/ (Agent-Formular)
2. Agent gibt folgendes ein:
   - E-Mail: anna.schmidt@example.com (existierend)
   - Telefonnummer: 030/9876543
   - Ticket-Details
3. Klick "Ticket für Kunde erstellen"
4. System findet existierenden Kunden
5. System aktualisiert Telefonnummer (da noch keine vorhanden)
6. Ticket wird erstellt
7. Ticket-Detail zeigt: "Telefonnummer: 030/9876543" (klickbar)
```

### Szenario 3: Existierender Kunde mit Telefonnummer

```
1. Agent: /tickets/create/ (Agent-Formular)
2. Agent gibt folgendes ein:
   - E-Mail: john.doe@example.com (existierend)
   - Telefonnummer: +49 (agent versucht zu ändern)
   - Ticket-Details
3. Klick "Ticket für Kunde erstellen"
4. System findet existierenden Kunden
5. System ÜBERSCHREIBT Telefonnummer NICHT (Schutz)
6. Ticket wird erstellt
7. Ticket-Detail zeigt: "Telefonnummer: +49 1234567890" (alte Nummer)
```

## Anzeige im Ticket-Detail

**Für Agenten und Admins:**
- Telefonnummer wird als Link angezeigt
- Link-Format: `<a href="tel:...">Nummer</a>`
- Ermöglicht direktes Anrufen auf Mobilgeräten
- Desktop: öffnet Telefonie-App

**Design:**
- Blauer Link (Farbe: #667eea)
- Keine Unterstreichung
- Neben "Erstellt von" in Grid-Layout (2 Spalten)

## Daten

### User-Modell Feld
```python
phone = models.CharField(
    _('phone'),
    max_length=20,
    blank=True,
    null=True
)
```

### Formular-Validierung
- Max 20 Zeichen
- Optional
- Unterstützt verschiedene Formate:
  - `+49 30 12345678`
  - `030/12345678`
  - `(030) 12345678`
  - Alle anderen Formate

## Sicherheit & Best Practices

1. **Keine Validierung des Formates**: Akzeptiert alle Telefonnummern-Formate
2. **Schutz vor Überschreibung**: Für existierende Kunden wird nur gespeichert, wenn leer
3. **Optional für existierende**: Agenten können Telefon jederzeit hinzufügen
4. **Datenschutz**: Telefonnummern werden nur in User-Profil gespeichert
5. **Admin-Kontrolle**: Telefonummern können im Admin-Interface bearbeitet werden

## Admin-Interface

**Telefonnummer ist editierbar:**
1. Admin geht zu: `/admin/accounts/user/`
2. Findet Kunden
3. Bearbeitet `phone` Feld
4. Speichert

## Testing-Szenarien

### Test 1: Neuer Kunde mit Telefonnummer
```
✓ Formular akzeptiert Telefonnummer
✓ Kunde wird mit Telefonnummer erstellt
✓ Telefonnummer wird im Ticket-Detail angezeigt
✓ Link funktioniert korrekt
```

### Test 2: Existierender Kunde ohne Telefonnummer
```
✓ Formular akzeptiert Telefonnummer
✓ Telefonnummer wird gespeichert
✓ Telefonnummer wird im Ticket-Detail angezeigt
```

### Test 3: Existierender Kunde mit Telefonnummer
```
✓ Formular akzeptiert neue Telefonnummer
✓ Alte Telefonnummer wird NICHT überschrieben
✓ Alte Telefonnummer wird im Ticket-Detail angezeigt
```

### Test 4: Keine Telefonnummer angegeben
```
✓ Formular akzeptiert leeres Feld (optional)
✓ Ticket-Detail zeigt "Nicht angegeben"
```

## Hinweise für Support-Agenten

Die Hinweise im Template wurden aktualisiert:

```
- Existing Customer: Geben Sie einfach die E-Mail des Kunden ein.
  Vor-, Nachname und Telefonnummer sind optional.

- Neuer Customer: Wenn der Kunde noch nicht registriert ist,
  füllen Sie Vor- und Nachname aus.

- Telefonnummer: Die Telefonnummer sollte immer angegeben werden,
  damit Sie den Kunden direkt kontaktieren können.

- Neue Kunden erhalten das Initial-Passwort P@ssw0rd123

- Der Kunde muss das Passwort bei der ersten Anmeldung ändern
```

## Validierung

✅ Django System Check: Keine Fehler
✅ Template Syntax: Valid
✅ Form Structure: Korrekt
✅ Views: Funktionstüchtig
