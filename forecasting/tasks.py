"""
Celery tasks for demand forecasting
"""
from celery import shared_task
from django.utils import timezone
from datetime import date, timedelta
import pandas as pd
import logging
from .models import Forecast, ForecastAccuracy
from .ml_engine import DemandForecaster
from .simple_forecast import generate_simple_forecasts_for_company, generate_simple_forecast_for_product
from products.models import Product
from sales.models import SalesHistory, DailySalesAggregate
from accounts.models import Company

logger = logging.getLogger(__name__)


@shared_task
def generate_all_forecasts():
    """Generate forecasts for all active companies and products"""
    companies = Company.objects.filter(is_active=True)
    
    results = []
    for company in companies:
        try:
            result = generate_company_forecasts.delay(company.id)
            results.append({
                'company_id': str(company.id),
                'company_name': company.name,
                'task_id': result.id
            })
        except Exception as e:
            logger.error(f"Failed to queue forecast for {company}: {str(e)}")
    
    return {
        'total_companies': len(results),
        'results': results
    }


@shared_task
def generate_company_forecasts(company_id):
    """Generate forecasts for all products in a company"""
    try:
        company = Company.objects.get(id=company_id)
    except Company.DoesNotExist:
        logger.error(f"Company {company_id} not found")
        return {'status': 'error', 'message': 'Company not found'}
    
    products = Product.objects.filter(company=company, is_active=True)
    
    success_count = 0
    failed_count = 0
    skipped_count = 0
    
    for product in products:
        try:
            result = generate_product_forecast(product.id)
            
            if result['status'] == 'success':
                success_count += 1
            elif result['status'] == 'skipped':
                skipped_count += 1
            else:
                failed_count += 1
                
        except Exception as e:
            logger.error(f"Failed to forecast {product}: {str(e)}")
            failed_count += 1
    
    return {
        'status': 'complete',
        'company': company.name,
        'total_products': products.count(),
        'success': success_count,
        'failed': failed_count,
        'skipped': skipped_count
    }


def generate_product_forecast(product_id):
    """Generate forecast for a single product"""
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return {'status': 'error', 'message': 'Product not found'}
    
    # Get historical sales data
    sales_history = prepare_sales_history(product)
    
    # Check if we have sufficient data
    if len(sales_history) < 30:
        logger.info(f"Insufficient data for {product.sku} ({len(sales_history)} days)")
        return {
            'status': 'skipped',
            'reason': 'insufficient_data',
            'days_available': len(sales_history)
        }
    
    try:
        # Initialize forecaster
        forecaster = DemandForecaster(horizon=30)
        
        # Train model
        training_metrics = forecaster.train(sales_history)
        
        # Generate forecasts
        forecasts_df = forecaster.predict(sales_history, forecast_days=30)
        
        # Save forecasts to database
        saved_count = 0
        for _, row in forecasts_df.iterrows():
            Forecast.objects.update_or_create(
                product=product,
                forecast_date=row['forecast_date'],
                defaults={
                    'predicted_quantity': row['predicted_quantity'],
                    'confidence_lower': row['confidence_lower'],
                    'confidence_upper': row['confidence_upper'],
                    'confidence_score': row['confidence_score'],
                    'model_version': forecaster.model_version
                }
            )
            saved_count += 1
        
        return {
            'status': 'success',
            'product_sku': product.sku,
            'forecasts_generated': saved_count,
            'model_metrics': training_metrics
        }
        
    except Exception as e:
        logger.error(f"Forecast generation failed for {product.sku}: {str(e)}")
        return {
            'status': 'error',
            'product_sku': product.sku,
            'error': str(e)
        }


