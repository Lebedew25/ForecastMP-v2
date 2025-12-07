"""
Celery tasks for procurement analysis
"""
from celery import shared_task
from django.utils import timezone
from datetime import date
import logging
from decimal import Decimal
from .models import ProcurementRecommendation
from .analyzer import ProcurementAnalyzer
from products.models import Product
from accounts.models import Company
from forecasting.models import Forecast

logger = logging.getLogger(__name__)


@shared_task
def analyze_all_procurement():
    """Analyze procurement needs for all active companies"""
    companies = Company.objects.filter(is_active=True)
    
    results = []
    for company in companies:
        try:
            result = analyze_company_procurement.delay(company.id)
            results.append({
                'company_id': str(company.id),
                'company_name': company.name,
                'task_id': result.id
            })
        except Exception as e:
            logger.error(f"Failed to queue procurement analysis for {company}: {str(e)}")
    
    return {
        'total_companies': len(results),
        'results': results
    }


@shared_task
def analyze_company_procurement(company_id):
    """Analyze procurement for all products in a company"""
    try:
        company = Company.objects.get(id=company_id)
    except Company.DoesNotExist:
        logger.error(f"Company {company_id} not found")
        return {'status': 'error', 'message': 'Company not found'}
    
    products = Product.objects.filter(company=company, is_active=True)
    today = date.today()
    
    success_count = 0
    failed_count = 0
    
    # Category counters
    order_today = 0
    already_ordered = 0
    attention_required = 0
    normal = 0
    
    for product in products:
        try:
            result = analyze_product_procurement(product.id, today)
            
            if result['status'] == 'success':
                success_count += 1
                
                # Count by category
                category = result['recommendation']['action_category']
                if category == 'ORDER_TODAY':
                    order_today += 1
                elif category == 'ALREADY_ORDERED':
                    already_ordered += 1
                elif category == 'ATTENTION_REQUIRED':
                    attention_required += 1
                else:
                    normal += 1
            else:
                failed_count += 1
                
        except Exception as e:
            logger.error(f"Failed to analyze {product}: {str(e)}")
            failed_count += 1
    
    return {
        'status': 'complete',
        'company': company.name,
        'analysis_date': today.isoformat(),
        'total_products': products.count(),
        'success': success_count,
        'failed': failed_count,
        'categories': {
            'order_today': order_today,
            'already_ordered': already_ordered,
            'attention_required': attention_required,
            'normal': normal
        }
    }


def analyze_product_procurement(product_id, analysis_date=None):
    """Analyze procurement needs for a single product"""
    if analysis_date is None:
        analysis_date = date.today()
    
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return {'status': 'error', 'message': 'Product not found'}
    
    try:
        # Initialize analyzer
        analyzer = ProcurementAnalyzer(product, analysis_date)
        
        # Get forecast confidence if available
        forecast_confidence = get_latest_forecast_confidence(product, analysis_date)
        
        # Perform analysis
        analysis_result = analyzer.analyze(forecast_confidence)
        
        # Save recommendation to database
        recommendation = ProcurementRecommendation.objects.update_or_create(
            product=product,
            analysis_date=analysis_date,
            defaults={
                'current_stock': analysis_result['current_stock'],
                'daily_burn_rate': analysis_result['daily_burn_rate'],
                'runway_days': analysis_result['runway_days'],
                'stockout_date': analysis_result['stockout_date'],
                'recommended_quantity': analysis_result['recommended_quantity'],
                'action_category': analysis_result['action_category'],
                'priority_score': analysis_result['priority_score'],
                'notes': analysis_result['notes'],
                'metadata': analysis_result['metadata']
            }
        )
        
        return {
            'status': 'success',
            'product_sku': product.sku,
            'recommendation': {
                'action_category': analysis_result['action_category'],
                'runway_days': analysis_result['runway_days'],
                'recommended_quantity': analysis_result['recommended_quantity'],
                'priority_score': float(analysis_result['priority_score'])
            }
        }
        
    except Exception as e:
        logger.error(f"Procurement analysis failed for {product.sku}: {str(e)}")
        return {
            'status': 'error',
            'product_sku': product.sku,
            'error': str(e)
        }


