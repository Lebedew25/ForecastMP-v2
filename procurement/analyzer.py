"""
Procurement Recommendation Engine
Calculates inventory runway, identifies stockout risks, and generates purchase recommendations
"""
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List, Tuple
from django.db.models import Sum, Q


class ProcurementAnalyzer:
    """Analyzes inventory and generates procurement recommendations"""
    
    def __init__(self, product, current_date=None):
        """
        Args:
            product: Product instance
            current_date: Analysis date (defaults to today)
        """
        self.product = product
        self.current_date = current_date or date.today()
        
        # Get product-specific settings
        self.attributes = getattr(product, 'extended_attributes', None)
        self.reorder_threshold = self.attributes.reorder_threshold_days if self.attributes else 7
        self.lead_time = self.attributes.lead_time_days if self.attributes else 14
        self.safety_stock_days = self.attributes.safety_stock_days if self.attributes else 3
        self.min_order_qty = self.attributes.minimum_order_quantity if self.attributes else 1
    
    def get_current_inventory(self) -> int:
        """Get current available inventory"""
        from sales.models import InventorySnapshot
        
        snapshot = InventorySnapshot.objects.filter(
            product=self.product,
            snapshot_date=self.current_date
        ).order_by('-snapshot_date').first()
        
        return snapshot.quantity_available if snapshot else 0
    
    def calculate_daily_burn_rate(self, lookback_days: int = 30) -> Decimal:
        """Calculate average daily sales over lookback period"""
        from sales.models import DailySalesAggregate
        
        start_date = self.current_date - timedelta(days=lookback_days)
        
        aggregates = DailySalesAggregate.objects.filter(
            product=self.product,
            date__gte=start_date,
            date__lte=self.current_date
        )
        
        total_quantity = aggregates.aggregate(total=Sum('total_quantity'))['total'] or 0
        days_with_sales = aggregates.count()
        
        if days_with_sales == 0:
            return Decimal('0')
        
        # Average daily sales
        return Decimal(total_quantity) / Decimal(days_with_sales)
    
    def calculate_runway_days(self, current_stock: int, daily_burn_rate: Decimal) -> int:
        """Calculate days until stockout"""
        if daily_burn_rate <= 0:
            return 999  # Effectively infinite if no sales
        
        runway = int(current_stock / daily_burn_rate)
        return max(0, runway)
    
    def calculate_stockout_date(self, runway_days: int) -> date:
        """Calculate predicted stockout date"""
        return self.current_date + timedelta(days=runway_days)
    
    def get_in_transit_quantity(self) -> int:
        """Get quantity from active purchase orders"""
        from procurement.models import PurchaseOrderItem, PurchaseOrder
        
        in_transit_statuses = ['SUBMITTED', 'CONFIRMED', 'IN_TRANSIT']
        
        po_items = PurchaseOrderItem.objects.filter(
            product=self.product,
            purchase_order__status__in=in_transit_statuses
        )
        
        total_in_transit = sum(item.quantity_in_transit for item in po_items)
        return total_in_transit
    
    def calculate_recommended_quantity(
        self,
        daily_burn_rate: Decimal,
        current_stock: int,
        in_transit_qty: int
    ) -> int:
        """Calculate optimal order quantity"""
        
        if daily_burn_rate <= 0:
            return 0
        
        # Total coverage period = lead time + safety stock
        total_coverage_days = self.lead_time + self.safety_stock_days
        
        # Required inventory = coverage period * burn rate
        required_inventory = int(daily_burn_rate * total_coverage_days)
        
        # Available inventory = current + in transit
        available_inventory = current_stock + in_transit_qty
        
        # Recommended order = required - available
        recommended = required_inventory - available_inventory
        
        # Apply minimum order quantity
        if 0 < recommended < self.min_order_qty:
            recommended = self.min_order_qty
        
        return max(0, recommended)
    
    def calculate_priority_score(
        self,
        runway_days: int,
        daily_burn_rate: Decimal,
        forecast_confidence: Decimal = None
    ) -> Decimal:
        """Calculate urgency/priority score (0-100)"""
        
        # Base score from runway days
        if runway_days <= 0:
            base_score = 100
        elif runway_days <= self.reorder_threshold:
            # Linear scale from 70-100 based on how close to zero
            base_score = 70 + (30 * (self.reorder_threshold - runway_days) / self.reorder_threshold)
        else:
            # Logarithmic decay for longer runway
            base_score = max(0, 70 - (runway_days - self.reorder_threshold) * 2)
        
        # Adjust for sales velocity (higher burn = higher priority)
        velocity_multiplier = min(1.2, 1.0 + (float(daily_burn_rate) / 100))
        
        # Adjust for forecast confidence (if available)
        confidence_multiplier = 1.0
        if forecast_confidence is not None:
            confidence_multiplier = float(forecast_confidence) / 100
        
        priority = Decimal(base_score) * Decimal(str(velocity_multiplier)) * Decimal(str(confidence_multiplier))
        
        return min(Decimal('100'), max(Decimal('0'), priority))
    
    def determine_action_category(
        self,
        runway_days: int,
        in_transit_qty: int,
        recommended_qty: int,
        daily_burn_rate: Decimal
    ) -> str:
        """Categorize product into action list"""
        
        # Check if already ordered and covers demand
        if in_transit_qty > 0:
            # Calculate if PO covers lead time demand
            lead_time_demand = int(daily_burn_rate * self.lead_time)
            
            if in_transit_qty >= lead_time_demand:
                return 'ALREADY_ORDERED'
            else:
                return 'ATTENTION_REQUIRED'
        
        # Check if critical (needs order today)
        if runway_days <= self.reorder_threshold and recommended_qty > 0:
            return 'ORDER_TODAY'
        
        # Check for anomalies requiring attention
        if recommended_qty > 0 and runway_days <= self.reorder_threshold * 1.5:
            return 'ATTENTION_REQUIRED'
        
        return 'NORMAL'
    
    def analyze(self, forecast_confidence: Decimal = None) -> Dict:
        """Perform complete procurement analysis"""
        
        # Get current state
        current_stock = self.get_current_inventory()
        daily_burn_rate = self.calculate_daily_burn_rate()
        in_transit_qty = self.get_in_transit_quantity()
        
        # Calculate metrics
        runway_days = self.calculate_runway_days(current_stock, daily_burn_rate)
        stockout_date = self.calculate_stockout_date(runway_days)
        recommended_qty = self.calculate_recommended_quantity(
            daily_burn_rate,
            current_stock,
            in_transit_qty
        )
        priority_score = self.calculate_priority_score(
            runway_days,
            daily_burn_rate,
            forecast_confidence
        )
        action_category = self.determine_action_category(
            runway_days,
            in_transit_qty,
            recommended_qty,
            daily_burn_rate
        )
        
        # Generate notes
        notes = self._generate_notes(
            runway_days,
            current_stock,
            in_transit_qty,
            recommended_qty,
            action_category
        )
        
        return {
            'product': self.product,
            'analysis_date': self.current_date,
            'current_stock': current_stock,
            'daily_burn_rate': daily_burn_rate,
            'runway_days': runway_days,
            'stockout_date': stockout_date,
            'recommended_quantity': recommended_qty,
            'action_category': action_category,
            'priority_score': priority_score,
            'notes': notes,
            'metadata': {
                'in_transit_quantity': in_transit_qty,
                'reorder_threshold': self.reorder_threshold,
                'lead_time': self.lead_time,
                'safety_stock_days': self.safety_stock_days,
            }
        }
    
    def _generate_notes(
        self,
        runway_days: int,
        current_stock: int,
        in_transit_qty: int,
        recommended_qty: int,
        action_category: str
    ) -> str:
        """Generate human-readable notes for recommendation"""
        
        notes = []
        
        if action_category == 'ORDER_TODAY':
            notes.append(f"Critical: Only {runway_days} days of inventory remaining.")
            notes.append(f"Recommended order: {recommended_qty} units.")
        
        elif action_category == 'ALREADY_ORDERED':
            notes.append(f"Purchase order in transit: {in_transit_qty} units.")
            notes.append(f"Current runway: {runway_days} days.")
        
        elif action_category == 'ATTENTION_REQUIRED':
            notes.append(f"Attention needed: {runway_days} days runway.")
            if in_transit_qty > 0:
                notes.append(f"Partial coverage from PO: {in_transit_qty} units.")
                notes.append(f"Additional {recommended_qty} units may be needed.")
        
        else:
            notes.append(f"Inventory healthy: {runway_days} days runway.")
        
        if current_stock == 0:
            notes.append("Currently out of stock!")
        
        return " ".join(notes)
