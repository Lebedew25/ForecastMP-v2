from django.urls import path
from . import views

app_name = 'procurement'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('product/<uuid:product_id>/', views.product_detail, name='product_detail'),
    path('api/recommendations/', views.api_recommendations, name='api_recommendations'),
]
