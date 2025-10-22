# Quick-Start Guide: Mobile Classroom & Statistiken

## ⚡ 5-Minuten Einrichtung

### 1. Server starten (falls nicht laufen)
```bash
python manage.py runserver
```

### 2. Admin-Bereich öffnen
```
http://localhost:8000/admin/
```

### 3. Standorte erstellen
1. Sidebar → "TICKETS" → "Mobile classroom locations"
2. Rechts oben: "+ Add Mobile Classroom Location"
3. Beispiel ausfüllen:
   ```
   Location name: Hauptgebäude
   Description: Erstes Schulungsgebäude
   Address: Hauptstraße 123
   City: Berlin
   ```
4. Speichern (SAVE)

### 4. Mobile Klassenräume erstellen
1. Sidebar → "TICKETS" → "Mobile classrooms"
2. Rechts oben: "+ Add Mobile Classroom"
3. Beispiele ausfüllen:

   **Klassenraum 1:**
   ```
   Name: Laptop-Wagen A1
   Description: Tragbarer Laptop-Wagen mit 20 Geräten
   Location: Hauptgebäude (aus Dropdown)
   Equipment type: Laptop Cart
   Serial number: LW-2024-001
   Active: ☑ (angehakt)
   ```

   **Klassenraum 2:**
   ```
   Name: Projektor-Set B2
   Description: Mobiler Beamer mit Lautsprechern
   Location: Hauptgebäude
   Equipment type: Projector Setup
   Serial number: PS-2024-001
   Active: ☑
   ```

4. Speichern für jeden Eintrag

### 5. Test: Ticket mit Klassenraum erstellen

**Als Admin:**
1. Gehen Sie zu: http://localhost:8000/tickets/
2. Klicken Sie "+ Neues Ticket"
3. Füllen Sie aus:
   ```
   Title: Test Ticket für Laptop-Wagen
   Description: Der Projektor funktioniert nicht
   Category: (beliebig)
   Priority: Medium
   Mobile classroom: Laptop-Wagen A1  ← HIER!
   ```
4. Speichern

### 6. Statistik-Dashboard ansehen
1. Gehen Sie zu: http://localhost:8000/tickets/statistics/
2. Sie sehen:
   - Top Trainer (die meisten Probleme)
   - Häufigste Fehler
   - Klassenräume mit meisten Fehlern
   - Prioritätsverteilung

## 📊 Statistik-Dashboard verstehen

### Top Trainer
```
Trainer: Stefan Albat
E-Mail: stefan@example.com
Ticket-Anzahl: 5
Hohe Priorität: 2
Ø Bearbeitungszeit: 3 Tage
```

**Was bedeutet das?**
- 5 Tickets insgesamt gemeldet
- Davon 2 mit hoher/kritischer Priorität
- Durchschnitt 3 Tage bis Lösung

**Aktion:**
- Trainer mit vielen Tickets: Schulung anbieten
- Trainer mit hoher Priorität: Hardwareprobleme überprüfen

### Häufigste Fehler
```
Fehler: Outlook funktioniert nicht (8 Tickets)
Fehler: WiFi-Verbindung (5 Tickets)
Fehler: Drucker offline (3 Tickets)
```

**Aktion:**
- Top-3 Fehler priorisieren
- Zentrale Lösung entwickeln
- Tipps/FAQ in Knowledge Base erstellen

### Klassenräume mit meisten Fehlern
```
Laptop-Wagen A1 (5 Fehler) - KRITISCH
Projektor-Set B2 (2 Fehler) - MITTEL
```

**Kritikalität:**
- 🔴 KRITISCH: 5+ Fehler → Sofort warten!
- 🟠 HOCH: 3-4 Fehler → Diese Woche
- 🟢 MITTEL: <3 Fehler → Nächste Woche

## 🎯 Praxisbeispiel: Fehler beheben

