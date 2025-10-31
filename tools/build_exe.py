#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Standalone EXE for License Generator GUI

This script builds a standalone Windows executable (.exe) using PyInstaller.
No Python installation needed to run the .exe - it includes everything!

Usage:
  python build_exe.py

Output:
  dist/license_generator.exe  (standalone executable)
  dist/license_generator/     (supporting files)

Requirements:
  - PyInstaller: pip install PyInstaller

Author: ABoro-Soft
Date: 31.10.2025
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Configuration
PROJECT_NAME = "license_generator"
SCRIPT_NAME = "license_generator_gui.py"
ICON_NAME = "license_generator.ico"

def print_header():
    """Print build header"""
    print("\n" + "="*70)
    print(f" Building {PROJECT_NAME}.exe with PyInstaller")
    print("="*70 + "\n")

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        print(f"[OK] PyInstaller {PyInstaller.__version__} found")
        return True
    except ImportError:
        print("[X] PyInstaller not installed!")
        print("    Install: pip install PyInstaller")
        return False

def create_icon():
    """Create a simple icon file if it doesn't exist"""
    icon_path = Path(ICON_NAME)
    if icon_path.exists():
        print(f"[OK] Icon found: {ICON_NAME}")
        return str(icon_path.absolute())

    print(f"[!] Icon not found, skipping (using default)")
    return None

def clean_build_dirs():
    """Clean up old build directories"""
    print("[*] Cleaning up old builds...")
    for dirname in ['build', 'dist', f'{PROJECT_NAME}.spec']:
        if Path(dirname).exists():
            try:
                if Path(dirname).is_dir():
                    shutil.rmtree(dirname)
                else:
                    Path(dirname).unlink()
                print(f"    Removed: {dirname}")
            except Exception as e:
                print(f"    [!] Could not remove {dirname}: {e}")

def build_exe(icon_path=None):
    """Build the EXE using PyInstaller"""
    print("[*] Building executable...")

    # Base PyInstaller command
    cmd = [
        'pyinstaller',
        '--name', PROJECT_NAME,
        '--onefile',  # Single file executable
        '--windowed',  # No console window
        '--add-data', f'{SCRIPT_NAME};.',  # Include main script
    ]

    # Add icon if available
    if icon_path:
        cmd.extend(['--icon', icon_path])

    # Add the main script
    cmd.append(SCRIPT_NAME)

    print(f"    Command: {' '.join(cmd)}\n")

    # Run PyInstaller
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("[OK] Build successful!")
            return True
        else:
            print("[X] Build failed!")
            print("\nSTDOUT:")
            print(result.stdout)
            print("\nSTDERR:")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"[X] Build error: {e}")
        return False

def verify_exe():
    """Verify that the EXE was created"""
    exe_path = Path('dist') / f'{PROJECT_NAME}.exe'

    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"\n[OK] EXE created: {exe_path}")
        print(f"    Size: {size_mb:.1f} MB")
        return True
    else:
        print(f"\n[X] EXE not found at: {exe_path}")
        return False

def print_instructions():
    """Print post-build instructions"""
    print("\n" + "="*70)
    print(" BUILD COMPLETE!")
    print("="*70 + "\n")
    print(f"Executable location: dist/{PROJECT_NAME}.exe\n")

    print("How to use:")
    print(f"  1. Double-click: dist/{PROJECT_NAME}.exe")
    print(f"  2. Browser opens automatically")
    print(f"  3. Generate license codes")
    print(f"  4. Done!\n")

    print("Distribution:")
    print(f"  - Share the entire 'dist' folder with your team")
    print(f"  - No Python installation required on target machine")
    print(f"  - Works on any Windows PC\n")

    print("For batch processing:")
    print(f"  - Create desktop shortcut to dist/{PROJECT_NAME}.exe")
    print(f"  - Sales team can access directly\n")

    print("="*70 + "\n")

def create_batch_launcher():
    """Create a batch file to launch the EXE"""
    batch_content = f'''@echo off
REM ABoro-Soft License Generator Launcher
REM This starts the license generator GUI

cd /d "%~dp0"
start "" dist\\{PROJECT_NAME}.exe

REM Optional: Show a message
REM echo License Generator starting...
REM timeout /t 2 /nobreak
'''

    batch_file = Path(f'start_{PROJECT_NAME}.bat')
    with open(batch_file, 'w') as f:
        f.write(batch_content)

    print(f"[OK] Created launcher: {batch_file}")
    print(f"    Double-click this file to start the generator\n")

def main():
    """Main build function"""
    os.chdir(Path(__file__).parent)  # Change to tools directory

    print_header()

    # Check PyInstaller
    if not check_pyinstaller():
        sys.exit(1)

    print()

    # Clean old builds
    clean_build_dirs()

    print()

    # Create icon (optional)
    icon_path = create_icon()

    print()

    # Build EXE
    if not build_exe(icon_path):
        print("\n[X] Build failed. Check errors above.")
        sys.exit(1)

    print()

    # Verify
    if not verify_exe():
        print("\n[X] Verification failed.")
        sys.exit(1)

    # Create launcher
    print()
    create_batch_launcher()

    # Print instructions
    print_instructions()

    print("Next steps:")
    print("  1. Test: Double-click dist/license_generator.exe")
    print("  2. Share: Send 'dist' folder to sales team")
    print("  3. Create shortcut: Right-click .exe > Send to > Desktop\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Build cancelled.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n[X] Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
