"""
Dashboard metrics calculation service
"""
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
from django.db.models import Sum, Avg, Count, Q
from products.models import Product
from sales.models import SalesTransaction, InventorySnapshot
from procurement.models import ProcurementRecommendation
from forecasting.models import Forecast

logger = logging.getLogger(__name__)


class DashboardMetricsService:
    """Service for calculating dashboard metrics"""
    
    def __init__(self, company):
        self.company = company
    
    def get_total_inventory_value(self) -> Dict[str, Any]:
        """Calculate total inventory value across all warehouses"""
        try:
            # Get all active products for the company
            products = Product.objects.filter(
                company=self.company,
                is_active=True
            )
            
            total_value = 0
            product_count = products.count()
            
            # Calculate value for each product
            for product in products:
                # Get latest inventory snapshot for this product
                latest_snapshot = InventorySnapshot.objects.filter(
                    product=product
                ).order_by('-created_at').first()
                
                if latest_snapshot:
                    quantity = latest_snapshot.quantity_available
                    cost_price = product.cost_price or 0
                    total_value += quantity * cost_price
            
            # Compare with previous period (last week)
            week_ago = datetime.now() - timedelta(days=7)
            previous_value = 0
            
            for product in products:
                # Get inventory snapshot from a week ago
                snapshot_week_ago = InventorySnapshot.objects.filter(
                    product=product,
                    created_at__date__lte=week_ago.date()
                ).order_by('-created_at').first()
                
                if snapshot_week_ago:
                    quantity = snapshot_week_ago.quantity_available
                    cost_price = product.cost_price or 0
                    previous_value += quantity * cost_price
            
            # Calculate change percentage
            if previous_value > 0:
                change_percentage = ((total_value - previous_value) / previous_value) * 100
            else:
                change_percentage = 0 if total_value == 0 else 100
            
            return {
                'success': True,
                'total_value': total_value,
                'product_count': product_count,
                'change_percentage': round(change_percentage, 2),
                'previous_value': previous_value
            }
            
        except Exception as e:
            logger.error(f"Error calculating total inventory value: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_average_inventory_turnover(self) -> Dict[str, Any]:
        """Calculate average inventory turnover rate"""
        try:
            # Calculate for last 30 days
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            # Get all active products with sales in the last 30 days
            products_with_sales = Product.objects.filter(
                company=self.company,
                is_active=True,
                salestransaction__transaction_date__gte=thirty_days_ago
            ).distinct()
            
            if not products_with_sales.exists():
                return {
                    'success': True,
                    'turnover_days': 0,
                    'turnover_rate': 0,
                    'product_count': 0
                }
            
            total_turnover_days = 0
            valid_products = 0
            
            for product in products_with_sales:
                # Calculate total sales in the period
                total_sales = SalesTransaction.objects.filter(
                    product=product,
                    transaction_date__gte=thirty_days_ago
                ).aggregate(total=Sum('quantity'))['total'] or 0
                
                if total_sales <= 0:
                    continue
                
                # Calculate average inventory during the period
                inventory_snapshots = InventorySnapshot.objects.filter(
                    product=product,
                    created_at__gte=thirty_days_ago
                ).order_by('created_at')
                
                if not inventory_snapshots.exists():
                    continue
                
                # Simple average of start and end inventory
                start_inventory = inventory_snapshots.first().quantity_available
                end_inventory = inventory_snapshots.last().quantity_available
                avg_inventory = (start_inventory + end_inventory) / 2
                
                if avg_inventory <= 0:
                    continue
                
                # Calculate turnover rate for this product
                turnover_rate = total_sales / avg_inventory
                turnover_days = 30 / turnover_rate if turnover_rate > 0 else 0
                
                total_turnover_days += turnover_days
                valid_products += 1
            
            if valid_products > 0:
                avg_turnover_days = total_turnover_days / valid_products
            else:
                avg_turnover_days = 0
            
            # Determine status color
            if avg_turnover_days < 30:
                status_color = 'green'
            elif avg_turnover_days <= 60:
                status_color = 'yellow'
            else:
                status_color = 'red'
            
            return {
                'success': True,
                'turnover_days': round(avg_turnover_days, 2),
                'turnover_rate': round(30 / avg_turnover_days if avg_turnover_days > 0 else 0, 2),
                'product_count': valid_products,
                'status_color': status_color
            }
            
        except Exception as e:
            logger.error(f"Error calculating inventory turnover: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_stock_status_distribution(self) -> Dict[str, Any]:
        """Get distribution of products by stock status"""
        try:
            # Get all procurement recommendations for active products
            recommendations = ProcurementRecommendation.objects.filter(
                product__company=self.company,
                product__is_active=True
            ).select_related('product')
            
            green_count = recommendations.filter(action_category='NORMAL').count()
            yellow_count = recommendations.filter(action_category='ATTENTION_REQUIRED').count()
            red_count = recommendations.filter(action_category='ORDER_TODAY').count()
            
            total_count = green_count + yellow_count + red_count
            
            # Calculate percentages
            green_percent = (green_count / total_count * 100) if total_count > 0 else 0
            yellow_percent = (yellow_count / total_count * 100) if total_count > 0 else 0
            red_percent = (red_count / total_count * 100) if total_count > 0 else 0
            
            return {
                'success': True,
                'distribution': {
                    'green': {
                        'count': green_count,
                        'percentage': round(green_percent, 2),
                        'label': 'Healthy'
                    },
                    'yellow': {
                        'count': yellow_count,
                        'percentage': round(yellow_percent, 2),
                        'label': 'Warning'
                    },
                    'red': {
                        'count': red_count,
                        'percentage': round(red_percent, 2),
                        'label': 'Critical'
                    }
                },
                'total_count': total_count
            }
            
        except Exception as e:
            logger.error(f"Error getting stock status distribution: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_top_urgent_products(self, limit: int = 5) -> Dict[str, Any]:
        """Get top urgent products based on priority score"""
        try:
            # Get top urgent products
            urgent_recommendations = ProcurementRecommendation.objects.filter(
                product__company=self.company,
                product__is_active=True,
                action_category='ORDER_TODAY'
            ).select_related('product').order_by('-priority_score')[:limit]
            
            urgent_products = []
            for rec in urgent_recommendations:
                # Try to get runway days from the recommendation or calculate it
                runway_days = getattr(rec, 'runway_days', 0)
                
                urgent_products.append({
                    'product_id': str(rec.product.id),
                    'sku': rec.product.sku,
                    'name': rec.product.name,
                    'runway_days': runway_days,
                    'recommended_quantity': rec.recommended_quantity,
                    'priority_score': rec.priority_score
                })
            
            return {
                'success': True,
                'products': urgent_products,
                'count': len(urgent_products)
            }
            
        except Exception as e:
            logger.error(f"Error getting top urgent products: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_recent_activity_summary(self) -> Dict[str, Any]:
        """Get summary of recent activities"""
        try:
            # Last 7 days
            week_ago = datetime.now() - timedelta(days=7)
            
            # Last synchronization time
            last_sync = None
            # This would typically come from integration logs or a sync tracking model
            # For now, we'll use a placeholder
            
            # Recent manual adjustments
            recent_adjustments = 0  # Would come from InventoryMovement with ADJUSTMENT type
            
            # Recent purchase orders
            recent_purchase_orders = 0  # Would come from PurchaseOrder model
            
            # Forecast generation timestamp
            last_forecast = Forecast.objects.filter(
                product__company=self.company
            ).order_by('-generated_at').first()
            
            last_forecast_time = last_forecast.generated_at if last_forecast else None
            
            return {
                'success': True,
                'activities': {
                    'last_sync': last_sync,
                    'recent_adjustments': recent_adjustments,
                    'recent_purchase_orders': recent_purchase_orders,
                    'last_forecast': last_forecast_time
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting recent activity summary: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_forecast_accuracy(self) -> Dict[str, Any]:
        """Calculate forecast accuracy if sufficient history exists"""
        try:
            # Need at least 14 days of data for meaningful accuracy calculation
            two_weeks_ago = datetime.now() - timedelta(days=14)
            
            # Get products with both forecasts and actual sales
            products_with_data = Product.objects.filter(
                company=self.company,
                is_active=True,
                forecasting_forecast__generated_at__gte=two_weeks_ago,
                salestransaction__transaction_date__gte=two_weeks_ago
            ).distinct()
            
            if not products_with_data.exists():
                return {
                    'success': True,
                    'accuracy_percentage': 0,
                    'trend': 'insufficient_data',
                    'message': 'Insufficient data for accuracy calculation'
                }
            
            total_forecast_error = 0
            total_actual_sales = 0
            product_count = 0
            
            for product in products_with_data:
                # Get forecasts for the last 14 days
                forecasts = Forecast.objects.filter(
                    product=product,
                    generated_at__gte=two_weeks_ago
                ).order_by('forecast_date')
                
                if not forecasts.exists():
                    continue
                
                # Get actual sales for the same period
                actual_sales = SalesTransaction.objects.filter(
                    product=product,
                    transaction_date__gte=two_weeks_ago
                ).aggregate(total=Sum('quantity'))['total'] or 0
                
                # Calculate forecasted sales for the same period
                forecasted_sales = sum(f.predicted_quantity for f in forecasts)
                
                if actual_sales > 0:
                    # Calculate absolute percentage error
                    error = abs(forecasted_sales - actual_sales) / actual_sales * 100
                    total_forecast_error += error
                    total_actual_sales += actual_sales
                    product_count += 1
            
            if product_count > 0:
                avg_accuracy = 100 - (total_forecast_error / product_count)
                
                # Determine trend (simplified)
                trend = 'stable'  # Would be calculated based on historical accuracy trends
                
                return {
                    'success': True,
                    'accuracy_percentage': round(avg_accuracy, 2),
                    'trend': trend,
                    'product_count': product_count
                }
            else:
                return {
                    'success': True,
                    'accuracy_percentage': 0,
                    'trend': 'insufficient_data',
                    'message': 'Insufficient data for accuracy calculation'
                }
                
        except Exception as e:
            logger.error(f"Error calculating forecast accuracy: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_all_dashboard_metrics(self) -> Dict[str, Any]:
        """Get all dashboard metrics in one call"""
        try:
            metrics = {
                'total_inventory_value': self.get_total_inventory_value(),
                'average_turnover': self.get_average_inventory_turnover(),
                'stock_status_distribution': self.get_stock_status_distribution(),
                'top_urgent_products': self.get_top_urgent_products(),
                'recent_activities': self.get_recent_activity_summary(),
                'forecast_accuracy': self.get_forecast_accuracy()
            }
            
            return {
                'success': True,
                'metrics': metrics,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting all dashboard metrics: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }