"""
Inventory management service for stock adjustments and movements
"""
from datetime import datetime, date
from typing import Dict, List, Optional
from django.db import transaction
from django.db.models import Sum
from .models import InventorySnapshot, InventoryMovement, Warehouse
from products.models import Product
from accounts.models import User
import logging

logger = logging.getLogger(__name__)


class InventoryService:
    """Service for managing inventory operations"""
    
    MOVEMENT_TYPES = {
        'ADD': 'INBOUND',
        'SUBTRACT': 'OUTBOUND',
        'SET_TO': 'ADJUSTMENT',
        'TRANSFER': 'TRANSFER'
    }
    
    REASON_CODES = {
        'RECEIVING': 'Receiving goods',
        'DAMAGE': 'Damaged goods',
        'LOSS': 'Lost inventory',
        'INVENTORY_COUNT': 'Inventory count adjustment',
        'CORRECTION': 'Data correction',
        'OTHER': 'Other reason'
    }
    
    def __init__(self):
        pass
    
    def adjust_stock(
        self,
        product_id: str,
        warehouse_id: str,
        adjustment_type: str,
        quantity: int,
        reason: str,
        notes: str = "",
        user: Optional[User] = None,
        adjustment_date: Optional[date] = None
    ) -> Dict:
        """
        Adjust stock level for a product in a specific warehouse
        
        Args:
            product_id: Product UUID string
            warehouse_id: Warehouse UUID string
            adjustment_type: Type of adjustment (ADD, SUBTRACT, SET_TO)
            quantity: Quantity to adjust (must be non-negative)
            reason: Reason code for adjustment
            notes: Optional additional notes
            user: User performing the adjustment
            adjustment_date: Date of adjustment (defaults to today)
            
        Returns:
            Dictionary with operation result
        """
        try:
            # Validate inputs
            if quantity < 0:
                return {
                    'success': False,
                    'error': 'Quantity must be non-negative'
                }
            
            if adjustment_type not in self.MOVEMENT_TYPES:
                return {
                    'success': False,
                    'error': f'Invalid adjustment type. Must be one of: {list(self.MOVEMENT_TYPES.keys())}'
                }
            
            if reason not in self.REASON_CODES:
                return {
                    'success': False,
                    'error': f'Invalid reason code. Must be one of: {list(self.REASON_CODES.keys())}'
                }
            
            # Get objects
            try:
                product = Product.objects.get(id=product_id)
                warehouse = Warehouse.objects.get(id=warehouse_id)
            except Product.DoesNotExist:
                return {
                    'success': False,
                    'error': 'Product not found'
                }
            except Warehouse.DoesNotExist:
                return {
                    'success': False,
                    'error': 'Warehouse not found'
                }
            
            # Set adjustment date
            if adjustment_date is None:
                adjustment_date = date.today()
            
            # Perform adjustment in transaction
            with transaction.atomic():
                # Get current snapshot
                snapshot, created = InventorySnapshot.objects.get_or_create(
                    product=product,
                    warehouse=warehouse,
                    snapshot_date=adjustment_date,
                    defaults={
                        'quantity_available': 0,
                        'quantity_reserved': 0,
                        'legacy_warehouse_id': warehouse.name
                    }
                )
                
                # Calculate new quantity based on adjustment type
                if adjustment_type == 'ADD':
                    new_quantity = snapshot.quantity_available + quantity
                    movement_quantity = quantity
                elif adjustment_type == 'SUBTRACT':
                    # Check if we have enough stock
                    if snapshot.quantity_available < quantity:
                        return {
                            'success': False,
                            'error': f'Insufficient stock. Available: {snapshot.quantity_available}, Requested: {quantity}'
                        }
                    new_quantity = snapshot.quantity_available - quantity
                    movement_quantity = -quantity
                elif adjustment_type == 'SET_TO':
                    new_quantity = quantity
                    movement_quantity = quantity - snapshot.quantity_available
                else:
                    return {
                        'success': False,
                        'error': 'Invalid adjustment type'
                    }
                
                # Update snapshot
                snapshot.quantity_available = new_quantity
                snapshot.save()
                
                # Create movement record
                movement = InventoryMovement.objects.create(
                    product=product,
                    warehouse=warehouse,
                    movement_type=self.MOVEMENT_TYPES[adjustment_type],
                    quantity=movement_quantity,
                    movement_date=datetime.now(),
                    reference_type='ADJUSTMENT',
                    reference_id=None,
                    notes=f"{self.REASON_CODES[reason]}: {notes}" if notes else self.REASON_CODES[reason],
                    created_by=user
                )
                
                return {
                    'success': True,
                    'new_quantity': new_quantity,
                    'movement_id': str(movement.id),
                    'snapshot_id': str(snapshot.id)
                }
                
        except Exception as e:
            logger.error(f"Stock adjustment failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def transfer_stock(
        self,
        product_id: str,
        from_warehouse_id: str,
        to_warehouse_id: str,
        quantity: int,
        notes: str = "",
        user: Optional[User] = None,
        transfer_date: Optional[date] = None
    ) -> Dict:
        """
        Transfer stock between warehouses
        
        Args:
            product_id: Product UUID string
            from_warehouse_id: Source warehouse UUID
            to_warehouse_id: Destination warehouse UUID
            quantity: Quantity to transfer
            notes: Optional notes
            user: User performing the transfer
            transfer_date: Date of transfer (defaults to today)
            
        Returns:
            Dictionary with operation result
        """
        try:
            # Validate inputs
            if quantity <= 0:
                return {
                    'success': False,
                    'error': 'Quantity must be positive'
                }
            
            if from_warehouse_id == to_warehouse_id:
                return {
                    'success': False,
                    'error': 'Source and destination warehouses must be different'
                }
            
            # Get objects
            try:
                product = Product.objects.get(id=product_id)
                from_warehouse = Warehouse.objects.get(id=from_warehouse_id)
                to_warehouse = Warehouse.objects.get(id=to_warehouse_id)
            except Product.DoesNotExist:
                return {
                    'success': False,
                    'error': 'Product not found'
                }
            except Warehouse.DoesNotExist:
                return {
                    'success': False,
                    'error': 'Warehouse not found'
                }
            
            # Set transfer date
            if transfer_date is None:
                transfer_date = date.today()
            
            # Perform transfer in transaction
            with transaction.atomic():
                # Get source snapshot
                from_snapshot, created = InventorySnapshot.objects.get_or_create(
                    product=product,
                    warehouse=from_warehouse,
                    snapshot_date=transfer_date,
                    defaults={
                        'quantity_available': 0,
                        'quantity_reserved': 0,
                        'legacy_warehouse_id': from_warehouse.name
                    }
                )
                
                # Check if we have enough stock
                if from_snapshot.quantity_available < quantity:
                    return {
                        'success': False,
                        'error': f'Insufficient stock in source warehouse. Available: {from_snapshot.quantity_available}, Requested: {quantity}'
                    }
                
                # Update source snapshot
                from_snapshot.quantity_available -= quantity
                from_snapshot.save()
                
                # Get/create destination snapshot
                to_snapshot, created = InventorySnapshot.objects.get_or_create(
                    product=product,
                    warehouse=to_warehouse,
                    snapshot_date=transfer_date,
                    defaults={
                        'quantity_available': 0,
                        'quantity_reserved': 0,
                        'legacy_warehouse_id': to_warehouse.name
                    }
                )
                
                # Update destination snapshot
                to_snapshot.quantity_available += quantity
                to_snapshot.save()
                
                # Create outbound movement
                outbound_movement = InventoryMovement.objects.create(
                    product=product,
                    warehouse=from_warehouse,
                    movement_type='TRANSFER',
                    quantity=-quantity,
                    movement_date=datetime.now(),
                    reference_type='TRANSFER',
                    reference_id=None,
                    notes=f"Transfer to {to_warehouse.name}: {notes}" if notes else f"Transfer to {to_warehouse.name}",
                    created_by=user
                )
                
                # Create inbound movement
                inbound_movement = InventoryMovement.objects.create(
                    product=product,
                    warehouse=to_warehouse,
                    movement_type='TRANSFER',
                    quantity=quantity,
                    movement_date=datetime.now(),
                    reference_type='TRANSFER',
                    reference_id=str(outbound_movement.id),
                    notes=f"Transfer from {from_warehouse.name}: {notes}" if notes else f"Transfer from {from_warehouse.name}",
                    created_by=user
                )
                
                return {
                    'success': True,
                    'from_quantity': from_snapshot.quantity_available,
                    'to_quantity': to_snapshot.quantity_available,
                    'outbound_movement_id': str(outbound_movement.id),
                    'inbound_movement_id': str(inbound_movement.id)
                }
                
        except Exception as e:
            logger.error(f"Stock transfer failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_current_stock(self, product_id: str, warehouse_id: str = None) -> Dict:
        """
        Get current stock level for a product
        
        Args:
            product_id: Product UUID string
            warehouse_id: Optional warehouse ID (if None, returns total across all warehouses)
            
        Returns:
            Dictionary with stock information
        """
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return {
                'success': False,
                'error': 'Product not found'
            }
        
        today = date.today()
        
        if warehouse_id:
            # Get stock for specific warehouse
            try:
                warehouse = Warehouse.objects.get(id=warehouse_id)
            except Warehouse.DoesNotExist:
                return {
                    'success': False,
                    'error': 'Warehouse not found'
                }
            
            snapshot = InventorySnapshot.objects.filter(
                product=product,
                warehouse=warehouse,
                snapshot_date=today
            ).first()
            
            if snapshot:
                return {
                    'success': True,
                    'product_id': product_id,
                    'warehouse_id': warehouse_id,
                    'warehouse_name': warehouse.name,
                    'quantity_available': snapshot.quantity_available,
                    'quantity_reserved': snapshot.quantity_reserved,
                    'total_quantity': snapshot.quantity_available + snapshot.quantity_reserved
                }
            else:
                return {
                    'success': True,
                    'product_id': product_id,
                    'warehouse_id': warehouse_id,
                    'warehouse_name': warehouse.name,
                    'quantity_available': 0,
                    'quantity_reserved': 0,
                    'total_quantity': 0
                }
        else:
            # Get total stock across all warehouses
            snapshots = InventorySnapshot.objects.filter(
                product=product,
                snapshot_date=today
            )
            
            total_available = sum(snapshot.quantity_available for snapshot in snapshots)
            total_reserved = sum(snapshot.quantity_reserved for snapshot in snapshots)
            
            warehouse_details = []
            for snapshot in snapshots:
                warehouse_details.append({
                    'warehouse_id': str(snapshot.warehouse.id) if snapshot.warehouse else None,
                    'warehouse_name': snapshot.warehouse.name if snapshot.warehouse else 'Unknown',
                    'quantity_available': snapshot.quantity_available,
                    'quantity_reserved': snapshot.quantity_reserved
                })
            
            return {
                'success': True,
                'product_id': product_id,
                'quantity_available': total_available,
                'quantity_reserved': total_reserved,
                'total_quantity': total_available + total_reserved,
                'warehouses': warehouse_details
            }
    
    def get_stock_history(
        self, 
        product_id: str, 
        warehouse_id: str = None, 
        start_date: date = None, 
        end_date: date = None,
        limit: int = 100
    ) -> Dict:
        """
        Get stock history for a product
        
        Args:
            product_id: Product UUID string
            warehouse_id: Optional warehouse ID
            start_date: Start date for history (default: 30 days ago)
            end_date: End date for history (default: today)
            limit: Maximum number of records to return
            
        Returns:
            Dictionary with stock history
        """
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return {
                'success': False,
                'error': 'Product not found'
            }
        
        # Set default dates
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = date(end_date.year, end_date.month, end_date.day - 30)
        
        # Build query
        query = InventorySnapshot.objects.filter(
            product=product,
            snapshot_date__gte=start_date,
            snapshot_date__lte=end_date
        ).order_by('-snapshot_date')
        
        if warehouse_id:
            try:
                warehouse = Warehouse.objects.get(id=warehouse_id)
                query = query.filter(warehouse=warehouse)
            except Warehouse.DoesNotExist:
                return {
                    'success': False,
                    'error': 'Warehouse not found'
                }
        
        # Limit results
        snapshots = query[:limit]
        
        # Format results
        history = []
        for snapshot in snapshots:
            history.append({
                'date': snapshot.snapshot_date.isoformat(),
                'warehouse_id': str(snapshot.warehouse.id) if snapshot.warehouse else None,
                'warehouse_name': snapshot.warehouse.name if snapshot.warehouse else 'Unknown',
                'quantity_available': snapshot.quantity_available,
                'quantity_reserved': snapshot.quantity_reserved,
                'total_quantity': snapshot.quantity_available + snapshot.quantity_reserved
            })
        
        return {
            'success': True,
            'product_id': product_id,
            'history': history,
            'count': len(history)
        }


# Convenience functions for easier usage
def adjust_product_stock(
    product_id: str,
    warehouse_id: str,
    adjustment_type: str,
    quantity: int,
    reason: str,
    notes: str = "",
    user: User = None
) -> Dict:
    """
    Adjust stock level for a product
    
    Returns:
        Dictionary with operation result
    """
    service = InventoryService()
    return service.adjust_stock(
        product_id=product_id,
        warehouse_id=warehouse_id,
        adjustment_type=adjustment_type,
        quantity=quantity,
        reason=reason,
        notes=notes,
        user=user
    )


def transfer_product_stock(
    product_id: str,
    from_warehouse_id: str,
    to_warehouse_id: str,
    quantity: int,
    notes: str = "",
    user: User = None
) -> Dict:
    """
    Transfer stock between warehouses
    
    Returns:
        Dictionary with operation result
    """
    service = InventoryService()
    return service.transfer_stock(
        product_id=product_id,
        from_warehouse_id=from_warehouse_id,
        to_warehouse_id=to_warehouse_id,
        quantity=quantity,
        notes=notes,
        user=user
    )


def get_product_stock(product_id: str, warehouse_id: str = None) -> Dict:
    """
    Get current stock level for a product
    
    Returns:
        Dictionary with stock information
    """
    service = InventoryService()
    return service.get_current_stock(product_id, warehouse_id)


def get_product_stock_history(
    product_id: str,
    warehouse_id: str = None,
    start_date: date = None,
    end_date: date = None,
    limit: int = 100
) -> Dict:
    """
    Get stock history for a product
    
    Returns:
        Dictionary with stock history
    """
    service = InventoryService()
    return service.get_stock_history(
        product_id=product_id,
        warehouse_id=warehouse_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )