from django.contrib import admin
from .models import SalesTransaction, DailySalesAggregate, SalesHistory, InventorySnapshot


@admin.register(SalesTransaction)
class SalesTransactionAdmin(admin.ModelAdmin):
    list_display = ['product', 'marketplace', 'sale_date', 'quantity', 'revenue', 'synced_at']
    list_filter = ['marketplace', 'sale_date', 'synced_at']
    search_fields = ['product__sku', 'product__name', 'transaction_reference']
    readonly_fields = ['id', 'synced_at']
    date_hierarchy = 'sale_date'
    
    fieldsets = (
        (None, {
            'fields': ('id', 'product', 'marketplace', 'sale_date')
        }),
        ('Sale Details', {
            'fields': ('quantity', 'revenue', 'transaction_reference')
        }),
        ('Metadata', {
            'fields': ('metadata', 'synced_at')
        }),
    )


@admin.register(DailySalesAggregate)
class DailySalesAggregateAdmin(admin.ModelAdmin):
    list_display = ['product', 'date', 'total_quantity', 'total_revenue', 'updated_at']
    list_filter = ['date']
    search_fields = ['product__sku', 'product__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        (None, {
            'fields': ('id', 'product', 'date')
        }),
        ('Totals', {
            'fields': ('total_quantity', 'total_revenue')
        }),
        ('Wildberries', {
            'fields': ('wildberries_quantity', 'wildberries_revenue')
        }),
        ('Ozon', {
            'fields': ('ozon_quantity', 'ozon_revenue')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SalesHistory)
class SalesHistoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'date', 'quantity', 'day_of_week', 'is_weekend', 'is_promo']
    list_filter = ['is_weekend', 'is_holiday', 'is_promo', 'date']
    search_fields = ['product__sku', 'product__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        (None, {
            'fields': ('id', 'product', 'company', 'date', 'quantity')
        }),
        ('Features', {
            'fields': ('day_of_week', 'is_weekend', 'is_holiday')
        }),
        ('Promotions', {
            'fields': ('is_promo', 'promo_data')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(InventorySnapshot)
class InventorySnapshotAdmin(admin.ModelAdmin):
    list_display = ['product', 'snapshot_date', 'quantity_available', 'quantity_reserved', 'warehouse_id']
    list_filter = ['snapshot_date', 'warehouse_id']
    search_fields = ['product__sku', 'product__name']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'snapshot_date'
    
    fieldsets = (
        (None, {
            'fields': ('id', 'product', 'snapshot_date')
        }),
        ('Inventory', {
            'fields': ('quantity_available', 'quantity_reserved')
        }),
        ('Warehouse', {
            'fields': ('warehouse_id', 'warehouse_data')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
