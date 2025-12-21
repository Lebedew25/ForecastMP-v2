"""
URL configuration for dashboard app
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Analytics dashboard page
    path('analytics/', views.analytics_view, name='analytics'),
    
    # Dashboard API endpoints
    path('api/dashboard/metrics/', views.DashboardMetricsView.as_view(), name='dashboard_metrics'),
    path('api/dashboard/inventory-value/', views.InventoryValueView.as_view(), name='inventory_value'),
    path('api/dashboard/inventory-turnover/', views.InventoryTurnoverView.as_view(), name='inventory_turnover'),
    path('api/dashboard/stock-status/', views.StockStatusDistributionView.as_view(), name='stock_status'),
    path('api/dashboard/urgent-products/', views.TopUrgentProductsView.as_view(), name='urgent_products'),
    path('api/dashboard/recent-activities/', views.RecentActivitiesView.as_view(), name='recent_activities'),
    path('api/dashboard/forecast-accuracy/', views.ForecastAccuracyView.as_view(), name='forecast_accuracy'),
]