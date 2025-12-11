from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Company, User, Permission, TelegramSubscription


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'subscription_tier', 'is_active', 'created_at']
    list_filter = ['subscription_tier', 'is_active']
    search_fields = ['name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'subscription_tier', 'is_active')
        }),
        ('Settings', {
            'fields': ('settings',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


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
