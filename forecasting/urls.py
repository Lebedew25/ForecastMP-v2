from django.urls import path
from . import views

app_name = 'forecasting'

urlpatterns = [
    path('', views.forecasting_dashboard, name='dashboard'),
    # Add other forecasting-related URLs here as needed
]