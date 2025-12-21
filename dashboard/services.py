"""
Dashboard metrics calculation service
"""
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
from django.db.models import Sum, Avg, Count, Q, F, DecimalField, OuterRef, Subquery, Case, When, Value, FloatField
from django.db.models.functions import Coalesce
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
        """Calculate total inventory value across all warehouses - OPTIMIZED"""
        try:
            week_ago = datetime.now() - timedelta(days=7)
            
            # Subquery for latest inventory snapshot per product
            latest_snapshot_subquery = InventorySnapshot.objects.filter(
                product=OuterRef('pk')
            ).order_by('-snapshot_date').values('quantity_available')[:1]
            
            # Subquery for snapshot from week ago
            week_ago_snapshot_subquery = InventorySnapshot.objects.filter(
                product=OuterRef('pk'),
                snapshot_date__lte=week_ago.date()
            ).order_by('-snapshot_date').values('quantity_available')[:1]
            
            # Single aggregated query instead of N+1 loops
            result = Product.objects.filter(
                company=self.company,
                is_active=True
            ).annotate(
                latest_qty=Coalesce(Subquery(latest_snapshot_subquery), Value(0)),
                week_ago_qty=Coalesce(Subquery(week_ago_snapshot_subquery), Value(0)),
                current_value=F('latest_qty') * Coalesce(F('cost_price'), Value(0), output_field=DecimalField()),
                previous_value=F('week_ago_qty') * Coalesce(F('cost_price'), Value(0), output_field=DecimalField())
            ).aggregate(
                total_value=Coalesce(Sum('current_value'), Value(0)),
                previous_value=Coalesce(Sum('previous_value'), Value(0)),
                product_count=Count('id')
            )
            
            total_value = float(result['total_value'] or 0)
            previous_value = float(result['previous_value'] or 0)
            product_count = result['product_count'] or 0
            
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
        """Calculate average inventory turnover rate - OPTIMIZED"""
        try:
            # Calculate for last 30 days
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            # Subquery for total sales per product
            sales_subquery = SalesTransaction.objects.filter(
                product=OuterRef('pk'),
                sale_date__gte=thirty_days_ago
            ).values('product').annotate(
                total=Sum('quantity')
            ).values('total')[:1]
            
            # Subquery for start inventory
            start_inventory_subquery = InventorySnapshot.objects.filter(
                product=OuterRef('pk'),
                snapshot_date__gte=thirty_days_ago
            ).order_by('snapshot_date').values('quantity_available')[:1]
            
            # Subquery for end inventory
            end_inventory_subquery = InventorySnapshot.objects.filter(
                product=OuterRef('pk'),
                snapshot_date__gte=thirty_days_ago
            ).order_by('-snapshot_date').values('quantity_available')[:1]
            
            # Single aggregated query with all calculations
            products_data = Product.objects.filter(
                company=self.company,
                is_active=True,
                salestransaction__sale_date__gte=thirty_days_ago
            ).distinct().annotate(
                total_sales=Coalesce(Subquery(sales_subquery), Value(0)),
                start_inv=Coalesce(Subquery(start_inventory_subquery), Value(0)),
                end_inv=Coalesce(Subquery(end_inventory_subquery), Value(0))
            ).annotate(
                avg_inventory=(F('start_inv') + F('end_inv')) / 2.0
            ).filter(
                total_sales__gt=0,
                avg_inventory__gt=0
            ).annotate(
                turnover_rate=F('total_sales') / F('avg_inventory'),
                turnover_days=Case(
                    When(turnover_rate__gt=0, then=Value(30.0) / F('turnover_rate')),
                    default=Value(0.0),
                    output_field=FloatField()
                )
            ).aggregate(
                total_turnover_days=Coalesce(Sum('turnover_days'), Value(0.0)),
                valid_products=Count('id')
            )
            
            valid_products = products_data['valid_products'] or 0
            
            if valid_products > 0:
                avg_turnover_days = products_data['total_turnover_days'] / valid_products
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
        """Calculate forecast accuracy if sufficient history exists - OPTIMIZED"""
        try:
            # Need at least 14 days of data for meaningful accuracy calculation
            two_weeks_ago = datetime.now() - timedelta(days=14)
            
            # Subquery for forecasted sales per product
            forecast_subquery = Forecast.objects.filter(
                product=OuterRef('pk'),
                generated_at__gte=two_weeks_ago
            ).values('product').annotate(
                total=Sum('predicted_quantity')
            ).values('total')[:1]
            
            # Subquery for actual sales per product
            actual_sales_subquery = SalesTransaction.objects.filter(
                product=OuterRef('pk'),
                sale_date__gte=two_weeks_ago
            ).values('product').annotate(
                total=Sum('quantity')
            ).values('total')[:1]
            
            # Single aggregated query with accuracy calculation
            products_data = Product.objects.filter(
                company=self.company,
                is_active=True,
                forecasting_forecast__generated_at__gte=two_weeks_ago,
                salestransaction__sale_date__gte=two_weeks_ago
            ).distinct().annotate(
                forecasted_sales=Coalesce(Subquery(forecast_subquery), Value(0.0)),
                actual_sales=Coalesce(Subquery(actual_sales_subquery), Value(0.0))
            ).filter(
                actual_sales__gt=0,
                forecasted_sales__gt=0
            ).annotate(
                abs_error=Case(
                    When(actual_sales__gt=0, 
                         then=(F('forecasted_sales') - F('actual_sales')) * 100.0 / F('actual_sales')),
                    default=Value(0.0),
                    output_field=FloatField()
                )
            ).annotate(
                abs_error_positive=Case(
                    When(abs_error__lt=0, then=-F('abs_error')),
                    default=F('abs_error'),
                    output_field=FloatField()
                )
            ).aggregate(
                total_error=Coalesce(Sum('abs_error_positive'), Value(0.0)),
                product_count=Count('id')
            )
            
            product_count = products_data['product_count'] or 0
            
            if product_count > 0:
                total_forecast_error = products_data['total_error'] or 0
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