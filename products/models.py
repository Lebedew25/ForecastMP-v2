import uuid
from django.db import models
from accounts.models import Company


class Product(models.Model):
    """Master product record with unified SKU"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='products'
    )
    sku = models.CharField(max_length=100, db_index=True)
    name = models.CharField(max_length=500)
    category = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    attributes = models.JSONField(default=dict, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['company', 'sku']
        ordering = ['company', 'sku']
        indexes = [
            models.Index(fields=['company', 'sku']),
            models.Index(fields=['company', 'is_active']),
            models.Index(fields=['company', 'category']),
        ]
    
    def __str__(self):
        return f"{self.sku} - {self.name}"


class MarketplaceProduct(models.Model):
    """Platform-specific product mapping"""
    
    MARKETPLACE_CHOICES = [
        ('WILDBERRIES', 'Wildberries'),
        ('OZON', 'Ozon'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='marketplace_mappings'
    )
    marketplace = models.CharField(max_length=50, choices=MARKETPLACE_CHOICES)
    external_id = models.CharField(max_length=200)
    barcode = models.CharField(max_length=200, blank=True)
    
    # Marketplace-specific data
    external_data = models.JSONField(default=dict, blank=True)
    
    active = models.BooleanField(default=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['product', 'marketplace']
        ordering = ['product', 'marketplace']
        indexes = [
            models.Index(fields=['marketplace', 'external_id']),
            models.Index(fields=['product', 'active']),
        ]
    
    def __str__(self):
        return f"{self.product.sku} @ {self.marketplace}"


class ProductAttributes(models.Model):
    """Additional product metadata and attributes"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='extended_attributes'
    )
    
    # Physical attributes
    brand = models.CharField(max_length=200, blank=True)
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        help_text='Weight in kg'
    )
    length = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Length in cm'
    )
    width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Width in cm'
    )
    height = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Height in cm'
    )
    
    # Business attributes
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Procurement settings
    reorder_threshold_days = models.IntegerField(
        default=7,
        help_text='Days of inventory runway that triggers reorder'
    )
    lead_time_days = models.IntegerField(
        default=14,
        help_text='Days from order to delivery'
    )
    safety_stock_days = models.IntegerField(
        default=3,
        help_text='Buffer days beyond lead time'
    )
    minimum_order_quantity = models.IntegerField(
        default=1,
        help_text='Minimum viable order size'
    )
    
    # Additional metadata
    tags = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Product Attributes'
    
    def __str__(self):
        return f"Attributes for {self.product.sku}"
