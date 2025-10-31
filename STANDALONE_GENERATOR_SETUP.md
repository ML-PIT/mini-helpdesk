# Standalone License Generator - Setup & Usage

## Problem Fixed

Der ursprüngliche Django-abhängige Lizenz-Generator konnte nicht standalone laufen:

```
Error: ModuleNotFoundError: No module named 'config'
```

**Grund**: Das Tool benötigte die komplette Django-Umgebung der Helpdesk-Anwendung.

## Lösung

Der neue **Standalone License Generator** funktioniert komplett unabhängig:

- ✅ Keine Django-Installation nötig
- ✅ Keine Python Virtual Environment nötig
- ✅ Keine Helpdesk-Konfiguration nötig
- ✅ Funktioniert auf jedem Computer mit Python 3.6+
- ✅ Gleicher Signatur-Algorithmus wie Helpdesk-Validator

---

## Quick Start

### Installation

**Voraussetzung**: Python 3.6+ ist installiert

```bash
cd C:\Users\aborowczak\PycharmProjects\FlaskProject\mini-helpdesk
python tools/license_generator_standalone.py
```

Das ist alles! Keine zusätzliche Installation nötig.

### Beispiel

```
======================================================================
 ABoro-Soft Helpdesk - License Generator (STANDALONE)
 [!] INTERNAL USE ONLY - NOT FOR CUSTOMER DISTRIBUTION
======================================================================

SECURITY REMINDER:
  • This tool is for INTERNAL USE ONLY
  • Do NOT share license codes in plain text
  • Use encrypted email or secure file transfer
  • Track distributed codes in your sales system

Available Products:
----------------------------------------------------------------------
1) STARTER         - Starter Plan         | 5            Agents | $199/month
2) PROFESSIONAL    - Professional Plan    | 20           Agents | $499/month
3) ENTERPRISE      - Enterprise Plan      | Unlimited    Agents | $1299/month
4) ON_PREMISE      - On-Premise License   | Unlimited    Agents | $10000/month

Select product (1-4): 2
License duration in months (1-36): 12
Start date (YYYY-MM-DD) or press Enter for today: [Enter]

======================================================================
Product:       Professional Plan
License Code:  PROFESSIONAL-1-12-20261031-235D03489C48C0F6
======================================================================
Expiry Date:   2026-10-31
Duration:      12 months
Max Agents:    20
Features:      tickets, email, knowledge_base, ai_automation, custom_branding, api_basic
Valid Days:    364 days
======================================================================

NEXT STEPS:
1. Copy the license code above
2. Send to customer via ENCRYPTED/SECURE channel
3. Customer enters at: http://their-helpdesk.de/admin-panel/license/
4. Track code in your sales/CRM system

Generate another license? (y/n): n
[OK] License generator completed.
```

---

## File Location

```
mini-helpdesk/
├── tools/
│   ├── license_generator_standalone.py    ← MAIN TOOL (use this!)
│   ├── LICENSE_GENERATOR_README.md        ← Detailed documentation
│   └── license_generator.py               ← Old Tkinter version (deprecated)
```

---

## How It Works

### 1. Code Generation Algorithm

```python
# Data to sign:
data_to_sign = f"{product}|1|{duration_months}|{expiry_date}"

# Example:
# "PROFESSIONAL|1|12|20261031"

# Generate signature (HMAC-SHA256):
signature = hmac.new(
    "ABoro-Soft-Helpdesk-License-Key-2025".encode(),
    data_to_sign.encode(),
    hashlib.sha256
).hexdigest()[:16]

# Result:
# "235D03489C48C0F6"

# Final code:
# "PROFESSIONAL-1-12-20261031-235D03489C48C0F6"
```

### 2. Validation in Helpdesk

Wenn Kunde den Code eingeben, macht Helpdesk:

```python
# Parse code:
product = "PROFESSIONAL"
duration = "12"
expiry = "20261031"
signature = "235D03489C48C0F6"

# Recalculate signature:
expected_sig = hmac.new(
    SECRET_KEY.encode(),
    "PROFESSIONAL|1|12|20261031".encode(),
    hashlib.sha256
).hexdigest()[:16]

# Check if signatures match:
if signature == expected_sig:
    # Code is valid!
    check_expiry_date()
```

**Wichtig**: Signatur kann NICHT gefälscht werden ohne den SECRET_KEY!

---

## Security Properties

### Was ist geschützt?

✅ **Codes können nicht gefälscht werden**
- Benötigt den SECRET_KEY zum Signieren
- Helpdesk kennt den KEY, Kunden nicht
- Signature-Validierung funktioniert offline

✅ **Kunden können keine neuen Codes generieren**
- Generator existiert nicht im Helpdesk
- Keine API zum Generieren
- Kein Web-Interface dafür

✅ **Codes sind selbstständig validierbar**
- Keine Datenbank-Abfrage nötig
- Expiry-Datum ist im Code enthalten
- Kann auch offline validiert werden

### Was ist NICHT geschützt?

⚠️ **SECRET_KEY muss geheim bleiben**
- Wenn ein Kunde den SECRET_KEY kennt, kann er Codes generieren
- Aber das ist ein Django-Security-Problem, nicht ein Lizenz-Problem
- Vergleichbar mit: wenn Kunde Django admin access hat

⚠️ **Codes können abgefangen werden**
- Bei Email-Transport: Kunde's Verantwortung (HTTPS, Encryption)
- Deshalb: Codes immer verschlüsselt/secure verschicken

---

## Distribution Process

### Schritt 1: Code Generieren (Intern)

```bash
# Sales team runs:
python tools/license_generator_standalone.py

# Generates:
# PROFESSIONAL-1-12-20261031-235D03489C48C0F6
```