### Szenario
Sie sehen, dass "Laptop-Wagen A1" 5 Fehler hat und "Outlook-Fehler" ist der häufigste Fehler.

### Schritt-für-Schritt

1. **Problematischen Trainer identifizieren**
   - Dashboard → Top Trainer
   - "Stefan Albat" hat 2 Outlook-Fehler

2. **Tickets filtern**
   - /tickets/ → Filter → "Laptop-Wagen A1"
   - Sehen Sie alle Tickets für diesen Wagen

3. **Fehler analysieren**
   - Tickets öffnen und lesen
   - Muster erkennen (z.B. nur bei Windows 11?)

4. **Lösung implementieren**
   - Laptop-Wagen A1 inspizieren
   - Outlook aktualisieren
   - Treiber neu installieren

5. **Resultat überprüfen**
   - Warten bis Tickets geschlossen
   - Dashboard erneut laden
   - Fehler-Anzahl sollte sinken

## 📱 Mobil-Ansicht

### Ticket erstellen (Mobil)
```
URL: /tickets/create/

1. Title eingeben
2. Description eingeben
3. Scroll down → Mobile classroom
4. Aus Liste auswählen
5. Submit
```

### Ticket-Detail (Mobil)
```
Zeigt auch:
- Mobiler Klassenraum
- Standort
- Equipment-Typ
```

## 🔒 Berechtigungen

### Wer darf was sehen?

**Statistik-Dashboard:**
- ✅ Admin
- ✅ Support Agent
- ❌ Customer (Zugriff verweigert)

**Mobile Classroom Admin:**
- ✅ Admin
- ❌ Andere

**Tickets mit Classroom:**
- ✅ Alle (können Classroom auswählen)
- ✅ Admin kann filtern/sehen

## 🐛 Häufige Probleme

### Problem: "Mobiler Klassenraum" nicht im Formular
**Lösung:** Django neu starten
```bash
Ctrl+C (im Terminal)
python manage.py runserver
```

### Problem: Statistiken leer
**Lösung:** Keine geschlossenen/gelösten Tickets vorhanden
- Erstellen Sie Test-Tickets
- Weisen Sie sie zu und schließen Sie sie

### Problem: Classroom-Dropdown leer
**Lösung:** Keine Klassenräume erstellt
- Admin → Mobile Classrooms
- "+ Add Mobile Classroom" klicken
- Mindestens ein Eintrag erstellen

## 📚 Nächste Schritte

1. **Klassenzimmer-Daten vervollständigen**
   - Alle Standorte und Geräte in Admin eingeben
   - Equipment-Typen konsistent benennen

2. **Statistiken regelmäßig überprüfen**
   - Wöchentlich: `/tickets/statistics/`
   - Trends beobachten

3. **Schulungs-Planung**
   - Trainer mit vielen Tickets identifizieren
   - Schulungen anbieten
   - Fortschritt überwachen

4. **Hardware-Wartung**
   - Klassenräume mit hohen Fehlerzahlen priorisieren
   - Wartungsplan erstellen

## 💡 Pro-Tipps

### Tip 1: Filter kombinieren
```
/tickets/ → Filter → Mobile Classroom + Status (Closed)
= Alle geschlossenen Tickets für einen Wagen
```

### Tip 2: Search verwenden
Admin → Tickets → Suche: "Laptop-Wagen A1"
= Schnell alle Tickets für ein Gerät finden

### Tip 3: Bulk Actions
Admin → Tickets → Filter → Select All → Action
= Mehrere Tickets gleichzeitig bearbeiten

### Tip 4: Export für Reports
Admin → Tickets → Export (falls Feature geladen)
= Statistiken als CSV/Excel für Berichte

## 📞 Support

Falls Probleme auftreten:
1. Server-Logs überprüfen: `python manage.py runserver` Ausgabe
2. Django-Checks: `python manage.py check`
3. Migrations: `python manage.py migrate tickets`

---

**Status:** Alle Features sind einsatzbereit! 🚀
