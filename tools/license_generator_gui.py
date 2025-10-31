#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ABoro-Soft License Generator - Web GUI (STANDALONE)
====================================================

[!] INTERNAL USE ONLY - DO NOT DISTRIBUTE

A simple web-based GUI for generating license codes.
No dependencies except Python stdlib!

Features:
  - Works in any web browser (Chrome, Firefox, Safari, Edge)
  - Modern, clean interface
  - Real-time validation
  - Copy-to-clipboard functionality
  - Starts local web server (localhost:5000)
  - Perfect for sales team

Usage:
  python license_generator_gui.py

Then open: http://localhost:5000/

Author: ABoro-Soft
Date: 31.10.2025
"""

import hashlib
import hmac
from datetime import datetime, timedelta
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import webbrowser
import os

# ============================================================================
# STANDALONE LICENSE MANAGER (Same as CLI version)
# ============================================================================

class StandaloneLicenseManager:
    """Standalone license code generator - SAME algorithm as Helpdesk"""

    SECRET_KEY = "ABoro-Soft-Helpdesk-License-Key-2025"

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
        """Generate a license code"""
        if product not in cls.PRODUCTS:
            raise ValueError(f"Invalid product: {product}")

        if not (1 <= duration_months <= 36):
            raise ValueError("Duration must be between 1 and 36 months")

        if start_date is None:
            start_date = datetime.now()
        elif isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')

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

        try:
            expiry_date = datetime.strptime(expiry_str, '%Y%m%d')
        except ValueError:
            raise ValueError("Invalid expiry date in license code")

        product_info = cls.PRODUCTS[product]
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
# WEB GUI
# ============================================================================

class LicenseGeneratorHandler(BaseHTTPRequestHandler):
    """HTTP request handler for web GUI"""

    def do_GET(self):
        """Handle GET requests"""
        path = urlparse(self.path).path

        if path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(self.get_html().encode('utf-8'))

        elif path == '/api/products':
            self.send_json_response({
                'products': [
                    {'code': k, 'name': v['name'], 'agents': v['agents'], 'price': v['monthly_price']}
                    for k, v in StandaloneLicenseManager.PRODUCTS.items()
                ]
            })

        else:
            self.send_error(404)

    def do_POST(self):
        """Handle POST requests (generate license)"""
        path = urlparse(self.path).path

        if path == '/api/generate':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(body)

                product = data.get('product')
                duration = int(data.get('duration', 12))
                start_date = data.get('start_date')

                # Generate license
                license_code = StandaloneLicenseManager.generate_license_code(
                    product, duration, start_date
                )

                # Get info
                license_info = StandaloneLicenseManager.get_license_info(license_code)

                self.send_json_response({
                    'success': True,
                    'license_code': license_code,
                    'license_info': license_info
                })

            except Exception as e:
                self.send_json_response({
                    'success': False,
                    'error': str(e)
                }, status=400)
        else:
            self.send_error(404)

    def send_json_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def log_message(self, format, *args):
        """Suppress request logging"""
        pass

    @staticmethod
    def get_html():
        """Return HTML page"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ABoro-Soft License Generator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 500px;
            padding: 40px;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }

        .header h1 {
            color: #333;
            font-size: 28px;
            margin-bottom: 5px;
        }

        .header p {
            color: #666;
            font-size: 14px;
        }

        .warning {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 12px;
            margin-bottom: 20px;
            border-radius: 4px;
            font-size: 13px;
            color: #856404;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            color: #333;
            font-weight: 500;
            margin-bottom: 8px;
            font-size: 14px;
        }

        select, input[type="text"], input[type="number"], input[type="date"] {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            font-family: inherit;
            transition: border-color 0.3s;
        }

        select:focus, input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }

        button:active {
            transform: translateY(0);
        }

        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .result {
            margin-top: 30px;
            display: none;
        }

        .result.show {
            display: block;
        }

        .result-box {
            background: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
        }

        .result-title {
            color: #28a745;
            font-weight: 600;
            margin-bottom: 15px;
            font-size: 16px;
        }

        .license-code {
            background: white;
            border: 2px solid #667eea;
            padding: 15px;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            word-break: break-all;
            margin: 15px 0;
            text-align: center;
            color: #333;
            font-weight: 600;
        }

        .copy-btn {
            padding: 8px 16px;
            font-size: 13px;
            width: auto;
            margin: 0 auto;
            display: block;
            background: #667eea;
        }

        .info-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-top: 15px;
        }

        .info-item {
            background: white;
            padding: 12px;
            border-radius: 6px;
            border-left: 3px solid #667eea;
        }

        .info-label {
            color: #666;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: 5px;
        }

        .info-value {
            color: #333;
            font-size: 16px;
            font-weight: 600;
        }

        .features-list {
            margin-top: 15px;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .feature-tag {
            background: #667eea;
            color: white;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 12px;
        }

        .error {
            background: #f8d7da;
            border-left: 4px solid #dc3545;
            color: #721c24;
            padding: 12px;
            border-radius: 4px;
            margin-top: 15px;
            display: none;
        }

        .error.show {
            display: block;
        }

        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }

        .loading.show {
            display: block;
        }

        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .success-message {
            color: #28a745;
            text-align: center;
            font-size: 14px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>License Generator</h1>
            <p>ABoro-Soft Helpdesk</p>
        </div>

        <div class="warning">
            <strong>WARNING:</strong> Internal use only. Do not share or distribute this tool.
        </div>

        <form id="generatorForm">
            <div class="form-group">
                <label for="product">Product</label>
                <select id="product" required>
                    <option value="">Select a product...</option>
                </select>
            </div>

            <div class="form-group">
                <label for="duration">Duration (Months)</label>
                <input type="number" id="duration" min="1" max="36" value="12" required>
            </div>

            <div class="form-group">
                <label for="startDate">Start Date (optional)</label>
                <input type="date" id="startDate">
            </div>

            <button type="submit" id="generateBtn">Generate License</button>
        </form>

        <div class="error" id="errorBox"></div>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Generating license code...</p>
        </div>

        <div class="result" id="result">
            <div class="result-box">
                <div class="result-title">[OK] License Generated Successfully</div>

                <div>
                    <strong>Product:</strong> <span id="resultProduct"></span>
                </div>

                <div class="license-code" id="resultCode"></div>

                <button class="copy-btn" onclick="copyToClipboard()">Copy Code</button>

                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">Expiry Date</div>
                        <div class="info-value" id="resultExpiry"></div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Max Agents</div>
                        <div class="info-value" id="resultAgents"></div>
                    </div>
                </div>

                <div class="features-list" id="features"></div>

                <div class="success-message">
                    This code is ready to be sent to the customer.
                </div>
            </div>
        </div>
    </div>

    <script>
        // Load products on page load
        window.addEventListener('DOMContentLoaded', loadProducts);

        async function loadProducts() {
            try {
                const response = await fetch('/api/products');
                const data = await response.json();

                const select = document.getElementById('product');
                data.products.forEach(product => {
                    const option = document.createElement('option');
                    option.value = product.code;
                    option.textContent = `${product.code} - ${product.name} ($${product.price}/month)`;
                    select.appendChild(option);
                });
            } catch (error) {
                showError('Failed to load products');
            }
        }

        document.getElementById('generatorForm').addEventListener('submit', generateLicense);

        async function generateLicense(e) {
            e.preventDefault();

            const product = document.getElementById('product').value;
            const duration = document.getElementById('duration').value;
            const startDate = document.getElementById('startDate').value;

            if (!product) {
                showError('Please select a product');
                return;
            }

            showLoading(true);
            hideError();

            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        product: product,
                        duration: duration,
                        start_date: startDate || null
                    })
                });

                const data = await response.json();

                if (data.success) {
                    displayResult(data.license_info, data.license_code);
                } else {
                    showError(data.error);
                }
            } catch (error) {
                showError('Failed to generate license: ' + error.message);
            } finally {
                showLoading(false);
            }
        }

        function displayResult(info, code) {
            document.getElementById('resultProduct').textContent = info.product_name;
            document.getElementById('resultCode').textContent = code;
            document.getElementById('resultExpiry').textContent = info.expiry_date;
            document.getElementById('resultAgents').textContent =
                info.max_agents >= 999 ? 'Unlimited' : info.max_agents;

            const featuresDiv = document.getElementById('features');
            featuresDiv.innerHTML = '';
            info.features.forEach(feature => {
                const tag = document.createElement('span');
                tag.className = 'feature-tag';
                tag.textContent = feature.replace('_', ' ');
                featuresDiv.appendChild(tag);
            });

            document.getElementById('result').classList.add('show');
        }

        function showError(message) {
            const errorBox = document.getElementById('errorBox');
            errorBox.textContent = message;
            errorBox.classList.add('show');
        }

        function hideError() {
            document.getElementById('errorBox').classList.remove('show');
        }

        function showLoading(show) {
            document.getElementById('loading').classList.toggle('show', show);
        }

        function copyToClipboard() {
            const code = document.getElementById('resultCode').textContent;
            navigator.clipboard.writeText(code).then(() => {
                alert('License code copied to clipboard!');
            });
        }
    </script>
</body>
</html>
'''


# ============================================================================
# SERVER STARTUP
# ============================================================================

def start_server(port=5000):
    """Start the web server"""
    server = HTTPServer(('127.0.0.1', port), LicenseGeneratorHandler)

    print("\n" + "="*70)
    print(" ABoro-Soft License Generator - Web GUI")
    print(" [!] INTERNAL USE ONLY - NOT FOR CUSTOMER DISTRIBUTION")
    print("="*70)
    print(f"\nServer running on: http://localhost:{port}/")
    print(f"Open your browser to: http://localhost:{port}/\n")
    print("Press Ctrl+C to stop the server.\n")
    print("="*70 + "\n")

    # Open browser automatically
    threading.Timer(1.0, lambda: webbrowser.open(f'http://localhost:{port}/')).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Server stopped.\n")
        server.shutdown()
        sys.exit(0)


if __name__ == '__main__':
    try:
        start_server(5000)
    except Exception as e:
        print(f"\n[X] Error: {str(e)}\n")
        sys.exit(1)