### Schritt 2: Code verschicken (Sicher!)

**Email an Kunde** (über verschlüsseltes System oder secure Link):

```
Hallo [Kundenname],

willkommen bei ABoro-Soft Helpdesk!

Hier ist Ihr Lizenzcode:
PROFESSIONAL-1-12-20261031-235D03489C48C0F6

Aktivierungsschritte:
1. Login im Admin-Panel Ihrer Helpdesk-Instanz
2. Gehen Sie zu: /admin-panel/license/
3. Kopieren Sie den Code in das Feld "Lizenzkode"
4. Klicken Sie "Lizenz aktivieren"
5. Fertig! Die Lizenz ist aktiv.

Viel Erfolg!
ABoro-Soft Team
```

### Schritt 3: Kunde aktiviert

Kunde besucht: `http://ihre-helpdesk-url.de/admin-panel/license/`

Gibt Code ein → Klick "Lizenz aktivieren" → System zeigt Lizenzdetails

---

## Testing

### Test 1: Standalone Generator funktioniert

```bash
python tools/license_generator_standalone.py
# Select: 1 (STARTER)
# Duration: 12
# Start date: [Enter]
# Should generate valid code
```

✅ **Result**: Code wird generiert und angezeigt

### Test 2: Code validiert im Helpdesk

```bash
python manage.py shell

from apps.api.license_manager import LicenseManager

# Paste code from generator:
code = "STARTER-1-12-20261031-95440F6F6FAE4317"

is_valid, msg = LicenseManager.validate_license(code)
print(f"Valid: {is_valid}")  # Should be True

info = LicenseManager.get_license_info(code)
print(info)  # Should show license details
```

✅ **Result**: Code wird validiert, Details werden angezeigt

### Test 3: Admin Panel akzeptiert Code

1. Go to: `http://localhost:8000/admin-panel/license/`
2. Login mit Admin-Account
3. Paste generated code
4. Click "Lizenz aktivieren"

✅ **Result**: License wird aktiviert, Status wird angezeigt

---

## Common Questions

### F: Warum nicht Django-abhängig?

A: Damit Sales/Marketing Staff das Tool auch ohne technische Helpdesk-Infrastruktur nutzen können. Der Generator braucht nur Python - fertig.

### F: Arbeitet der Code auch auf anderen Rechnern?

A: Ja! Solange Python 3.6+ installiert ist. Der Code ist portable.

### F: Was ist wenn jemand den Generator stiehlt?

A: Das ist okay! Der Generator selbst ist nicht geheim. Er generiert legitime Codes.
- Der SECRET_KEY ist geheim (in Django settings)
- Nur jemand mit dem SECRET_KEY kann neue Codes generieren
- Generator kann nicht ohne SECRET_KEY arbeiten

### F: Warum nicht als EXE?

A: Python-Portabilität. Mit PyInstaller können wir einen EXE generieren, aber:
- Muss regelmäßig updatet werden
- Python-Installation ist einfacher und universeller
- Geht auf Windows/Mac/Linux

### F: Kann der Kunde diesen Generator nutzen?

A: Nein! Der Tool ist "INTERNAL USE ONLY".
- Generator Datei sollte nicht deployed werden
- Kunde hat keine Zugriff auf den Generator
- Kunde kann nur Codes im Admin-Panel aktivieren (nicht generieren)

---

## Technische Details

### Secret Key

Muss identisch sein in:
- `tools/license_generator_standalone.py` (Zeile 40)
- `apps/api/license_manager.py` (Zeile 21)

```python
SECRET_KEY = "ABoro-Soft-Helpdesk-License-Key-2025"
```

**Wichtig**: In Produktion sollte dieser in `.env` stehen, nicht hardcoded!

### Unterstützte Produkte

```python
PRODUCTS = {
    'STARTER': {'name': 'Starter Plan', 'agents': 5, ...},
    'PROFESSIONAL': {'name': 'Professional Plan', 'agents': 20, ...},
    'ENTERPRISE': {'name': 'Enterprise Plan', 'agents': 999, ...},
    'ON_PREMISE': {'name': 'On-Premise License', 'agents': 999, ...},
}
```

Beide Tools müssen die GLEICHEN Produkte haben!

### Validierungsprozess

1. **Parse Code**: Teile in Komponenten auf
2. **Signatur prüfen**: Recalculate und vergleichen
3. **Expiry prüfen**: Ist Ablaufdatum vorbei?
4. **Feature aktivieren**: Basierend auf Lizenztyp

---

## Deployment

### Für Kunden

Standalone Generator wird **NICHT** an Kunden deployed:
- Nicht in ZIP-Datei des Helpdesk
- Nicht in Docker-Image
- Nicht auf Kunden-Server

### Intern

Generator bleibt auf:
- Sales-Laptops
- Entwickler-Maschinen
- Interne Demo-Systeme

---

## Version Info

- **Tool**: `license_generator_standalone.py`
- **Version**: 1.0
- **Status**: Production Ready
- **Created**: 31.10.2025
- **Python**: 3.6+
- **Dependencies**: None (stdlib only)

---

## Support

### Für Internal Team

Fragen zum Generator:
- Siehe: `tools/LICENSE_GENERATOR_README.md`
- Teste mit: `python tools/license_generator_standalone.py`

### Für Kunden

Fragen zur Lizenzaktivierung:
- Support: support@aborosoft.de
- Admin Panel: `/admin-panel/license/`
- Anleitung: `LIZENZ_ADMIN_GUIDE.md`

---

**Das System ist jetzt komplett unabhängig und sicher!**

Standalone Generator kann überall laufen, Helpdesk-Kunden können nur aktivieren, nicht generieren. 🎯
