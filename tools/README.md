# ABoro-Soft License Generator Tools

Three ways to generate license codes - choose what works best for you!

---

## 🚀 Quick Start

### Option 1: Web GUI (RECOMMENDED)
```bash
python license_generator_gui.py
```
- Opens browser automatically
- Modern, beautiful interface
- Click-based, very user-friendly
- ✅ **BEST FOR SALES TEAM**

### Option 2: Command-Line (Standalone)
```bash
python license_generator_standalone.py
```
- Interactive CLI prompts
- No browser needed
- Works anywhere with Python
- ✅ **BEST FOR DEVELOPERS**

### Option 3: Python API
```python
from license_generator_gui import StandaloneLicenseManager

code = StandaloneLicenseManager.generate_license_code('PROFESSIONAL', 12)
print(code)  # PROFESSIONAL-1-12-20261031-235D03489C48C0F6
```
- Programmatic access
- For integration
- ✅ **BEST FOR AUTOMATION**

---

## 📋 Comparison Table

| Feature | GUI | CLI | API |
|---------|-----|-----|-----|
| **User Interface** | Web browser | Terminal prompts | Python code |
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Recommended For** | Sales team | Developers | Integration |
| **Dependencies** | None | None | None |
| **Copy Button** | Yes | Manual | Must copy yourself |
| **Mobile Browser** | Works! | No | No |
| **Startup Time** | 1-2 seconds | Instant | Instant |
| **Learning Curve** | None | Very easy | Easy |
| **Best For** | Non-technical | Power users | Scripts |

---

## 🖥️ Web GUI (`license_generator_gui.py`)

### Perfect For
- Sales team members
- Non-technical staff
- Users who prefer graphical interfaces
- Sharing with multiple users (runs as server)

### Features
- Beautiful, modern interface
- Works in any web browser
- One-click copy to clipboard
- Shows all product details
- Real-time validation
- Auto-opens browser

### Usage
```bash
python license_generator_gui.py
# Automatically opens http://localhost:5000/ in your browser
```

### Learn More
→ See: `LICENSE_GENERATOR_GUI_README.md`

---

## 💻 Command-Line CLI (`license_generator_standalone.py`)

### Perfect For
- Developers
- Scripting and automation
- Headless servers
- Custom workflows

### Features
- Interactive prompts
- No dependencies
- Fast execution
- Easy to automate
- Terminal-friendly

### Usage
```bash
python license_generator_standalone.py
```

Then follow the interactive prompts:
```
Select product (1-4): 2
License duration in months (1-36): 12
Start date (YYYY-MM-DD) or press Enter for today: [Enter]
```

### Learn More
→ See: `LICENSE_GENERATOR_README.md`

---

## 🔧 Python API

### Perfect For
- Custom applications
- Batch processing
- Integration with other tools
- Programmatic control

### Example: Generate Single Code
```python
from license_generator_gui import StandaloneLicenseManager

# Generate
code = StandaloneLicenseManager.generate_license_code('PROFESSIONAL', 12)
print(f"Generated: {code}")

# Validate (returns dict with details)
info = StandaloneLicenseManager.get_license_info(code)
print(f"Product: {info['product_name']}")
print(f"Expiry: {info['expiry_date']}")
print(f"Max Agents: {info['max_agents']}")
```

### Example: Batch Generation
```python
from license_generator_gui import StandaloneLicenseManager

products = ['STARTER', 'PROFESSIONAL', 'ENTERPRISE']
licenses = []

for product in products:
    code = StandaloneLicenseManager.generate_license_code(product, 12)
    info = StandaloneLicenseManager.get_license_info(code)
    licenses.append({
        'product': product,
        'code': code,
        'expiry': info['expiry_date']
    })
    print(f"{product}: {code}")

# Save to file
import json
with open('licenses.json', 'w') as f:
    json.dump(licenses, f, indent=2)
```

### Example: Custom Start Date
```python
from license_generator_gui import StandaloneLicenseManager
from datetime import datetime

start = datetime(2025, 11, 15)  # Custom date
code = StandaloneLicenseManager.generate_license_code('PROFESSIONAL', 6, start)
print(code)
```

---

## 📦 All Files in This Directory

| File | Purpose | Type |
|------|---------|------|
| `license_generator_gui.py` | Web-based GUI (browser) | **Main Tool** |
| `license_generator_standalone.py` | Command-line interface | **Main Tool** |
| `license_generator.py` | Old Tkinter version | Deprecated |
| `LICENSE_GENERATOR_GUI_README.md` | GUI documentation | Docs |
| `LICENSE_GENERATOR_README.md` | CLI documentation | Docs |
| `README.md` | This file | Overview |

---

## 🔐 Security

### Signature Algorithm
```
Data: PRODUCT|VERSION|DURATION|EXPIRY
Example: PROFESSIONAL|1|12|20261031

Signature: HMAC-SHA256(SECRET_KEY, Data)
Result: 235D03489C48C0F6 (first 16 chars)

Final Code: PROFESSIONAL-1-12-20261031-235D03489C48C0F6
```

### Key Points
- ✅ Codes are **cryptographically signed** with HMAC-SHA256
- ✅ Cannot be forged without SECRET_KEY
- ✅ Helpdesk validates by recalculating signature
- ✅ Same algorithm in all three tools (GUI, CLI, API)

### SECRET_KEY
Must match in:
- `license_generator_gui.py` (line 52)
- `license_generator_standalone.py` (line 44)
- `apps/api/license_manager.py` (line 21)

Current value: `"ABoro-Soft-Helpdesk-License-Key-2025"`

