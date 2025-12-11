"""
Warehouse backfill migration script

This script creates default warehouses for existing companies that don't have them yet.
It also migrates legacy warehouse_id strings to proper Warehouse foreign key relationships.
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockpredictor.settings')
django.setup()

from accounts.models import Company
from sales.models import Warehouse, InventorySnapshot
from integrations.models import MarketplaceCredential
from django.utils import timezone


def create_default_warehouses():
    """Create default warehouses for all companies"""
    print("Creating default warehouses for companies...")
    
    companies = Company.objects.all()
    created_count = 0
    
    for company in companies:
        print(f"\nProcessing company: {company.name}")
        
        # Check if company already has warehouses
        existing_warehouses = Warehouse.objects.filter(company=company).count()
        if existing_warehouses > 0:
            print(f"  ✓ Company already has {existing_warehouses} warehouse(s)")
            continue
        
        # Create main warehouse
        main_warehouse, created = Warehouse.objects.get_or_create(
            company=company,
            name="Main Warehouse",
            defaults={
                'warehouse_type': 'OWN',
                'is_primary': True,
                'is_active': True
            }
        )
        
        if created:
            print(f"  ✓ Created main warehouse: {main_warehouse.name}")
            created_count += 1
        
        # Create marketplace warehouses based on existing credentials
        credentials = MarketplaceCredential.objects.filter(company=company, is_active=True)
        
        for cred in credentials:
            warehouse_name = f"{cred.marketplace.title()} Fulfillment"
            marketplace_warehouse, created = Warehouse.objects.get_or_create(
                company=company,
                marketplace=cred.marketplace,
                defaults={
                    'name': warehouse_name,
                    'warehouse_type': 'MARKETPLACE_FF',
                    'is_active': True
                }
            )
            
            if created:
                print(f"  ✓ Created marketplace warehouse: {warehouse_name}")
                created_count += 1
    
    print(f"\n✅ Total warehouses created: {created_count}")
    return created_count


def migrate_inventory_snapshots():
    """Migrate inventory snapshots to use Warehouse foreign keys"""
    print("\nMigrating inventory snapshots to use warehouse foreign keys...")
    
    # Get all inventory snapshots without a warehouse FK
    snapshots_without_warehouse = InventorySnapshot.objects.filter(warehouse__isnull=True)
    total_count = snapshots_without_warehouse.count()
    
    if total_count == 0:
        print("  ✓ All inventory snapshots already have warehouse references")
        return 0
    
    print(f"  Found {total_count} snapshots to migrate")
    
    migrated_count = 0
    error_count = 0
    
    for snapshot in snapshots_without_warehouse:
        try:
            company = snapshot.product.company
            
            # Try to find appropriate warehouse
            # If legacy_warehouse_id exists, try to match by marketplace
            warehouse = None
            
            if hasattr(snapshot, 'legacy_warehouse_id') and snapshot.legacy_warehouse_id:
                # Try to match by marketplace in the legacy warehouse ID
                if 'ozon' in snapshot.legacy_warehouse_id.lower():
                    warehouse = Warehouse.objects.filter(
                        company=company,
                        marketplace='OZON'
                    ).first()
                elif 'wildberries' in snapshot.legacy_warehouse_id.lower() or 'wb' in snapshot.legacy_warehouse_id.lower():
                    warehouse = Warehouse.objects.filter(
                        company=company,
                        marketplace='WILDBERRIES'
                    ).first()
            
            # If no match found, use primary warehouse
            if not warehouse:
                warehouse = Warehouse.objects.filter(
                    company=company,
                    is_primary=True
                ).first()
            
            # If still no warehouse, create one
            if not warehouse:
                warehouse = Warehouse.objects.create(
                    company=company,
                    name="Main Warehouse",
                    warehouse_type='OWN',
                    is_primary=True,
                    is_active=True
                )
            
            # Update snapshot
            snapshot.warehouse = warehouse
            snapshot.save()
            migrated_count += 1
            
            if migrated_count % 100 == 0:
                print(f"  Progress: {migrated_count}/{total_count}")
        
        except Exception as e:
            print(f"  ✗ Error migrating snapshot {snapshot.id}: {str(e)}")
            error_count += 1
    
    print(f"\n✅ Migrated {migrated_count} inventory snapshots")
    if error_count > 0:
        print(f"⚠️  {error_count} errors occurred during migration")
    
    return migrated_count


def validate_migration():
    """Validate that all data has been properly migrated"""
    print("\nValidating migration...")
    
    issues = []
    
    # Check that all companies have at least one warehouse
    companies_without_warehouses = []
    for company in Company.objects.all():
        if Warehouse.objects.filter(company=company).count() == 0:
            companies_without_warehouses.append(company.name)
    
    if companies_without_warehouses:
        issues.append(f"Companies without warehouses: {', '.join(companies_without_warehouses)}")
    else:
        print("  ✓ All companies have at least one warehouse")
    
    # Check that all inventory snapshots have warehouse references
    snapshots_without_warehouse = InventorySnapshot.objects.filter(warehouse__isnull=True).count()
    if snapshots_without_warehouse > 0:
        issues.append(f"{snapshots_without_warehouse} inventory snapshots still missing warehouse references")
    else:
        print("  ✓ All inventory snapshots have warehouse references")
    
    # Check that each company has a primary warehouse
    companies_without_primary = []
    for company in Company.objects.all():
        if not Warehouse.objects.filter(company=company, is_primary=True).exists():
            companies_without_primary.append(company.name)
    
    if companies_without_primary:
        issues.append(f"Companies without primary warehouse: {', '.join(companies_without_primary)}")
    else:
        print("  ✓ All companies have a primary warehouse")
    
    if issues:
        print("\n⚠️  Validation issues found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("\n✅ All validation checks passed!")
        return True


def main():
    """Main migration function"""
    print("=" * 60)
    print("WAREHOUSE BACKFILL MIGRATION")
    print("=" * 60)
    
    try:
        # Step 1: Create default warehouses
        warehouses_created = create_default_warehouses()
        
        # Step 2: Migrate inventory snapshots
        snapshots_migrated = migrate_inventory_snapshots()
        
        # Step 3: Validate migration
        validation_passed = validate_migration()
        
        print("\n" + "=" * 60)
        print("MIGRATION SUMMARY")
        print("=" * 60)
        print(f"Warehouses created: {warehouses_created}")
        print(f"Inventory snapshots migrated: {snapshots_migrated}")
        print(f"Validation: {'PASSED' if validation_passed else 'FAILED'}")
        print("=" * 60)
        
        if validation_passed:
            print("\n✅ Migration completed successfully!")
            return 0
        else:
            print("\n⚠️  Migration completed with issues. Please review the validation errors above.")
            return 1
    
    except Exception as e:
        print(f"\n❌ Migration failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = main()