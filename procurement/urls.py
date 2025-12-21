from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'procurement'

urlpatterns = [
    path('test/', TemplateView.as_view(template_name='test_page.html'), name='test_page'),  # Test page
    path('', views.dashboard, name='dashboard'),
    path('buying-table/', views.buying_table, name='buying_table'),
    path('orders/', views.purchase_orders, name='purchase_orders'),
    path('orders/<uuid:po_id>/', views.purchase_order_detail, name='purchase_order_detail'),
    path('orders/<uuid:po_id>/update-status/', views.update_order_status, name='update_order_status'),
    path('product/<uuid:product_id>/', views.product_detail, name='product_detail'),
    path('api/recommendations/', views.api_recommendations, name='api_recommendations'),
    path('create-order/', views.create_order, name='create_order'),
    path('submit-order/', views.submit_order, name='submit_order'),
    path('quick-order/<uuid:product_id>/', views.quick_order, name='quick_order'),
    path('export/', views.export_buying_table, name='export_buying_table'),
]
