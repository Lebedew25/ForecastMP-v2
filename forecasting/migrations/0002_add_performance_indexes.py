# Generated manually for dashboard performance optimization

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forecasting', '0001_initial'),
    ]

    operations = [
        # Index for Forecast - used in forecast accuracy metric
        migrations.AddIndex(
            model_name='forecast',
            index=models.Index(
                fields=['product', 'generated_at'],
                name='idx_forecast_prod_gen'
            ),
        ),
    ]
