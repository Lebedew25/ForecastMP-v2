import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockpredictor.settings')
django.setup()

from products.models import Product
from sales.models import InventorySnapshot
from accounts.models import Company

# Get the test product
try:
    product = Product.objects.get(sku="TEST-001")
    print(f"Using product: {product.sku} - {product.name}")
except Product.DoesNotExist:
    print("Test product TEST-001 not found!")
    exit(1)

# Create inventory snapshot
inventory = InventorySnapshot.objects.create(
    product=product,
    snapshot_date=date.today(),
    quantity_available=150,  # Available stock
    quantity_reserved=20      # Reserved stock
)

print(f"Created inventory snapshot:")
print(f"  Available: {inventory.quantity_available}")
print(f"  Reserved: {inventory.quantity_reserved}")
print(f"  Date: {inventory.snapshot_date}")

# Also create warehouse
from sales.models import Warehouse

company = product.company
warehouse, created = Warehouse.objects.get_or_create(
    company=company,
    name="Основной склад",
    defaults={
        'warehouse_type': 'OWN',
        'is_primary': True,
        'is_active': True
    }
)

if created:
    print(f"Created warehouse: {warehouse.name}")
else:
    print(f"Using existing warehouse: {warehouse.name}")

print("Test inventory data generation complete!")