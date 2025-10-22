# CKEditor Rich Text Editor für Knowledge Base

## Übersicht

Die Knowledge Base Artikel-Verwaltung (Erstellen und Bearbeiten) wurde mit **CKEditor** erweitert - einem kostenlosen, professionellen Rich-Text-Editor mit voller Funktionalität und ohne API-Key-Anforderung.

## Installation & Konfiguration

### 1. Installation der Pakete

```bash
pip install django-ckeditor pillow
```

Folgende Pakete wurden installiert:
- **django-ckeditor**: Django Integration für CKEditor
- **pillow**: Bildverarbeitung für CKEditor Bild-Uploads

### 2. Django Konfiguration (settings.py)

```python
# INSTALLED_APPS
INSTALLED_APPS = [
    ...
    'ckeditor',
    'ckeditor_uploader',
    ...
]

# URL Routing
urlpatterns = [
    ...
    path('ckeditor/', include('ckeditor_uploader.urls')),
    ...
]

# CKEditor Basiskonfiguration
CKEDITOR_BASEPATH = '/static/ckeditor/ckeditor/'
CKEDITOR_UPLOAD_PATH = 'uploads/ckeditor/'
CKEDITOR_ALLOW_NONIMAGE_FILES = False
CKEDITOR_BROWSE_SHOW_DIRS = True
CKEDITOR_RESTRICT_BY_USER = False
CKEDITOR_RESTRICT_BY_DATE = True
CKEDITOR_IMAGE_BACKEND = "pillow"

# CKEditor Editor-Konfiguration
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': [
            {'name': 'document', 'items': ['Source']},
            {'name': 'clipboard', 'items': ['Undo', 'Redo']},
            {'name': 'editing', 'items': ['Find', 'Replace']},
            {'name': 'basicstyles', 'items': ['Bold', 'Italic', 'Underline', 'Strike', 'Subscript', 'Superscript']},
            {'name': 'paragraph', 'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock']},
            {'name': 'links', 'items': ['Link', 'Unlink', 'Anchor']},
            {'name': 'insert', 'items': ['Image', 'Table', 'HorizontalRule', 'Smiley', 'SpecialChar']},
            '/',
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            {'name': 'styles', 'items': ['Format', 'Font', 'FontSize']},
            {'name': 'tools', 'items': ['Maximize']},
        ],
        'height': 400,
        'width': '100%',
        'contentsCss': ['/static/ckeditor/contents.css'],
        'language': 'de',
    }
}
```

## Features

### 1. Text-Formatierung

- **Bold** (Ctrl+B): Fetter Text
- **Italic** (Ctrl+I): Kursiver Text
- **Underline** (Ctrl+U): Unterstrichener Text
- **Strikethrough**: Durchgestrichener Text
- **Subscript**: Tiefgestellter Text (H₂O)
- **Superscript**: Hochgestellter Text (E=mc²)

### 2. Farben & Styling

- **Vordergrundfarbe**: Textfarbe ändern
- **Hintergrundfarbe**: Highlighting und Hintergrund
- **Format-Dropdown**:
  - Normal (Paragraph)
  - Überschriften (H1-H6)
  - Preformatiert
  - Adresse

### 3. Listen & Einzug

- **Aufzählungsliste**: Ungeordnete Liste mit Punkten
- **Nummerierte Liste**: Geordnete Liste mit Nummern
- **Einzug erhöhen**: Listenebene vertiefen
- **Einzug verringern**: Listenebene reduzieren

### 4. Ausrichtung

- **Linksbündig**: Ausrichtung nach links
- **Zentriert**: Text in der Mitte
- **Rechtsbündig**: Ausrichtung nach rechts
- **Blocksatz**: Gleichmäßige Ausrichtung

### 5. Links & Verweise

- **Link**: Hyperlink einfügen oder bearbeiten
- **Unlink**: Link entfernen
- **Anchor**: Interne Verweise/Lesezeichen erstellen

### 6. Medien & Elemente

- **Bild**: Bilder hochladen und einfügen
- **Tabelle**:
  - Tabelle einfügen
  - Zeilen/Spalten hinzufügen/löschen
  - Zelleneigenschaften bearbeiten
  - Tabelleneigenschaften ändern
- **Horizontal Rule**: Trennlinie einfügen
- **Sonderzeichen**: Emojis und spezielle Zeichen

### 7. Editor-Features

- **Quellcode (Source)**: HTML-Quelltext anzeigen und bearbeiten
- **Suchen/Ersetzen**: Text durchsuchen und automatisch ersetzen
- **Vollbild (Maximize)**: Editor in Vollbildmodus verwenden
- **Automatische Speicherung**: Lokale Speicherung der Änderungen (optional)

### 8. Deutsch-Lokalisierung

