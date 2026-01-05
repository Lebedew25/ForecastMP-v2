from django.db import migrations, models
import django.db.models


class Migration(migrations.Migration):
    dependencies = [
        ('sales', '0005_alter_inventorysnapshot_unique_together'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='salestransaction',
            constraint=models.UniqueConstraint(
                fields=['marketplace', 'transaction_reference'],
                condition=~django.db.models.Q(transaction_reference=''),
                name='unique_sales_transaction_reference',
            ),
        ),
    ]
