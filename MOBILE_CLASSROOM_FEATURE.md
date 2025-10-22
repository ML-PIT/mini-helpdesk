# Mobile Classroom & Statistik-Feature

## Übersicht

Dieses Feature ermöglicht es dir, Tickets mit mobilen Klassenräumen und Standorten zu verknüpfen sowie umfangreiche Statistiken zu Trainer-Problemen und Klassenraum-Fehlern zu analysieren.

## Neue Features

### 1. Mobile Klassenräume zu Tickets
- Optionale Zuordnung von Tickets zu mobilen Klassenräumen
- Verfolgung des Standorts jedes Klassenraums
- Equipment-Typ und Seriennummern für jedes Gerät

### 2. Statistik-Dashboard
- **Trainer-Statistiken**: Zeigt welche Trainer/Kunden wie oft Probleme haben
- **Problem-Kategorien**: Häufigste Fehler und Probleme
- **Klassenraum-Fehler**: Welche Klassenräume die meisten Probleme haben
- **Prioritätsverteilung**: Übersicht über Prioritäten aller Tickets

## Datenmodelle

### MobileClassroomLocation
```python
- name: Standortname (Pflicht)
- description: Beschreibung
- address: Adresse
- city: Stadt
```

### MobileClassroom
```python
- name: Klassenraum-Name (Pflicht)
- description: Beschreibung
- location: ForeignKey zu MobileClassroomLocation
- equipment_type: Art der Ausrüstung (z.B. Laptop Cart)
- serial_number: Seriennummer (optional)
- is_active: Aktiv/Inaktiv Status
```

### Ticket (erweitert)
```python
- mobile_classroom: ForeignKey zu MobileClassroom (optional)
```

## Admin-Interface

### Neue Admin-Seiten:
1. **Mobile Classroom Locations** (`/admin/tickets/mobileclassroomlocation/`)
   - Verwaltung von Standorten
   - Filter nach Stadt und Erstellungsdatum
   - Suche nach Name, Adresse, Stadt

2. **Mobile Classrooms** (`/admin/tickets/mobileclassroom/`)
   - Verwaltung von Klassenräumen
   - Filter nach Standort, Equipment-Typ, Status
   - Suche nach Name und Seriennummer
   - Fieldsets für bessere Organisation

3. **Ticket Admin** (aktualisiert)
   - Neues Feld: `mobile_classroom`
   - Filter nach Klassenraum hinzugefügt
   - Klassenraum wird in der Liste angezeigt

## Verwendung

### Tickets mit Klassenraum erstellen

1. **Kunde erstellt Ticket**:
   - Wählen Sie Klassenraum aus der Dropdown-Liste
   - Klassenraum ist optional

2. **Agent erstellt Ticket für Kunde**:
   - Geben Sie Kunden-Email ein
   - Wählen Sie Klassenraum aus

3. **Admin aktualisiert Ticket**:
   - Im Admin-Interface: Classroom-Feld setzen

### Statistik-Dashboard ansehen

**Zugang**: `/tickets/statistics/` oder über Dashboard-Link

**Nur für**:
- Admins
- Support Agents

**Angezeigte Daten**:

#### 1. Top Trainer (die meisten Probleme)
- Trainer-Name und Email
- Anzahl Tickets
- High-Priority Tickets
- Durchschnittliche Bearbeitungszeit in Tagen

**Farb-Kodierung**:
- Trainer mit ≥5 Tickets werden gelb hervorgehoben
- Hilft zu identifizieren, wer Schulung braucht

#### 2. Häufigste Fehler/Probleme
- Problem-Kategorien mit Balken-Diagramm
- Zeigt an, welche Fehler am häufigsten vorkommen
- Hilft bei Priorisierung von Fixes/Updates

#### 3. Klassenräume mit meisten Fehlern
- Klassenraum-Name und Standort
- Fehleranzahl
- Kritikalität-Badge:
  - KRITISCH: ≥5 Fehler
  - HOCH: ≥3 Fehler
  - MITTEL: <3 Fehler

#### 4. Prioritätsverteilung
- Übersicht über Critical, High, Medium, Low
- Farblich kodiert

## Einrichtung

### Schritt 1: Admin-Bereich öffnen
```
http://localhost:8000/admin/
```

### Schritt 2: Standorte erstellen
1. Gehen Sie zu "Mobile Classroom Locations"
2. "Add Mobile Classroom Location" anklicken
3. Tragen Sie Name, Adresse, Stadt ein
4. Speichern

### Schritt 3: Klassenräume erstellen
1. Gehen Sie zu "Mobile Classrooms"
2. "Add Mobile Classroom" anklicken
3. Tragen Sie:
   - Name (z.B. "Laptop-Wagen 1")
   - Standort (Link zu Location)
   - Equipment-Type (z.B. "Laptop Cart")
   - Seriennummer (optional)
