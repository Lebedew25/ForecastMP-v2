from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Case, When, IntegerField
from datetime import date, timedelta
import csv
from .models import ProcurementRecommendation, PurchaseOrder, PurchaseOrderItem
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
    
    # Split by category - use lists to evaluate queryset once
    all_recommendations = list(recommendations)  # Evaluate queryset once
    order_today = [r for r in all_recommendations if r.action_category == 'ORDER_TODAY']
    already_ordered = [r for r in all_recommendations if r.action_category == 'ALREADY_ORDERED']
    attention_required = [r for r in all_recommendations if r.action_category == 'ATTENTION_REQUIRED']
    
    context = {
        'company': company,
        'analysis_date': today,
        'order_today': order_today,
        'already_ordered': already_ordered,
        'attention_required': attention_required,
        'summary': {
            'total_products': len(all_recommendations),
            'order_today_count': len(order_today),
            'already_ordered_count': len(already_ordered),
            'attention_required_count': len(attention_required),
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


@login_required
def buying_table(request):
    """Buying table with filters and bulk actions"""
    company = request.user.company
    today = date.today()
    
    if not company:
        return render(request, 'procurement/no_company.html')
    
    # Get all recommendations for today
    recommendations = ProcurementRecommendation.objects.filter(
        product__company=company,
        analysis_date=today
    ).select_related('product')
    
    # Apply filters
    category = request.GET.get('category')
    if category:
        recommendations = recommendations.filter(product__category=category)
    
    supplier = request.GET.get('supplier')
    if supplier:
        recommendations = recommendations.filter(
            product__attributes__supplier=supplier
        )
    
    health_status = request.GET.get('health_status')
    if health_status:
        recommendations = recommendations.filter(action_category=health_status)
    
    search = request.GET.get('search')
    if search:
        recommendations = recommendations.filter(
            Q(product__sku__icontains=search) |
            Q(product__name__icontains=search)
        )
    
    # Calculate summary stats with single optimized query
    summary_result = recommendations.aggregate(
        normal_count=Count(Case(When(action_category='NORMAL', then=1), output_field=IntegerField())),
        attention_count=Count(Case(When(action_category='ATTENTION_REQUIRED', then=1), output_field=IntegerField())),
        order_today_count=Count(Case(When(action_category='ORDER_TODAY', then=1), output_field=IntegerField())),
        already_ordered_count=Count(Case(When(action_category='ALREADY_ORDERED', then=1), output_field=IntegerField())),
    )
    summary = summary_result
    
    # Get unique categories and suppliers for filters
    categories = Product.objects.filter(
        company=company,
        category__isnull=False
    ).values_list('category', flat=True).distinct().order_by('category')
    
    suppliers = []  # TODO: Get from product attributes or supplier model
    
    # Pagination
    paginator = Paginator(recommendations.order_by('-priority_score'), 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'recommendations': page_obj,
        'summary': summary,
        'categories': categories,
        'suppliers': suppliers,
    }
    
    # If HTMX request, return only table rows
    if request.headers.get('HX-Request'):
        return render(request, 'procurement/partials/buying_table_rows.html', context)
    
    return render(request, 'procurement/buying_table.html', context)


@login_required
def create_order(request):
    """Create purchase order from selected products"""
    if request.method == 'POST':
        company = request.user.company
        product_ids = request.POST.getlist('product_ids')
        
        if not product_ids:
            return JsonResponse({'error': 'No products selected'}, status=400)
        
        # Get recommendations for selected products
        recommendations = ProcurementRecommendation.objects.filter(
            product_id__in=product_ids,
            product__company=company
        ).select_related('product')
        
        context = {
            'recommendations': recommendations,
            'total_items': recommendations.count(),
        }
        
        return render(request, 'procurement/partials/create_order_form.html', context)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def submit_order(request):
    """Submit the purchase order"""
    if request.method == 'POST':
        company = request.user.company
        
        # Generate PO number
        today = date.today()
        po_count = PurchaseOrder.objects.filter(
            company=company,
            order_date=today
        ).count()
        po_number = f"PO-{today.strftime('%Y%m%d')}-{po_count + 1:03d}"
        
        # Create PO
        po = PurchaseOrder.objects.create(
            company=company,
            po_number=po_number,
            order_date=today,
            expected_delivery=today + timedelta(days=14),  # Default 14 days
            status='DRAFT',
            supplier_name=request.POST.get('supplier_name', ''),
            notes=request.POST.get('notes', '')
        )
        
        # Add items
        product_ids = request.POST.getlist('product_ids')
        for product_id in product_ids:
            quantity = request.POST.get(f'quantity_{product_id}')
            if quantity and int(quantity) > 0:
                product = Product.objects.get(id=product_id, company=company)
                PurchaseOrderItem.objects.create(
                    purchase_order=po,
                    product=product,
                    quantity_ordered=int(quantity),
                    unit_cost=request.POST.get(f'unit_cost_{product_id}', 0)
                )
        
        # Update PO status
        po.status = 'SUBMITTED'
        po.save()
        
        return redirect('procurement:purchase_order_detail', po_id=po.id)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def quick_order(request, product_id):
    """Quick order for a single product"""
    if request.method == 'POST':
        company = request.user.company
        product = get_object_or_404(Product, id=product_id, company=company)
        
        # Get latest recommendation
        recommendation = ProcurementRecommendation.objects.filter(
            product=product
        ).order_by('-analysis_date').first()
        
        if not recommendation:
            return JsonResponse({'error': 'No recommendation found'}, status=404)
        
        # Generate PO number
        today = date.today()
        po_count = PurchaseOrder.objects.filter(
            company=company,
            order_date=today
        ).count()
        po_number = f"PO-{today.strftime('%Y%m%d')}-{po_count + 1:03d}"
        
        # Create PO
        po = PurchaseOrder.objects.create(
            company=company,
            po_number=po_number,
            order_date=today,
            expected_delivery=today + timedelta(days=14),
            status='SUBMITTED'
        )
        
        # Add item
        PurchaseOrderItem.objects.create(
            purchase_order=po,
            product=product,
            quantity_ordered=recommendation.recommended_quantity
        )
        
        return JsonResponse({
            'success': True,
            'po_number': po_number,
            'redirect_url': f'/procurement/orders/{po.id}/'
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def export_buying_table(request):
    """Export buying table to CSV"""
    company = request.user.company
    today = date.today()
    
    recommendations = ProcurementRecommendation.objects.filter(
        product__company=company,
        analysis_date=today
    ).select_related('product').order_by('-priority_score')
    
    # Apply same filters as buying_table view
    category = request.GET.get('category')
    if category:
        recommendations = recommendations.filter(product__category=category)
    
    health_status = request.GET.get('health_status')
    if health_status:
        recommendations = recommendations.filter(action_category=health_status)
    
    search = request.GET.get('search')
    if search:
        recommendations = recommendations.filter(
            Q(product__sku__icontains=search) |
            Q(product__name__icontains=search)
        )
    
    # Create CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="buying_table_{today}.csv"'
    response.write('\ufeff'.encode('utf-8'))  # BOM for Excel UTF-8
    
    writer = csv.writer(response)
    writer.writerow([
        'SKU',
        'Название',
        'Категория',
        'Текущий остаток',
        'Дней до стокаута',
        'Прогноз расхода/день',
        'Рекомендуемое количество',
        'Статус',
        'Дата стокаута'
    ])
    
    for rec in recommendations:
        writer.writerow([
            rec.product.sku,
            rec.product.name,
            rec.product.category or '',
            rec.current_stock,
            rec.runway_days,
            float(rec.daily_burn_rate),
            rec.recommended_quantity,
            rec.get_action_category_display(),
            rec.stockout_date.strftime('%d.%m.%Y') if rec.stockout_date else ''
        ])
    
    return response


@login_required
def purchase_orders(request):
    """Purchase orders list with filters"""
    company = request.user.company
    
    if not company:
        return render(request, 'procurement/no_company.html')
    
    # Get all purchase orders
    orders = PurchaseOrder.objects.filter(
        company=company
    ).prefetch_related('items')
    
    # Apply filters
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    period = request.GET.get('period')
    if period == 'today':
        orders = orders.filter(order_date=date.today())
    elif period == 'week':
        week_ago = date.today() - timedelta(days=7)
        orders = orders.filter(order_date__gte=week_ago)
    elif period == 'month':
        month_ago = date.today() - timedelta(days=30)
        orders = orders.filter(order_date__gte=month_ago)
    
    search = request.GET.get('search')
    if search:
        orders = orders.filter(
            Q(po_number__icontains=search) |
            Q(supplier_name__icontains=search)
        )
    
    # Calculate stats with single optimized query
    stats_result = PurchaseOrder.objects.filter(company=company).aggregate(
        draft_count=Count(Case(When(status='DRAFT', then=1), output_field=IntegerField())),
        submitted_count=Count(Case(When(status='SUBMITTED', then=1), output_field=IntegerField())),
        confirmed_count=Count(Case(When(status='CONFIRMED', then=1), output_field=IntegerField())),
        in_transit_count=Count(Case(When(status='IN_TRANSIT', then=1), output_field=IntegerField())),
        delivered_count=Count(Case(When(status='DELIVERED', then=1), output_field=IntegerField())),
    )
    stats = stats_result
    
    # Pagination
    paginator = Paginator(orders.order_by('-order_date'), 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'purchase_orders': page_obj,
        'stats': stats,
    }
    
    # If HTMX request, return only table rows
    if request.headers.get('HX-Request'):
        return render(request, 'procurement/partials/purchase_orders_rows.html', context)
    
    return render(request, 'procurement/purchase_orders.html', context)


@login_required
def purchase_order_detail(request, po_id):
    """Purchase order detail view"""
    company = request.user.company
    po = get_object_or_404(
        PurchaseOrder.objects.prefetch_related('items__product'),
        id=po_id,
        company=company
    )
    
    context = {
        'po': po,
    }
    
    return render(request, 'procurement/purchase_order_detail.html', context)


@login_required
def update_order_status(request, po_id):
    """Update purchase order status"""
    if request.method == 'POST':
        company = request.user.company
        po = get_object_or_404(PurchaseOrder, id=po_id, company=company)
        
        new_status = request.POST.get('status')
        if new_status in dict(PurchaseOrder.STATUS_CHOICES):
            po.status = new_status
            
            # If delivered, update actual delivery date
            if new_status == 'DELIVERED':
                po.actual_delivery = date.today()
            
            po.save()
            
            return JsonResponse({
                'success': True,
                'status': po.get_status_display()
            })
        
        return JsonResponse({'error': 'Invalid status'}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