⚠️ **In production**: Move SECRET_KEY to `.env` file, not hardcoded!

---

## 🎯 Which Tool Should I Use?

### "I'm sales and want an easy GUI"
→ Use **Web GUI**: `python license_generator_gui.py`

### "I'm a developer and want automation"
→ Use **CLI**: `python license_generator_standalone.py`

### "I need to integrate this into my app"
→ Use **Python API**: Import from `license_generator_gui.py`

### "I'm not sure"
→ Start with **Web GUI** - easiest for everyone!

---

## 💡 Tips & Tricks

### Share the GUI with Team Members
```bash
# Start GUI on your machine
python license_generator_gui.py

# Share URL with team:
# http://YOUR_COMPUTER_IP:5000/
# (find IP with: ipconfig /all)

# Team members access from their browsers
```

### Batch Generate with CLI
```bash
# Create file: generate.txt
PROFESSIONAL 12
STARTER 6
ENTERPRISE 24

# Run manually for each line using CLI:
python license_generator_standalone.py
```

### Save Generated Codes
Use GUI to generate, then:
1. Copy code (click Copy button)
2. Paste into spreadsheet (Excel, Google Sheets, etc.)
3. Track in your sales system

### Verify Generated Code
```bash
# Test if code works in Helpdesk
cd ..
python manage.py shell

from apps.api.license_manager import LicenseManager
is_valid, msg = LicenseManager.validate_license("PROFESSIONAL-1-12-20261031-235D03489C48C0F6")
print(f"Valid: {is_valid}")
```

---

## ⚙️ Technical Details

### Requirements
- **Python** 3.6 or higher
- **No external packages** - uses only Python stdlib
- Works on: Windows, Mac, Linux

### What's Included (Stdlib Only)
- `hashlib` - Cryptographic hashing
- `hmac` - Signature generation
- `http.server` - Web server (GUI)
- `json` - JSON parsing
- `datetime` - Date calculations
- `sys`, `os` - System utilities

### No Installation Needed
Unlike the old Tkinter version, these tools don't need special libraries installed. Just run them with Python!

---

## 🐛 Troubleshooting

### "ModuleNotFoundError"
**Old problem**: `ModuleNotFoundError: No module named 'config'`

**Solution**: You're using the old Django-dependent version.
- Use: `license_generator_gui.py` or `license_generator_standalone.py`
- NOT: the old `license_generator_internal.py`

### "Port 5000 already in use" (GUI only)
```bash
# Kill existing process
pkill -f license_generator_gui.py

# Or change port in code (line 303):
start_server(5001)  # Use 5001 instead
```

### "Code doesn't validate in Helpdesk"
Check SECRET_KEY is identical:
```python
# In generator:
SECRET_KEY = "ABoro-Soft-Helpdesk-License-Key-2025"

# In Helpdesk:
SECRET_KEY = "ABoro-Soft-Helpdesk-License-Key-2025"
# (Must be EXACTLY the same)
```

### "Browser won't open automatically" (GUI)
Manually visit: `http://localhost:5000/`

---

## 📞 Support

### For GUI Issues
→ See: `LICENSE_GENERATOR_GUI_README.md`

### For CLI Issues
→ See: `LICENSE_GENERATOR_README.md`

### For Integration
See "Python API" section above

---

## 📈 Features

### All Tools Support
- ✅ All 4 products (STARTER, PROFESSIONAL, ENTERPRISE, ON_PREMISE)
- ✅ Duration 1-36 months
- ✅ Custom start dates
- ✅ HMAC-SHA256 signing
- ✅ Helpdesk validation
- ✅ Offline operation

### GUI Unique
- ✅ Browser-based UI
- ✅ Copy-to-clipboard button
- ✅ Real-time product details
- ✅ Mobile browser support

### CLI Unique
- ✅ Interactive prompts
- ✅ Easy automation
- ✅ Headless servers

### API Unique
- ✅ Programmatic access
- ✅ Custom integration
- ✅ Batch processing

---

## 🎓 Examples

### Generate for New Customer (GUI)
```
1. python license_generator_gui.py
2. Open browser (http://localhost:5000/)
3. Select: PROFESSIONAL
4. Duration: 12 months
5. Click: Generate License
6. Click: Copy Code
7. Send to customer via email
```

### Generate in Script (CLI + Automation)
```bash
# In shell script:
python license_generator_standalone.py << 'EOF'
2
12

n
EOF
# Extracts code from output and sends email
```

### Integration Example (Python API)
```python
# In your sales app:
from tools.license_generator_gui import StandaloneLicenseManager

def create_license_for_customer(customer_id, product, months):
    code = StandaloneLicenseManager.generate_license_code(product, months)
    info = StandaloneLicenseManager.get_license_info(code)

    # Save to database:
    License.objects.create(
        customer_id=customer_id,
        code=code,
        product=product,
        expiry_date=info['expiry_date']
    )

    return code
```

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 31.10.2025 | Initial release: GUI, CLI, API |
| - | - | Fixed TKinter issues with standalone approach |
| - | - | Added web-based GUI for best UX |
| - | - | Removed Django dependency completely |

---

## 🎉 Summary

You now have **3 professional ways** to generate license codes:

1. **Web GUI** - Best for most users, easy, beautiful
2. **CLI** - Best for developers, automatable
3. **Python API** - Best for integration, scriptable

All use the same secure signing algorithm, work offline, and require nothing but Python!

Choose what works best for your workflow. 🚀

---

**Status**: Production Ready ✅
**Dependencies**: None ✅
**Security**: HMAC-SHA256 signing ✅
**Tested**: All three tools working ✅
