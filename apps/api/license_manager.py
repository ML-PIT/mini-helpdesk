"""
ABoro-Soft Helpdesk License Manager
Database-independent license validation using hash-based algorithm
"""
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Tuple, Dict, Optional


class LicenseManager:
    """
    License management system using hash-based validation.
    Database-independent - validates licenses using cryptographic signatures.

    License Code Format: PROD-VERSION-DURATION-EXPIRY-SIGNATURE
    Example: STARTER-1-12-20251231-A7F3B2C1D9E8F4A6
    """

    # Secret key for generating signatures (should be in .env in production)
    SECRET_KEY = "ABoro-Soft-Helpdesk-License-Key-2025"

    # Product codes and their features
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

    # Trial settings
    TRIAL_DAYS = 30

    @classmethod
    def generate_license_code(
        cls,
        product: str,
        duration_months: int,
        start_date: Optional[datetime] = None
    ) -> str:
        """
        Generate a license code for the given product and duration.

        Args:
            product: Product code (STARTER, PROFESSIONAL, ENTERPRISE, ON_PREMISE)
            duration_months: License validity in months (1-36)
            start_date: License start date (defaults to today)

        Returns:
            License code string

        Example:
            >>> code = LicenseManager.generate_license_code('STARTER', 12)
            >>> # Returns: STARTER-1-12-20261031-A7F3B2C1D9E8F4A6
        """
        if product not in cls.PRODUCTS:
            raise ValueError(f"Invalid product: {product}")

        if not (1 <= duration_months <= 36):
            raise ValueError("Duration must be between 1 and 36 months")

        if start_date is None:
            start_date = datetime.now()

        # Calculate expiry date
        # Add duration_months to start_date
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

        # Format: PRODUCT-VERSION-DURATION-EXPIRY-SIGNATURE
        license_code = f"{product}-1-{duration_months}-{expiry_str}-{signature}"

        return license_code

    @classmethod
    def validate_license(cls, license_code: str) -> Tuple[bool, str]:
        """
        Validate a license code.

        Args:
            license_code: License code to validate

        Returns:
            Tuple of (is_valid: bool, message: str)

        Examples:
            >>> is_valid, msg = LicenseManager.validate_license('STARTER-1-12-20261031-A7F3B2C1D9E8F4A6')
            >>> print(is_valid, msg)
            (True, 'License valid')
        """
        if not license_code or not isinstance(license_code, str):
            return False, "Invalid license code format"

        try:
            parts = license_code.strip().split('-')
            if len(parts) != 5:
                return False, "Invalid license code format (expected 5 parts)"

            product, version, duration_str, expiry_str, signature = parts

            # Validate product
            if product not in cls.PRODUCTS:
                return False, f"Unknown product: {product}"

            # Validate version
            if version != '1':
                return False, f"Unsupported license version: {version}"

            # Validate duration
            try:
                duration = int(duration_str)
                if not (1 <= duration <= 36):
                    return False, f"Invalid duration: {duration}"
            except ValueError:
                return False, "Invalid duration format"

            # Validate expiry date
            try:
                expiry_date = datetime.strptime(expiry_str, '%Y%m%d')
            except ValueError:
                return False, "Invalid expiry date format"

            # Check if license has expired
            now = datetime.now()
            if now > expiry_date:
                return False, "License has expired"

            # Validate signature
            data_to_sign = f"{product}|{version}|{duration_str}|{expiry_str}"
            expected_signature = cls._generate_signature(data_to_sign)

            if not hmac.compare_digest(signature, expected_signature):
                return False, "Invalid license signature (possibly tampered)"

            return True, "License valid"

        except Exception as e:
            return False, f"License validation error: {str(e)}"

    @classmethod
    def get_license_info(cls, license_code: str) -> Optional[Dict]:
        """
        Get detailed information about a license code.

        Args:
            license_code: License code to inspect

        Returns:
            Dictionary with license info or None if invalid

        Example:
            >>> info = LicenseManager.get_license_info('STARTER-1-12-20261031-A7F3B2C1D9E8F4A6')
            >>> print(info)
            {
                'product': 'STARTER',
                'product_name': 'Starter Plan',
                'duration_months': 12,
                'expiry_date': '2026-10-31',
                'days_remaining': 245,
                'max_agents': 5,
                'features': ['tickets', 'email', 'knowledge_base'],
                'valid': True
            }
        """
        is_valid, msg = cls.validate_license(license_code)
        if not is_valid:
            return None

        try:
            parts = license_code.strip().split('-')
            product, version, duration_str, expiry_str, signature = parts

            expiry_date = datetime.strptime(expiry_str, '%Y%m%d')
            now = datetime.now()
            days_remaining = (expiry_date - now).days

            product_info = cls.PRODUCTS[product]

            return {
                'product': product,
                'product_name': product_info['name'],
                'version': int(version),
                'duration_months': int(duration_str),
                'expiry_date': expiry_date.strftime('%Y-%m-%d'),
                'days_remaining': days_remaining,
                'max_agents': product_info['agents'],
                'features': product_info['features'],
                'valid': True,
                'message': 'License is active'
            }

        except Exception as e:
            return None

    @classmethod
    def validate_trial(cls) -> Tuple[bool, str]:
        """
        Validate if trial period is still valid (30 days from first install).
        This would typically check a local file or system state.

        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        # In a real implementation, you'd check a local installation timestamp
        # For now, return a message that trial is available
        return True, f"Trial period available ({cls.TRIAL_DAYS} days)"

    @classmethod
    def _generate_signature(cls, data: str) -> str:
        """
        Generate HMAC signature for license data.

        Args:
            data: Data to sign (format: PRODUCT|VERSION|DURATION|EXPIRY)

        Returns:
            Hex signature
        """
        signature = hmac.new(
            cls.SECRET_KEY.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha256
        ).digest()

        # Return first 16 bytes as hex (32 chars)
        return hashlib.sha256(signature).hexdigest()[:16].upper()

    @classmethod
    def get_all_products(cls) -> Dict:
        """Get all available products and their details."""
        return cls.PRODUCTS

    @classmethod
    def calculate_license_cost(cls, product: str, duration_months: int) -> Dict:
        """
        Calculate license cost for given product and duration.

        Returns:
            Dictionary with cost breakdown
        """
        if product not in cls.PRODUCTS:
            raise ValueError(f"Invalid product: {product}")

        product_info = cls.PRODUCTS[product]
        monthly_price = product_info['monthly_price']

        # Setup fees
        setup_fees = {
            'STARTER': 499,
            'PROFESSIONAL': 999,
            'ENTERPRISE': 2499,
            'ON_PREMISE': 0,  # Included in initial price
        }

        setup_fee = setup_fees.get(product, 0)
        monthly_total = monthly_price * duration_months
        total_cost = setup_fee + monthly_total

        return {
            'product': product,
            'product_name': product_info['name'],
            'monthly_price': monthly_price,
            'duration_months': duration_months,
            'setup_fee': setup_fee,
            'monthly_total': monthly_total,
            'total_cost': total_cost,
            'cost_per_day': round(total_cost / (duration_months * 30), 2),
        }
