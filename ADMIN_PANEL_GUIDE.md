# Admin Panel - Benutzerhandbuch

## Übersicht

Das Admin Panel ist eine umfassende Verwaltungsschnittstelle für das Helpdesk-System. Administratoren können hier alle Systemkonfigurationen, E-Mail-Einstellungen, Berechtigungen und mehr verwalten.

## Zugriff auf das Admin Panel

1. Melden Sie sich als Administrator an
2. Klicken Sie auf "Admin Panel" im Navigationsmenü
3. URL: `http://your-site.com/admin-panel/`

## Hauptfunktionen

### 1. 📧 E-Mail-Konfiguration

#### SMTP-Einstellungen (Outgoing Email)
Konfigurieren Sie den SMTP-Server für ausgehende E-Mails:

- **SMTP Host**: z.B. `smtp.office365.com`, `smtp.gmail.com`
- **SMTP Port**: Standard 587 (TLS) oder 465 (SSL)
- **SMTP Username**: E-Mail-Adresse des SMTP-Kontos
- **SMTP Password**: Passwort des SMTP-Kontos
- **Verschlüsselung**: TLS oder SSL auswählen

**Beispiele:**
- **Office 365**: smtp.office365.com:587 (TLS)
- **Gmail**: smtp.gmail.com:587 (TLS)
- **Outlook**: smtp-mail.outlook.com:587 (TLS)

**E-Mail Test:** Klicken Sie auf "🧪 E-Mail Test", um eine Test-E-Mail an eine beliebige Adresse zu senden.

#### IMAP-Einstellungen (Incoming Email)
Aktivieren Sie IMAP, um E-Mails automatisch aus Ihrem Postfach zu lesen:

- **IMAP aktivieren**: Checkbox zum Aktivieren von IMAP
- **IMAP Host**: z.B. `outlook.office365.com`
- **IMAP Port**: Standard 993 (SSL)
- **IMAP Username**: E-Mail-Adresse des IMAP-Kontos
- **IMAP Password**: Passwort des IMAP-Kontos
- **Postfach-Ordner**: z.B. `INBOX`, `Tickets`, etc.

**IMAP Test:** Klicken Sie auf "🧪 IMAP Test", um die Verbindung zu testen oder die letzten 5 E-Mails zu abrufen.

#### E-Mail Benachrichtigungen
- **E-Mail Benachrichtigungen aktivieren**: E-Mails für wichtige Ereignisse senden
- **E-Mail Signatur**: Automatische Signatur für alle ausgehenden E-Mails

---

### 2. 🎨 Branding & Erscheinungsbild

Passen Sie das Erscheinungsbild der Anwendung an:

#### Logo
- **Logo hochladen**: Company-Logo (empfohlen: 200x50px, max 2MB)
- Unterstützte Formate: PNG, JPG, GIF, WebP
- Das Logo wird in der Navigationsleiste angezeigt

