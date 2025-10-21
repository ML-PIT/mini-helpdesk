# 📘 Benutzerhandbuch für Support Agents
## ML Gruppe Helpdesk System

---

## 🎯 Inhaltsverzeichnis

1. [Erste Schritte](#erste-schritte)
2. [Dashboard-Übersicht](#dashboard-übersicht)
3. [Ticket-Management](#ticket-management)
4. [Support Levels & Eskalation](#support-levels--eskalation)
5. [FAQ/Wissensdatenbank](#faqwissensdatenbank)
6. [Best Practices](#best-practices)
7. [Häufige Fragen](#häufige-fragen)

---

## 🚀 Erste Schritte

### Login
1. Öffnen Sie die Helpdesk-URL in Ihrem Browser
2. Geben Sie Ihre Email und Passwort ein
3. Klicken Sie auf "Anmelden"

### Dashboard
Nach dem Login sehen Sie Ihr persönliches Dashboard mit:
- **Mir zugewiesen**: Tickets, die Ihnen zugeordnet sind
- **Nicht zugewiesen**: Neue Tickets im Pool
- **In Bearbeitung**: Ihre aktiven Tickets
- **Gelöst**: Ihre kürzlich gelösten Tickets

---

## 📊 Dashboard-Übersicht

### Navigation
Die Hauptnavigation enthält:
- **Dashboard**: Ihre Übersicht
- **Tickets**: Alle verfügbaren Tickets
- **FAQ**: Wissensdatenbank
- **Ticket erstellen**: Für telefonische Anfragen
- **Logout**: Abmelden

### Statistiken

**Ihre Kennzahlen:**
- Anzahl zugewiesener Tickets
- Unzugewiesene Tickets (verfügbar zur Übernahme)
- Tickets in Bearbeitung
- Gelöste Tickets

---

## 🎫 Ticket-Management

### 1. Neues Ticket übernehmen

#### Aus der Ticket-Liste:
1. Gehen Sie zu **Tickets**
2. Finden Sie ein Ticket mit Status "Offen" ohne Zuweisung
3. Klicken Sie auf "Ansehen"
4. Klicken Sie auf **"Mir zuweisen"**

✅ **Das Ticket wird Ihnen zugewiesen und der Status ändert sich auf "In Bearbeitung"**

### 2. Ticket für Kunde erstellen (Telefonanfrage)

Wenn ein Kunde telefonisch anruft:

1. Klicken Sie auf **"Ticket erstellen"** in der Navigation
2. Geben Sie die **Kunden-Email** ein (Kunde muss im System existieren)
3. Füllen Sie aus:
   - **Titel**: Kurze Zusammenfassung des Problems
   - **Beschreibung**: Detaillierte Problembeschreibung vom Kunden
   - **Kategorie**: Passende Kategorie wählen
   - **Priorität**:
     - 🟢 **Low**: Nicht dringend
     - 🟡 **Medium**: Normale Priorität (Standard)
     - 🟠 **High**: Dringend
     - 🔴 **Critical**: Sehr dringend, blockiert Arbeit
4. Klicken Sie auf **"Ticket für Kunde erstellen"**

**💡 Hinweis:** Ein interner Kommentar wird automatisch erstellt, der vermerkt, dass Sie dieses Ticket für den Kunden erstellt haben.

### 3. Auf Ticket antworten

1. Öffnen Sie das Ticket
2. Scrollen Sie zum Kommentar-Bereich
3. Geben Sie Ihre Antwort ein
4. **Optional**: Haken bei "Interner Kommentar" setzen
   - ✅ **Mit Haken**: Nur für Support-Team sichtbar
   - ❌ **Ohne Haken**: Kunde kann den Kommentar sehen
5. Klicken Sie auf **"Nachricht senden"**

### 4. Ticket-Status ändern

Tickets durchlaufen folgende Status:

| Status | Bedeutung | Wann verwenden |
|--------|-----------|----------------|
| 🟢 **Offen** | Neu erstellt | Automatisch bei Erstellung |
| 🟡 **In Bearbeitung** | Wird bearbeitet | Automatisch bei Zuweisung |
| 🔵 **Wartet auf Kunde** | Kunde muss antworten | Wenn Sie auf Rückmeldung warten |
| 🟢 **Gelöst** | Problem behoben | Nach erfolgreicher Lösung |
| ⚫ **Geschlossen** | Abgeschlossen | Final geschlossen |

**Status wird automatisch geändert durch:**
- Zuweisung → "In Bearbeitung"
- Schließen → "Geschlossen"

### 5. Ticket eskalieren

Wenn Sie Hilfe von einem höheren Support Level benötigen:

1. Öffnen Sie das Ticket
2. Klicken Sie auf **"Eskalieren"**
3. Wählen Sie:
   - **Agent**: Support Agent mit höherem Level
   - **Neuer Support Level**: (Optional) Level 2, 3 oder 4
   - **Grund**: Warum wird eskaliert?
4. Klicken Sie auf **"Ticket eskalieren"**

**Eskalations-Regeln:**
- Level 1 → kann zu Level 2, 3 oder 4 eskalieren
- Level 2 → kann zu Level 3 oder 4 eskalieren
- Level 3 → kann zu Level 4 eskalieren
- Level 4 → kann alle Tickets bearbeiten

### 6. Ticket schließen

**Nur Sie oder ein Admin kann Ihre zugewiesenen Tickets schließen!**

1. Öffnen Sie das Ticket
2. Stellen Sie sicher, dass das Problem gelöst ist
3. Klicken Sie auf **"Schließen"**
4. **Bestätigen** Sie die Aktion

**Was passiert beim Schließen:**
- ✅ Status wird auf "Geschlossen" gesetzt
- ✅ Zeitstempel wird gespeichert
- ✅ **Kunde erhält Email mit komplettem Ticket-Verlauf**
- ✅ Ticket verschwindet aus Ihrer aktiven Liste

---

## 📈 Support Levels & Eskalation

### Support Level Struktur

#### 🔵 Level 1 - Basic Support
- Erste Anlaufstelle
- Einfache Anfragen
- Standard-Probleme aus FAQ
- **Kann eskalieren zu**: Level 2, 3, 4

#### 🟠 Level 2 - Technical Support
- Technische Probleme
- Komplexe Konfigurationen
- Kann FAQ-Artikel erstellen
- **Kann eskalieren zu**: Level 3, 4

#### 🔴 Level 3 - Expert Support
- Sehr komplexe Probleme
- Spezialwissen erforderlich
- Kann FAQ-Artikel erstellen
- **Kann eskalieren zu**: Level 4

#### 🟣 Level 4 - Senior Expert / Team Lead
- Kritische Probleme
- Alle anderen Levels
- Kann FAQ-Artikel erstellen
- Management-Funktionen

### Wann eskalieren?

**Eskalieren Sie, wenn:**
- ✅ Problem außerhalb Ihres Kompetenzbereichs
- ✅ Spezialwissen erforderlich
- ✅ Kritisches/dringendes Problem
- ✅ Sie nach 30 Minuten keine Lösung haben

**Nicht eskalieren, wenn:**
- ❌ Sie noch nicht in der FAQ/Wissensdatenbank gesucht haben
- ❌ Sie noch nicht gegoogelt haben
- ❌ Problem ist lösbar mit mehr Zeit

---

## 📚 FAQ/Wissensdatenbank

### FAQ durchsuchen

1. Klicken Sie auf **"FAQ"** in der Navigation
2. Nutzen Sie die **Suchleiste** oben
3. Oder filtern Sie nach **Kategorie**
4. Klicken Sie auf einen Artikel zum Lesen

**💡 Tipp:** Suchen Sie IMMER zuerst in der FAQ, bevor Sie eskalieren!

### FAQ-Artikel erstellen (Level 2+)

**Nur für Support Level 2, 3 und 4**

1. Gehen Sie zu **FAQ**
2. Klicken Sie auf **"+ Neuer Artikel"**
3. Füllen Sie aus:
   - **Titel**: Frage oder Problem (z.B. "Wie setze ich mein Passwort zurück?")
   - **Kurzbeschreibung**: 1-2 Sätze Zusammenfassung
   - **Inhalt**: Detaillierte Schritt-für-Schritt Anleitung
   - **Kategorie**: Passende Kategorie
   - **Suchbegriffe**: Komma-getrennt (z.B. "passwort, reset, vergessen")
   - **Öffentlich**: ✅ Für Kunden sichtbar | ❌ Nur intern
   - **Als häufige Frage**: ✅ Auf Hauptseite hervorheben
   - **Status**: Entwurf oder Veröffentlicht
4. Klicken Sie auf **"Artikel erstellen"**

### FAQ-Artikel bearbeiten

1. Öffnen Sie den Artikel
2. Klicken Sie auf **"Bearbeiten"** (nur bei eigenen Artikeln oder Level 2+)
3. Nehmen Sie Änderungen vor
4. Klicken Sie auf **"Änderungen speichern"**

---

## ✅ Best Practices

### Kommunikation mit Kunden

#### DO ✅
- Freundlich und professionell bleiben
- Klar und verständlich schreiben
- Problem zusammenfassen
- Lösung Schritt-für-Schritt erklären
- Nachfragen, ob Problem gelöst ist
- Danken für Geduld

#### DON'T ❌
- Technisches Kauderwelsch
- Ungeduldig oder genervt wirken
- Schuld beim Kunden suchen
- Zu lange Wartezeiten ohne Update
- Ticket ohne Lösung schließen

### Ticket-Bearbeitung

**Response-Zeiten einhalten:**
- 🔴 **Critical**: Innerhalb 4 Stunden
- 🟠 **High**: Innerhalb 24 Stunden
- 🟡 **Medium**: Innerhalb 72 Stunden
- 🟢 **Low**: Innerhalb 1 Woche

**Ticket-Qualität:**
1. **Erste Antwort**: Bestätigen Sie Ticket-Erhalt
2. **Diagnose**: Analysieren Sie das Problem
3. **Lösung**: Bieten Sie klare Lösung an
4. **Verifizierung**: Bestätigen Sie, dass es funktioniert
5. **Schließen**: Erst nach Kundenzustimmung

### Interne Notizen nutzen

Nutzen Sie interne Kommentare für:
- ✅ Technische Details
- ✅ Recherche-Notizen
- ✅ Eskalations-Begründungen
- ✅ Informationen für Kollegen
- ❌ NICHT für Kundenkommunikation

---

## 🤖 Claude AI Auto-Response

### Wie funktioniert die KI?

Bei neuen Tickets:
1. Claude AI analysiert automatisch die Ticket-Beschreibung
2. Sucht in der Wissensdatenbank nach passenden Artikeln
3. Generiert eine hilfreiche Antwort auf Deutsch
4. Fügt automatisch einen Kommentar hinzu

**Die KI antwortet NUR bei:**
- ✅ Neuen, unzugewiesenen Tickets
- ✅ Low/Medium Priorität
- ✅ Einfachen Fragen mit FAQ-Lösungen

**Die KI antwortet NICHT bei:**
- ❌ High/Critical Priorität
- ❌ Komplexen Problemen
- ❌ Sensiblen Daten
- ❌ Abrechnungs-Fragen

**💡 Sie müssen trotzdem das Ticket prüfen und nachfassen!**

---

## ❓ Häufige Fragen

### Wie finde ich meine zugewiesenen Tickets?
Klicken Sie auf **"Tickets"** → Ihre Tickets haben Ihren Namen in der Spalte "Zugewiesen an"

### Kann ich ein Ticket einem anderen Agent zuweisen?
Ja! Nutzen Sie die **"Eskalieren"**-Funktion

### Was passiert, wenn ich ein Ticket schließe?
Der Kunde erhält automatisch eine Email mit dem kompletten Ticket-Verlauf.

### Kann ich gelöschte Tickets wiederherstellen?
Tickets werden nicht gelöscht, nur geschlossen. Admins können den Status ändern.

### Wo sehe ich geschlossene Tickets?
In der Ticket-Liste können Sie nach Status filtern (bald verfügbar) oder im Admin-Bereich.

### Wie ändere ich mein Passwort?
Klicken Sie auf Ihren Namen → **"Passwort ändern"**

### Bekomme ich Benachrichtigungen?
Ja! Sie erhalten Emails bei:
- Neuen Tickets (alle Agents)
- Antworten auf Ihre zugewiesenen Tickets
- Eskalationen an Sie

### Kann ich mehrere Tickets gleichzeitig bearbeiten?
Ja! Es gibt keine Begrenzung für zugewiesene Tickets.

### Was bedeutet "SLA"?
**Service Level Agreement** - Die maximale Zeit bis zur Antwort:
- Critical: 4 Stunden
- High: 24 Stunden
- Medium: 72 Stunden
- Low: 1 Woche

### Wo finde ich Statistiken?
Auf Ihrem Dashboard sehen Sie Ihre persönlichen Statistiken. Detaillierte Reports sind im Admin-Bereich (nur für Admins).

---

## 📞 Support für Support

Bei technischen Problemen mit dem Helpdesk-System:
- **Email**: admin@ml-gruppe.de
- **Telefon**: [Ihre Nummer]
- **Notfall**: Kontaktieren Sie Ihren Team Lead (Level 4 Agent)

---

## 📝 Changelog

**Version 1.0** - Januar 2025
- Initiale Version
- Support Levels 1-4
- Claude AI Integration
- FAQ-System
- Email-Benachrichtigungen

---

© 2025 ML Gruppe - Internes Dokument
