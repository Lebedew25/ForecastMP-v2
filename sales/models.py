import uuid
from django.db import models
from django.conf import settings
from products.models import Product
from accounts.models import Company


class Warehouse(models.Model):
    """Warehouse locations for inventory tracking"""
    
    WAREHOUSE_TYPE_CHOICES = [
        ('OWN', 'Own Warehouse'),
        ('MARKETPLACE_FF', 'Marketplace Fulfillment'),
    ]
    
    MARKETPLACE_CHOICES = [
        ('WILDBERRIES', 'Wildberries'),
        ('OZON', 'Ozon'),
        ('WEBSITE', 'Website'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='warehouses'
    )
    name = models.CharField(max_length=255)
    warehouse_type = models.CharField(
        max_length=20,
        choices=WAREHOUSE_TYPE_CHOICES,
        default='OWN'
    )
    marketplace = models.CharField(
        max_length=50,
        choices=MARKETPLACE_CHOICES,
        blank=True,
        null=True,
        help_text='Associated marketplace for MARKETPLACE_FF type'
    )
    is_primary = models.BooleanField(
        default=False,
        help_text='Designates the default warehouse'
    )
    metadata = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['company', '-is_primary', 'name']
        indexes = [
            models.Index(fields=['company', 'warehouse_type']),
            models.Index(fields=['company', 'is_primary']),
        ]
        unique_together = ['company', 'name']
    
    def __str__(self):
        return f"{self.company.name} - {self.name}"


class SalesTransaction(models.Model):
    """Individual sale record from marketplaces"""
    
    MARKETPLACE_CHOICES = [
        ('WILDBERRIES', 'Wildberries'),
        ('OZON', 'Ozon'),
        ('WEBSITE', 'Website/E-commerce'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='sales_transactions'
    )
    marketplace = models.CharField(max_length=50, choices=MARKETPLACE_CHOICES)
    
    sale_date = models.DateField(db_index=True)
    quantity = models.IntegerField()
    revenue = models.DecimalField(max_digits=12, decimal_places=2)
    
    # For idempotency and tracking
    transaction_reference = models.CharField(max_length=200, blank=True)
    synced_at = models.DateTimeField(auto_now_add=True)
    
    # Additional sale metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-sale_date', '-synced_at']
        indexes = [
            models.Index(fields=['product', 'sale_date']),
            models.Index(fields=['marketplace', 'sale_date']),
            models.Index(fields=['product', 'marketplace', 'sale_date']),
        ]
    
    def __str__(self):
        return f"{self.product.sku} - {self.quantity} units on {self.sale_date}"


class DailySalesAggregate(models.Model):
    """Pre-aggregated daily sales for performance optimization"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='daily_sales'
    )
    date = models.DateField(db_index=True)
    
    total_quantity = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Per-marketplace breakdown
    wildberries_quantity = models.IntegerField(default=0)
    wildberries_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ozon_quantity = models.IntegerField(default=0)
    ozon_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['product', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['product', 'date']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.product.sku} - {self.total_quantity} units on {self.date}"


class SalesHistory(models.Model):
    """Time-series sales data optimized for forecasting"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='sales_history'
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='sales_history'
    )
    date = models.DateField(db_index=True)
    quantity = models.IntegerField()
    
    # Calculated features for ML
    day_of_week = models.IntegerField()
    is_weekend = models.BooleanField(default=False)
    is_holiday = models.BooleanField(default=False)
    
    # Flags for special events
    is_promo = models.BooleanField(default=False)
    promo_data = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['product', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['product', 'date']),
            models.Index(fields=['company', 'date']),
        ]
    
    def __str__(self):
        return f"{self.product.sku} - {self.quantity} on {self.date}"


class InventoryMovement(models.Model):
    """Track all inventory movements for audit trail"""
    
    MOVEMENT_TYPE_CHOICES = [
        ('INBOUND', 'Inbound - Stock Increase'),
        ('OUTBOUND', 'Outbound - Sales/Consumption'),
        ('TRANSFER', 'Transfer Between Warehouses'),
        ('ADJUSTMENT', 'Manual Adjustment'),
        ('SYNC_UPDATE', 'Marketplace Synchronization'),
        ('INITIAL_LOAD', 'Initial Inventory Load'),
    ]
    
    REFERENCE_TYPE_CHOICES = [
        ('SALE', 'Sales Transaction'),
        ('PURCHASE_ORDER', 'Purchase Order'),
        ('ADJUSTMENT', 'Manual Adjustment'),
        ('SYNC', 'API Synchronization'),
        ('IMPORT', 'Bulk Import'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='inventory_movements'
    )
    warehouse = models.ForeignKey(
        'Warehouse',
        on_delete=models.CASCADE,
        related_name='movements'
    )
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPE_CHOICES)
    
    # Signed quantity: positive for inbound, negative for outbound
    quantity = models.IntegerField(help_text='Positive for inbound, negative for outbound')
    
    movement_date = models.DateTimeField(db_index=True)
    
    # Reference to source of movement
    reference_type = models.CharField(
        max_length=20,
        choices=REFERENCE_TYPE_CHOICES,
        blank=True
    )
    reference_id = models.CharField(
        max_length=255,
        blank=True,
        help_text='ID of related record (sale, PO, etc.)'
    )
    
    notes = models.TextField(blank=True)
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_movements'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-movement_date', '-created_at']
        indexes = [
            models.Index(fields=['product', 'movement_date']),
            models.Index(fields=['warehouse', 'movement_date']),
            models.Index(fields=['product', 'warehouse', 'movement_date']),
            models.Index(fields=['reference_type', 'reference_id']),
        ]
    
    def __str__(self):
        direction = '+' if self.quantity >= 0 else ''
        return f"{self.product.sku} @ {self.warehouse.name}: {direction}{self.quantity} ({self.movement_type})"


class InventorySnapshot(models.Model):
    """Daily inventory level snapshots"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='inventory_snapshots'
    )
    snapshot_date = models.DateField(db_index=True)
    
    quantity_available = models.IntegerField(default=0)
    quantity_reserved = models.IntegerField(default=0)
    
    warehouse = models.ForeignKey(
        'Warehouse',
        on_delete=models.CASCADE,
        related_name='inventory_snapshots',
        null=True,
        blank=True,
        help_text='Warehouse location for this inventory'
    )
    # Legacy field - kept for backward compatibility, renamed to avoid clash
    legacy_warehouse_id = models.CharField(max_length=100, blank=True)
    warehouse_data = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['product', 'warehouse', 'snapshot_date']
        ordering = ['-snapshot_date']
        indexes = [
            models.Index(fields=['product', 'snapshot_date']),
            models.Index(fields=['product', 'warehouse', 'snapshot_date']),
        ]
    
    def __str__(self):
        return f"{self.product.sku} - {self.quantity_available} available on {self.snapshot_date}"