#### Branding-Texte
- **Applikationsname**: Name in der Navigationsleiste (z.B. "ABoro-Soft Helpdesk")
- **Unternehmensname**: Name des Unternehmens
- **Website URL**: Basis-URL für E-Mail-Links (z.B. https://example.com)

---

### 3. ✏️ Rich-Text Editor

Wählen Sie den Text-Editor für die gesamte Anwendung:

#### TinyMCE
- **Vorteile**: Leichtgewichtig, schnell, einfach zu bedienen
- **Funktionen**: Bold, Italic, Überschriften, Linklisten
- **Best für**: Schnelle Bearbeitung, einfache Formatierung

#### CKEditor
- **Vorteile**: Umfangreichere Funktionen, mehr Formatierungsoptionen
- **Funktionen**: Erweiterte Formatierung, Tabellen, Code-Blöcke
- **Best für**: Professionelle Inhalte, komplexere Formatierung

**Verwendung in Templates:**
```django
{% load admin_tags %}

<!-- Automatische Editor-Integration -->
{{ form.description }}

<!-- Oder mit Template Tag -->
{% render_editor 'field_name' content_text %}
```

---

### 4. 🔒 Berechtigungen für Statistiken

Steuern Sie, welche Benutzerrollen Zugriff auf Statistiken haben:

- **Administrator**: Alle Statistiken anzeigen (standard: aktiviert)
- **Support Agent**: Statistiken anzeigen (standard: deaktiviert)
- **Customer**: Eigene Statistiken anzeigen (standard: deaktiviert)

Diese Einstellungen werden global für alle Statistik-Seiten angewendet.

---

### 5. 📁 Datei-Upload Einstellungen

Verwalten Sie Datei-Upload-Optionen:

#### Maximale Dateigröße
- **Max. Upload Size**: Standard 16MB
- Gilt für alle Datei-Uploads (Tickets, Wissensbase, etc.)

#### Erlaubte Dateitypen
- PDF-Dateien
- Bilder (JPG, PNG, GIF)
- Word-Dokumente (DOC, DOCX)
- ZIP Archive

**Hinweis**: Jede unterstützte Dateitype wird validiert, bevor sie akzeptiert wird.

---

### 6. ⚙️ System-Einstellungen

#### Zeitzone
- Standard: `Europe/Berlin`
- Auswirkung: Datum/Zeit-Anzeige überall in der Anwendung
- Format: `Continent/City` (z.B. `America/New_York`, `Asia/Tokyo`)

#### Sprache
- **Deutsch** (de)
- **Englisch** (en)
- Auswirkung: Sprachauswahl für UI und E-Mails

---

## Datei-Upload-API

### Für Entwickler

Die Anwendung bietet zwei API-Endpunkte für Datei-Uploads:

#### 1. Allgemeiner Datei-Upload
```
POST /admin-panel/api/upload-file/
Content-Type: multipart/form-data

Parameters:
- file: File to upload
- upload_type: 'ticket_attachment', 'knowledge_attachment', 'logo', etc.
```

**Antwort:**
```json
{
    "success": true,
    "file_name": "tickets/attachments/document.pdf",
    "file_url": "/media/tickets/attachments/document.pdf",
    "file_size": "2.50MB",
    "message": "File uploaded successfully"
}
```

#### 2. Bild-Upload für Editor
```
POST /admin-panel/api/upload-image/
Content-Type: multipart/form-data

Parameters:
- upload: Image file
```

**Antwort (CKEditor-kompatibel):**
```json
{
    "uploaded": true,
    "url": "/media/editor_images/image.png"
}
```

### Verwendung in JavaScript

```javascript
// Datei-Upload mit Fetch
async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('upload_type', 'ticket_attachment');

    const response = await fetch('/admin-panel/api/upload-file/', {
        method: 'POST',
        body: formData
    });

    const data = await response.json();
    if (data.success) {
        console.log('Datei-URL:', data.file_url);
    }
}

// Verwendung
const fileInput = document.querySelector('input[type="file"]');
fileInput.addEventListener('change', (e) => {
    uploadFile(e.target.files[0]);
});
```

---

## Editor-Integration in Templates

### Methode 1: Form Widgets (einfach)
```django
<!-- In Django Forms automatisch -->
{% load admin_tags %}
<form method="post">
    {% csrf_token %}
    {{ form.description }}  <!-- Wird automatisch mit richtigem Editor gerendert -->
    <button type="submit">Speichern</button>
</form>
```

### Methode 2: Template Tags (flexibel)
```django
{% load admin_tags %}

<!-- Automatischer Editor basierend auf Einstellungen -->
{% render_editor 'description' my_content %}

<!-- Mit benutzerdefiniertem CSS -->
{% render_editor 'description' my_content css_class='custom-class' %}

<!-- Aktiven Editor-Typ abrufen -->
{{ get_editor_type }}  <!-- Gibt 'tinymce' oder 'ckeditor' zurück -->
```

### Methode 3: Direkt in HTML (für spezielle Fälle)
```html
<!-- TinyMCE Editor -->
<textarea class="tinymce-editor" name="content"></textarea>

<!-- CKEditor -->
<textarea class="ckeditor-editor" name="content"></textarea>
```

---

## Audit-Log

Das Admin-Panel protokolliert alle Änderungen:

### Gespeicherte Informationen
- **Aktion**: Erstellt, Aktualisiert, Gelöscht, E-Mail versendet, Datei hochgeladen
- **Benutzer**: Wer die Aktion durchgeführt hat
- **Beschreibung**: Was geändert wurde
- **Alte Werte**: Vorherige Konfiguration
- **Neue Werte**: Neue Konfiguration
- **IP-Adresse**: Aus welcher IP-Adresse die Aktion kam
- **Zeit**: Wann die Aktion durchgeführt wurde

### Zugriff auf Audit-Logs
1. Navigieren Sie zu "Audit Logs" im Admin Panel
2. Filtern Sie nach Aktion oder Benutzer
3. Klicken Sie auf "Details anzeigen" für alte/neue Werte

---

## Sicherheit

### Best Practices
1. **Passwörter**: E-Mail-Passwörter werden verschlüsselt gespeichert
2. **Datei-Uploads**: Alle Dateien werden validiert (Größe, Typ, Inhalt)
3. **Audit Trail**: Alle Änderungen werden protokolliert
4. **Berechtigungen**: Nur Administratoren können auf dieses Panel zugreifen

### Verschlüsselte Felder
Folgende Felder werden mit ROT13-Verschlüsselung gespeichert:
- SMTP-Passwort
- IMAP-Passwort

**Hinweis**: Für Production sollten Sie stärkere Verschlüsselung verwenden!

---

## Häufig Gestellte Fragen (FAQ)

**F: Ich kann keine E-Mail senden, was sollte ich prüfen?**
A:
1. Überprüfen Sie SMTP-Einstellungen (Host, Port, Username, Password)
2. Verwenden Sie den "E-Mail Test" Button
3. Prüfen Sie Firewall/Antivirus Einstellungen
4. Überprüfen Sie E-Mail Account 2FA Einstellungen

**F: IMAP funktioniert nicht, obwohl SMTP funktioniert**
A:
1. Verschiedene Zugangsdaten können erforderlich sein
2. Überprüfen Sie den IMAP-Host (unterschied von SMTP-Host)
3. Manche E-Mail-Provider erfordern App-Passwörter für IMAP
4. Verwenden Sie den "IMAP Test" Button

**F: Wie ändere ich den Text-Editor nach der Installation?**
A:
1. Gehen Sie zu "Admin Panel" > "System Einstellungen"
2. Wählen Sie den Tab "✏️ Editor"
3. Wählen Sie TinyMCE oder CKEditor
4. Klicken Sie "💾 Speichern"

**F: Können Kunden und Support Agents Dateien hochladen?**
A:
Ja! Aktivieren Sie die Datei-Upload-Funktion in den Einstellungen:
1. Tab: "📁 Datei-Upload"
2. Wählen Sie erlaubte Dateitypen
3. Setzen Sie maximale Dateigröße
4. "💾 Speichern"

---

## Technische Details

### Dateistruktur
```
apps/admin_panel/
├── models.py              # SystemSettings und AuditLog Modelle
├── views.py              # Admin-Views und Formular-Verarbeitung
├── forms.py              # Django Forms für Settings
├── urls.py               # URL-Routing
├── file_handler.py       # Datei-Upload Validierung
├── file_upload_api.py    # API-Endpunkte für Uploads
├── context_processors.py # Template-Kontext-Prozessoren
├── admin.py              # Django Admin Integration
└── templatetags/
    └── admin_tags.py     # Custom Template Tags
```

### Umgebungsvariablen

Die Standard-Einstellungen werden aus `.env` geladen, können aber im Admin Panel überschrieben werden:

```bash
# SMTP
SMTP_HOST=smtp.office365.com
SMTP_PORT=587
EMAIL_USERNAME=your-email@example.com
EMAIL_PASSWORD=your-password

# IMAP
EMAIL_HOST=outlook.office365.com
EMAIL_PORT=993

# Branding
APP_NAME=My Helpdesk
COMPANY_NAME=My Company
LOGO_URL=/static/images/logo.png
SITE_URL=https://example.com

# Editor
TEXT_EDITOR=tinymce  # or ckeditor

# System
LANGUAGE_CODE=de
TIME_ZONE=Europe/Berlin
```

---

## Support & Troubleshooting

### Probleme und Lösungen

**Problem: Admin Panel ist nicht zugänglich**
- Überprüfen Sie, ob Sie als Administrator angemeldet sind
- Überprüfen Sie die URL: `/admin-panel/`
- Prüfen Sie in der Django Admin die App-Registrierung

**Problem: Datei-Uploads funktionieren nicht**
- Überprüfen Sie die MEDIA_ROOT Verzeichnisberechtigungen
- Überprüfen Sie die konfigurierte Dateigröße
- Überprüfen Sie die erlaubten Dateitypen

**Problem: E-Mail-Tests schlagen fehl**
- Verwenden Sie einen E-Mail-Debugger (z.B. Mailtrap)
- Prüfen Sie ob TLS/SSL korrekt ist
- Prüfen Sie Firewall-Einstellungen

---

## Version & Änderungsverlauf

**Version**: 1.0.0
**Veröffentlicht**: 2025-10-31

### Features in 1.0.0
- ✅ Vollständige SMTP/IMAP-Konfiguration
- ✅ Branding & Logo Management
- ✅ Rich-Text Editor Auswahl (TinyMCE/CKEditor)
- ✅ Berechtigungsverwaltung für Statistiken
- ✅ Datei-Upload Konfiguration
- ✅ System-Einstellungen (Sprache, Zeitzone)
- ✅ Audit-Logging für alle Änderungen
- ✅ File Upload APIs für Entwickler
- ✅ Template Tags für Template-Integration

---

## Lizenz & Copyright

© 2025 ABoro-Soft. Alle Rechte vorbehalten.
