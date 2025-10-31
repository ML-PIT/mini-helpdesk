#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create distributable desktop client package
Packages the support agent app and license manager as a zip file
"""

import os
import sys
import shutil
import zipfile
import json
from pathlib import Path
from datetime import datetime

# Force UTF-8 output encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def create_desktop_package():
    """Create desktop client distribution package"""

    # Define paths
    project_root = Path(__file__).parent.parent
    desktop_client_dir = project_root / "desktop_client"
    tools_dir = project_root / "tools"
    api_dir = project_root / "apps" / "api"
    build_dir = project_root / "build" / "desktop"
    output_file = build_dir / "ABoro-Soft-Helpdesk-Desktop-Client.zip"

    # Create build directory
    os.makedirs(build_dir, exist_ok=True)

    # Create staging directory
    staging_dir = build_dir / "ABoro-Soft-Helpdesk-Desktop-Client"
    if os.path.exists(staging_dir):
        shutil.rmtree(staging_dir)
    os.makedirs(staging_dir)

    print("📦 Creating ABoro-Soft Helpdesk Desktop Client Package...")
    print(f"   Building to: {staging_dir}")

    # Copy desktop client app
    print("   ✓ Copying Support Agent Application...")
    shutil.copy(
        desktop_client_dir / "support_agent_app.py",
        staging_dir / "support_agent_app.py"
    )
    if (desktop_client_dir / "__init__.py").exists():
        shutil.copy(
            desktop_client_dir / "__init__.py",
            staging_dir / "__init__.py"
        )

    # Copy license manager (needed for validation)
    print("   ✓ Copying License Manager...")
    os.makedirs(staging_dir / "lib", exist_ok=True)
    shutil.copy(
        api_dir / "license_manager.py",
        staging_dir / "lib" / "license_manager.py"
    )
    Path(staging_dir / "lib" / "__init__.py").touch()

    # Create main launcher script
    print("   ✓ Creating launcher script...")
    launcher_script = f'''#!/usr/bin/env python3
"""
ABoro-Soft Helpdesk - Desktop Client Launcher
Version: 1.0
"""

import sys
import os
from pathlib import Path

# Add lib directory to path
lib_path = Path(__file__).parent / "lib"
sys.path.insert(0, str(lib_path))

# Import and run the app
from support_agent_app import main

if __name__ == "__main__":
    main()
'''

    with open(staging_dir / "run.py", "w") as f:
        f.write(launcher_script)

    # Create README
    print("   ✓ Creating documentation...")
    readme_content = """# ABoro-Soft Helpdesk - Support Agent Desktop Client

## Installation

1. Extract this folder
2. Install Python 3.8 or higher if not already installed
3. Install required dependencies:
   ```
   pip install requests
   ```

## Running the Application

### Option 1: Python Script
```bash
python run.py
```

### Option 2: Windows Batch File
Double-click `run.bat` (if included)

### Option 3: Linux/Mac
```bash
./run.sh
```

## Features

- **Ticket Management**: View and manage assigned tickets
- **Real-time Updates**: Sync with ABoro-Soft Helpdesk server
- **Add Comments**: Respond to tickets directly from the desktop
- **License Support**: Validate license or start 30-day free trial
- **Secure Authentication**: Token-based API authentication

## Configuration

### Environment Variables

Set these before running (or in .env file):

```
HELPDESK_API_URL=http://your-helpdesk-server/api/v1
```

Default: `http://localhost:8000/api/v1`

### License

On first run, you can either:
- Enter a valid license code
- Start a 30-day free trial

License information is stored locally (encrypted on some systems).

## Troubleshooting

### "Connection refused" error
Make sure the ABoro-Soft Helpdesk server is running and accessible.

### "Invalid credentials"
Check your username and password. Contact your support administrator if needed.

### License expired
Purchase a new license or contact sales@aborosoft.de

### Application won't start
1. Verify Python 3.8+ is installed: `python --version`
2. Install dependencies: `pip install requests`
3. Check file permissions
4. Run from terminal to see error messages: `python run.py`

## Support

- **Email**: support@aborosoft.de
- **Website**: www.aborosoft.de
- **Documentation**: docs.aborosoft.de

## License

This is licensed software. See LICENSE file for terms.

## Version History

### v1.0 (2025-10-31)
- Initial release
- Support for ticket management
- License validation
- 30-day free trial

---

**ABoro-Soft Helpdesk**
*Professional Support Without Professional Prices*
"""

    with open(staging_dir / "README.md", "w") as f:
        f.write(readme_content)

    # Create run scripts for different platforms
    print("   ✓ Creating platform-specific launchers...")

    # Windows batch file
    batch_content = """@echo off
REM ABoro-Soft Helpdesk - Desktop Client Launcher
echo Starting ABoro-Soft Helpdesk Support Agent Client...
python run.py
pause
"""
    with open(staging_dir / "run.bat", "w") as f:
        f.write(batch_content)

    # Linux/Mac shell script
    shell_content = """#!/bin/bash
