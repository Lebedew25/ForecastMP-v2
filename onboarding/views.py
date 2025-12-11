"""
Onboarding views
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging

logger = logging.getLogger(__name__)


@login_required
def onboarding_wizard(request):
    """Main onboarding wizard view"""
    # Check if user has already completed onboarding
    if request.user.company and request.user.company.settings.get('onboarding_completed'):
        return redirect('procurement:dashboard')
    
    # Calculate progress based on current step
    current_step = request.user.company.settings.get('onboarding_step', 1) if request.user.company else 1
    progress = (current_step / 5) * 100
    
    context = {
        'current_step': current_step,
        'progress': progress
    }
    
    return render(request, 'onboarding/wizard.html', context)


@login_required
@csrf_exempt
def submit_onboarding(request):
    """Handle onboarding form submission"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        # Get or create company
        from accounts.models import Company
        from sales.models import Warehouse
        from integrations.models import MarketplaceCredential
        
        company_name = request.POST.get('company_name')
        currency = request.POST.get('currency', 'USD')
        timezone = request.POST.get('timezone', 'UTC')
        low_stock_threshold = int(request.POST.get('low_stock_threshold', 7))
        
        # Create or update company
        if request.user.company:
            company = request.user.company
            company.name = company_name
        else:
            company = Company.objects.create(name=company_name)
            request.user.company = company
            request.user.save()
        
        # Update company settings
        company.settings.update({
            'currency': currency,
            'timezone': timezone,
            'low_stock_threshold_days': low_stock_threshold,
            'onboarding_completed': True,
            'onboarding_step': 5
        })
        company.save()
        
        # Create warehouses
        warehouse_name = request.POST.get('warehouse_name', 'Main Warehouse')
        Warehouse.objects.get_or_create(
            company=company,
            name=warehouse_name,
            defaults={
                'warehouse_type': 'OWN',
                'is_primary': True
            }
        )
        
        # Create Ozon warehouse if requested
        if request.POST.get('add_ozon_warehouse') == 'on':
            Warehouse.objects.get_or_create(
                company=company,
                name='Ozon Fulfillment',
                defaults={
                    'warehouse_type': 'MARKETPLACE_FF',
                    'marketplace': 'OZON'
                }
            )
        
        # Create Wildberries warehouse if requested
        if request.POST.get('add_wb_warehouse') == 'on':
            Warehouse.objects.get_or_create(
                company=company,
                name='Wildberries Fulfillment',
                defaults={
                    'warehouse_type': 'MARKETPLACE_FF',
                    'marketplace': 'WILDBERRIES'
                }
            )
        
        # Create marketplace credentials if provided
        ozon_client_id = request.POST.get('ozon_client_id')
        ozon_api_key = request.POST.get('ozon_api_key')
        
        if ozon_client_id and ozon_api_key:
            MarketplaceCredential.objects.update_or_create(
                company=company,
                marketplace='OZON',
                defaults={
                    'api_key': ozon_client_id,
                    'api_secret': ozon_api_key,
                    'is_active': True
                }
            )
        
        # Handle product file upload if provided
        if 'product_file' in request.FILES:
            product_file = request.FILES['product_file']
            # This would trigger the product import process
            # For now, we'll just acknowledge receipt
            logger.info(f"Product file uploaded: {product_file.name}")
        
        return JsonResponse({
            'success': True,
            'message': 'Onboarding completed successfully'
        })
        
    except Exception as e:
        logger.error(f"Onboarding submission error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)