4. Speichern

### Schritt 4: Tickets mit Klassenräumen verknüpfen
- Bei Ticket-Erstellung: Klassenraum aus Dropdown wählen
- Bei Admin-Interface: Im "Assignment" Fieldset

## SQL-Migrationen

Folgende Migrationen wurden erstellt:
```
apps/tickets/migrations/0003_mobileclassroom_mobileclassroomlocation_and_more.py
```

Automatisch angewendet mit:
```bash
python manage.py migrate tickets
```

## Abfrage-Beispiele

### Alle Tickets für einen Klassenraum
```python
from apps.tickets.models import Ticket, MobileClassroom

classroom = MobileClassroom.objects.get(name="Laptop-Wagen 1")
tickets = classroom.tickets.all()
```

### Klassenraum mit meisten Problemen
```python
from django.db.models import Count

classroom_stats = (
    MobileClassroom.objects
    .annotate(ticket_count=Count('tickets'))
    .order_by('-ticket_count')
    .first()
)
```

### Trainer mit meisten Problemen
```python
from apps.tickets.models import Ticket
from django.db.models import Count

trainer_stats = (
    Ticket.objects
    .filter(status__in=['closed', 'resolved'])
    .values('created_by__full_name')
    .annotate(count=Count('id'))
    .order_by('-count')
)
```

## Best Practices

1. **Regelmäßig Statistiken überprüfen**
   - Wöchentlich oder monatlich
   - Trends und Muster identifizieren

2. **Classroom-Status aktualisieren**
   - Setzen Sie `is_active=False` für außer Betrieb genommene Geräte
   - Helft bei der Datenbereinigung

3. **Equipment-Typ konsistent benennen**
   - Z.B. immer "Laptop Cart" oder "Projector Setup"
   - Ermöglicht bessere Filterung

4. **Standorte logisch organisieren**
   - Nach Gebäude, Campus oder Region
   - Macht Wartungsplanung einfacher

## Support-Arbeitsablauf

### Beispiel: Häufiges Problem in einem Klassenraum

1. **Statistik-Dashboard öffnen**
   - `/tickets/statistics/`

2. **Klassenraum mit vielen Fehlern identifizieren**
   - "Klassenräume mit meisten Fehlern" Tab
   - Rot markierte Einträge priorisieren

3. **Tickets für diesen Klassenraum filtern**
   - `/tickets/` → Filter nach Klassenraum
   - Oder Admin: Ticket Admin → Filter → mobile_classroom

4. **Häufige Fehler analysieren**
   - "Häufigste Fehler/Probleme" Tab
   - Sehen, welche Kategorien dominieren

5. **Wartung oder Schulung durchführen**
   - Hardware-Wartung wenn Geräte fehlerhaft
   - Trainer-Schulung wenn Bedienungsfehler

## Überblick der Änderungen

### Neue Dateien
- `templates/tickets/statistics.html` - Statistik-Dashboard
- `MOBILE_CLASSROOM_FEATURE.md` - Diese Datei

### Geänderte Dateien
- `apps/tickets/models.py` - Neue Modelle + Erweiterung Ticket
- `apps/tickets/views.py` - Neue View für Statistiken
- `apps/tickets/forms.py` - Beide Formulare erweitert
- `apps/tickets/admin.py` - Admin-Registrierungen
- `apps/tickets/urls.py` - Neue URL für Statistiken
- `templates/tickets/detail.html` - Zeigt Klassenraum-Info
- `templates/tickets/list.html` - Klassenraum-Spalte hinzugefügt
- `templates/dashboard/index.html` - Link zu Statistiken

### Migrationen
- `apps/tickets/migrations/0003_mobileclassroom_mobileclassroomlocation_and_more.py`

## Häufig gestellte Fragen

**F: Kann ich Statistiken exportieren?**
A: Derzeit nicht direkt im Frontend, aber Sie können Daten über Django Admin oder SQL-Abfragen exportieren.

**F: Werden historische Daten berücksichtigt?**
A: Ja, nur geschlossene/gelöste Tickets werden in Statistiken verwendet, um korrekte Metriken zu gewährleisten.

**F: Kann ich Klassenzimmer in Tickets löschen?**
A: Bei Löschung wird das Feld auf NULL gesetzt (optional), sodass historische Daten erhalten bleiben.

**F: Wie oft sollte ich Statistiken aktualisieren?**
A: Sie werden in Echtzeit berechnet. Laden Sie einfach die Seite neu um aktuelle Daten zu sehen.
