# ABoro-Soft Helpdesk - Lizenzverwaltung im Admin Panel

## 🔑 Lizenzcode im Admin Panel eingeben

Die Lizenzverwaltung ist jetzt direkt im Admin Panel erreichbar!

### Zugriff

**URL**: `http://localhost:8000/admin-panel/license/`

Oder über das Admin Panel Dashboard:
1. Login mit Admin-Account
2. Menü → Lizenzverwaltung
3. Lizenzcode eingeben

---

## 📋 Lizenzcodes - Beispiele

Hier sind gültige Lizenzcodes zum Testen:

### STARTER (€199/Monat)
```
STARTER-1-12-20261031-038357A3F9C143BA
```
- 5 Support Agenten
- Gültig bis: 31.10.2026 (364 Tage)

### PROFESSIONAL (€499/Monat)
```
PROFESSIONAL-1-12-20261031-235D03489C48C0F6
```
- 20 Support Agenten
- Gültig bis: 31.10.2026 (364 Tage)
- KI-Automation aktiviert

### ENTERPRISE (€1,299/Monat)
```
ENTERPRISE-1-12-20261031-AEBDB402E807D20E
```
- Unbegrenzte Agenten
- Gültig bis: 31.10.2026 (364 Tage)
- Alle Features aktiviert

### ON_PREMISE (€10,000 einmalig)
```
ON_PREMISE-1-12-20261031-2F93F10A02C5BCCD
```
- Unbegrenzte Agenten
- Gültig bis: 31.10.2026 (364 Tage)

---

## 🎯 So funktioniert's

### Schritt 1: Admin Panel öffnen
```
http://localhost:8000/admin-panel/license/
```

### Schritt 2: Lizenzcode eingeben
1. Kopieren Sie einen der obigen Lizenzcodes
2. Fügen Sie ihn in das Feld "Lizenzkode" ein
3. Klicken Sie auf "Lizenz aktivieren"

### Schritt 3: Bestätigung
Sie sehen dann:
- ✅ Erfolgsmeldung
- 📊 Lizenzdetails (Produkt, Gültigkeitsdatum, Features)
- 🔒 Lizenzstatus (gültig/ungültig)
- 📈 Maximale Anzahl Agenten

---

## 📊 Lizenzinformationen

Nach der Aktivierung sehen Sie im Admin Panel:

| Feld | Beispiel | Bedeutung |
|------|----------|-----------|
| **Produkt** | PROFESSIONAL | Lizenztyp (Starter, Professional, Enterprise, On-Premise) |
| **Gültig bis** | 31.10.2026 | Ablaufdatum der Lizenz |
| **Tage verbleibend** | 364 Tage | Wie lange die Lizenz noch gültig ist |
| **Max. Agenten** | 20 | Maximale Anzahl von Support Agents |
| **Features** | tickets, email, ... | Aktivierte Funktionen |

---

## 🔐 Lizenzcode Format

Ein ABoro-Soft Lizenzkode hat das Format:

```
PRODUKT-VERSION-DAUER-VERFALLSDATUM-SIGNATUR
STARTER-1-12-20261031-038357A3F9C143BA
```

Komponenten:
- **PRODUKT**: STARTER, PROFESSIONAL, ENTERPRISE, ON_PREMISE
- **VERSION**: 1 (aktuelle Verslon)
- **DAUER**: 12 (Gültig für 12 Monate)
- **VERFALLSDATUM**: 20261031 (Format: YYYYMMDD)
- **SIGNATUR**: 038357A3F9C143BA (Kryptographische Signatur für Authentizität)

---

## 🛠️ Neuen Lizenzcode generieren

### Für Sales/Admin: Desktop-Tool

```bash
python tools/license_generator.py
```

Dann:
1. Produkt wählen (z.B. PROFESSIONAL)
2. Dauer eingeben (z.B. 12 Monate)
3. "Generate License Code" klicken
4. Code kopieren
5. Im Admin Panel eingeben

### Mit Python-Code

```python
from apps.api.license_manager import LicenseManager

# Neuen Code generieren
code = LicenseManager.generate_license_code('PROFESSIONAL', 12)
print(f"Generierter Code: {code}")

# Validieren
is_valid, msg = LicenseManager.validate_license(code)
print(f"Gültig: {is_valid} - {msg}")

# Infos abrufen
info = LicenseManager.get_license_info(code)
print(f"Produkt: {info['product_name']}")
print(f"Gültig bis: {info['expiry_date']}")
print(f"Features: {info['features']}")
```

---

## 📧 Lizenzcode an Kunden senden

Nach der Generierung:

