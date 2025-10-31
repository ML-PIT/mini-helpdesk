# License Generator - Web GUI

## Overview

A **modern, web-based GUI** for generating ABoro-Soft Helpdesk license codes.

**Features:**
- ✅ Works in **any web browser** (Chrome, Firefox, Safari, Edge)
- ✅ No installation needed - just Python 3.6+
- ✅ Modern, clean interface with real-time validation
- ✅ Copy-to-clipboard functionality
- ✅ Automatic browser opening
- ✅ Same secure signing algorithm as Helpdesk
- ✅ No external dependencies (pure Python stdlib)

## Quick Start

### Windows
```bash
python tools/license_generator_gui.py
```

Browser automatically opens to: **http://localhost:5000/**

### Mac/Linux
```bash
python3 tools/license_generator_gui.py
```

Then open: **http://localhost:5000/**

## How to Use

### Step 1: Start the Server
```bash
python tools/license_generator_gui.py
```

Output:
```
======================================================================
 ABoro-Soft License Generator - Web GUI
 [!] INTERNAL USE ONLY - NOT FOR CUSTOMER DISTRIBUTION
======================================================================

Server running on: http://localhost:5000/
Open your browser to: http://localhost:5000/

Press Ctrl+C to stop the server.

======================================================================
```

### Step 2: Open in Browser
Automatically opens, or manually visit: `http://localhost:5000/`

### Step 3: Generate License
1. **Select Product**
   - STARTER ($199/month) - 5 agents
   - PROFESSIONAL ($499/month) - 20 agents
   - ENTERPRISE ($1,299/month) - Unlimited agents
   - ON_PREMISE ($10,000 one-time) - Unlimited agents

2. **Enter Duration**
   - 1-36 months
   - Default: 12 months

3. **Optional: Start Date**
   - Leave empty for today
   - Or specify custom date (YYYY-MM-DD)

4. **Click "Generate License"**

### Step 4: Get Results
- License code displayed with all details
- Copy button for easy clipboard access
- Shows expiry date, max agents, included features

### Step 5: Send to Customer
Copy the code and send via secure channel (encrypted email, secure file transfer, etc.)

## Screenshot Example

```
┌─────────────────────────────────────────────┐
│  ABoro-Soft License Generator               │
│                                             │
│  [WARNING] Internal use only                │
│                                             │
│  Product:         [PROFESSIONAL ▼]          │
│  Duration:        [12 months]               │
│  Start Date:      [2025-10-31]             │
│                                             │
│          [Generate License]                 │
│                                             │
├─────────────────────────────────────────────┤
│                                             │
│  [OK] License Generated Successfully        │
│                                             │
│  Product: Professional Plan                 │
│                                             │
│  PROFESSIONAL-1-12-20261031-235D03489C48C0F6 │
│           [Copy Code]                       │
│                                             │
│  Expiry: 2026-10-31 | Max Agents: 20       │
│  Features: tickets email knowledge_base ... │
│                                             │
│  This code is ready to send to customer.    │
│                                             │
└─────────────────────────────────────────────┘
```

## Features

### User Interface
- **Responsive Design**: Works on desktop, tablet, mobile browsers
- **Modern Styling**: Clean purple/gradient theme
- **Real-time Feedback**: Instant validation and error messages
- **Copy-to-Clipboard**: One-click code copying

### Security
- **HMAC-SHA256 Signatures**: Codes cannot be forged
- **Same Algorithm**: Works with Helpdesk validator
- **Offline Capable**: No internet required after startup
- **Internal Only**: Not distributed to customers

### Functionality
- Generate codes for any product
- Custom duration (1-36 months)
- Optional custom start date
- Product details on generation
- Feature list display
- Days remaining counter

## API Endpoints

### GET /
Returns the HTML GUI interface

### GET /api/products
Returns list of available products

**Response:**
```json
{
  "products": [
    {
      "code": "STARTER",
      "name": "Starter Plan",
      "agents": 5,
      "price": 199
    },
    ...
  ]
}
```

### POST /api/generate
Generates a license code

