#!/usr/bin/env python3
"""
ABoro-Soft Helpdesk License Generator
Desktop application for generating license codes
Run as: python license_generator.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from apps.api.license_manager import LicenseManager


class LicenseGeneratorApp:
    """License Generator GUI Application"""

    def __init__(self, root):
        self.root = root
        self.root.title("ABoro-Soft Helpdesk - License Generator v1.0")
        self.root.geometry("900x700")
        self.root.resizable(True, True)

        # Configure style
        style = ttk.Style()
        style.theme_use('clam')

        # Main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights for responsiveness
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="ABoro-Soft Helpdesk License Generator",
            font=("Helvetica", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Product selection
        ttk.Label(main_frame, text="Product:", font=("Helvetica", 10, "bold")).grid(
            row=1, column=0, sticky=tk.W, pady=5
        )

        self.product_var = tk.StringVar(value="STARTER")
        products = list(LicenseManager.PRODUCTS.keys())
        product_combo = ttk.Combobox(
            main_frame,
            textvariable=self.product_var,
            values=products,
            state="readonly",
            width=30
        )
        product_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        product_combo.bind("<<ComboboxSelected>>", self._on_product_change)

        # Product info frame
        info_frame = ttk.LabelFrame(main_frame, text="Product Details", padding="10")
        info_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        info_frame.columnconfigure(0, weight=1)

        self.product_info_text = tk.Text(info_frame, height=6, width=60, state="disabled")
        self.product_info_text.pack(fill=tk.BOTH, expand=True)

        # Duration selection
        ttk.Label(main_frame, text="Duration (months):", font=("Helvetica", 10, "bold")).grid(
            row=3, column=0, sticky=tk.W, pady=5
        )

        self.duration_var = tk.StringVar(value="12")
        duration_spin = ttk.Spinbox(
            main_frame,
            from_=1,
            to=36,
            textvariable=self.duration_var,
            width=10
        )
        duration_spin.grid(row=3, column=1, sticky=tk.W, pady=5)

        # Start date selection
        ttk.Label(main_frame, text="Start Date:", font=("Helvetica", 10, "bold")).grid(
            row=4, column=0, sticky=tk.W, pady=5
        )

        self.start_date_var = tk.StringVar(
            value=datetime.date.today().strftime("%Y-%m-%d")
        )
        start_date_entry = ttk.Entry(main_frame, textvariable=self.start_date_var, width=20)
        start_date_entry.grid(row=4, column=1, sticky=tk.W, pady=5)

        # Generate button
        generate_btn = ttk.Button(
            main_frame,
            text="Generate License Code",
            command=self._generate_license
        )
        generate_btn.grid(row=5, column=0, columnspan=2, pady=20, sticky=(tk.W, tk.E))

        # License code output frame
        output_frame = ttk.LabelFrame(main_frame, text="Generated License Code", padding="10")
        output_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        output_frame.columnconfigure(0, weight=1)

        self.license_code_text = tk.Text(output_frame, height=4, width=60, state="disabled")
        self.license_code_text.pack(fill=tk.BOTH, expand=True)

        # Copy button
        copy_btn = ttk.Button(
            main_frame,
            text="Copy to Clipboard",
            command=self._copy_to_clipboard
        )
        copy_btn.grid(row=7, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))

        # Cost calculation frame
        cost_frame = ttk.LabelFrame(main_frame, text="Cost Calculation", padding="10")
        cost_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        cost_frame.columnconfigure(0, weight=1)

        self.cost_text = tk.Text(cost_frame, height=5, width=60, state="disabled")
        self.cost_text.pack(fill=tk.BOTH, expand=True)

        # Update cost on product/duration change
        product_combo.bind("<<ComboboxSelected>>", self._update_cost)
        duration_spin.bind("<KeyRelease>", self._update_cost)

        # Footer
        footer_label = ttk.Label(
            main_frame,
            text="Generated codes are valid based on start date and duration. Database-independent validation.",
            font=("Helvetica", 8, "italic"),
            foreground="gray"
        )
        footer_label.grid(row=9, column=0, columnspan=2, pady=10)

        # Initial updates
        self._on_product_change()
        self._update_cost()

    def _on_product_change(self, event=None):
        """Update product info when product is selected"""
        product = self.product_var.get()
        if product in LicenseManager.PRODUCTS:
            info = LicenseManager.PRODUCTS[product]

            info_text = f"""Product: {info['name']}