1. **Email an Kunde**:
   ```
   Hallo [Kundenname],

   willkommen bei ABoro-Soft Helpdesk!

   Hier ist Ihr Lizenzcode:
   PROFESSIONAL-1-12-20261031-235D03489C48C0F6

   Aktivierungsschritte:
   1. Gehen Sie zu: https://helpdesk.aborosoft.de/admin-panel/license/
   2. Login mit Admin-Account
   3. Fügen Sie den Code in das Feld ein
   4. Klicken Sie "Lizenz aktivieren"

   Bei Fragen: support@aborosoft.de

   Viele Grüße,
   ABoro-Soft Team
   ```

2. **Desktop Client Download**:
   - Link: `https://helpdesk.aborosoft.de/downloads/desktop-client.zip`
   - Anleitung: README.md in der ZIP-Datei

---

## ⚠️ Häufige Fehler und Lösungen

### "Invalid license code"
- Stellen Sie sicher, dass der Code vollständig ist (keine Zeichen fehlen)
- Überprüfen Sie, dass keine Leerzeichen am Anfang/Ende sind
- Der Code ist kryptographisch signiert - jeder Buchstabe muss korrekt sein

### "License has expired"
- Das Ablaufdatum ist vorbei
- Generieren Sie einen neuen Code mit aktuellem Datum
- Oder verlängern Sie das Abonnement

### "License validation error"
- Möglicherweise wurde der Code manipuliert
- Generieren Sie einen neuen Code
- Kontaktieren Sie den technischen Support

---

## 🔄 Lizenz erneuern

Wenn die Lizenz abläuft:

1. **Neuen Code generieren**:
   ```bash
   python tools/license_generator.py
   # oder per Python API
   ```

2. **Im Admin Panel aktualisieren**:
   - Alte Code wird überschrieben
   - Neue Gültigkeitsdauer wird gespeichert
   - Alle Features werden neu aktiviert

3. **Kunden benachrichtigen**:
   - Email mit neuem Code senden
   - Aktivierungsanleitung beifügen

---

## 📊 Lizenzstatus in der Datenbank

Alle Lizenzinformationen werden gespeichert unter:
- **Modell**: `SystemSettings`
- **Tabelle**: `admin_panel_systemsettings`
- **Felder**:
  - `license_code`: Der Lizenzcode
  - `license_product`: Produkttyp
  - `license_expiry_date`: Ablaufdatum
  - `license_max_agents`: Max. Agenten
  - `license_features`: Aktivierte Features (JSON)
  - `license_valid`: Gültig ja/nein
  - `license_last_validated`: Letzte Validierung

---

## 🔍 Audit-Log

Alle Lizenzverwaltungs-Aktionen werden geloggt:

**Zu sehen unter**: http://localhost:8000/admin-panel/audit-logs/

Einträge:
- Lizenzcode aktualisiert
- Alte und neue Werte
- Benutzer der Änderung vorgenommen hat
- Timestamp
- IP-Adresse

---

## 💡 Best Practices

### Für Admins:
1. ✅ Regelmäßig Lizenzen überprüfen (Ablaufdatum)
2. ✅ Alarm-Email 30 Tage vor Ablauf einrichten
3. ✅ Audit-Logs regelmäßig prüfen
4. ✅ Lizenzcode nicht in Logs/Mails speichern (nur Anfang/Ende zeigen)

### Für Sales:
1. ✅ Lizenzcodes in CRM-System tracken
2. ✅ Rechnungen mit Lizenzcodes verknüpfen
3. ✅ Kundenspezifische Dauer mit Codes matchen
4. ✅ Erneuerungen 30 Tage voraus planen

### Für Support:
1. ✅ Kunden beim Code-Setup helfen
2. ✅ Ungültige Codes schnell erkennen und melden
3. ✅ Kurze Aktivierungsanleitung haben

---

## 📞 Support

Falls Fragen zur Lizenzverwaltung:

- **Technical Support**: support@aborosoft.de
- **Sales Questions**: sales@aborosoft.de
- **Admin Panel Issues**: admin@aborosoft.de

---

## 🎓 Weitere Ressourcen

- **Lizenz-Dokumentation**: `docs/LICENSE_GUIDE.md`
- **Desktop-Client**: `desktop_client/support_agent_app.py`
- **API-Dokumentation**: `docs/IMPLEMENTATION_SUMMARY.md`
- **Sales-Materials**: `SALES_PITCH.md`

---

**Stand**: 31.10.2025
**Version**: 1.0
**Status**: ✅ Produktionsbereit

*"Professioneller Support ohne die professionellen Preise"* 💪
