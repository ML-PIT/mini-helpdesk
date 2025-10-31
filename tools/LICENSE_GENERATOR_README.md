# License Generator - Standalone Tool

## Overview

This is a **completely standalone** license code generator for ABoro-Soft Helpdesk.

**Key Features:**
- ✅ No Django required
- ✅ No Python venv required
- ✅ No database required
- ✅ No Helpdesk environment setup needed
- ✅ Works on ANY machine with Python 3.6+
- ✅ Same signature algorithm as the Helpdesk system

## Usage

### Quick Start

```bash
python license_generator_standalone.py
```

Then follow the interactive prompts:
1. Select product (STARTER, PROFESSIONAL, ENTERPRISE, ON_PREMISE)
2. Enter duration (1-36 months)
3. Enter start date (YYYY-MM-DD) or press Enter for today
4. Get cryptographically signed license code

### Example Session

```
======================================================================
 ABoro-Soft Helpdesk - License Generator (STANDALONE)
 [!] INTERNAL USE ONLY - NOT FOR CUSTOMER DISTRIBUTION
======================================================================

Available Products:
----------------------------------------------------------------------
1) STARTER         - Starter Plan         | 5            Agents | $199/month
2) PROFESSIONAL    - Professional Plan    | 20           Agents | $499/month
3) ENTERPRISE      - Enterprise Plan      | Unlimited    Agents | $1299/month
4) ON_PREMISE      - On-Premise License   | Unlimited    Agents | $10000/month

Select product (1-4): 2
License duration in months (1-36): 12
Start date (YYYY-MM-DD) or press Enter for today:

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
```

## Products

### 1. STARTER
- **Price:** $199/month
- **Max Agents:** 5
- **Features:**
  - Tickets
  - Email
  - Knowledge Base

### 2. PROFESSIONAL (Recommended)
- **Price:** $499/month
- **Max Agents:** 20
- **Features:**
  - All STARTER features
  - AI Automation
  - Custom Branding
  - Basic API

### 3. ENTERPRISE
- **Price:** $1,299/month
- **Max Agents:** Unlimited
- **Features:**
  - All PROFESSIONAL features
  - Full API
  - SSO/LDAP
  - SLA Management

### 4. ON_PREMISE
- **Price:** $10,000 (one-time)
- **Max Agents:** Unlimited
- **Features:**
  - All ENTERPRISE features
  - On-Premise Hosting

## License Code Format

Generated codes have this format:

```
PRODUCT-VERSION-DURATION-EXPIRY-SIGNATURE
```

Example:
```
PROFESSIONAL-1-12-20261031-235D03489C48C0F6
```

Components:
- **PRODUCT:** STARTER, PROFESSIONAL, ENTERPRISE, or ON_PREMISE
- **VERSION:** 1 (current version)
- **DURATION:** Months (1-36)
- **EXPIRY:** YYYYMMDD format (expiration date)
- **SIGNATURE:** HMAC-SHA256 signature (first 16 chars)

## Security

### How It Works

1. License codes contain all information needed for validation
2. Signature is HMAC-SHA256(SECRET_KEY, data_to_sign)
3. Helpdesk validates by recalculating signature
4. No database lookup needed - offline validation possible
5. Cannot be forged without the SECRET_KEY

### Critical

⚠️ **The SECRET_KEY must match between:**
- Generator: `tools/license_generator_standalone.py` line 40
- Helpdesk: `apps/api/license_manager.py` line 21

If they don't match, generated codes won't validate!

```python
# Must be identical in both files:
SECRET_KEY = "ABoro-Soft-Helpdesk-License-Key-2025"
```

## Distribution to Customers

### Step 1: Generate Code
```bash
python license_generator_standalone.py
```

### Step 2: Send Securely
**Email Template:**

```
Hallo [Customer Name],

willkommen bei ABoro-Soft Helpdesk!

Hier ist Ihr Lizenzcode:
PROFESSIONAL-1-12-20261031-235D03489C48C0F6

Aktivierungsschritte:
1. Login im Admin-Panel Ihrer Helpdesk-Instanz
2. Gehen Sie zu: /admin-panel/license/
3. Kopieren Sie den Lizenzcode in das Feld "Lizenzkode"
4. Klicken Sie "Lizenz aktivieren"
5. Fertig! Die Lizenz ist aktiv.

Bei Fragen oder Problemen:
- Email: support@aborosoft.de
- Telefon: +49 (0) XXX-XXXXXX

Viele Grüße,
ABoro-Soft Team
```

### Step 3: Customer Activates
Customer goes to: `http://their-helpdesk.de/admin-panel/license/`

Enters the code and clicks "Lizenz aktivieren"

## Tracking

Always track generated codes in your:
- Sales/CRM system
- Invoice/Billing system
- License register

**Recommended fields:**
- License Code
- Product
- Customer Name
- Start Date
- Expiry Date
- Generated Date
- Sales Representative

## Common Issues

### "ModuleNotFoundError: No module named 'config'"
This happens with the old `license_generator_internal.py`

**Solution:** Use `license_generator_standalone.py` instead - it doesn't need Django!

### License code doesn't validate in Helpdesk
Possible causes:
1. Code was typed incorrectly (check each character)
2. Spaces before/after code (strip whitespace)
3. SECRET_KEY doesn't match (see Security section above)
4. Code is expired (check expiry date)

### "Invalid product" error
Only valid products are:
- STARTER
- PROFESSIONAL
- ENTERPRISE
- ON_PREMISE

(Case-sensitive)

## Development Notes

### Running Standalone vs. With Django

**Standalone (Recommended):**
```bash
python license_generator_standalone.py
```
- Works anywhere
- No dependencies
- No environment setup needed

**With Django (Advanced):**
```bash
cd /path/to/mini-helpdesk
python manage.py shell
from apps.api.license_manager import LicenseManager
code = LicenseManager.generate_license_code('PROFESSIONAL', 12)
print(code)
```

### Signature Algorithm

The signature is calculated as:

```python
import hmac
import hashlib

data_to_sign = f"{product}|1|{duration_months}|{expiry_date}"
signature = hmac.new(
    SECRET_KEY.encode(),
    data_to_sign.encode(),
    hashlib.sha256
).hexdigest()[:16]
```

This is **identical** between generator and Helpdesk validator.

### Extending Products

To add new products, edit the PRODUCTS dict in both:
1. `tools/license_generator_standalone.py` (around line 43)
2. `apps/api/license_manager.py` (around line 24)

They **must be identical** to work correctly!

## Support

### Internal Team
- Check this README first
- Verify SECRET_KEY matches
- Test with Helpdesk admin panel

### Customers
- Direct to: support@aborosoft.de
- Send license via secure channel
- Provide activation instructions

## Files

- `license_generator_standalone.py` - Main tool (use this!)
- `LICENSE_GENERATOR_README.md` - This file
- `../apps/api/license_manager.py` - Helpdesk validator

## Version

**Standalone License Generator v1.0**
Created: 31.10.2025
Status: Production Ready