Max Agents: {info['agents']}
Monthly Price: €{info['monthly_price']}
Features: {', '.join(info['features'])}"""

            self.product_info_text.config(state="normal")
            self.product_info_text.delete("1.0", tk.END)
            self.product_info_text.insert("1.0", info_text)
            self.product_info_text.config(state="disabled")

            self._update_cost()

    def _update_cost(self, event=None):
        """Calculate and display cost"""
        try:
            product = self.product_var.get()
            duration = int(self.duration_var.get())

            cost_info = LicenseManager.calculate_license_cost(product, duration)

            cost_text = f"""Setup Fee: €{cost_info['setup_fee']}
Monthly Price: €{cost_info['monthly_price']} × {cost_info['duration_months']} months = €{cost_info['monthly_total']}
Total Cost: €{cost_info['total_cost']}
Cost per Day: €{cost_info['cost_per_day']}"""

            self.cost_text.config(state="normal")
            self.cost_text.delete("1.0", tk.END)
            self.cost_text.insert("1.0", cost_text)
            self.cost_text.config(state="disabled")

        except Exception as e:
            self.cost_text.config(state="normal")
            self.cost_text.delete("1.0", tk.END)
            self.cost_text.insert("1.0", f"Error: {str(e)}")
            self.cost_text.config(state="disabled")

    def _generate_license(self):
        """Generate license code"""
        try:
            product = self.product_var.get()
            duration = int(self.duration_var.get())
            start_date_str = self.start_date_var.get()

            # Parse start date
            try:
                start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror(
                    "Invalid Date",
                    "Please enter date in format: YYYY-MM-DD\nExample: 2025-10-31"
                )
                return

            # Validate duration
            if not (1 <= duration <= 36):
                messagebox.showerror("Invalid Duration", "Duration must be between 1 and 36 months")
                return

            # Generate license
            license_code = LicenseManager.generate_license_code(product, duration, start_date)

            # Get license info for verification
            is_valid, msg = LicenseManager.validate_license(license_code)
            license_info = LicenseManager.get_license_info(license_code)

            # Display license code
            self.license_code_text.config(state="normal")
            self.license_code_text.delete("1.0", tk.END)

            display_text = f"""License Code:
{license_code}

Product: {license_info['product_name']}
Valid Until: {license_info['expiry_date']}
Days Valid: {license_info['duration_months']} months ({license_info['days_remaining']} days)
Max Agents: {license_info['max_agents']}
Status: ✓ {msg}"""

            self.license_code_text.insert("1.0", display_text)
            self.license_code_text.config(state="disabled")

            messagebox.showinfo("Success", f"License code generated successfully!\n\n{license_code}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate license: {str(e)}")

    def _copy_to_clipboard(self):
        """Copy license code to clipboard"""
        try:
            self.license_code_text.config(state="normal")
            content = self.license_code_text.get("1.0", tk.END)
            self.license_code_text.config(state="disabled")

            # Extract just the license code (first line after "License Code:")
            lines = content.strip().split('\n')
            if len(lines) > 1:
                license_code = lines[1].strip()
                self.root.clipboard_clear()
                self.root.clipboard_append(license_code)
                messagebox.showinfo("Success", f"Copied to clipboard:\n{license_code}")
            else:
                messagebox.showwarning("No Code", "Please generate a license code first")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy: {str(e)}")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = LicenseGeneratorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
