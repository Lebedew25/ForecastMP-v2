"""
Celery tasks for Telegram notifications
"""
from celery import shared_task
import logging
from typing import Dict
from django.db import models
from accounts.models import User, TelegramSubscription
from .services import TelegramNotificationService

logger = logging.getLogger(__name__)


@shared_task
def send_telegram_notification(user_id: str, message_type: str, data: Dict) -> bool:
    """Send individual Telegram notification"""
    try:
        user = User.objects.get(id=user_id)
        subscription = TelegramSubscription.objects.get(user=user, is_active=True)
        
        # Get company bot token from company settings
        company = user.company
        bot_token = company.settings.get('telegram_bot_token')
        if not bot_token:
            logger.error(f"No Telegram bot token configured for company {company.name}")
            return False
        
        # Initialize notification service
        service = TelegramNotificationService()
        service.configure_bot(bot_token)
        
        # Send appropriate notification based on type
        if message_type == 'critical_alert':
            return service.send_critical_stock_alert(user, data)
        elif message_type == 'daily_digest':
            return service.send_daily_digest(user, data)
        elif message_type == 'weekly_report':
            return service.send_weekly_report(user, data)
        else:
            logger.warning(f"Unknown message type: {message_type}")
            return False
            
    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} not found")
        return False
    except TelegramSubscription.DoesNotExist:
        logger.warning(f"No active Telegram subscription for user ID {user_id}")
        return False
    except Exception as e:
        logger.error(f"Failed to send Telegram notification: {str(e)}")
        return False


@shared_task
def generate_daily_digest(company_id: str) -> bool:
    """Generate and send daily digest to all subscribed users in a company"""
    try:
        from accounts.models import Company
        from procurement.models import ProcurementRecommendation
        from products.models import Product
        
        company = Company.objects.get(id=company_id)
        
        # Get company bot token
        bot_token = company.settings.get('telegram_bot_token')
        if not bot_token:
            logger.error(f"No Telegram bot token configured for company {company.name}")
            return False
        
        # Initialize notification service
        service = TelegramNotificationService()
        service.configure_bot(bot_token)
        
        # Prepare digest data
        total_products = Product.objects.filter(company=company, is_active=True).count()
        
        # Get status counts
        recommendations = ProcurementRecommendation.objects.filter(
            product__company=company,
            product__is_active=True
        ).select_related('product')
        
        healthy_count = recommendations.filter(action_category='NORMAL').count()
        warning_count = recommendations.filter(action_category='ATTENTION_REQUIRED').count()
        critical_count = recommendations.filter(action_category='ORDER_TODAY').count()
        
        # Get top urgent products
        urgent_recommendations = recommendations.filter(
            action_category='ORDER_TODAY'
        ).order_by('-priority_score')[:5]
        
        urgent_products = []
        for rec in urgent_recommendations:
            urgent_products.append({
                'name': rec.product.name,
                'sku': rec.product.sku,
                'days_to_stockout': getattr(rec, 'runway_days', 0)
            })
        
        digest_data = {
            'total_products': total_products,
            'healthy_count': healthy_count,
            'warning_count': warning_count,
            'critical_count': critical_count,
            'urgent_products': urgent_products
        }
        
        # Send to all subscribed users
        subscriptions = TelegramSubscription.objects.filter(
            user__company=company,
            is_active=True,
            daily_digest_enabled=True
        ).select_related('user')
        
        success_count = 0
        for subscription in subscriptions:
            if service.send_daily_digest(subscription.user, digest_data):
                success_count += 1
        
        logger.info(f"Daily digest sent to {success_count}/{subscriptions.count()} users in company {company.name}")
        return True
        
    except Company.DoesNotExist:
        logger.error(f"Company with ID {company_id} not found")
        return False
    except Exception as e:
        logger.error(f"Failed to generate daily digest: {str(e)}")
        return False


@shared_task
def generate_weekly_report(company_id: str) -> bool:
    """Generate and send weekly report to all subscribed users in a company"""
    try:
        from accounts.models import Company
        from procurement.models import ProcurementRecommendation
        from products.models import Product
        from sales.models import SalesTransaction
        
        company = Company.objects.get(id=company_id)
        
        # Get company bot token
        bot_token = company.settings.get('telegram_bot_token')
        if not bot_token:
            logger.error(f"No Telegram bot token configured for company {company.name}")
            return False
        
        # Initialize notification service
        service = TelegramNotificationService()
        service.configure_bot(bot_token)
        
        # Prepare report data
        total_products = Product.objects.filter(company=company, is_active=True).count()
        
        # Get top selling products (last 7 days)
        from datetime import datetime, timedelta
        week_ago = datetime.now() - timedelta(days=7)
        
        top_selling = SalesTransaction.objects.filter(
            product__company=company,
            transaction_date__gte=week_ago
        ).values('product__name', 'product__sku').annotate(
            total_sold=models.Sum('quantity')
        ).order_by('-total_sold')[:5]
        
        top_selling_products = []
        for item in top_selling:
            top_selling_products.append({
                'name': item['product__name'],
                'sku': item['product__sku'],
                'sold': item['total_sold']
            })
        
        # Get slow moving products (high stock, low sales)
        slow_moving_products = []
        recommendations = ProcurementRecommendation.objects.filter(
            product__company=company,
            product__is_active=True
        ).select_related('product')
        
        # Find products with high stock but low movement
        for rec in recommendations:
            if hasattr(rec, 'current_stock') and rec.current_stock > 100:  # Arbitrary threshold
                # Check if there were few sales in the last week
                recent_sales = SalesTransaction.objects.filter(
                    product=rec.product,
                    transaction_date__gte=week_ago
                ).aggregate(total_sold=models.Sum('quantity'))['total_sold'] or 0
                
                if recent_sales < 10:  # Arbitrary threshold
                    slow_moving_products.append({
                        'name': rec.product.name,
                        'sku': rec.product.sku,
                        'stock': rec.current_stock
                    })
        
        # Limit to top 5 slow moving products
        slow_moving_products = sorted(slow_moving_products, key=lambda x: x['stock'], reverse=True)[:5]
        
        report_data = {
            'total_products': total_products,
            'top_selling_products': top_selling_products,
            'slow_moving_products': slow_moving_products
        }
        
        # Send to all subscribed users
        subscriptions = TelegramSubscription.objects.filter(
            user__company=company,
            is_active=True,
            weekly_report_enabled=True
        ).select_related('user')
        
        success_count = 0
        for subscription in subscriptions:
            if service.send_weekly_report(subscription.user, report_data):
                success_count += 1
        
        logger.info(f"Weekly report sent to {success_count}/{subscriptions.count()} users in company {company.name}")
        return True
        
    except Company.DoesNotExist:
        logger.error(f"Company with ID {company_id} not found")
        return False
    except Exception as e:
        logger.error(f"Failed to generate weekly report: {str(e)}")
        return False