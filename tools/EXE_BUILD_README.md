# Building & Distributing License Generator EXE

## Overview

Mit `build_exe.py` kann man einen **standalone Windows .exe** bauen, den man ohne Python-Installation verteilen kann!

### Was ist das?

- **Standalone EXE**: Funktioniert auf jedem Windows-PC ohne Python
- **Keine Abhängigkeiten**: Alles enthalten (HTTP-Server, UI, etc.)
- **Einfache Verteilung**: Nur den `dist` Ordner kopieren
- **Professionell**: Sieht aus wie eine normale Windows-App

---

## Build-Prozess

### Voraussetzungen

```bash
# 1. PyInstaller installieren
pip install PyInstaller

# 2. Sicherstellen, dass license_generator_gui.py existiert
cd tools/
```

### EXE bauen

```bash
python build_exe.py
```

### Output

```
======================================================================
 Building license_generator.exe with PyInstaller
======================================================================

[OK] PyInstaller 6.14.2 found

[*] Cleaning up old builds...
[!] Icon not found, skipping (using default)

[*] Building executable...
[OK] Build successful!

[OK] EXE created: dist\license_generator.exe
    Size: 7.5 MB

[OK] Created launcher: start_license_generator.bat

======================================================================
 BUILD COMPLETE!
======================================================================

Executable location: dist/license_generator.exe
```

---

## Dateien nach dem Build

```
tools/
├── build_exe.py                          (Build-Script)
├── dist/
│   ├── license_generator.exe             (Main EXE - 7.5 MB)
│   ├── _internal/                        (Support files - auto created)
│   └── ...
├── start_license_generator.bat           (Quick launcher)
└── license_generator.spec                (PyInstaller config)
```

---

## Verwendung

### Option 1: Direkt ausführen

```bash
# Windows:
dist\license_generator.exe

# Oder doppelklick:
# dist/license_generator.exe
```

Dann:
1. Browser öffnet sich automatisch
2. http://localhost:5000 lädt
3. Lizenz generieren
4. Fertig!

### Option 2: Mit Batch-Launcher

```bash
start_license_generator.bat
```

**Oder**: Erstelle einen Desktop-Shortcut
1. Right-click auf `license_generator.exe`
2. "Create Shortcut"
3. Verschiebe auf Desktop
4. Doppelklick zum Starten

---

## Für das Sales-Team verteilen

### Schritt 1: EXE bauen
```bash
cd tools
python build_exe.py
```

### Schritt 2: Folder vorbereiten
```
license_generator/
├── license_generator.exe
├── start_license_generator.bat
└── README.txt (optional - kurze Anleitung)
```

### Schritt 3: Verteilen
- **Per Email**: ZIP file mit `dist` folder
- **USB Stick**: Copy `dist` folder
- **Network Share**: Share the folder
- **Cloud**: Upload to Google Drive, OneDrive, etc.

### Schritt 4: Installation auf Sales-PC
```
1. Download ZIP
2. Extract
3. Doppelklick: license_generator.exe
4. Browser öffnet sich
5. Done!
```

---

## README für Sales-Team

Erstelle diese Datei: `dist/README.txt`

```
======================================================================
  ABoro-Soft License Generator
======================================================================

EINFACH ZU NUTZEN:

1. Doppelklick auf: license_generator.exe

2. Browser öffnet sich

3. Lizenz generieren:
   - Produkt wählen (z.B. PROFESSIONAL)
   - Dauer eingeben (z.B. 12 Monate)
   - Klick auf "Generate License"

4. Code an Kunde senden:
   - Klick auf "Copy Code"
   - In Email einfügen
   - Senden!

======================================================================

ANFORDERUNGEN:
- Windows 7 oder neuer
- Internetbrowser (Chrome, Firefox, Edge, etc.)
- Keine weitere Installation nötig!

PROBLEME?

1. "Port 5000 already in use"
   - Schließe andere Fenster/Program mit port 5000
   - oder warte 5 Minuten und versuche erneut

2. Browser öffnet nicht
   - Gehe manuell zu: http://localhost:5000/

3. Server läuft, aber Fehler beim Generieren
   - Schließe und starte erneut
   - Überprüfe Internetverbindung

SUPPORT: support@aborosoft.de

======================================================================
```

---

## Größe & Performance

| Aspekt | Wert |
|--------|------|
| **EXE Größe** | 7.5 MB |
| **Startzeit** | 2-3 Sekunden |
| **RAM Usage** | ~50-80 MB |
| **Disk Required** | ~100 MB (mit internals) |
| **Windows Versions** | 7+ (auch 11, Server, etc.) |
| **Architecture** | x86-64 (64-bit) |

---

## Customization

### Icon ändern

1. Erstelle ein `.ico` file (256x256 pixels)
2. Speichere als: `tools/license_generator.ico`
3. Baue neu: `python build_exe.py`

Wenn `license_generator.ico` existiert, wird es automatisch verwendet.

### Größe reduzieren (optional)

In `build_exe.py` ändern:
```python
cmd = [
    'pyinstaller',
    '--name', PROJECT_NAME,
    '--onefile',
    '--windowed',
    '--strip',  # Add this line
    # ...
]
```

Das reduziert Größe um ~20%, aber exe lädt langsamer.

### Dateiname ändern

In `build_exe.py`:
```python
PROJECT_NAME = "ABoro-License-Generator"  # Ändere Namen hier
```

Dann `python build_exe.py` erneut ausführen.

---

## Advanced: Multi-User Setup

### Shared Network Version

