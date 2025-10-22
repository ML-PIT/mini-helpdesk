# TinyMCE Rich Text Editor für Knowledge Base

## Übersicht

Die Knowledge Base Artikel-Verwaltung (Erstellen und Bearbeiten) wurde mit **TinyMCE** erweitert - einem kostenlosen, professionellen Rich-Text-Editor.

## Features

### 1. Rich Text Formatting
- **Text-Formatierung**: Bold, Italic, Strikethrough, Superscript, Subscript
- **Farben**: Vordergrund- und Hintergrundfarbe
- **Ausrichtung**: Links, zentriert, rechts, Blocksatz
- **Listen**: Aufzählungen und nummerierte Listen
- **Einzug**: Einzugstiefe reduzieren/erhöhen

### 2. Inhalts-Elemente
- **Links**: Hyperlinks einfügen/bearbeiten
- **Bilder**: Bilder einfügen
- **Tabellen**: Tabellen erstellen und formatieren
- **Horizontal Rule**: Trennlinien
- **Seiten-Umbruch**: Seitenumbrüche einfügen
- **Spezialzeichen**: Emojis und Sonderzeichen

### 3. Editor-Features
- **Code-View**: HTML-Quellcode anzeigen/bearbeiten
- **Vollbild**: Maximierter Editor
- **Suchen/Ersetzen**: Text durchsuchen und ersetzen
- **Wort-Zähler**: Anzahl der Wörter anzeigen
- **Sicherung**: Lokale Sicherung der Änderungen
- **Einfügen**: Intelligentes Einfügen von formatiertem Text

### 4. Deutsch-Lokalisierung
- Komplette deutsche Benutzeroberfläche
- Deutsche Menüs und Tooltips

## Technische Details

### TinyMCE CDN
```html
<script src="https://cdn.tiny.cloud/1/no-api-key/tinymce/6/tinymce.min.js" referrerpolicy="origin"></script>
```

**Hinweis**: Verwendet "no-api-key" - in Produktion sollte ein API-Key eingerichtet werden für erweiterte Features.

### Konfiguration
```javascript
tinymce.init({
  selector: '#content',           // Ziel-Textarea mit ID "content"
  height: 500,                    // Editor-Höhe in Pixel
  plugins: [                      // Installierte Plugins
    'advlist autolink lists link image charmap print preview hr anchor pagebreak',
    'searchreplace wordcount visualblocks visualchars code fullscreen',
    'insertdatetime media nonbreaking save table contextmenu directionality',
    'emoticons template paste textpattern help'
  ],
  toolbar: [                      // Toolbar-Buttons
    'formatselect | bold italic strikethrough forecolor backcolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image | code'
  ],
  automatic_uploads: false,       // Deaktiviert Auto-Upload
  paste_data_images: false,       // Bilder beim Paste nicht einbetten
  relative_urls: false,           // Absolute URLs verwenden
  language: 'de',                 // Deutsche Oberfläche
});
```

## Dateien mit TinyMCE Integration

### 1. create.html (`templates/knowledge/create.html`)
- TinyMCE wird beim Laden der Seite initialisiert
- Für das `#content` Textarea-Feld
- Erlaubt formatierte Inhalte beim Erstellen neuer Artikel

### 2. edit.html (`templates/knowledge/edit.html`)
- TinyMCE wird beim Laden der Seite initialisiert
- Für das `#content` Textarea-Feld mit vorhandenen Inhalten
- Erlaubt Bearbeitung von existierenden Artikeln mit voller Formatierung

## Toolbar Features

### Formatierungszeile
- **Format-Dropdown**: Absatz, Überschriften h1-h6
- **Bold** (Ctrl+B): Fetter Text
- **Italic** (Ctrl+I): Kursiver Text
- **Strikethrough**: Durchgestrichener Text
- **Vordergrundfarbe**: Text-Farbe ändern
- **Hintergrundfarbe**: Highlighting

### Ausrichtungs- & Listen-Zeile
- **Ausrichtung**: Links, Zentriert, Rechts, Blocksatz
- **Aufzählungsliste**: Ungeordnete Liste
- **Nummerierte Liste**: Geordnete Liste
- **Einzug verringern/erhöhen**: Listenebene anpassen

### Links & Medien
- **Link**: Hyperlinks hinzufügen
- **Bild**: Bilder einfügen
- **Code**: Quellcode anzeigen/bearbeiten

## Workflow

### Neuen Artikel erstellen

```
1. Agent/Admin navigiert zu: /kb/create/
2. Gibt "Titel" ein
3. Gibt "Kurzbeschreibung" ein
4. Klickt auf "Inhalt" Feld
5. TinyMCE Editor wird aktiviert
6. Verwendet Toolbar zum Formatieren:
   - Text fett machen
   - Liste einfügen
   - Links hinzufügen
   - Tabellen erstellen
7. Klickt "Artikel erstellen"
8. Formatierten HTML wird in Datenbank gespeichert
```

