"""
URL configuration for dashboard app
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard API endpoints
    path('metrics/', views.DashboardMetricsView.as_view(), name='dashboard_metrics'),
    path('inventory-value/', views.InventoryValueView.as_view(), name='inventory_value'),
    path('inventory-turnover/', views.InventoryTurnoverView.as_view(), name='inventory_turnover'),
    path('stock-status/', views.StockStatusDistributionView.as_view(), name='stock_status'),
    path('urgent-products/', views.TopUrgentProductsView.as_view(), name='urgent_products'),
    path('recent-activities/', views.RecentActivitiesView.as_view(), name='recent_activities'),
    path('forecast-accuracy/', views.ForecastAccuracyView.as_view(), name='forecast_accuracy'),
]