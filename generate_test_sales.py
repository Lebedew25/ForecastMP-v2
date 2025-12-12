import os
import django
import random
from datetime import date, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockpredictor.settings')
django.setup()

from products.models import Product
from sales.models import SalesTransaction, DailySalesAggregate

# Get the test product
try:
    product = Product.objects.get(sku="TEST-001")
    print(f"Using product: {product.sku} - {product.name}")
except Product.DoesNotExist:
    print("Test product TEST-001 not found!")
    exit(1)

# Generate sales for the last 365 days
print("Generating sales data for the last 365 days...")

sales_created = 0
for i in range(365):
    sale_date = date.today() - timedelta(days=i)
    # Generate random quantity between 5 and 50
    quantity = random.randint(5, 50)
    revenue = Decimal(quantity * random.randint(1400, 1600))  # Price around 1500
    
    SalesTransaction.objects.create(
        product=product,
        marketplace='WILDBERRIES',
        sale_date=sale_date,
        quantity=quantity,
        revenue=revenue
    )
    sales_created += 1

print(f"Created {sales_created} sales transactions")

# Now we need to update daily aggregates
print("Updating daily sales aggregates...")

from integrations.tasks import update_daily_aggregates
result = update_daily_aggregates(
    str(product.company.id),
    date.today() - timedelta(days=365),
    date.today()
)

print("Daily sales aggregates updated")
print("Test data generation complete!")