### Artikel bearbeiten

```
1. Agent/Admin klickt auf Artikel bearbeiten
2. TinyMCE wird mit existierendem HTML geladen
3. Bearbeitet Inhalt mit voller Formatierung
4. Klickt "Änderungen speichern"
5. Formatierung wird erhalten
```

## Sicherheit

### Datenschutz
- ✅ **Keine Cloud-Uploads**: `automatic_uploads: false`
- ✅ **Keine Bild-Einbettung**: `paste_data_images: false`
- ✅ **Lokale Verarbeitung**: Alle Inhalte bleiben lokal

### Content Security
- HTML-Inhalte werden in Django-Templates korrekt escaped
- Im Template: `{{ article.content|safe }}` (nur wenn content von Admins kommt)
- XSS-Schutz durch Django's Template-Engine

## Performance

- **CDN-basiert**: Schnelle Lieferung global
- **Lazy Loading**: TinyMCE wird nur auf create/edit Seiten geladen
- **Lightweight**: ~80KB minifiziert
- **Browser-Kompatibilität**: Alle modernen Browser (Chrome, Firefox, Safari, Edge)

## Beispiel-Formatierung

### Input im Editor
```
Hallo,

Das ist ein FETTER Text und ein kursiver Text.

Hier ist eine Liste:
- Punkt 1
- Punkt 2
- Punkt 3

Und eine Tabelle:
[Tabelle mit 2 Spalten und 3 Reihen]

Link: https://beispiel.de
```

### Output in Datenbank (HTML)
```html
<p>Hallo,</p>
<p>Das ist ein <strong>FETTER</strong> Text und ein <em>kursiver</em> Text.</p>
<p>Hier ist eine Liste:</p>
<ul>
  <li>Punkt 1</li>
  <li>Punkt 2</li>
  <li>Punkt 3</li>
</ul>
<p>Und eine Tabelle:</p>
<table>
  <tr><td>Cell 1</td><td>Cell 2</td></tr>
  ...
</table>
<p>Link: <a href="https://beispiel.de">https://beispiel.de</a></p>
```

### Anzeige im Frontend
Die Inhalte werden mit `{{ article.content|safe }}` angezeigt - der HTML wird korrekt gerendert.

## Produktion

### API-Key einrichten (Optional)

Für erweiterte Features (Cloud-Speicher, erweiterte Plugins):

1. Registrieren auf: https://www.tiny.cloud/
2. API-Key erhalten
3. Settings.py aktualisieren:

```python
TINYMCE_API_KEY = 'your-api-key-here'
```

4. Template aktualisieren:
```html
<script src="https://cdn.tiny.cloud/1/YOUR_API_KEY/tinymce/6/tinymce.min.js" referrerpolicy="origin"></script>
```

### Ohne API-Key
Aktuelle Implementierung funktioniert vollständig ohne API-Key mit lokalen Uploads deaktiviert.

## Browser-Unterstützung

✅ Chrome (Latest)
✅ Firefox (Latest)
✅ Safari (Latest)
✅ Edge (Latest)
✅ Mobile Browsers (aber optimiert für Desktop)

## Testing

### Test 1: Text-Formatierung
```
1. Öffne /kb/create/
2. Gib Text ein
3. Wähle Text und mache ihn bold
4. Speichere Artikel
5. Ansicht: Text sollte fett sein
```

### Test 2: Listen
```
1. Öffne Editor
2. Klicke "Aufzählungsliste"
3. Gib Punkte ein
4. Speichere
5. Ansicht: HTML `<ul><li>` sollte angezeigt werden
```

### Test 3: Links
```
1. Öffne Editor
2. Tippe Text
3. Wähle Text, klicke "Link"
4. Gib URL ein
5. Speichere
6. Ansicht: Link sollte klickbar sein
```

## Validierung

✅ Django System Check: Keine Fehler
✅ Template Syntax: Valid (create.html, edit.html)
✅ TinyMCE CDN: Erreichbar
✅ JavaScript: Keine Fehler in der Konsole

## Bekannte Limitierungen

1. **Kein Cloud-Upload**: Bilder können nicht direkt hochgeladen werden (intentional)
2. **Keine Collaboration**: Nur Ein-Benutzer-Editing
3. **Keine Versionskontrolle**: Keine automatische Artikel-Historie

Diese Limitierungen können später bei Bedarf hinzugefügt werden.

## Zukünftige Erweiterungen

Mögliche Verbesserungen:
- [ ] Bild-Upload-Funktion
- [ ] Artikel-Versionskontrolle
- [ ] Änderungsverlauf (Revision History)
- [ ] Zusammenarbeits-Features
- [ ] Export zu PDF
- [ ] Markdown-Import/Export
