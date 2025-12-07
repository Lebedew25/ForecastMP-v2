import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockpredictor.settings')
django.setup()

from accounts.models import User, Company

# Get the superuser
superuser = User.objects.filter(is_superuser=True).first()

if not superuser:
    print("❌ No superuser found!")
    exit(1)

print(f"✅ Found superuser: {superuser.email}")

# Check if company already exists
if superuser.company:
    print(f"ℹ️  User already has company: {superuser.company.name}")
else:
    # Create a company
    company = Company.objects.create(
        name="My Company v2",
        is_active=True
    )
    print(f"✅ Created company: {company.name}")
    
    # Assign company to superuser
    superuser.company = company
    superuser.save()
    print(f"✅ Assigned company to user: {superuser.email}")

print("\n=== Final Status ===")
print(f"User: {superuser.email}")
print(f"Company: {superuser.company.name if superuser.company else 'None'}")
print(f"Company Active: {superuser.company.is_active if superuser.company else 'N/A'}")
print("\n✅ Setup complete! You can now access the dashboard.")