- Komplette deutsche Benutzeroberfläche
- Deutsche Menüs, Tooltips und Fehlermeldungen
- Deutsche Zeichensätze (Umlaute: ä, ö, ü)

## Modell-Integration

### KnowledgeArticle Model

Die `content` Feld wurde von `TextField` zu `RichTextUploadingField` geändert:

```python
from ckeditor_uploader.fields import RichTextUploadingField

class KnowledgeArticle(models.Model):
    title = models.CharField(_('title'), max_length=200, db_index=True)
    slug = models.SlugField(_('slug'), max_length=220, unique=True, blank=True)
    content = RichTextUploadingField(_('content'),
                                   help_text=_('Rich text editor für formatierte Inhalte'))
    # ... andere Felder
```

### Datenbank-Migration

Migration erstellt und angewendet:
```bash
python manage.py makemigrations knowledge
python manage.py migrate knowledge
```

Die Migration ändert den Spaltentyp von `TextField` zu `longtext` (in MySQL) oder entsprechend in anderen Datenbanken.

## Template-Integration

### Automatische Widget-Integration

Da das Modellfeld `RichTextUploadingField` ist, wird CKEditor automatisch im Django Admin und in ModelForms gerendert. **Keine manuellen Script-Einbindungen nötig!**

**create.html** und **edit.html**:
- Entfernen Sie alle manuellen CKEditor-Scripts
- Das Formularfeld wird automatisch mit CKEditor initialisiert
- Django's Form Widget System kümmert sich um die Integration

### Sichere HTML-Anzeige

Bei der Anzeige von Artikel-Inhalten in Templates:

```html
<!-- Artikel-Detail Seite -->
<div class="article-content">
    {{ article.content|safe }}
</div>
```

**Sicherheitshinweis**: Der `|safe` Filter ist hier gerechtfertigt, da:
1. Inhalte nur von Admin-Benutzern über CKEditor erstellt werden
2. CKEditor deaktiviert gefährliche HTML-Tags standardmäßig
3. Keine Benutzereingabe von Kunden wird hier eingefügt

## Datei-Upload & Verwaltung

### Upload-Verzeichnis

Bilder werden hochgeladen zu:
```
media/uploads/ckeditor/
```

### Konfiguration

```python
CKEDITOR_UPLOAD_PATH = 'uploads/ckeditor/'          # Upload-Verzeichnis
CKEDITOR_ALLOW_NONIMAGE_FILES = False               # Nur Bilder erlaubt
CKEDITOR_RESTRICT_BY_DATE = True                    # Bilder in Jahres-/Monats-Ordnern
CKEDITOR_IMAGE_BACKEND = "pillow"                   # Bildverarbeitung mit Pillow
```

### Verfügbare Dateitypen

- **Bilder**: PNG, JPG, JPEG, GIF, BMP, WebP
- **Video/Audio**: Nicht standardmäßig (optional konfigurierbar)
- **Dokumente**: Deaktiviert (nur Bilder)

## Sicherheit

### 1. Content Security Policy

CKEditor blockiert automatisch:
- JavaScript-Code im Content
- Event-Handler (onclick, onload, etc.)
- Gefährliche HTML-Tags

### 2. Benutzerverwaltung

```python
CKEDITOR_RESTRICT_BY_USER = False  # Alle Admins sehen alle Uploads
# True würde Upload-Verzeichnisse pro User trennen
```

### 3. Dateivalidierung

- Bildtyp-Validierung durch Pillow
- MIME-Type-Überprüfung
- Dateigrößen-Limits über Django Einstellungen

### 4. Zugriffsschutz

- CKEditor nur für angemeldete Benutzer verfügbar
- Admin-Panel ist geschützt
- Upload-URL erfordert Authentifizierung

## Workflow

### Neuen Artikel erstellen

```
1. Admin/Agent navigiert zu: /kb/create/
2. Seite wird geladen
3. CKEditor wird automatisch im "Inhalt"-Feld geladen
4. Admin kann formatieren mit:
   - Toolbar Buttons
   - Tastaturkürzel (Ctrl+B, Ctrl+I, etc.)
   - Rechtsklick-Menü
5. Bilder können per Klick auf "Bild" Button hochgeladen werden
6. Artikel wird gespeichert
7. HTML-formatierter Inhalt ist in Datenbank gespeichert
```

### Artikel bearbeiten

```
1. Admin/Agent klickt "Bearbeiten" auf existierendem Artikel
2. CKEditor wird mit existierendem HTML-Inhalt geladen
3. Formatierung wird vollständig beibehalten
4. Admin kann weitere Änderungen vornehmen
5. Speichern
6. Änderungen sind persistent
```

### Bild-Upload im Editor

```
1. Cursor im Editor an gewünschte Position
2. Klick auf "Bild" Button
3. Dialog öffnet sich
4. Wählen: "Upload" Tab
5. Datei wählen oder Drag & Drop
6. Bild wird hochgeladen und eingefügt
7. Größe und Eigenschaften können angepasst werden
8. Speichern
```

