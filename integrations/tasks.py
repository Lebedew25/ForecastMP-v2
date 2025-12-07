"""
Celery tasks for marketplace synchronization
"""
from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta, date
from .models import MarketplaceCredential, SyncLog
from .clients import get_client
from products.models import Product, MarketplaceProduct
from sales.models import SalesTransaction, InventorySnapshot, DailySalesAggregate
import logging

logger = logging.getLogger(__name__)


@shared_task
def sync_all_marketplaces():
    """Sync all active marketplace credentials"""
    credentials = MarketplaceCredential.objects.filter(is_active=True)
    
    results = []
    for credential in credentials:
        try:
            result = sync_marketplace.delay(credential.id)
            results.append({
                'credential_id': str(credential.id),
                'company': credential.company.name,
                'marketplace': credential.marketplace,
                'task_id': result.id
            })
        except Exception as e:
            logger.error(f"Failed to queue sync for {credential}: {str(e)}")
    
    return {
        'total_queued': len(results),
        'results': results
    }


@shared_task
def sync_marketplace(credential_id):
    """Sync single marketplace"""
    try:
        credential = MarketplaceCredential.objects.get(id=credential_id)
    except MarketplaceCredential.DoesNotExist:
        logger.error(f"Credential {credential_id} not found")
        return {'status': 'error', 'message': 'Credential not found'}
    
    # Create sync log
    sync_log = SyncLog.objects.create(
        credential=credential,
        status='STARTED'
    )
    
    try:
        # Get marketplace client
        client = get_client(
            credential.marketplace,
            credential.api_key,
            credential.api_secret
        )
        
        # Sync products
        products_synced = sync_products(credential, client)
        
        # Sync sales (last 7 days)
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        sales_synced = sync_sales(credential, client, start_date, end_date)
        
        # Sync inventory
        inventory_synced = sync_inventory(credential, client)
        
        # Update sync log
        sync_log.status = 'SUCCESS'
        sync_log.completed_at = timezone.now()
        sync_log.records_fetched = products_synced + sales_synced + inventory_synced
        sync_log.records_saved = sync_log.records_fetched
        sync_log.save()
        
        # Update credential last sync
        credential.last_sync_at = timezone.now()
        credential.save()
        
        return {
            'status': 'success',
            'products': products_synced,
            'sales': sales_synced,
            'inventory': inventory_synced,
            'total': sync_log.records_fetched
        }
        
    except Exception as e:
        logger.error(f"Sync failed for {credential}: {str(e)}")
        
        sync_log.status = 'FAILED'
        sync_log.completed_at = timezone.now()
        sync_log.error_message = str(e)
        sync_log.save()
        
        return {
            'status': 'failed',
            'error': str(e)
        }


def sync_products(credential, client):
    """Sync products from marketplace"""
    try:
        products_data = client.fetch_products()
        count = 0
        
        for product_data in products_data:
            # Extract product info (marketplace-specific mapping)
            external_id = product_data.get('id') or product_data.get('nmId') or product_data.get('offer_id')
            name = product_data.get('name') or product_data.get('title', 'Unknown')
            barcode = product_data.get('barcode', '')
            
            if not external_id:
                continue
            
            # Create or get product
            sku = f"{credential.marketplace}_{external_id}"
            product, created = Product.objects.get_or_create(
                company=credential.company,
                sku=sku,
                defaults={'name': name}
            )
            
            # Create or update marketplace mapping
            MarketplaceProduct.objects.update_or_create(
                product=product,
                marketplace=credential.marketplace,
                defaults={
                    'external_id': external_id,
                    'barcode': barcode,
                    'external_data': product_data,
                    'active': True,
                    'last_synced_at': timezone.now()
                }
            )
            
            count += 1
        
        return count
        
    except Exception as e:
        logger.error(f"Product sync error: {str(e)}")
        return 0