**Request:**
```json
{
  "product": "PROFESSIONAL",
  "duration": 12,
  "start_date": "2025-10-31" or null
}
```

**Response (Success):**
```json
{
  "success": true,
  "license_code": "PROFESSIONAL-1-12-20261031-235D03489C48C0F6",
  "license_info": {
    "product": "PROFESSIONAL",
    "product_name": "Professional Plan",
    "expiry_date": "2026-10-31",
    "max_agents": 20,
    "features": ["tickets", "email", "knowledge_base", ...],
    ...
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Invalid product: XYZ"
}
```

## Technical Details

### Requirements
- Python 3.6+ (any OS)
- No external packages required!
- Standard library only:
  - `hashlib` - Cryptographic hashing
  - `hmac` - Signature generation
  - `http.server` - Web server
  - `json` - JSON handling
  - `webbrowser` - Auto-open browser

### Server
- **Host**: 127.0.0.1 (localhost only)
- **Port**: 5000 (default)
- **Protocol**: HTTP (local only, secure enough for internal)

### Browser Compatibility
- Chrome/Chromium 60+
- Firefox 55+
- Safari 12+
- Edge 79+
- All modern browsers

## Troubleshooting

### "Port 5000 already in use"
Another application is using port 5000.

**Solution 1**: Kill existing process
```bash
# Windows:
taskkill /F /IM python.exe

# Mac/Linux:
pkill -f license_generator_gui.py
```

**Solution 2**: Wait a moment and restart
```bash
python tools/license_generator_gui.py
```

### Browser doesn't open automatically
Manually visit: `http://localhost:5000/`

### Server won't start
Check Python installation:
```bash
python --version
# Should be 3.6 or higher
```

### Generated code doesn't validate in Helpdesk
Verify SECRET_KEY matches:
- File: `tools/license_generator_gui.py` line 52
- File: `apps/api/license_manager.py` line 21
- Must be identical: `"ABoro-Soft-Helpdesk-License-Key-2025"`

## Keyboard Shortcuts

| Keys | Action |
|------|--------|
| `Ctrl+C` | Stop the server |
| `Ctrl+A` | Select license code in result box |
| `Ctrl+C` | Copy selected text (or use Copy button) |

## Files

- `license_generator_gui.py` - Main web GUI (use this!)
- `license_generator_standalone.py` - CLI version (alternative)
- `LICENSE_GENERATOR_GUI_README.md` - This file

## Comparison: GUI vs CLI

| Feature | GUI | CLI |
|---------|-----|-----|
| Interface | Modern web UI | Terminal prompts |
| Browser | Any web browser | None (terminal only) |
| Copy button | Yes | Manual copy |
| Mobile browser | Works! | No |
| Learning curve | Very easy | Easy |
| Installation | Python only | Python only |
| Recommended | YES! | When no browser available |

**Recommendation**: Use the **GUI** for best user experience!

## Deployment for Sales Team

### For Windows Sales Staff
```bash
1. Download Python 3.11+ from python.org
2. Download mini-helpdesk folder
3. Double-click batch file:
   @echo off
   cd /d %~dp0\tools
   python license_generator_gui.py
```

Save as: `start_license_generator.bat`

### For Mac/Linux
```bash
#!/bin/bash
cd "$(dirname "$0")/tools"
python3 license_generator_gui.py
```

Save as: `start_license_generator.sh`
Make executable: `chmod +x start_license_generator.sh`

## Version Info

- **Tool**: `license_generator_gui.py`
- **Version**: 1.0
- **Status**: Production Ready
- **Created**: 31.10.2025
- **Python**: 3.6+
- **Dependencies**: None (stdlib only)

## Support

### Internal Team
- See this README for detailed usage
- Test with: `python tools/license_generator_gui.py`
- Check API with: `curl http://localhost:5000/api/products`

### Code Integration
- Same signature algorithm as `LicenseManager` class
- Compatible with Helpdesk validator
- Can be used alongside CLI version

## License

Internal use only. Do not distribute to customers.

---

**The easiest way to generate license codes!** 🎯