def get_latest_forecast_confidence(product, target_date):
    """Get forecast confidence for the target date"""
    try:
        forecast = Forecast.objects.filter(
            product=product,
            forecast_date=target_date
        ).order_by('-generated_at').first()
        
        if forecast:
            return forecast.confidence_score
        
        return None
        
    except Exception:
        return None


@shared_task
def generate_procurement_report(company_id):
    """Generate detailed procurement report for a company"""
    try:
        company = Company.objects.get(id=company_id)
    except Company.DoesNotExist:
        return {'status': 'error', 'message': 'Company not found'}
    
    today = date.today()
    
    # Get all recommendations for today
    recommendations = ProcurementRecommendation.objects.filter(
        product__company=company,
        analysis_date=today
    ).select_related('product')
    
    # Group by category
    order_today = recommendations.filter(action_category='ORDER_TODAY').order_by('-priority_score')
    already_ordered = recommendations.filter(action_category='ALREADY_ORDERED').order_by('runway_days')
    attention_required = recommendations.filter(action_category='ATTENTION_REQUIRED').order_by('-priority_score')
    
    report = {
        'company': company.name,
        'report_date': today.isoformat(),
        'summary': {
            'total_products': recommendations.count(),
            'order_today_count': order_today.count(),
            'already_ordered_count': already_ordered.count(),
            'attention_required_count': attention_required.count(),
            'total_recommended_value': 0
        },
        'order_today': [],
        'already_ordered': [],
        'attention_required': []
    }
    
    # Build order today list
    for rec in order_today[:20]:  # Top 20
        report['order_today'].append({
            'sku': rec.product.sku,
            'name': rec.product.name,
            'current_stock': rec.current_stock,
            'runway_days': rec.runway_days,
            'stockout_date': rec.stockout_date.isoformat() if rec.stockout_date else None,
            'recommended_quantity': rec.recommended_quantity,
            'priority_score': float(rec.priority_score),
            'notes': rec.notes
        })
    
    # Build already ordered list
    for rec in already_ordered[:10]:  # Top 10
        report['already_ordered'].append({
            'sku': rec.product.sku,
            'name': rec.product.name,
            'runway_days': rec.runway_days,
            'notes': rec.notes
        })
    
    # Build attention required list
    for rec in attention_required[:15]:  # Top 15
        report['attention_required'].append({
            'sku': rec.product.sku,
            'name': rec.product.name,
            'current_stock': rec.current_stock,
            'runway_days': rec.runway_days,
            'recommended_quantity': rec.recommended_quantity,
            'priority_score': float(rec.priority_score),
            'notes': rec.notes
        })
    
    return report


@shared_task
def cleanup_old_recommendations(days_to_keep=30):
    """Delete old procurement recommendations"""
    from datetime import timedelta
    
    cutoff_date = date.today() - timedelta(days=days_to_keep)
    
    deleted_count, _ = ProcurementRecommendation.objects.filter(
        analysis_date__lt=cutoff_date
    ).delete()
    
    return {
        'status': 'success',
        'deleted_count': deleted_count,
        'cutoff_date': cutoff_date.isoformat()
    }


@shared_task
def send_daily_alerts(company_id):
    """Send daily alerts for critical items (placeholder for email/notification)"""
    try:
        company = Company.objects.get(id=company_id)
    except Company.DoesNotExist:
        return {'status': 'error', 'message': 'Company not found'}
    
    today = date.today()
    
    # Get critical items
    critical_items = ProcurementRecommendation.objects.filter(
        product__company=company,
        analysis_date=today,
        action_category='ORDER_TODAY',
        priority_score__gte=80
    ).select_related('product').order_by('-priority_score')[:10]
    
    if not critical_items.exists():
        return {
            'status': 'success',
            'message': 'No critical items',
            'count': 0
        }
    
    # TODO: Implement email/notification sending
    # For now, just log the critical items
    alert_data = {
        'company': company.name,
        'date': today.isoformat(),
        'critical_count': critical_items.count(),
        'items': []
    }
    
    for item in critical_items:
        alert_data['items'].append({
            'sku': item.product.sku,
            'name': item.product.name,
            'runway_days': item.runway_days,
            'priority_score': float(item.priority_score)
        })
    
    logger.info(f"Daily alert for {company.name}: {critical_items.count()} critical items")
    
    return alert_data
