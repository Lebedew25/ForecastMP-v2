import uuid
from django.db import models
from accounts.models import Company


class MarketplaceCredential(models.Model):
    """Store API credentials for marketplace integrations"""
    
    MARKETPLACE_CHOICES = [
        ('WILDBERRIES', 'Wildberries'),
        ('OZON', 'Ozon'),
        ('WEBSITE', 'Website/E-commerce'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='marketplace_credentials'
    )
    marketplace = models.CharField(max_length=50, choices=MARKETPLACE_CHOICES)
    
    # Credentials (should be encrypted in production)
    api_key = models.CharField(max_length=500)
    api_secret = models.CharField(max_length=500, blank=True)
    
    # Additional settings
    settings = models.JSONField(default=dict, blank=True)
    
    is_active = models.BooleanField(default=True)
    last_sync_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['company', 'marketplace']
        ordering = ['company', 'marketplace']
    
    def __str__(self):
        return f"{self.company.name} - {self.marketplace}"


class SyncLog(models.Model):
    """Log synchronization operations"""
    
    STATUS_CHOICES = [
        ('STARTED', 'Started'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('PARTIAL', 'Partial Success'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    credential = models.ForeignKey(
        MarketplaceCredential,
        on_delete=models.CASCADE,
        related_name='sync_logs'
    )
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='STARTED')
    
    # Metrics
    records_fetched = models.IntegerField(default=0)
    records_saved = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    
    # Error tracking
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['credential', '-started_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.credential.marketplace} sync - {self.status} at {self.started_at}"