```
# Auf Fileserver:
\\fileserver\tools\license_generator.exe

# Sales-Team erstellt Shortcut:
1. Right-click auf network path
2. "Create Link"
3. Desktop oder Startmenu
4. Klick => EXE lädt vom Server
```

### IT Installation

```batch
REM For IT Admins: Deploy via Group Policy
REM Store in: \\fileserver\apps\license_generator.exe

rem Deploy to all sales PCs:
rem Use GPO or imaging solution
```

---

## Sicherheit

### Was ist im EXE?

- ✅ Alle Python Runtime Files (7.0 MB)
- ✅ HTTP Server
- ✅ HTML/CSS/JavaScript GUI
- ✅ License Manager Logic
- ✅ Standard Library

### Was IST NICHT drin?

- ❌ Keine Django Abhängigkeiten
- ❌ Keine externen Packages
- ❌ Keine Datenbankverbindung
- ❌ Keine Internet-Connection nötig

### Sicherheits-Notes

- EXE läuft auf `127.0.0.1:5000` (local only)
- Browser-nur Zugriff (kein Remote-Zugriff ohne Konfiguration)
- HMAC-SHA256 Signatur-Validierung
- Keine Lizenzcodes gespeichert

---

## Troubleshooting

### "license_generator.exe wurde nicht gefunden"

```
Lösung 1: Überprüfe den Pfad
  cd tools/dist/
  license_generator.exe

Lösung 2: Starte von tools/ ordner
  cd tools
  dist/license_generator.exe
```

### "Die Anwendung konnte nicht gestartet werden"

```
Das bedeutet wahrscheinlich:
- Windows Defender hat exe geblockt
  -> Whitelist in Windows Defender
  -> oder: Run Anyway klicken

- .NET Framework fehlt?
  -> Nein! (wird nicht benötigt)

- Versuch neuesten Build:
  -> python build_exe.py
```

### "Port 5000 in Verwendung"

```
Port ist schon belegt.

Lösung 1: Warte 2-3 Minuten
Lösung 2: Schließe alle Browser-Tabs
Lösung 3: Starte PC neu
```

### Browser öffnet nicht automatisch

```
Manuelle Lösung:
1. Öffne Browser (Chrome, Firefox, etc.)
2. Gehe zu: http://localhost:5000/
3. Fertig!
```

---

## Update & Rebuild

### Wenn license_generator_gui.py aktualisiert wurde

```bash
# 1. Gehe zu tools/
cd tools

# 2. Lösche alten Build
rm -r dist build *.spec

# 3. Baue neu
python build_exe.py

# 4. Verteile neue EXE
```

### Version-Management

```
In build_exe.py ändern:
PROJECT_NAME = "license_generator_v2"

So kannst du verschiedene Versionen distribuieren:
- license_generator_v1.exe (old)
- license_generator_v2.exe (current)
- etc.
```

---

## CI/CD Integration

### Automatischer Build (Optional)

Erstelle `tools/build.sh`:
```bash
#!/bin/bash
cd "$(dirname "$0")"
python build_exe.py

# Upload to cloud
# aws s3 cp dist/license_generator.exe s3://bucket/tools/
# or similar
```

### GitHub Actions (Advanced)

```yaml
name: Build EXE
on: [push]
jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install PyInstaller
      - run: cd tools && python build_exe.py
      - uses: actions/upload-artifact@v2
        with:
          name: license_generator.exe
          path: tools/dist/license_generator.exe
```

---

## Verteilung Checkliste

- [ ] EXE gebaut: `python build_exe.py`
- [ ] EXE getestet: doppelklick und Browser öffnet sich
- [ ] Größe akzeptabel: 7.5 MB
- [ ] README für Sales-Team erstellt
- [ ] Launcher Batch-File included
- [ ] ZIP gepackt für Email-Versand
- [ ] Versionsnummer dokumentiert
- [ ] Upload-Pfad bekannt (Google Drive, etc.)
- [ ] Sales-Team informiert
- [ ] Support-Contact bereitgestellt

---

## Best Practices

### Für Sales-Team

1. **Einfach halten**
   - Nur EXE verteilen
   - Batch-Launcher optional
   - README.txt mitnehmen

2. **Support vorbereiten**
   - FAQ-Dokument
   - Support-Email/Phone
   - Remote-Access für Hilfe

3. **Versioning**
   - EXE mit Datum benennen: `license_gen_20251031.exe`
   - Alte Versionen archivieren
   - Updates kommunizieren

### Für IT

1. **Deployment**
   - Network Share statt USB
   - Shortcuts statt Copy-Paste
   - Updates zentral verwalten

2. **Sicherheit**
   - Firewall: Allow 127.0.0.1:5000 (local)
   - No changes to antivirus rules needed
   - EXE Code-signed? (optional, für Enterprises)

3. **Monitoring**
   - Server läuft auf localhost - kein Monitoring nötig
   - Pro User: eigener Process
   - Kein Datenverlust - alles ephemeral

---

## Größenvergleich

| Tool | Größe | Abhängigkeiten |
|------|-------|-----------------|
| EXE (PyInstaller) | 7.5 MB | None |
| Python + GUI | ~100 MB | Python 3.9+ |
| Docker Image | ~500 MB | Docker |
| Web-Server Deploy | 1-2 GB | Full stack |

**EXE ist der beste Weg für Offline-Distribution!**

---

## Version

**EXE Build Tool v1.0**
Created: 31.10.2025
Status: Production Ready

---

**Ready to distribute!** 🚀

Nächste Schritte:
1. `python build_exe.py` ausführen
2. `dist/license_generator.exe` testen
3. Zu Kunden/Team verteilen
4. Erfolgreich! ✅
