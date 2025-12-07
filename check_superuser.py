import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockpredictor.settings')
django.setup()

from accounts.models import User

superusers = User.objects.filter(is_superuser=True)
print(f"\n=== Superusers check ===")
print(f"Total superusers found: {superusers.count()}\n")

if superusers.exists():
    for user in superusers:
        print(f"Email: {user.email}")
        print(f"Active: {user.is_active}")
        print(f"Staff: {user.is_staff}")
        print(f"Superuser: {user.is_superuser}")
        print(f"Company: {user.company if user.company else 'Not assigned'}")
        print(f"Created: {user.date_joined}")
        print("-" * 50)
else:
    print("No superusers found!")
