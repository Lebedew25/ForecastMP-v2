import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from datetime import time, timedelta, date


class Company(models.Model):
    """Tenant organization for multi-tenancy"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    settings = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = 'Companies'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model with company-based multi-tenancy"""
    
    ROLE_CHOICES = [
        ('ADMIN', 'Administrator'),
        ('MANAGER', 'Manager'),
        ('ANALYST', 'Analyst'),
        ('VIEWER', 'Viewer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='VIEWER')
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        ordering = ['email']
        indexes = [
            models.Index(fields=['company', 'email']),
        ]
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email
    
    def get_short_name(self):
        return self.first_name or self.email


class Permission(models.Model):
    """Access control rules for users"""
    
    ACTION_CHOICES = [
        ('VIEW', 'View'),
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('EXPORT', 'Export'),
    ]
    
    RESOURCE_CHOICES = [
        ('PRODUCTS', 'Products'),
        ('SALES', 'Sales'),
        ('FORECASTS', 'Forecasts'),
        ('PROCUREMENT', 'Procurement'),
        ('INTEGRATIONS', 'Integrations'),
        ('SETTINGS', 'Settings'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='custom_permissions'
    )
    resource = models.CharField(max_length=50, choices=RESOURCE_CHOICES)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    is_granted = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'resource', 'action']
        ordering = ['user', 'resource', 'action']
    
    def __str__(self):
        grant_status = 'allowed' if self.is_granted else 'denied'
        return f"{self.user.email} - {grant_status} {self.action} on {self.resource}"


class TelegramSubscription(models.Model):
    """Telegram bot subscription for notifications"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='telegram_subscription'
    )
    chat_id = models.CharField(
        max_length=255,
        unique=True,
        help_text='Telegram chat ID for this user'
    )
    
    # Notification preferences
    critical_alerts_enabled = models.BooleanField(default=True)
    daily_digest_enabled = models.BooleanField(default=True)
    weekly_report_enabled = models.BooleanField(default=True)
    
    digest_time = models.TimeField(
        default=time(8, 0),  # 8:00 AM
        help_text='Time to send daily digest'
    )
    
    custom_threshold_days = models.IntegerField(
        null=True,
        blank=True,
        help_text='Custom alert threshold, overrides company default'
    )
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user']
        indexes = [
            models.Index(fields=['chat_id']),
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - Telegram: {self.chat_id}"


class Subscription(models.Model):
    """Subscription plan management for companies"""
    
    PLAN_CHOICES = [
        ('START', 'Start'),
        ('MINI', 'Mini'),
        ('PRO', 'Pro'),
        ('ENTERPRISE', 'Enterprise'),
    ]
    
    BILLING_CYCLE_CHOICES = [
        ('MONTHLY', 'Monthly'),
        ('ANNUAL', 'Annual'),
    ]
    
    STATUS_CHOICES = [
        ('TRIAL', 'Trial'),
        ('ACTIVE', 'Active'),
        ('PAST_DUE', 'Past Due'),
        ('CANCELLED', 'Cancelled'),
        ('EXPIRED', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name='subscription'
    )
    
    plan = models.CharField(
        max_length=20,
        choices=PLAN_CHOICES,
        default='START'
    )
    billing_cycle = models.CharField(
        max_length=20,
        choices=BILLING_CYCLE_CHOICES,
        default='MONTHLY'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='TRIAL'
    )
    
    # Trial management
    trial_start_date = models.DateField(null=True, blank=True)
    trial_end_date = models.DateField(null=True, blank=True)
    
    # Subscription dates
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    next_billing_date = models.DateField(null=True, blank=True)
    
    # Payment information (simplified - in production use payment gateway)
    payment_method_last4 = models.CharField(max_length=4, blank=True)
    payment_method_type = models.CharField(
        max_length=50,
        blank=True,
        help_text='e.g., Visa, Mastercard, Bank Transfer'
    )
    
    # Pricing
    monthly_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Monthly price in RUB'
    )
    annual_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Annual price in RUB'
    )
    
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company', 'status']),
            models.Index(fields=['status', 'next_billing_date']),
        ]
    
    def __str__(self):
        return f"{self.company.name} - {self.plan} ({self.status})"
    
    @property
    def is_trial(self):
        """Check if subscription is in trial period"""
        return self.status == 'TRIAL'
    
    @property
    def trial_days_left(self):
        """Calculate days remaining in trial"""
        if not self.is_trial or not self.trial_end_date:
            return 0
        delta = self.trial_end_date - date.today()
        return max(0, delta.days)
    
    @property
    def is_active(self):
        """Check if subscription is active (trial or paid)"""
        return self.status in ['TRIAL', 'ACTIVE']
    
    def get_plan_limits(self):
        """Get current plan limits"""
        limits = {
            'START': {
                'max_skus': 100,
                'max_integrations': 1,
                'max_warehouses': 1,
                'ai_forecasting': False,
                'telegram_notifications': False,
                'report_frequency': 'WEEKLY',
                'max_users': 2,
            },
            'MINI': {
                'max_skus': 500,
                'max_integrations': 2,
                'max_warehouses': 3,
                'ai_forecasting': True,
                'telegram_notifications': False,
                'report_frequency': 'DAILY',
                'max_users': 5,
            },
            'PRO': {
                'max_skus': 2000,
                'max_integrations': None,  # Unlimited
                'max_warehouses': None,  # Unlimited
                'ai_forecasting': True,
                'telegram_notifications': True,
                'report_frequency': 'REALTIME',
                'max_users': 20,
            },
            'ENTERPRISE': {
                'max_skus': None,  # Unlimited
                'max_integrations': None,  # Unlimited
                'max_warehouses': None,  # Unlimited
                'ai_forecasting': True,
                'telegram_notifications': True,
                'report_frequency': 'REALTIME',
                'max_users': None,  # Unlimited
                'api_access': True,
                'white_label': True,
            },
        }
        return limits.get(self.plan, limits['START'])


class PlanUsage(models.Model):
    """Track current usage against plan limits"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name='plan_usage'
    )
    
    # Current usage metrics
    active_skus_count = models.IntegerField(default=0)
    active_integrations_count = models.IntegerField(default=0)
    active_warehouses_count = models.IntegerField(default=0)
    active_users_count = models.IntegerField(default=0)
    
    # API usage (for Enterprise plan)
    api_requests_this_month = models.IntegerField(default=0)
    
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Plan usage'
    
    def __str__(self):
        return f"{self.company.name} - Usage tracking"
    
    def get_usage_percentage(self, metric):
        """Calculate usage percentage for a specific metric"""
        if not hasattr(self.company, 'subscription'):
            return 0
        
        limits = self.company.subscription.get_plan_limits()
        current_usage = getattr(self, f'{metric}_count', 0)
        limit = limits.get(f'max_{metric}s')
        
        if limit is None:  # Unlimited
            return 0
        if limit == 0:
            return 100
        
        return (current_usage / limit) * 100
    
    def is_approaching_limit(self, metric, threshold=80):
        """Check if usage is approaching limit (default 80%)"""
        return self.get_usage_percentage(metric) >= threshold
    
    def is_at_limit(self, metric):
        """Check if usage has reached the limit"""
        if not hasattr(self.company, 'subscription'):
            return False
        
        limits = self.company.subscription.get_plan_limits()
        current_usage = getattr(self, f'{metric}_count', 0)
        limit = limits.get(f'max_{metric}s')
        
        if limit is None:  # Unlimited
            return False
        
        return current_usage >= limit


class Invoice(models.Model):
    """Billing invoices for subscriptions"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    
    invoice_number = models.CharField(max_length=100, unique=True)
    invoice_date = models.DateField()
    due_date = models.DateField()
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='RUB')
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    
    paid_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=100, blank=True)
    
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-invoice_date']
        indexes = [
            models.Index(fields=['subscription', 'status']),
            models.Index(fields=['invoice_date']),
        ]
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.amount} {self.currency}"