# ABoro-Soft Helpdesk - Desktop Client Launcher
echo "Starting ABoro-Soft Helpdesk Support Agent Client..."
python3 run.py
"""
    with open(staging_dir / "run.sh", "w") as f:
        f.write(shell_content)
    os.chmod(staging_dir / "run.sh", 0o755)

    # Create requirements.txt
    print("   ✓ Creating requirements file...")
    requirements = """requests>=2.28.0
"""
    with open(staging_dir / "requirements.txt", "w") as f:
        f.write(requirements)

    # Create package metadata
    print("   ✓ Creating package metadata...")
    metadata = {
        "name": "ABoro-Soft Helpdesk Desktop Client",
        "version": "1.0.0",
        "build_date": datetime.now().isoformat(),
        "description": "Support Agent Desktop Client for ABoro-Soft Helpdesk",
        "features": [
            "Ticket Management",
            "Real-time Synchronization",
            "Comment Management",
            "License Validation",
            "30-day Free Trial",
            "Token-based Authentication"
        ],
        "system_requirements": [
            "Python 3.8 or higher",
            "Windows 7+, macOS 10.12+, or Linux",
            "Minimum 100 MB disk space",
            "Internet connection"
        ],
        "pricing": {
            "included_with": [
                "STARTER (€199/month)",
                "PROFESSIONAL (€499/month)",
                "ENTERPRISE (€1,299/month)",
                "ON_PREMISE (€10,000 one-time)"
            ],
            "trial": "30 days free"
        }
    }

    with open(staging_dir / "package.json", "w") as f:
        json.dump(metadata, f, indent=2)

    # Create LICENSE file
    license_content = """ABoro-Soft Helpdesk - Desktop Client License

Copyright 2025 ABoro-Soft GmbH

This software is provided as part of your ABoro-Soft Helpdesk subscription.
You are licensed to use this software only in accordance with the terms
of your subscription agreement.

TRIAL LICENSE:
- 30-day trial available at no cost
- Limited functionality during trial
- Trial license cannot be extended
- Requires valid license code for full functionality

COMMERCIAL LICENSE:
- Valid for the duration of your subscription
- User count limited by subscription tier
- Support and updates included
- License tied to product and duration

RESTRICTIONS:
- No reverse engineering
- No commercial redistribution
- No concurrent use beyond licensed seat count
- License code is non-transferable

For full terms, contact: legal@aborosoft.de
"""
    with open(staging_dir / "LICENSE", "w") as f:
        f.write(license_content)

    # Create INSTALL.txt for quick start
    install_txt = """QUICK START GUIDE

1. EXTRACT
   Extract this zip file to your desired location

2. REQUIREMENTS
   Python 3.8+ required
   Windows: Download from python.org
   macOS: brew install python3 (or from python.org)
   Linux: sudo apt-get install python3 (or equivalent)

3. INSTALL DEPENDENCIES
   Windows CMD:
     pip install -r requirements.txt

   Mac/Linux Terminal:
     pip3 install -r requirements.txt

4. RUN APPLICATION
   Windows: Double-click run.bat or: python run.py
   Mac/Linux: ./run.sh or: python3 run.py

5. FIRST RUN
   - Enter your email and password
   - Or use 30-day free trial
   - Or enter your license code

6. START WORKING
   - View your assigned tickets
   - Click ticket to see details
   - Add comments and update status
   - Logout when done

TROUBLESHOOTING

No module named 'requests':
  pip install requests

Connection refused:
  Check server is running
  Check API URL in error message

Invalid credentials:
  Verify email/password
  Contact your admin

Need help?
  Email: support@aborosoft.de
  Web: www.aborosoft.de
"""
    with open(staging_dir / "INSTALL.txt", "w") as f:
        f.write(install_txt)

    # Create the zip file
    print(f"   ✓ Packaging as ZIP file...")
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(staging_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, build_dir)
                zipf.write(file_path, arcname)

    print(f"\n✅ Desktop package created successfully!")
    print(f"   📦 Package: {output_file}")
    print(f"   📊 Size: {os.path.getsize(output_file) / 1024:.1f} KB")
    print(f"   📁 Location: {build_dir}")

    # Print summary
    print("\n📋 Package Contents:")
    print("   ✓ support_agent_app.py - Main application")
    print("   ✓ run.py - Python launcher")
    print("   ✓ run.bat - Windows launcher")
    print("   ✓ run.sh - Linux/Mac launcher")
    print("   ✓ README.md - Full documentation")
    print("   ✓ INSTALL.txt - Quick start guide")
    print("   ✓ requirements.txt - Python dependencies")
    print("   ✓ package.json - Package metadata")
    print("   ✓ LICENSE - License terms")
    print("   ✓ lib/license_manager.py - License validation")

    print("\n🚀 Distribution Ready!")
    print(f"   Download from: {output_file}")
    print("   Share with customers or make available on website")

    return output_file


if __name__ == "__main__":
    create_desktop_package()