def prepare_sales_history(product):
    """Prepare sales history DataFrame for forecasting"""
    # Get daily aggregates for last 180 days
    end_date = date.today()
    start_date = end_date - timedelta(days=180)
    
    aggregates = DailySalesAggregate.objects.filter(
        product=product,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')
    
    if not aggregates.exists():
        return pd.DataFrame()
    
    # Convert to DataFrame
    data = []
    for agg in aggregates:
        data.append({
            'date': agg.date,
            'quantity': agg.total_quantity,
            'product_id': str(product.id)
        })
    
    df = pd.DataFrame(data)
    
    # Fill missing dates with zero sales
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    df_full = pd.DataFrame({'date': date_range})
    df_full['date'] = pd.to_datetime(df_full['date']).dt.date
    df = df_full.merge(df, on='date', how='left')
    df['quantity'] = df['quantity'].fillna(0)
    df['product_id'] = str(product.id)
    
    return df


@shared_task
def evaluate_forecast_accuracy():
    """Evaluate forecast accuracy by comparing predictions with actual sales"""
    # Get forecasts from 7 days ago
    evaluation_date = date.today()
    forecast_date = evaluation_date - timedelta(days=7)
    
    forecasts = Forecast.objects.filter(forecast_date=forecast_date)
    
    evaluated_count = 0
    
    for forecast in forecasts:
        # Get actual sales for this date
        try:
            actual_sales = DailySalesAggregate.objects.get(
                product=forecast.product,
                date=forecast_date
            )
            
            actual_value = actual_sales.total_quantity
            predicted_value = forecast.predicted_quantity
            
            # Calculate errors
            absolute_error = abs(actual_value - predicted_value)
            percentage_error = (absolute_error / (actual_value + 1)) * 100
            
            # Save accuracy record
            ForecastAccuracy.objects.create(
                product=forecast.product,
                evaluation_date=evaluation_date,
                forecast_date=forecast_date,
                predicted_value=predicted_value,
                actual_value=actual_value,
                absolute_error=absolute_error,
                percentage_error=percentage_error,
                model_version=forecast.model_version
            )
            
            evaluated_count += 1
            
        except DailySalesAggregate.DoesNotExist:
            logger.warning(f"No actual sales data for {forecast.product.sku} on {forecast_date}")
            continue
    
    return {
        'status': 'success',
        'evaluation_date': evaluation_date.isoformat(),
        'forecasts_evaluated': evaluated_count
    }


@shared_task
def cleanup_old_forecasts(days_to_keep=90):
    """Delete old forecasts to save space"""
    cutoff_date = date.today() - timedelta(days=days_to_keep)
    
    deleted_count, _ = Forecast.objects.filter(
        forecast_date__lt=cutoff_date
    ).delete()
    
    return {
        'status': 'success',
        'deleted_count': deleted_count,
        'cutoff_date': cutoff_date.isoformat()
    }


@shared_task
def generate_all_simple_forecasts():
    """Generate simple forecasts for all active companies and products"""
    companies = Company.objects.filter(is_active=True)
    
    results = []
    for company in companies:
        try:
            result = generate_simple_company_forecasts.delay(company.id)
            results.append({
                'company_id': str(company.id),
                'company_name': company.name,
                'task_id': result.id
            })
        except Exception as e:
            logger.error(f"Failed to queue simple forecast for {company}: {str(e)}")
    
    return {
        'total_companies': len(results),
        'results': results
    }


@shared_task
def generate_simple_company_forecasts(company_id):
    """Generate simple forecasts for all products in a company"""
    try:
        result = generate_simple_forecasts_for_company(company_id)
        return {
            'status': 'success',
            'company_id': company_id,
            'success_count': result['success_count'],
            'failure_count': result['failure_count']
        }
    except Exception as e:
        logger.error(f"Failed to generate simple forecasts for company {company_id}: {str(e)}")
        return {
            'status': 'error',
            'company_id': company_id,
            'error': str(e)
        }


@shared_task
def generate_simple_product_forecast(product_id):
    """Generate simple forecast for a single product"""
    try:
        success = generate_simple_forecast_for_product(product_id)
        return {
            'status': 'success' if success else 'failed',
            'product_id': product_id
        }
    except Exception as e:
        logger.error(f"Failed to generate simple forecast for product {product_id}: {str(e)}")
        return {
            'status': 'error',
            'product_id': product_id,
            'error': str(e)
        }
