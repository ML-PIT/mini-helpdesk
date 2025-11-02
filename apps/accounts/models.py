from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""

    def create_user(self, email, username, password=None, **extra_fields):
        """Create and save a regular user"""
        if not email:
            raise ValueError(_('The Email field must be set'))
        if not username:
            raise ValueError(_('The Username field must be set'))

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model with role-based access control"""

    ROLE_CHOICES = [
        ('admin', _('Administrator')),
        ('support_agent', _('Support Agent')),
        ('customer', _('Customer')),
    ]

    SUPPORT_LEVEL_CHOICES = [
        (1, _('Level 1 - Basic Support')),
        (2, _('Level 2 - Technical Support')),
        (3, _('Level 3 - Expert Support')),
        (4, _('Level 4 - Senior Expert / Team Lead')),
    ]

    # Basic information
    username = models.CharField(_('username'), max_length=80, unique=True, db_index=True)
    email = models.EmailField(_('email address'), max_length=120, unique=True, db_index=True)
    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100)

    # Role and permissions
    role = models.CharField(_('role'), max_length=20, choices=ROLE_CHOICES,
                          default='customer', db_index=True)
    support_level = models.IntegerField(_('support level'), choices=SUPPORT_LEVEL_CHOICES,
                                       null=True, blank=True,
                                       help_text=_('Support level for agents (1-3). Only applicable for support_agent role.'))

    # Microsoft OAuth2 integration
    microsoft_id = models.CharField(_('Microsoft ID'), max_length=100,
                                   unique=True, null=True, blank=True)
    microsoft_token = models.TextField(_('Microsoft Token'), null=True, blank=True)

    # Profile information
    phone = models.CharField(_('phone'), max_length=20, blank=True, null=True)
    department = models.CharField(_('department'), max_length=100, blank=True, null=True)
    location = models.CharField(_('location'), max_length=100, blank=True, null=True)
    
    # Address information for customers
    street = models.CharField(_('street'), max_length=200, blank=True, null=True)
    postal_code = models.CharField(_('postal code'), max_length=10, blank=True, null=True)
    city = models.CharField(_('city'), max_length=100, blank=True, null=True)
    country = models.CharField(_('country'), max_length=100, blank=True, null=True, default='Deutschland')

    # Status and metadata
    is_active = models.BooleanField(_('active'), default=True, db_index=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    email_verified = models.BooleanField(_('email verified'), default=False)
    force_password_change = models.BooleanField(_('force password change on next login'),
                                               default=False,
                                               help_text=_('If True, user must change password on next login'))
    last_login = models.DateTimeField(_('last login'), null=True, blank=True)
    last_activity = models.DateTimeField(_('last activity'), null=True, blank=True, 
                                        help_text=_('Last time user was active (for online status)'))
    created_at = models.DateTimeField(_('created at'), default=timezone.now, db_index=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        """Return the user's full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_online(self):
        """Check if user is considered online (active within last 5 minutes)"""
        if not self.last_activity:
            return False
        
        from datetime import timedelta
        return timezone.now() - self.last_activity < timedelta(minutes=5)
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])

    def has_permission(self, permission):
        """Check if user has specific permission based on role"""
        permissions = {
            'admin': ['all'],
            'support_agent': ['view_assigned_tickets', 'view_unassigned_tickets', 'update_tickets',
                            'create_tickets', 'self_assign', 'escalate_tickets', 'close_tickets'],
            'customer': ['view_own_tickets', 'create_tickets', 'comment_own_tickets']
        }

        role_permissions = permissions.get(self.role, [])
        return 'all' in role_permissions or permission in role_permissions

    def can_access_ticket(self, ticket):
        """Check if user can access a specific ticket"""
        if self.role == 'admin':
            return True
        elif self.role == 'support_agent':
            return True  # Agents can access all tickets
        elif self.role == 'customer':
            return ticket.created_by == self
        return False

    def can_escalate_to_level(self, target_level):
        """Check if agent can escalate to target support level"""
        if self.role != 'support_agent' or not self.support_level:
            return False
        return target_level > self.support_level and target_level <= 4

    def get_dashboard_stats(self):
        """Get dashboard statistics for the user"""
        from apps.tickets.models import Ticket

        if self.role == 'customer':
            return {
                'my_tickets': Ticket.objects.filter(created_by=self).count(),
                'open_tickets': Ticket.objects.filter(created_by=self, status__in=['open', 'in_progress']).count(),
                'resolved_tickets': Ticket.objects.filter(created_by=self, status='resolved').count(),
                'closed_tickets': Ticket.objects.filter(created_by=self, status='closed').count()
            }
        elif self.role == 'support_agent':
            return {
                'my_assigned': Ticket.objects.filter(assigned_to=self).exclude(status='closed').count(),
                'unassigned': Ticket.objects.filter(assigned_to__isnull=True, status='open').count(),
                'in_progress': Ticket.objects.filter(assigned_to=self, status='in_progress').count(),
                'resolved': Ticket.objects.filter(assigned_to=self, status='resolved').count()
            }
        else:  # admin
            return {
                'total_tickets': Ticket.objects.count(),
                'open_tickets': Ticket.objects.filter(status='open').count(),
                'in_progress': Ticket.objects.filter(status='in_progress').count(),
                'resolved': Ticket.objects.filter(status='resolved').count(),
                'closed_today': Ticket.objects.filter(status='closed', closed_at__date=timezone.now().date()).count()
            }

    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary for API responses"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'role': self.role,
            'support_level': self.support_level,
            'phone': self.phone,
            'department': self.department,
            'location': self.location,
            'street': self.street,
            'postal_code': self.postal_code,
            'city': self.city,
            'country': self.country,
            'is_active': self.is_active,
            'email_verified': self.email_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat()
        }

        if include_sensitive and self.role == 'admin':
            data['microsoft_id'] = self.microsoft_id

        return data
