# 📄 Word-Konvertierung Anleitung
## Markdown zu Word mit Aboro-IT Branding

---

## 🎯 Übersicht

Die folgenden Handbücher sind bereit für die Konvertierung zu Word-Dateien:

1. **ADMINISTRATOR_HANDBUCH.md** → `Aboro-IT_Administrator_Handbuch.docx`
2. **BENUTZERHANDBUCH.md** → `Aboro-IT_Support_Agent_Handbuch.docx`
3. **ENTWICKLER_HANDBUCH.md** → `Aboro-IT_Entwickler_Handbuch.docx`
4. **DOKUMENTATION_INDEX.md** → `Aboro-IT_Dokumentation_Index.docx`

---

## 🔧 Konvertierung mit Pandoc (Empfohlen)

### 1. Pandoc installieren
```bash
# Windows (mit Chocolatey)
choco install pandoc

# Oder direkt von: https://pandoc.org/installing.html
```

### 2. Markdown zu Word konvertieren
```bash
# Administrator Handbuch
pandoc ADMINISTRATOR_HANDBUCH.md -o "Aboro-IT_Administrator_Handbuch.docx" --reference-doc=template.docx

# Support Agent Handbuch  
pandoc BENUTZERHANDBUCH.md -o "Aboro-IT_Support_Agent_Handbuch.docx" --reference-doc=template.docx

# Entwickler Handbuch
pandoc ENTWICKLER_HANDBUCH.md -o "Aboro-IT_Entwickler_Handbuch.docx" --reference-doc=template.docx

# Dokumentation Index
pandoc DOKUMENTATION_INDEX.md -o "Aboro-IT_Dokumentation_Index.docx" --reference-doc=template.docx
```

### 3. Word-Template erstellen (template.docx)
1. Öffnen Sie Microsoft Word
2. Erstellen Sie ein neues Dokument
3. Konfigurieren Sie:
   - **Kopfzeile**: Aboro-IT Logo (mittig)
   - **Fußzeile**: © 2025 Aboro-IT | https://aboro-it.net
   - **Schriftart**: Calibri 11pt (Standard)
   - **Überschriften**: Calibri 14pt (Heading 1), 12pt (Heading 2)
   - **Farben**: Rot (#FF4444) für Akzente
4. Speichern als `template.docx`

---

## 📝 Alternative: Manuelle Konvertierung

### Option 1: Copy & Paste
1. Öffnen Sie die .md Datei in einem Markdown-Viewer (z.B. Typora, Mark Text)
2. Kopieren Sie den gerenderten Inhalt
3. Fügen Sie in Word ein
4. Formatieren Sie manuell nach

### Option 2: Word Import
1. Öffnen Sie Microsoft Word
2. Datei → Öffnen → Dateityp: "Alle Dateien"
3. Wählen Sie die .md Datei
4. Word konvertiert automatisch
5. Formatierung anpassen

---

## 🎨 Logo-Integration

### Aboro-IT Logo Spezifikationen
- **Position**: Erste Seite, mittig
- **Größe**: 400x150px oder proportional
- **Format**: PNG mit transparentem Hintergrund
- **Farben**: Rot (#FF4444) + Schwarz (#333333)

### Logo in Word einfügen:
1. **Einfügen** → **Bilder** → **Dieses Gerät**
2. Aboro-IT Logo auswählen
3. **Größe anpassen**: Rechtsklick → Größe und Eigenschaften
4. **Position**: Layout → Position → Weitere Layoutoptionen
5. **Zentrieren**: Horizontal → Ausrichtung → Zentriert

---

## 📋 Formatierungs-Checkliste

### Für alle Word-Dokumente:

#### Deckblatt
- ✅ Aboro-IT Logo (mittig, oben)
- ✅ Dokumenttitel (groß, zentriert)
- ✅ Untertitel (System-Beschreibung)
- ✅ Version und Datum
- ✅ "Professionelle IT-Lösungen für Ihr Unternehmen"

#### Kopf-/Fußzeilen
- ✅ **Kopfzeile**: Dokumentname + Aboro-IT Logo (klein)
- ✅ **Fußzeile**: © 2025 Aboro-IT | Seite X von Y | https://aboro-it.net

#### Formatierung
- ✅ **Überschrift 1**: Calibri 16pt, Rot (#FF4444), Fett
- ✅ **Überschrift 2**: Calibri 14pt, Schwarz, Fett  
- ✅ **Überschrift 3**: Calibri 12pt, Schwarz, Fett
- ✅ **Fließtext**: Calibri 11pt, Schwarz
- ✅ **Code**: Courier New 10pt, Grau
- ✅ **Tabellen**: Aboro-IT Rot für Header

#### Seitenlayout
- ✅ **Ränder**: 2,5cm oben/unten, 2cm links/rechts
- ✅ **Zeilenabstand**: 1,15 (Standard)
- ✅ **Seitenumbrüche**: Vor jedem Hauptkapitel
- ✅ **Inhaltsverzeichnis**: Automatisch generiert

---

## 🔍 Qualitätskontrolle

### Nach der Konvertierung prüfen:
- ✅ Logo korrekt positioniert und sichtbar
- ✅ Alle Überschriften korrekt formatiert
- ✅ Tabellen vollständig übernommen
- ✅ Code-Blöcke lesbar formatiert
- ✅ Links funktionsfähig
- ✅ Seitenzahlen korrekt
- ✅ Rechtschreibung prüfen
- ✅ Aboro-IT Branding konsistent

### Dateinamen-Konvention:
```
Aboro-IT_Administrator_Handbuch_v2.0_2025-11.docx
Aboro-IT_Support_Agent_Handbuch_v2.0_2025-11.docx  
Aboro-IT_Entwickler_Handbuch_v2.0_2025-11.docx
Aboro-IT_Dokumentation_Index_v2.0_2025-11.docx
```

---

## 📧 Support

Bei Fragen zur Konvertierung:
- **E-Mail**: docs@aboro-it.net
- **Telefon**: [Ihre Nummer]
- **Website**: https://aboro-it.net

---

**© 2025 Aboro-IT - Word-Konvertierung Anleitung**  
*Professionelle IT-Lösungen für Ihr Unternehmen*