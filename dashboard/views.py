"""
Dashboard views for enhanced metrics and widgets
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import render
import logging
from .services import DashboardMetricsService

logger = logging.getLogger(__name__)


@login_required
def dashboard_view(request):
    """Main dashboard HTML view"""
    return render(request, 'dashboard/dashboard.html')


@method_decorator(login_required, name='dispatch')
class DashboardMetricsView(View):
    """API endpoint for retrieving dashboard metrics"""
    
    def get(self, request):
        """Get all dashboard metrics"""
        try:
            # Initialize metrics service
            service = DashboardMetricsService(request.user.company)
            
            # Get all metrics
            metrics = service.get_all_dashboard_metrics()
            
            if metrics['success']:
                return JsonResponse({
                    'success': True,
                    'metrics': metrics['metrics'],
                    'generated_at': metrics['generated_at']
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': metrics['error']
                }, status=500)
                
        except Exception as e:
            logger.error(f"Dashboard metrics error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)


@method_decorator(login_required, name='dispatch')
class InventoryValueView(View):
    """API endpoint for total inventory value metric"""
    
    def get(self, request):
        """Get total inventory value"""
        try:
            service = DashboardMetricsService(request.user.company)
            result = service.get_total_inventory_value()
            
            if result['success']:
                return JsonResponse({
                    'success': True,
                    'metric': result
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result['error']
                }, status=500)
                
        except Exception as e:
            logger.error(f"Inventory value error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)


@method_decorator(login_required, name='dispatch')
class InventoryTurnoverView(View):
    """API endpoint for average inventory turnover metric"""
    
    def get(self, request):
        """Get average inventory turnover"""
        try:
            service = DashboardMetricsService(request.user.company)
            result = service.get_average_inventory_turnover()
            
            if result['success']:
                return JsonResponse({
                    'success': True,
                    'metric': result
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result['error']
                }, status=500)
                
        except Exception as e:
            logger.error(f"Inventory turnover error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)


@method_decorator(login_required, name='dispatch')
class StockStatusDistributionView(View):
    """API endpoint for stock status distribution metric"""
    
    def get(self, request):
        """Get stock status distribution"""
        try:
            service = DashboardMetricsService(request.user.company)
            result = service.get_stock_status_distribution()
            
            if result['success']:
                return JsonResponse({
                    'success': True,
                    'metric': result
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result['error']
                }, status=500)
                
        except Exception as e:
            logger.error(f"Stock status distribution error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)


@method_decorator(login_required, name='dispatch')
class TopUrgentProductsView(View):
    """API endpoint for top urgent products"""
    
    def get(self, request):
        """Get top urgent products"""
        try:
            # Get limit from query parameters, default to 5
            limit = int(request.GET.get('limit', 5))
            
            service = DashboardMetricsService(request.user.company)
            result = service.get_top_urgent_products(limit)
            
            if result['success']:
                return JsonResponse({
                    'success': True,
                    'metric': result
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result['error']
                }, status=500)
                
        except Exception as e:
            logger.error(f"Top urgent products error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)


@method_decorator(login_required, name='dispatch')
class RecentActivitiesView(View):
    """API endpoint for recent activities summary"""
    
    def get(self, request):
        """Get recent activities summary"""
        try:
            service = DashboardMetricsService(request.user.company)
            result = service.get_recent_activity_summary()
            
            if result['success']:
                return JsonResponse({
                    'success': True,
                    'metric': result
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result['error']
                }, status=500)
                
        except Exception as e:
            logger.error(f"Recent activities error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)


@method_decorator(login_required, name='dispatch')
class ForecastAccuracyView(View):
    """API endpoint for forecast accuracy metric"""
    
    def get(self, request):
        """Get forecast accuracy"""
        try:
            service = DashboardMetricsService(request.user.company)
            result = service.get_forecast_accuracy()
            
            if result['success']:
                return JsonResponse({
                    'success': True,
                    'metric': result
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result['error']
                }, status=500)
                
        except Exception as e:
            logger.error(f"Forecast accuracy error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)


@login_required
def analytics_view(request):
    """Analytics dashboard view"""
    return render(request, 'dashboard/analytics.html')