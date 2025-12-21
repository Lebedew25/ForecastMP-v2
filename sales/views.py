"""
Views for inventory management API
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Q
from django.shortcuts import render
import json
from datetime import datetime, date
from .inventory_service import (
    adjust_product_stock,
    transfer_product_stock,
    get_product_stock,
    get_product_stock_history
)
from .models import InventoryMovement, Warehouse
from products.models import Product
from accounts.models import User
import logging

logger = logging.getLogger(__name__)


class InventoryAdjustmentView(View):
    """API endpoint for adjusting inventory levels"""
    
    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        """Handle stock adjustment requests"""
        try:
            # Parse JSON data
            data = json.loads(request.body.decode('utf-8'))
            
            # Extract required fields
            product_id = data.get('product_id')
            warehouse_id = data.get('warehouse_id')
            adjustment_type = data.get('adjustment_type')
            quantity = data.get('quantity')
            reason = data.get('reason')
            notes = data.get('notes', '')
            
            # Validate required fields
            if not all([product_id, warehouse_id, adjustment_type, quantity is not None, reason]):
                return JsonResponse({
                    'success': False,
                    'error': 'Missing required fields: product_id, warehouse_id, adjustment_type, quantity, reason'
                }, status=400)
            
            # Perform adjustment
            result = adjust_product_stock(
                product_id=product_id,
                warehouse_id=warehouse_id,
                adjustment_type=adjustment_type,
                quantity=int(quantity),
                reason=reason,
                notes=notes,
                user=request.user
            )
            
            if result['success']:
                return JsonResponse({
                    'success': True,
                    'message': 'Stock adjusted successfully',
                    'new_quantity': result['new_quantity'],
                    'movement_id': result['movement_id']
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result['error']
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Inventory adjustment error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)


class InventoryTransferView(View):
    """API endpoint for transferring inventory between warehouses"""
    
    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        """Handle stock transfer requests"""
        try:
            # Parse JSON data
            data = json.loads(request.body.decode('utf-8'))
            
            # Extract required fields
            product_id = data.get('product_id')
            from_warehouse_id = data.get('from_warehouse_id')
            to_warehouse_id = data.get('to_warehouse_id')
            quantity = data.get('quantity')
            notes = data.get('notes', '')
            
            # Validate required fields
            if not all([product_id, from_warehouse_id, to_warehouse_id, quantity]):
                return JsonResponse({
                    'success': False,
                    'error': 'Missing required fields: product_id, from_warehouse_id, to_warehouse_id, quantity'
                }, status=400)
            
            # Perform transfer
            result = transfer_product_stock(
                product_id=product_id,
                from_warehouse_id=from_warehouse_id,
                to_warehouse_id=to_warehouse_id,
                quantity=int(quantity),
                notes=notes,
                user=request.user
            )
            
            if result['success']:
                return JsonResponse({
                    'success': True,
                    'message': 'Stock transferred successfully',
                    'from_quantity': result['from_quantity'],
                    'to_quantity': result['to_quantity'],
                    'outbound_movement_id': result['outbound_movement_id'],
                    'inbound_movement_id': result['inbound_movement_id']
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result['error']
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Inventory transfer error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)


class InventoryStatusView(View):
    """API endpoint for checking inventory status"""
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, product_id=None):
        """Get current inventory status"""
        try:
            if product_id:
                # Get specific product stock
                warehouse_id = request.GET.get('warehouse_id')
                result = get_product_stock(product_id, warehouse_id)
                
                if result['success']:
                    return JsonResponse(result)
                else:
                    return JsonResponse({
                        'success': False,
                        'error': result['error']
                    }, status=404)
            else:
                # Get all products stock (paginated)
                page = int(request.GET.get('page', 1))
                page_size = min(int(request.GET.get('page_size', 50)), 100)
                
                # Get products for current company
                products = Product.objects.filter(
                    company=request.user.company
                ).order_by('sku')[(page-1)*page_size:page*page_size]
                
                # Get stock for each product
                results = []
                for product in products:
                    stock_result = get_product_stock(str(product.id))
                    if stock_result['success']:
                        results.append({
                            'product_id': str(product.id),
                            'sku': product.sku,
                            'name': product.name,
                            'quantity_available': stock_result['quantity_available'],
                            'quantity_reserved': stock_result['quantity_reserved'],
                            'total_quantity': stock_result['total_quantity']
                        })
                
                return JsonResponse({
                    'success': True,
                    'products': results,
                    'page': page,
                    'page_size': page_size
                })
                
        except Exception as e:
            logger.error(f"Inventory status error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)


class InventoryHistoryView(View):
    """API endpoint for inventory history"""
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, product_id):
        """Get inventory history for a product"""
        try:
            # Parse query parameters
            warehouse_id = request.GET.get('warehouse_id')
            start_date_str = request.GET.get('start_date')
            end_date_str = request.GET.get('end_date')
            limit = min(int(request.GET.get('limit', 100)), 1000)
            
            # Parse dates
            start_date = None
            end_date = None
            
            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid start_date format. Use YYYY-MM-DD'
                    }, status=400)
            
            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid end_date format. Use YYYY-MM-DD'
                    }, status=400)
            
            # Get history
            result = get_product_stock_history(
                product_id=product_id,
                warehouse_id=warehouse_id,
                start_date=start_date,
                end_date=end_date,
                limit=limit
            )
            
            if result['success']:
                return JsonResponse(result)
            else:
                return JsonResponse({
                    'success': False,
                    'error': result['error']
                }, status=404)
                
        except Exception as e:
            logger.error(f"Inventory history error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)


class InventoryMovementsView(View):
    """API endpoint for inventory movements"""
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        """Get inventory movements with filtering"""
        try:
            # Parse query parameters
            product_id = request.GET.get('product_id')
            warehouse_id = request.GET.get('warehouse_id')
            movement_type = request.GET.get('movement_type')
            start_date_str = request.GET.get('start_date')
            end_date_str = request.GET.get('end_date')
            page = int(request.GET.get('page', 1))
            page_size = min(int(request.GET.get('page_size', 50)), 100)
            
            # Build query
            query = InventoryMovement.objects.filter(
                product__company=request.user.company
            ).select_related('product', 'warehouse', 'created_by')
            
            # Apply filters
            if product_id:
                query = query.filter(product_id=product_id)
            
            if warehouse_id:
                query = query.filter(warehouse_id=warehouse_id)
            
            if movement_type:
                query = query.filter(movement_type=movement_type)
            
            # Parse and apply date filters
            if start_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    query = query.filter(movement_date__date__gte=start_date)
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid start_date format. Use YYYY-MM-DD'
                    }, status=400)
            
            if end_date_str:
                try:
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                    query = query.filter(movement_date__date__lte=end_date)
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid end_date format. Use YYYY-MM-DD'
                    }, status=400)
            
            # Order and paginate
            movements = query.order_by('-movement_date')[(page-1)*page_size:page*page_size]
            
            # Serialize results
            results = []
            for movement in movements:
                results.append({
                    'id': str(movement.id),
                    'product_id': str(movement.product.id),
                    'product_sku': movement.product.sku,
                    'product_name': movement.product.name,
                    'warehouse_id': str(movement.warehouse.id) if movement.warehouse else None,
                    'warehouse_name': movement.warehouse.name if movement.warehouse else 'Unknown',
                    'movement_type': movement.movement_type,
                    'quantity': movement.quantity,
                    'movement_date': movement.movement_date.isoformat(),
                    'reference_type': movement.reference_type,
                    'reference_id': movement.reference_id,
                    'notes': movement.notes,
                    'created_by': movement.created_by.email if movement.created_by else None
                })
            
            return JsonResponse({
                'success': True,
                'movements': results,
                'page': page,
                'page_size': page_size,
                'total_count': query.count()
            })
            
        except Exception as e:
            logger.error(f"Inventory movements error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)


class WebhookHandlerView(View):
    """API endpoint for handling incoming webhooks from e-commerce platforms"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        """Handle incoming webhook events"""
        try:
            # Parse JSON data
            data = json.loads(request.body.decode('utf-8'))
            
            # Extract event information
            event_type = data.get('event_type')
            timestamp = data.get('timestamp')
            event_data = data.get('data', {})
            
            # Log the incoming webhook
            logger.info(f"Received webhook: {event_type} at {timestamp}")
            
            # Process based on event type
            if event_type == 'order.created':
                return self._handle_order_created(event_data)
            elif event_type == 'order.cancelled':
                return self._handle_order_cancelled(event_data)
            elif event_type == 'inventory.updated':
                return self._handle_inventory_updated(event_data)
            else:
                logger.warning(f"Unknown webhook event type: {event_type}")
                return JsonResponse({
                    'success': False,
                    'error': f'Unsupported event type: {event_type}'
                }, status=400)
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON in webhook payload")
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)
    
    def _handle_order_created(self, data):
        """Handle order.created webhook event"""
        try:
            # Extract order information
            order_id = data.get('order_id')
            order_date = data.get('order_date')
            items = data.get('items', [])
            
            # Validate required fields
            if not order_id or not order_date or not items:
                return JsonResponse({
                    'success': False,
                    'error': 'Missing required order fields'
                }, status=400)
            
            # Process each item in the order
            processed_items = []
            for item in items:
                sku = item.get('sku')
                quantity = item.get('quantity', 0)
                
                if sku and quantity > 0:
                    # Here we would typically:
                    # 1. Find the product by SKU
                    # 2. Create a sales transaction
                    # 3. Update inventory levels
                    # For now, we'll just log the processing
                    logger.info(f"Processing order item: {sku} x{quantity}")
                    processed_items.append({
                        'sku': sku,
                        'quantity': quantity
                    })
            
            logger.info(f"Processed order {order_id} with {len(processed_items)} items")
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully processed order {order_id}',
                'processed_items': len(processed_items)
            })
            
        except Exception as e:
            logger.error(f"Order creation handling error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to process order creation'
            }, status=500)
    
    def _handle_order_cancelled(self, data):
        """Handle order.cancelled webhook event"""
        try:
            # Extract order information
            order_id = data.get('order_id')
            
            if not order_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Missing order_id'
                }, status=400)
            
            # Here we would typically:
            # 1. Find the cancelled order
            # 2. Reverse the sales transaction
            # 3. Restore inventory levels
            # For now, we'll just log the cancellation
            logger.info(f"Processing order cancellation: {order_id}")
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully processed cancellation for order {order_id}'
            })
            
        except Exception as e:
            logger.error(f"Order cancellation handling error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to process order cancellation'
            }, status=500)
    
    def _handle_inventory_updated(self, data):
        """Handle inventory.updated webhook event"""
        try:
            # Extract inventory information
            sku = data.get('sku')
            quantity = data.get('quantity')
            last_updated = data.get('last_updated')
            
            # Validate required fields
            if not sku or quantity is None:
                return JsonResponse({
                    'success': False,
                    'error': 'Missing required inventory fields'
                }, status=400)
            
            # Here we would typically:
            # 1. Find the product by SKU
            # 2. Update the inventory snapshot
            # 3. Create an inventory movement record
            # For now, we'll just log the update
            logger.info(f"Processing inventory update: {sku} = {quantity}")
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully processed inventory update for {sku}'
            })
            
        except Exception as e:
            logger.error(f"Inventory update handling error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to process inventory update'
            }, status=500)


@login_required
def warehouses(request):
    """Display all warehouses for the company"""
    company = request.user.company
    
    if not company:
        return render(request, 'procurement/no_company.html')
    
    # Get all warehouses for the company
    warehouses = Warehouse.objects.filter(company=company).order_by('-is_primary', 'name')
    
    context = {
        'warehouses': warehouses,
    }
    
    return render(request, 'sales/warehouses.html', context)


# Convenience view functions for URL routing
inventory_adjustment = InventoryAdjustmentView.as_view()
inventory_transfer = InventoryTransferView.as_view()
inventory_status = InventoryStatusView.as_view()
inventory_history = InventoryHistoryView.as_view()
inventory_movements = InventoryMovementsView.as_view()
webhook_handler = WebhookHandlerView.as_view()
