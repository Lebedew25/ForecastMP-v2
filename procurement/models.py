import uuid
from django.db import models
from products.models import Product
from accounts.models import Company


class ProcurementRecommendation(models.Model):
    """Actionable procurement recommendations based on forecasts"""
    
    ACTION_CATEGORIES = [
        ('ORDER_TODAY', 'Order Today'),
        ('ALREADY_ORDERED', 'Already Ordered'),
        ('ATTENTION_REQUIRED', 'Attention Required'),
        ('NORMAL', 'Normal - No Action Needed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='procurement_recommendations'
    )
    analysis_date = models.DateField(db_index=True)
    
    # Current inventory status
    current_stock = models.IntegerField()
    daily_burn_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Average daily sales'
    )
    
    # Calculated metrics
    runway_days = models.IntegerField(
        help_text='Days until stockout at current burn rate'
    )
    stockout_date = models.DateField(
        null=True,
        blank=True,
        help_text='Predicted date of stockout'
    )
    
    # Recommendation
    recommended_quantity = models.IntegerField(
        default=0,
        help_text='Suggested order quantity'
    )
    action_category = models.CharField(
        max_length=50,
        choices=ACTION_CATEGORIES,
        default='NORMAL'
    )
    priority_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text='Urgency score (0-100)'
    )
    
    # Additional context
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['product', 'analysis_date']
        ordering = ['-priority_score', 'runway_days']
        indexes = [
            models.Index(fields=['product', 'analysis_date']),
            models.Index(fields=['action_category', 'analysis_date']),
            models.Index(fields=['-priority_score']),
        ]
    
    def __str__(self):
        return f"{self.product.sku} - {self.action_category} ({self.runway_days} days)"


class PurchaseOrder(models.Model):
    """Track purchase orders placed with suppliers"""
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('CONFIRMED', 'Confirmed'),
        ('IN_TRANSIT', 'In Transit'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='purchase_orders'
    )
    
    po_number = models.CharField(max_length=100, unique=True)
    order_date = models.DateField(db_index=True)
    expected_delivery = models.DateField(
        null=True,
        blank=True,
        help_text='Expected delivery date'
    )
    actual_delivery = models.DateField(
        null=True,
        blank=True,
        help_text='Actual delivery date'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )
    
    supplier_name = models.CharField(max_length=255, blank=True)
    supplier_data = models.JSONField(default=dict, blank=True)
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-order_date']
        indexes = [
            models.Index(fields=['company', 'order_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"PO #{self.po_number} - {self.status}"


class PurchaseOrderItem(models.Model):
    """Individual items in a purchase order"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='po_items'
    )
    
    quantity_ordered = models.IntegerField()
    quantity_received = models.IntegerField(default=0)
    
    unit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['purchase_order', 'product']
        ordering = ['purchase_order', 'product']
    
    def __str__(self):
        return f"{self.product.sku} x {self.quantity_ordered} in {self.purchase_order.po_number}"
    
    @property
    def quantity_in_transit(self):
        """Quantity still to be received"""
        return max(0, self.quantity_ordered - self.quantity_received)
