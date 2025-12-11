"""
URL configuration for export app
"""
from django.urls import path
from . import views

app_name = 'export'

urlpatterns = [
    # Export API endpoints
    path('api/export/order/', views.ExportOrderView.as_view(), name='export_order'),
    path('api/export/order/<str:export_id>/', views.ExportStatusView.as_view(), name='export_status'),
]