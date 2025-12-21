"""
URL configuration for sales app
"""
from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    # Warehouse management page
    path('warehouses/', views.warehouses, name='warehouses'),
    
    # Inventory management API endpoints
    path('api/inventory/adjust/', views.inventory_adjustment, name='inventory_adjustment'),
    path('api/inventory/transfer/', views.inventory_transfer, name='inventory_transfer'),
    path('api/inventory/status/', views.inventory_status, name='inventory_status'),
    path('api/inventory/status/<uuid:product_id>/', views.inventory_status, name='inventory_status_product'),
    path('api/inventory/history/<uuid:product_id>/', views.inventory_history, name='inventory_history'),
    path('api/inventory/movements/', views.inventory_movements, name='inventory_movements'),
    
    # Webhook endpoint for e-commerce platform integrations
    path('api/integrations/webhook/', views.webhook_handler, name='webhook_handler'),
]