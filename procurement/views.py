from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import date
from .models import ProcurementRecommendation
from products.models import Product


@login_required
def dashboard(request):
    """Main procurement dashboard"""
    company = request.user.company
    today = date.today()
    
    if not company:
        return render(request, 'procurement/no_company.html')
    
    # Get today's recommendations
    recommendations = ProcurementRecommendation.objects.filter(
        product__company=company,
        analysis_date=today
    ).select_related('product').order_by('-priority_score')
    
    # Split by category
    order_today = recommendations.filter(action_category='ORDER_TODAY')
    already_ordered = recommendations.filter(action_category='ALREADY_ORDERED')
    attention_required = recommendations.filter(action_category='ATTENTION_REQUIRED')
    
    context = {
        'company': company,
        'analysis_date': today,
        'order_today': order_today,
        'already_ordered': already_ordered,
        'attention_required': attention_required,
        'summary': {
            'total_products': recommendations.count(),
            'order_today_count': order_today.count(),
            'already_ordered_count': already_ordered.count(),
            'attention_required_count': attention_required.count(),
        }
    }
    
    return render(request, 'procurement/dashboard.html', context)


@login_required
def product_detail(request, product_id):
    """Detailed view for a single product"""
    company = request.user.company
    
    try:
        product = Product.objects.get(id=product_id, company=company)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    
    # Get recent recommendations
    recommendations = ProcurementRecommendation.objects.filter(
        product=product
    ).order_by('-analysis_date')[:30]
    
    # Get forecasts
    from forecasting.models import Forecast
    forecasts = Forecast.objects.filter(
        product=product,
        forecast_date__gte=date.today()
    ).order_by('forecast_date')[:30]
    
    # Get recent sales
    from sales.models import DailySalesAggregate
    recent_sales = DailySalesAggregate.objects.filter(
        product=product
    ).order_by('-date')[:30]
    
    context = {
        'product': product,
        'recommendations': recommendations,
        'forecasts': forecasts,
        'recent_sales': recent_sales
    }
    
    return render(request, 'procurement/product_detail.html', context)


@login_required
def api_recommendations(request):
    """API endpoint for recommendations data"""
    company = request.user.company
    today = date.today()
    
    if not company:
        return JsonResponse({'error': 'No company associated'}, status=400)
    
    recommendations = ProcurementRecommendation.objects.filter(
        product__company=company,
        analysis_date=today
    ).select_related('product')
    
    data = {
        'date': today.isoformat(),
        'items': []
    }
    
    for rec in recommendations:
        data['items'].append({
            'product_id': str(rec.product.id),
            'sku': rec.product.sku,
            'name': rec.product.name,
            'current_stock': rec.current_stock,
            'runway_days': rec.runway_days,
            'stockout_date': rec.stockout_date.isoformat() if rec.stockout_date else None,
            'recommended_quantity': rec.recommended_quantity,
            'action_category': rec.action_category,
            'priority_score': float(rec.priority_score),
            'notes': rec.notes
        })
    
    return JsonResponse(data)