def sync_sales(credential, client, start_date, end_date):
    """Sync sales transactions from marketplace"""
    try:
        sales_data = client.fetch_sales(start_date, end_date)
        count = 0
        
        for sale in sales_data:
            # Extract sale info (marketplace-specific)
            external_id = sale.get('nmId') or sale.get('offer_id')
            sale_date_str = sale.get('date') or sale.get('sale_date')
            quantity = sale.get('quantity') or sale.get('ordered_units', 0)
            revenue = sale.get('revenue') or sale.get('price', 0)
            
            if not external_id or not sale_date_str:
                continue
            
            # Parse date
            if isinstance(sale_date_str, str):
                sale_date = datetime.fromisoformat(sale_date_str.replace('Z', '+00:00')).date()
            else:
                sale_date = sale_date_str
            
            # Find product
            try:
                mp_product = MarketplaceProduct.objects.get(
                    marketplace=credential.marketplace,
                    external_id=external_id
                )
                
                # Create sales transaction
                SalesTransaction.objects.create(
                    product=mp_product.product,
                    marketplace=credential.marketplace,
                    sale_date=sale_date,
                    quantity=quantity,
                    revenue=revenue,
                    transaction_reference=sale.get('id', ''),
                    metadata=sale
                )
                
                count += 1
                
            except MarketplaceProduct.DoesNotExist:
                logger.warning(f"Product not found for external_id: {external_id}")
                continue
        
        # Update daily aggregates
        update_daily_aggregates.delay(credential.company.id, start_date, end_date)
        
        return count
        
    except Exception as e:
        logger.error(f"Sales sync error: {str(e)}")
        return 0


def sync_inventory(credential, client):
    """Sync inventory snapshots from marketplace"""
    try:
        inventory_data = client.fetch_inventory()
        count = 0
        today = date.today()
        
        for inv in inventory_data:
            external_id = inv.get('nmId') or inv.get('offer_id')
            quantity_available = inv.get('quantity') or inv.get('present', 0)
            quantity_reserved = inv.get('reserved', 0)
            warehouse = inv.get('warehouse') or inv.get('warehouse_id', '')
            
            if not external_id:
                continue
            
            try:
                mp_product = MarketplaceProduct.objects.get(
                    marketplace=credential.marketplace,
                    external_id=external_id
                )
                
                InventorySnapshot.objects.update_or_create(
                    product=mp_product.product,
                    snapshot_date=today,
                    warehouse_id=warehouse,
                    defaults={
                        'quantity_available': quantity_available,
                        'quantity_reserved': quantity_reserved,
                        'warehouse_data': inv
                    }
                )
                
                count += 1
                
            except MarketplaceProduct.DoesNotExist:
                logger.warning(f"Product not found for external_id: {external_id}")
                continue
        
        return count
        
    except Exception as e:
        logger.error(f"Inventory sync error: {str(e)}")
        return 0


@shared_task
def update_daily_aggregates(company_id, start_date, end_date):
    """Update daily sales aggregates for date range"""
    from django.db.models import Sum
    from accounts.models import Company
    
    try:
        company = Company.objects.get(id=company_id)
    except Company.DoesNotExist:
        return {'status': 'error', 'message': 'Company not found'}
    
    products = Product.objects.filter(company=company, is_active=True)
    current_date = start_date
    
    while current_date <= end_date:
        for product in products:
            # Aggregate sales for this product and date
            sales = SalesTransaction.objects.filter(
                product=product,
                sale_date=current_date
            )
            
            if not sales.exists():
                current_date += timedelta(days=1)
                continue
            
            total = sales.aggregate(
                total_qty=Sum('quantity'),
                total_rev=Sum('revenue')
            )
            
            wb_sales = sales.filter(marketplace='WILDBERRIES').aggregate(
                qty=Sum('quantity'),
                rev=Sum('revenue')
            )
            
            ozon_sales = sales.filter(marketplace='OZON').aggregate(
                qty=Sum('quantity'),
                rev=Sum('revenue')
            )
            
            DailySalesAggregate.objects.update_or_create(
                product=product,
                date=current_date,
                defaults={
                    'total_quantity': total['total_qty'] or 0,
                    'total_revenue': total['total_rev'] or 0,
                    'wildberries_quantity': wb_sales['qty'] or 0,
                    'wildberries_revenue': wb_sales['rev'] or 0,
                    'ozon_quantity': ozon_sales['qty'] or 0,
                    'ozon_revenue': ozon_sales['rev'] or 0
                }
            )
        
        current_date += timedelta(days=1)
    
    return {'status': 'success', 'date_range': f"{start_date} to {end_date}"}
