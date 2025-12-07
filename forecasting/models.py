import uuid
from django.db import models
from products.models import Product


class Forecast(models.Model):
    """Daily demand forecast for products"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='forecasts'
    )
    forecast_date = models.DateField(db_index=True)
    
    predicted_quantity = models.IntegerField()
    confidence_lower = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Lower bound of prediction interval'
    )
    confidence_upper = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Upper bound of prediction interval'
    )
    
    # Model metadata
    model_version = models.CharField(max_length=50, default='v1.0')
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text='Model confidence percentage'
    )
    
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['product', 'forecast_date']
        ordering = ['forecast_date']
        indexes = [
            models.Index(fields=['product', 'forecast_date']),
            models.Index(fields=['generated_at']),
        ]
    
    def __str__(self):
        return f"{self.product.sku} - {self.predicted_quantity} on {self.forecast_date}"


class ForecastAccuracy(models.Model):
    """Track forecast performance metrics"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='forecast_accuracy'
    )
    
    # Evaluation period
    evaluation_date = models.DateField(db_index=True)
    forecast_date = models.DateField()
    
    # Metrics
    predicted_value = models.IntegerField()
    actual_value = models.IntegerField()
    absolute_error = models.IntegerField()
    percentage_error = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Model info
    model_version = models.CharField(max_length=50)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-evaluation_date']
        indexes = [
            models.Index(fields=['product', 'evaluation_date']),
        ]
    
    def __str__(self):
        return f"{self.product.sku} - {self.percentage_error}% error"
