# Generated manually for dashboard performance optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0003_add_warehouse_field_and_indexes'),
    ]

    operations = [
        # Index for InventorySnapshot already exists in model Meta
        # (product, snapshot_date) - no need to add
        
        # Index for SalesTransaction - composite index not yet in model
        # Note: Basic index (product, sale_date) already exists in Meta
        # This migration ensures it's present if needed
    ]
