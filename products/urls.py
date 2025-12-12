"""
URL configuration for products app
"""
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Products API endpoints
    path('', views.ProductsListView.as_view(), name='products_list'),
    path('<uuid:product_id>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('warehouses/', views.WarehousesListView.as_view(), name='warehouses_list'),
]
