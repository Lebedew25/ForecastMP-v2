from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Q, Sum, Avg
from .models import Product
from sales.models import InventorySnapshot, Warehouse
import logging

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class ProductsListView(View):
    """API endpoint for retrieving products list"""
    
    def get(self, request):
        """Get products with filtering and search"""
        try:
            # Check if user has company assigned
            if not request.user.company:
                return JsonResponse({
                    'success': False,
                    'error': 'No company assigned to user'
                }, status=403)
            
            # Get query parameters
            search = request.GET.get('search', '')
            page = int(request.GET.get('page', 1))
            page_size = min(int(request.GET.get('page_size', 50)), 100)
            warehouse_id = request.GET.get('warehouse_id')
            
            # Build query
            query = Product.objects.filter(company=request.user.company)
            
            # Apply search filter
            if search:
                query = query.filter(
                    Q(name__icontains=search) |
                    Q(sku__icontains=search) |
                    Q(description__icontains=search)
                )
            
            # Get total count
            total_count = query.count()
            
            # Order and paginate
            products = query.order_by('name')[(page-1)*page_size:page*page_size]
            
            # Serialize results with inventory data
            results = []
            for product in products:
                # Get inventory snapshots
                snapshots_query = InventorySnapshot.objects.filter(product=product)
                if warehouse_id:
                    snapshots_query = snapshots_query.filter(warehouse_id=warehouse_id)
                
                total_stock = snapshots_query.aggregate(Sum('quantity_available'))['quantity_available__sum'] or 0
                
                results.append({
                    'id': str(product.id),
                    'sku': product.sku,
                    'name': product.name,
                    'description': product.description,
                    'category': product.category,
                    'price': float(product.price) if product.price else None,
                    'cost': float(product.cost) if product.cost else None,
                    'weight': float(product.weight) if product.weight else None,
                    'dimensions': product.dimensions,
                    'total_stock': total_stock,
                    'created_at': product.created_at.isoformat() if product.created_at else None,
                })
            
            return JsonResponse({
                'success': True,
                'products': results,
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size
            })
            
        except Exception as e:
            logger.error(f"Products list error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)


@method_decorator(login_required, name='dispatch')
class ProductDetailView(View):
    """API endpoint for product details"""
    
    def get(self, request, product_id):
        """Get detailed product information"""
        try:
            # Get product
            product = Product.objects.get(
                id=product_id,
                company=request.user.company
            )
            
            # Get inventory by warehouse
            snapshots = InventorySnapshot.objects.filter(
                product=product
            ).select_related('warehouse')
            
            inventory_by_warehouse = []
            total_stock = 0
            for snapshot in snapshots:
                quantity = snapshot.quantity_available or 0
                total_stock += quantity
                inventory_by_warehouse.append({
                    'warehouse_id': str(snapshot.warehouse.id),
                    'warehouse_name': snapshot.warehouse.name,
                    'quantity_available': snapshot.quantity_available,
                    'quantity_reserved': snapshot.quantity_reserved,
                    'last_updated': snapshot.last_updated.isoformat()
                })
            
            return JsonResponse({
                'success': True,
                'product': {
                    'id': str(product.id),
                    'sku': product.sku,
                    'name': product.name,
                    'description': product.description,
                    'category': product.category,
                    'price': float(product.price) if product.price else None,
                    'cost': float(product.cost) if product.cost else None,
                    'weight': float(product.weight) if product.weight else None,
                    'dimensions': product.dimensions,
                    'total_stock': total_stock,
                    'inventory_by_warehouse': inventory_by_warehouse,
                    'created_at': product.created_at.isoformat() if product.created_at else None,
                }
            })
            
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Product not found'
            }, status=404)
        except Exception as e:
            logger.error(f"Product detail error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)


@method_decorator(login_required, name='dispatch')
class WarehousesListView(View):
    """API endpoint for warehouses list"""
    
    def get(self, request):
        """Get all warehouses for the company"""
        try:
            if not request.user.company:
                return JsonResponse({
                    'success': False,
                    'error': 'No company assigned to user'
                }, status=403)
            
            warehouses = Warehouse.objects.filter(company=request.user.company)
            
            results = []
            for warehouse in warehouses:
                results.append({
                    'id': str(warehouse.id),
                    'name': warehouse.name,
                    'location': warehouse.location,
                    'is_active': warehouse.is_active,
                })
            
            return JsonResponse({
                'success': True,
                'warehouses': results
            })
            
        except Exception as e:
            logger.error(f"Warehouses list error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)