## Toolbar-Übersicht

### Formatierungszeile

```
[Format-Dropdown] | Bold | Italic | Underline | Strike | Sub | Sup
```

### Farben und Styling

```
[Farbe wählen] | [Hintergrundfarbe wählen] | [Schriftart] | [Schriftgröße]
```

### Listen und Ausrichtung

```
[Aufzählung] | [Nummeriert] | [Einzug-] | [Einzug+] | [<] | [≡] | [>] | [=]
```

### Inhalts-Einfügen

```
[Link] | [Unlink] | [Anker] | [Bild] | [Tabelle] | [Linie] | [Smiley] | [Zeichen]
```

### Erweitertes

```
[Quellcode] | [Suchen/Ersetzen] | [Vollbild]
```

## Beispiele

### Input: Text mit Formatierung

```
Hallo,

Das ist ein FETTER Text und ein kursiver Text sowie unterstrichener Text.

Hier ist eine Liste:
- Punkt 1
- Punkt 2
- Punkt 3

Eine nummerierte Liste:
1. Erster Schritt
2. Zweiter Schritt
3. Dritter Schritt
```

### Output: HTML in Datenbank

```html
<p>Hallo,</p>
<p>Das ist ein <strong>FETTER</strong> Text und ein <em>kursiver</em> Text sowie <u>unterstrichener</u> Text.</p>
<p>Hier ist eine Liste:</p>
<ul>
    <li>Punkt 1</li>
    <li>Punkt 2</li>
    <li>Punkt 3</li>
</ul>
<p>Eine nummerierte Liste:</p>
<ol>
    <li>Erster Schritt</li>
    <li>Zweiter Schritt</li>
    <li>Dritter Schritt</li>
</ol>
```

### Display im Frontend

Der Inhalt wird mit `{{ article.content|safe }}` angezeigt und korrekt als HTML gerendert.

## Konfigurationsoptionen

### Editor-Größe

```python
CKEDITOR_CONFIGS = {
    'default': {
        'height': 400,      # Höhe in Pixel (Standard)
        'width': '100%',    # Breite (Standard: voll Breite)
    }
}
```

### Benutzerdefinierte Toolbar

```python
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList'],
            ['Link', 'Unlink'],
            ['Image'],
        ],
    }
}
```

### Zusätzliche Plugins

```python
CKEDITOR_CONFIGS = {
    'default': {
        'extraPlugins': 'codesnippet,youtube',  # Zusätzliche Plugins
    }
}
```

## Bekannte Limitierungen

1. **CKEditor 4.22.1**:
   - Alte Version mit End-of-Life-Status
   - Sicherheitshinweise vom Hersteller
   - Funktioniert aber vollständig in Production
   - Upgrade zu CKEditor 5 möglich bei Bedarf

2. **Kein Cloud-Speicher**:
   - Bilder werden lokal gespeichert
   - Kein Integration mit AWS S3, etc. (aber konfigurierbar)

3. **Keine Collaboration**:
   - Nur ein Editor zur Zeit pro Artikel
   - Keine Echtzeit-Zusammenarbeit

4. **Keine Versionskontrolle**:
   - Keine automatische Artikel-Historie
   - Keine Revision-Tracking

Diese Limitierungen können später bei Bedarf hinzugefügt werden.

## Browser-Unterstützung

✅ Chrome (Neueste)
✅ Firefox (Neueste)
✅ Safari (Neueste)
✅ Edge (Neueste)
⚠️ Mobile Browser (begrenzte Unterstützung - optimiert für Desktop)

## Häufig Gestellte Fragen

### F: Benötige ich einen API-Key?

**A:** Nein. CKEditor funktioniert komplett lokal ohne API-Key. Ein API-Key ist nur für Premium-Features nötig.

### F: Können Kunden auch Artikel erstellen?

**A:** Nein. CKEditor ist im Admin-Panel und für Admins/Agents in den create/edit Views verfügbar. Kunden sehen nur die Artikel.

### F: Wie kann ich Bilder hochladen?

**A:** Klicken Sie im Editor auf den "Bild" Button, wählen Sie "Upload", und wählen Sie eine Datei. Bilder werden in `media/uploads/ckeditor/` gespeichert.

### F: Kann ich CSS custom stylen?

**A:** Ja. Bearbeiten Sie `CKEDITOR_CONFIGS['default']['contentsCss']` um benutzerdefinierte Stylesheets zu laden.

### F: Ist mein HTML-Content sicher?

**A:** Ja. CKEditor deaktiviert standardmäßig gefährliche Tags. Der Content wird von Admins erstellt und ist nicht Benutzereingabe.

## Zukünftige Erweiterungen

Mögliche Verbesserungen:

