#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ABoro-Soft Helpdesk - License Generator (STANDALONE)
=====================================================

[!] INTERNAL USE ONLY - DO NOT DISTRIBUTE

This is a completely independent tool that can run WITHOUT Django,
venv, or any Helpdesk environment dependencies.

It generates cryptographically signed license codes that can be
distributed to customers for activation in their Helpdesk instances.

Features:
  - Works completely standalone
  - No Django dependencies
  - No database required
  - Same signature algorithm as Helpdesk
  - Interactive CLI interface

Usage:
  python license_generator_standalone.py

Author: ABoro-Soft
Date: 31.10.2025
Version: 1.0
"""

import hashlib
import hmac
from datetime import datetime, timedelta
import sys
import os

# ============================================================================
# STANDALONE LICENSE MANAGER (No Django required!)
# ============================================================================

class StandaloneLicenseManager:
    """
    Standalone license code generator.
    Uses the SAME algorithm as the Helpdesk LicenseManager.
    """

    # This MUST match the SECRET_KEY in the Helpdesk installation!
    # See: apps/api/license_manager.py -> LicenseManager.SECRET_KEY
    SECRET_KEY = "ABoro-Soft-Helpdesk-License-Key-2025"

    # Product configurations (same as in Helpdesk)
    PRODUCTS = {
        'STARTER': {
            'name': 'Starter Plan',
            'agents': 5,
            'features': ['tickets', 'email', 'knowledge_base'],
            'monthly_price': 199,
        },
        'PROFESSIONAL': {
            'name': 'Professional Plan',
            'agents': 20,
            'features': ['tickets', 'email', 'knowledge_base', 'ai_automation', 'custom_branding', 'api_basic'],
            'monthly_price': 499,
        },
        'ENTERPRISE': {
            'name': 'Enterprise Plan',
            'agents': 999,
            'features': ['tickets', 'email', 'knowledge_base', 'ai_automation', 'custom_branding', 'api_full', 'sso_ldap', 'sla'],
            'monthly_price': 1299,
        },
        'ON_PREMISE': {
            'name': 'On-Premise License',
            'agents': 999,
            'features': ['tickets', 'email', 'knowledge_base', 'ai_automation', 'custom_branding', 'api_full', 'sso_ldap', 'sla', 'on_premise'],
            'monthly_price': 10000,
        },
    }

    @classmethod
    def _generate_signature(cls, data: str) -> str:
        """Generate HMAC-SHA256 signature"""
        signature = hmac.new(
            cls.SECRET_KEY.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature.upper()

    @classmethod
    def generate_license_code(cls, product: str, duration_months: int, start_date=None) -> str:
        """
        Generate a license code.
        Format: PRODUCT-VERSION-DURATION-EXPIRY-SIGNATURE
        Example: STARTER-1-12-20261031-A7F3B2C1D9E8F4A6
        """
        if product not in cls.PRODUCTS:
            raise ValueError(f"Invalid product: {product}")

        if not (1 <= duration_months <= 36):
            raise ValueError("Duration must be between 1 and 36 months")

        if start_date is None:
            start_date = datetime.now()

        # Calculate expiry date
        year = start_date.year
        month = start_date.month + duration_months
        day = start_date.day

        while month > 12:
            month -= 12
            year += 1

        expiry_date = datetime(year, month, day, 23, 59, 59)
        expiry_str = expiry_date.strftime('%Y%m%d')

        # Create signature
        data_to_sign = f"{product}|1|{duration_months}|{expiry_str}"
        signature = cls._generate_signature(data_to_sign)

        # Construct license code
        license_code = f"{product}-1-{duration_months}-{expiry_str}-{signature[:16]}"
        return license_code

    @classmethod
    def get_license_info(cls, license_code: str) -> dict:
        """Parse license code and return information"""
        parts = license_code.split('-')
        if len(parts) != 5:
            raise ValueError("Invalid license code format")

        product, version, duration, expiry_str, signature = parts

        if product not in cls.PRODUCTS:
            raise ValueError(f"Unknown product: {product}")

        # Parse expiry date
        try:
            expiry_date = datetime.strptime(expiry_str, '%Y%m%d')
        except ValueError:
            raise ValueError("Invalid expiry date in license code")

        product_info = cls.PRODUCTS[product]

        # Calculate remaining days
        today = datetime.now()
        days_remaining = (expiry_date - today).days

        return {
            'product': product,
            'product_name': product_info['name'],
            'version': int(version),
            'duration_months': int(duration),
            'expiry_date': expiry_date.strftime('%Y-%m-%d'),
            'days_remaining': days_remaining,
            'max_agents': product_info['agents'],
            'features': product_info['features'],
            'is_valid': days_remaining >= 0,
            'monthly_price': product_info['monthly_price'],
        }


# ============================================================================
# INTERACTIVE CLI INTERFACE
# ============================================================================

class LicenseGeneratorCLI:
    """Interactive command-line interface for license generation"""

    @staticmethod
    def print_header():
        """Print banner"""
        print("\n" + "="*70)
        print(" ABoro-Soft Helpdesk - License Generator (STANDALONE)")
        print(" [!] INTERNAL USE ONLY - NOT FOR CUSTOMER DISTRIBUTION")
        print("="*70 + "\n")

    @staticmethod
    def print_products():
        """Show available products"""
        print("Available Products:")
        print("-" * 70)
        for i, (code, info) in enumerate(StandaloneLicenseManager.PRODUCTS.items(), 1):
            agents = "Unlimited" if info['agents'] >= 999 else str(info['agents'])
            price = f"${info['monthly_price']}/month"
            print(f"{i}) {code:15} - {info['name']:20} | {agents:12} Agents | {price}")
        print()

    @staticmethod
    def get_product_choice() -> str:
        """Get product selection from user"""
        choices = list(StandaloneLicenseManager.PRODUCTS.keys())

        while True:
            LicenseGeneratorCLI.print_products()
            choice = input("Select product (1-4): ").strip()

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(choices):
                    return choices[idx]
            except ValueError:
                pass

            print("[X] Invalid choice. Please select 1-4.\n")

    @staticmethod
    def get_duration() -> int:
        """Get license duration in months"""
        while True:
            try:
                duration = input("License duration in months (1-36): ").strip()
                duration_int = int(duration)
                if 1 <= duration_int <= 36:
                    return duration_int
                print("[X] Duration must be between 1 and 36 months.\n")
            except ValueError:
                print("[X] Please enter a valid number.\n")

    @staticmethod
    def get_start_date():
        """Get start date for license"""
        while True:
            date_str = input("Start date (YYYY-MM-DD) or press Enter for today: ").strip()

            if not date_str:
                return None

            try:
                datetime.strptime(date_str, '%Y-%m-%d')
                return date_str
            except ValueError:
                print("[X] Invalid date format. Please use YYYY-MM-DD.\n")

    @staticmethod
    def run():
        """Main CLI loop"""
        LicenseGeneratorCLI.print_header()

        print("SECURITY REMINDER:")
        print("  • This tool is for INTERNAL USE ONLY")
        print("  • Do NOT share license codes in plain text")
        print("  • Use encrypted email or secure file transfer")
        print("  • Track distributed codes in your sales system")
        print()

        try:
            while True:
                try:
                    # Get product
                    product = LicenseGeneratorCLI.get_product_choice()

                    # Get duration
                    duration_months = LicenseGeneratorCLI.get_duration()

                    # Get start date
                    start_date_str = LicenseGeneratorCLI.get_start_date()
                    start_date = None
                    if start_date_str:
                        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')

                    print("\n" + "-" * 70)
                    print("Generating license code...\n")

                    # Generate license
                    license_code = StandaloneLicenseManager.generate_license_code(
                        product,
                        duration_months,
                        start_date
                    )

                    # Get license info
                    license_info = StandaloneLicenseManager.get_license_info(license_code)

                    # Display results
                    print("[OK] LICENSE CODE GENERATED SUCCESSFULLY\n")
                    print("=" * 70)
                    print(f"Product:       {license_info['product_name']}")
                    print(f"License Code:  {license_code}")
                    print("=" * 70)
                    print(f"Expiry Date:   {license_info['expiry_date']}")
                    print(f"Duration:      {duration_months} months")
                    print(f"Max Agents:    {license_info['max_agents']}")
                    print(f"Features:      {', '.join(license_info['features'])}")
                    print(f"Valid Days:    {license_info['days_remaining']} days")
                    print("=" * 70 + "\n")

                    print("NEXT STEPS:")
                    print("1. Copy the license code above")
                    print("2. Send to customer via ENCRYPTED/SECURE channel")
                    print("3. Customer enters at: http://their-helpdesk.de/admin-panel/license/")
                    print("4. Track code in your sales/CRM system")
                    print()

                    # Generate another?
                    while True:
                        again = input("Generate another license? (y/n): ").strip().lower()
                        if again in ['y', 'n']:
                            break

                    if again != 'y':
                        break

                    print()

                except ValueError as e:
                    print(f"\n[X] Error: {str(e)}\n")
                except Exception as e:
                    print(f"\n[X] Unexpected error: {str(e)}\n")
                    import traceback
                    traceback.print_exc()

        except KeyboardInterrupt:
            print("\n\n[!] License generator cancelled.\n")
            sys.exit(0)

        print("[OK] License generator completed.\n")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    try:
        LicenseGeneratorCLI.run()
    except Exception as e:
        print(f"\n[X] Fatal error: {str(e)}\n")
        sys.exit(1)
