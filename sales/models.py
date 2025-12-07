import uuid
from django.db import models
from products.models import Product
from accounts.models import Company


class SalesTransaction(models.Model):
    """Individual sale record from marketplaces"""
    
    MARKETPLACE_CHOICES = [
        ('WILDBERRIES', 'Wildberries'),
        ('OZON', 'Ozon'),
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
    
    warehouse_id = models.CharField(max_length=100, blank=True)
    warehouse_data = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['product', 'snapshot_date', 'warehouse_id']
        ordering = ['-snapshot_date']
        indexes = [
            models.Index(fields=['product', 'snapshot_date']),
        ]
    
    def __str__(self):
        return f"{self.product.sku} - {self.quantity_available} available on {self.snapshot_date}"