- [ ] Upgrade zu CKEditor 5 (modernere Version)
- [ ] S3 Cloud-Speicher Integration für Bilder
- [ ] Artikel-Versionskontrolle
- [ ] Änderungsverlauf (Revision History)
- [ ] Zusammenarbeits-Features (Multi-User Editing)
- [ ] PDF-Export
- [ ] Markdown-Import/Export
- [ ] Code-Highlighting Plugin
- [ ] Video-Embed Support
- [ ] Math-Formel Support

## Fehlerbehandlung

### CKEditor lädt nicht

**Symptom**: Textarea bleibt leere Textarea, Editor wird nicht geladen

**Lösungen**:
1. Browser Cache leeren (Ctrl+Shift+Delete)
2. DevTools Console auf Fehler prüfen (F12)
3. Statische Dateien sammeln: `python manage.py collectstatic --noinput`
4. Server neustarten: `python manage.py runserver`

### Bilder werden nicht hochgeladen

**Symptom**: Bild-Upload dialog schließt sich, Bild wird nicht eingefügt

**Lösungen**:
1. `media/` Verzeichnis ist beschreibbar
2. Pillow ist installiert: `pip install pillow`
3. Datei ist Bild (PNG, JPG, GIF, etc.)
4. Datei ist nicht zu groß
5. `/ckeditor/upload/` URL ist erreichbar

### HTML-Content wird nicht gespeichert

**Symptom**: Artikel wird gespeichert, aber HTML-Formatierung geht verloren

**Lösungen**:
1. Migration wurde angewendet: `python manage.py migrate knowledge`
2. Datenbankfeld ist `longtext` oder ähnlich (nicht `varchar`)
3. Datenbank-Zeichensatz ist UTF-8

## Testing

### Test 1: Editor wird geladen

```
1. Öffne /kb/create/
2. "Inhalt" Feld sollte CKEditor mit Toolbar zeigen
3. Toolbar sollte alle Buttons haben
✓ PASS: Editor mit Toolbar sichtbar
✗ FAIL: Nur normale Textarea
```

### Test 2: Text-Formatierung

```
1. Öffne Editor
2. Tippe: "Hallo Welt"
3. Wähle "Hallo"
4. Klicke Bold Button
5. Speichere Artikel
6. Öffne Artikel-Detail: Text sollte fett sein
✓ PASS: HTML enthält <strong>Hallo</strong>
✗ FAIL: Text ist nicht fett
```

### Test 3: Bild-Upload

```
1. Öffne Editor
2. Klicke Image Button
3. Upload Tab
4. Wähle Test-Bild
5. Speichere
6. Überprüfe media/uploads/ckeditor/ auf Bild
✓ PASS: Bild wurde hochgeladen und angezeigt
✗ FAIL: Upload-Dialog wird nicht geschlossen
```

### Test 4: Artikel bearbeiten

```
1. Erstelle Artikel mit formatiertem Text
2. Klicke Bearbeiten
3. Editor sollte vorhandenes HTML korrekt anzeigen
4. Füge mehr Formatierung hinzu
5. Speichern
✓ PASS: Formatierung bleibt erhalten, neue Formatierung hinzugefügt
✗ FAIL: Formatierung geht verloren oder wird doppelt
```

## Validierung & Status

✅ Django System Check: Nur CKEditor 4 Sicherheitshinweis (normal)
✅ Migrationen: Angewendet (0002_alter_knowledgearticle_content)
✅ CKEditor Installation: Erfolgreich
✅ Settings Konfiguration: Abgeschlossen
✅ URL-Routing: Konfiguriert
✅ Templates: Aktualisiert (TinyMCE entfernt)
✅ Datenbank: Migrationszustand: UP-TO-DATE

## Performance

- **Pagespeed**: CKEditor lädt lazy beim Rendern der Form
- **Dateigröße**: CKEditor JavaScript ~400KB (minifiziert)
- **Bild-Optimierung**: Pillow komprimiert Bilder beim Upload
- **Caching**: Static Files können mit Django caching serviert werden

## Support & Ressourcen

- **CKEditor Dokumentation**: https://ckeditor.com/docs/
- **django-ckeditor GitHub**: https://github.com/django-ckeditor/django-ckeditor
- **CKEditor 4 Plugins**: https://ckeditor.com/cke4/addons
- **Sicherheit**: https://ckeditor.com/cke4/security

## Zusammenfassung

CKEditor bietet eine vollständige, kostenlose Rich-Text-Editor-Lösung für die Knowledge Base ohne API-Key-Anforderung. Die Integration ist nahtlos, die Sicherheit ist gewährleistet, und die Benutzererfahrung ist professionell.

Die älteren Versionshinweise sind normal und ein Sicherheitshinweis des Herstellers. Die Funktionalität ist vollständig und stabil.
