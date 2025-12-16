from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Company, User, Permission, TelegramSubscription,
    Subscription, PlanUsage, Invoice
)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_subscription_plan', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'is_active')
        }),
        ('Settings', {
            'fields': ('settings',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_subscription_plan(self, obj):
        if hasattr(obj, 'subscription'):
            return f"{obj.subscription.plan} ({obj.subscription.status})"
        return "No subscription"
    get_subscription_plan.short_description = 'Subscription'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'company', 'role', 'is_active']
    list_filter = ['is_active', 'is_staff', 'role', 'company']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']
    readonly_fields = ['id', 'date_joined', 'last_login']
    
    fieldsets = (
        (None, {
            'fields': ('id', 'email', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name')
        }),
        ('Company & Role', {
            'fields': ('company', 'role')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('date_joined', 'last_login')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'company', 'role')
        }),
    )


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'resource', 'action', 'is_granted', 'created_at']
    list_filter = ['resource', 'action', 'is_granted']
    search_fields = ['user__email']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        (None, {
            'fields': ('id', 'user', 'resource', 'action', 'is_granted')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(TelegramSubscription)
class TelegramSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'chat_id', 'critical_alerts_enabled', 'daily_digest_enabled', 'is_active']
    list_filter = ['critical_alerts_enabled', 'daily_digest_enabled', 'weekly_report_enabled', 'is_active']
    search_fields = ['user__email', 'chat_id']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('id', 'user', 'chat_id', 'is_active')
        }),
        ('Notification Preferences', {
            'fields': (
                'critical_alerts_enabled',
                'daily_digest_enabled',
                'weekly_report_enabled',
                'digest_time',
                'custom_threshold_days'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['company', 'plan', 'status', 'billing_cycle', 'next_billing_date', 'trial_days_left']
    list_filter = ['plan', 'status', 'billing_cycle']
    search_fields = ['company__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('id', 'company', 'plan', 'status', 'billing_cycle')
        }),
        ('Trial Period', {
            'fields': ('trial_start_date', 'trial_end_date')
        }),
        ('Subscription Dates', {
            'fields': ('start_date', 'end_date', 'next_billing_date')
        }),
        ('Payment Info', {
            'fields': ('payment_method_type', 'payment_method_last4')
        }),
        ('Pricing', {
            'fields': ('monthly_price', 'annual_price')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PlanUsage)
class PlanUsageAdmin(admin.ModelAdmin):
    list_display = [
        'company',
        'active_skus_count',
        'active_integrations_count',
        'active_warehouses_count',
        'active_users_count',
        'last_updated'
    ]
    readonly_fields = ['id', 'last_updated']
    search_fields = ['company__name']
    
    fieldsets = (
        (None, {
            'fields': ('id', 'company')
        }),
        ('Current Usage', {
            'fields': (
                'active_skus_count',
                'active_integrations_count',
                'active_warehouses_count',
                'active_users_count',
                'api_requests_this_month'
            )
        }),
        ('Timestamps', {
            'fields': ('last_updated',)
        }),
    )


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_number',
        'subscription',
        'invoice_date',
        'amount',
        'currency',
        'status',
        'paid_date'
    ]
    list_filter = ['status', 'invoice_date', 'currency']
    search_fields = ['invoice_number', 'subscription__company__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('id', 'subscription', 'invoice_number', 'status')
        }),
        ('Dates', {
            'fields': ('invoice_date', 'due_date', 'paid_date')
        }),
        ('Amount', {
            'fields': ('amount', 'currency')
        }),
        ('Payment', {
            'fields': ('payment_method',)
        }),
        ('Details', {
            'fields': ('description', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
