from django.contrib import admin
from .models import Product, MarketplaceProduct, ProductAttributes


class MarketplaceProductInline(admin.TabularInline):
    model = MarketplaceProduct
    extra = 0
    fields = ['marketplace', 'external_id', 'barcode', 'active', 'last_synced_at']
    readonly_fields = ['last_synced_at']


class ProductAttributesInline(admin.StackedInline):
    model = ProductAttributes
    can_delete = False
    fields = [
        ('brand', 'category'),
        ('weight', 'length', 'width', 'height'),
        ('cost_price', 'selling_price'),
        ('reorder_threshold_days', 'lead_time_days', 'safety_stock_days', 'minimum_order_quantity'),
        'tags',
        'notes'
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['sku', 'name', 'company', 'category', 'is_active', 'created_at']
    list_filter = ['company', 'is_active', 'category']
    search_fields = ['sku', 'name', 'category']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [MarketplaceProductInline, ProductAttributesInline]
    
    fieldsets = (
        (None, {
            'fields': ('id', 'company', 'sku', 'name', 'category', 'is_active')
        }),
        ('Details', {
            'fields': ('description', 'attributes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MarketplaceProduct)
class MarketplaceProductAdmin(admin.ModelAdmin):
    list_display = ['product', 'marketplace', 'external_id', 'barcode', 'active', 'last_synced_at']
    list_filter = ['marketplace', 'active']
    search_fields = ['product__sku', 'product__name', 'external_id', 'barcode']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_synced_at']
    
    fieldsets = (
        (None, {
            'fields': ('id', 'product', 'marketplace', 'external_id', 'barcode', 'active')
        }),
        ('Sync Info', {
            'fields': ('last_synced_at', 'external_data')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProductAttributes)
class ProductAttributesAdmin(admin.ModelAdmin):
    list_display = ['product', 'brand', 'weight', 'cost_price', 'selling_price']
    search_fields = ['product__sku', 'product__name', 'brand']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('id', 'product')
        }),
        ('Physical Attributes', {
            'fields': ('brand', 'weight', 'length', 'width', 'height')
        }),
        ('Business', {
            'fields': ('cost_price', 'selling_price')
        }),
        ('Procurement Settings', {
            'fields': ('reorder_threshold_days', 'lead_time_days', 'safety_stock_days', 'minimum_order_quantity')
        }),
        ('Additional', {
            'fields': ('tags', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
