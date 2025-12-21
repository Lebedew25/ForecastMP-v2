from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from django.db import models
from .models import Forecast, ForecastAccuracy
from products.models import Product
from datetime import date, timedelta

@login_required
def forecasting_dashboard(request):
    """Forecasting dashboard view"""
    company = request.user.company
    
    if not company:
        # Handle case where user has no company
        return render(request, 'dashboard/dashboard.html')
    
    # Get forecast data
    today = date.today()
    forecasts = Forecast.objects.filter(
        product__company=company,
        forecast_date__gte=today
    ).select_related('product').order_by('forecast_date')[:30]
    
    # Get products with forecasts
    products_with_forecasts = Product.objects.filter(
        company=company,
        forecasts__isnull=False
    ).distinct().count()
    
    # Get forecast accuracy data
    accuracy_records = ForecastAccuracy.objects.filter(
        product__company=company
    ).aggregate(
        avg_error=models.Avg('percentage_error')
    )
    avg_accuracy = 100 - (accuracy_records['avg_error'] or 0)
    
    context = {
        'company': company,
        'forecasts': forecasts,
        'products_with_forecasts': products_with_forecasts,
        'forecast_range': f"{today.strftime('%d.%m.%Y')} - {(today + timedelta(days=30)).strftime('%d.%m.%Y')}",
        'avg_accuracy': round(avg_accuracy, 1)
    }
    
    return render(request, 'forecasting/dashboard.html', context)
