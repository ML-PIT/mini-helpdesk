from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.conf import settings as django_settings
from django.http import JsonResponse
from django.utils.timezone import now as timezone_now
import smtplib
import imaplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

from .models import SystemSettings, AuditLog
from .forms import SystemSettingsForm, TestEmailForm, TestIMAPForm, LicenseForm
from apps.api.license_manager import LicenseManager

logger = logging.getLogger(__name__)


def is_admin(user):
    """Check if user is admin"""
    return user.is_authenticated and user.role == 'admin'


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to check if user is admin"""
    def test_func(self):
        return self.request.user.role == 'admin'

    def handle_no_permission(self):
        messages.error(self.request, 'Sie haben keine Berechtigung für diese Seite.')
        return redirect('/')


def log_audit(user, action, content_type, description, old_values=None, new_values=None, ip_address=None):
    """Log an audit event"""
    if ip_address is None:
        ip_address = get_client_ip(None)

    AuditLog.objects.create(
        action=action,
        user=user,
        content_type=content_type,
        description=description,
        old_values=old_values or {},
        new_values=new_values or {},
        ip_address=ip_address
    )


def get_client_ip(request):
    """Get client IP address from request"""
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    return None


class SettingsView(AdminRequiredMixin, FormView):
    """Main settings page view"""
    template_name = 'admin/settings.html'
    form_class = SystemSettingsForm
    success_url = reverse_lazy('admin:settings')

    def get_object(self):
        """Get or create default settings"""
        return SystemSettings.get_settings()

    def get_initial(self):
        """Load current settings into form"""
        settings_obj = self.get_object()
        initial = {
            'smtp_host': settings_obj.smtp_host,
            'smtp_port': settings_obj.smtp_port,
            'smtp_username': settings_obj.smtp_username,
            'smtp_use_tls': settings_obj.smtp_use_tls,
            'smtp_use_ssl': settings_obj.smtp_use_ssl,

            'imap_enabled': settings_obj.imap_enabled,
            'imap_host': settings_obj.imap_host,
            'imap_port': settings_obj.imap_port,
            'imap_username': settings_obj.imap_username,
            'imap_use_ssl': settings_obj.imap_use_ssl,
            'imap_folder': settings_obj.imap_folder,

            'logo': settings_obj.logo,
            'app_name': settings_obj.app_name,
            'company_name': settings_obj.company_name,
            'site_url': settings_obj.site_url,

            'text_editor': settings_obj.text_editor,
            'max_upload_size_mb': settings_obj.max_upload_size_mb,

            'send_email_notifications': settings_obj.send_email_notifications,
            'email_signature': settings_obj.email_signature,

            'timezone': settings_obj.timezone,
            'language': settings_obj.language,
        }
        return initial

    def get_form_kwargs(self):
        """Pass instance to form"""
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs

    def form_valid(self, form):
        """Save settings and log changes"""
        settings_obj = self.get_object()

        # Store old values for audit log
        old_values = {
            'smtp_host': settings_obj.smtp_host,
            'smtp_port': settings_obj.smtp_port,
            'app_name': settings_obj.app_name,
            'company_name': settings_obj.company_name,
            'text_editor': settings_obj.text_editor,
            'imap_enabled': settings_obj.imap_enabled,
        }

        # Save form
        form.save()

        # Log changes
        log_audit(
            user=self.request.user,
            action='updated',
            content_type='SystemSettings',
            description='System settings updated',
            old_values=old_values,
            new_values={
                'smtp_host': form.cleaned_data.get('smtp_host'),
                'smtp_port': form.cleaned_data.get('smtp_port'),
                'app_name': form.cleaned_data.get('app_name'),
                'company_name': form.cleaned_data.get('company_name'),
                'text_editor': form.cleaned_data.get('text_editor'),
                'imap_enabled': form.cleaned_data.get('imap_enabled'),
            },
            ip_address=get_client_ip(self.request)
        )

        messages.success(self.request, 'Einstellungen erfolgreich gespeichert.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['settings'] = self.get_object()
        context['test_email_form'] = TestEmailForm()
        context['test_imap_form'] = TestIMAPForm()
        context['page_title'] = 'System Einstellungen'
        return context


@login_required
@user_passes_test(is_admin)
def test_email_config(request):
    """Test SMTP email configuration"""
    if request.method == 'POST':
        form = TestEmailForm(request.POST)
        if form.is_valid():
            test_email = form.cleaned_data['test_email']
            settings_obj = SystemSettings.get_settings()

            try:
                # Create test message
                subject = 'Helpdesk - Test Email'
                message = f"""
                <html>
                    <body>
                        <h2>Email Configuration Test</h2>
                        <p>This is a test email from your Helpdesk system.</p>
                        <p><strong>Configuration Details:</strong></p>
                        <ul>
                            <li>SMTP Host: {settings_obj.smtp_host}</li>
                            <li>SMTP Port: {settings_obj.smtp_port}</li>
                            <li>TLS Enabled: {settings_obj.smtp_use_tls}</li>
                        </ul>
                        <p><strong>Sent at:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    </body>
                </html>
                """

                # Send email using Django's email backend
                send_mail(
                    subject,
                    message,
                    django_settings.DEFAULT_FROM_EMAIL,
                    [test_email],
                    html_message=message,
                    fail_silently=False,
                )

                log_audit(
                    user=request.user,
                    action='email_sent',
                    content_type='SystemSettings',
                    description=f'Test email sent to {test_email}',
                    ip_address=get_client_ip(request)
                )

                messages.success(request, f'Test-Email erfolgreich an {test_email} versendet!')
                return redirect('admin:settings')

            except Exception as e:
                logger.error(f'Email test failed: {str(e)}')
                messages.error(request, f'Email-Test fehlgeschlagen: {str(e)}')
                return redirect('admin:settings')

    return redirect('admin:settings')


@login_required
@user_passes_test(is_admin)
def test_imap_config(request):
    """Test IMAP configuration"""
    if request.method == 'POST':
        form = TestIMAPForm(request.POST)
        if form.is_valid():
            settings_obj = SystemSettings.get_settings()
            test_action = form.cleaned_data['test_action']

            if not settings_obj.imap_enabled:
                messages.error(request, 'IMAP ist in den Einstellungen nicht aktiviert.')
                return redirect('admin:settings')

            try:
                # Connect to IMAP server
                imap_class = imaplib.IMAP4_SSL if settings_obj.imap_use_ssl else imaplib.IMAP4
                imap = imap_class(settings_obj.imap_host, settings_obj.imap_port)
                imap.login(settings_obj.imap_username, settings_obj.imap_password)

                if test_action == 'test_connection':
                    messages.success(request, 'IMAP-Verbindung erfolgreich getestet!')

                elif test_action == 'fetch_emails':
                    # Select mailbox
                    imap.select(settings_obj.imap_folder)

                    # Get last 5 emails
                    status, messages_data = imap.search(None, 'ALL')
                    email_ids = messages_data[0].split()[-5:]  # Last 5

                    email_count = len(email_ids)
                    messages.success(request, f'IMAP-Verbindung erfolgreich! {email_count} E-Mails im Postfach gefunden.')

                imap.close()
                imap.logout()

                log_audit(
                    user=request.user,
                    action='updated',
                    content_type='SystemSettings',
                    description=f'IMAP configuration tested: {test_action}',
                    ip_address=get_client_ip(request)
                )

            except Exception as e:
                logger.error(f'IMAP test failed: {str(e)}')
                messages.error(request, f'IMAP-Test fehlgeschlagen: {str(e)}')

        return redirect('admin:settings')

    return redirect('admin:settings')


class AdminDashboardView(AdminRequiredMixin, TemplateView):
    """Admin dashboard view"""
    template_name = 'admin/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get audit logs
        audit_logs = AuditLog.objects.all().order_by('-created_at')[:20]

        context.update({
            'page_title': 'Admin Dashboard',
            'audit_logs': audit_logs,
            'total_users': 0,  # Will be set from signals/context processors
        })

        return context


@login_required
@user_passes_test(is_admin)
def audit_logs_view(request):
    """View audit logs"""
    logs = AuditLog.objects.all().order_by('-created_at')

    # Filter by action if provided
    action = request.GET.get('action')
    if action:
        logs = logs.filter(action=action)

    # Filter by user if provided
    user_id = request.GET.get('user_id')
    if user_id:
        logs = logs.filter(user_id=user_id)

    context = {
        'page_title': 'Audit Logs',
        'logs': logs,
        'action_filter': action,
        'user_filter': user_id,
    }

    return render(request, 'admin/audit_logs.html', context)


@login_required
@user_passes_test(is_admin)
def manage_license(request):
    """Manage license code"""
    settings_obj = SystemSettings.get_settings()
    license_info = None
    form = None

    if request.method == 'POST':
        form = LicenseForm(request.POST)
        if form.is_valid():
            license_code = form.cleaned_data['license_code']
            license_info = form.get_license_info()

            # Update system settings
            settings_obj.license_code = license_code
            settings_obj.license_product = license_info.get('product', 'STARTER')
            settings_obj.license_expiry_date = datetime.strptime(license_info.get('expiry_date'), '%Y-%m-%d').date()
            settings_obj.license_max_agents = license_info.get('max_agents', 5)
            settings_obj.license_features = license_info.get('features', [])
            settings_obj.license_valid = True
            settings_obj.license_last_validated = timezone_now()
            settings_obj.updated_by = request.user
            settings_obj.save()

            # Log audit
            log_audit(
                user=request.user,
                action='updated',
                content_type='SystemSettings',
                description=f'License code updated: {license_info.get("product")}',
                new_values={
                    'license_code': license_code[:10] + '...',  # Don't log full code
                    'license_product': license_info.get('product'),
                    'license_expiry': license_info.get('expiry_date'),
                },
                ip_address=get_client_ip(request)
            )

            messages.success(
                request,
                f'Lizenz erfolgreich aktiviert! Produkt: {license_info.get("product_name")}, '
                f'Gültig bis: {license_info.get("expiry_date")}'
            )
            return redirect('admin:manage_license')
    else:
        form = LicenseForm()
        # Load current license info if exists
        if settings_obj.license_code:
            license_info = LicenseManager.get_license_info(settings_obj.license_code)

    context = {
        'page_title': 'Lizenzverwaltung',
        'form': form,
        'settings': settings_obj,
        'license_info': license_info,
    }

    return render(request, 'admin/manage_license.html', context)
