"""
Telegram notification service
"""
import requests
import logging
from typing import Dict, List, Optional
from django.conf import settings
from accounts.models import User, TelegramSubscription
from procurement.models import ProcurementRecommendation

logger = logging.getLogger(__name__)


class TelegramNotificationService:
    """Service for sending Telegram notifications"""
    
    def __init__(self):
        self.bot_token = None
        self.base_url = None
    
    def configure_bot(self, bot_token: str):
        """Configure the Telegram bot"""
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, chat_id: str, text: str, parse_mode: str = 'Markdown') -> bool:
        """Send a message to a Telegram chat"""
        if not self.bot_token:
            logger.error("Telegram bot not configured")
            return False
        
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                logger.info(f"Message sent successfully to chat {chat_id}")
                return True
            else:
                logger.error(f"Failed to send message: {result.get('description')}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"Failed to send Telegram message: {str(e)}")
            return False
    
    def send_critical_stock_alert(self, user: User, product_info: Dict) -> bool:
        """Send critical stock alert notification"""
        try:
            subscription = TelegramSubscription.objects.get(user=user, is_active=True)
        except TelegramSubscription.DoesNotExist:
            logger.warning(f"No active Telegram subscription for user {user.email}")
            return False
        
        # Format the alert message
        message = self._format_critical_stock_alert(product_info)
        return self.send_message(subscription.chat_id, message)
    
    def send_daily_digest(self, user: User, digest_data: Dict) -> bool:
        """Send daily digest notification"""
        try:
            subscription = TelegramSubscription.objects.get(user=user, is_active=True)
        except TelegramSubscription.DoesNotExist:
            logger.warning(f"No active Telegram subscription for user {user.email}")
            return False
        
        # Check if daily digest is enabled
        if not subscription.daily_digest_enabled:
            return False
        
        # Format the digest message
        message = self._format_daily_digest(digest_data)
        return self.send_message(subscription.chat_id, message)
    
    def send_weekly_report(self, user: User, report_data: Dict) -> bool:
        """Send weekly report notification"""
        try:
            subscription = TelegramSubscription.objects.get(user=user, is_active=True)
        except TelegramSubscription.DoesNotExist:
            logger.warning(f"No active Telegram subscription for user {user.email}")
            return False
        
        # Check if weekly report is enabled
        if not subscription.weekly_report_enabled:
            return False
        
        # Format the report message
        message = self._format_weekly_report(report_data)
        return self.send_message(subscription.chat_id, message)
    
    def _format_critical_stock_alert(self, product_info: Dict) -> str:
        """Format critical stock alert message"""
        product_name = product_info.get('name', 'Unknown Product')
        sku = product_info.get('sku', 'N/A')
        current_stock = product_info.get('current_stock', 0)
        days_to_stockout = product_info.get('days_to_stockout', 0)
        recommended_order = product_info.get('recommended_order', 0)
        
        message = (
            f"🔴 *CRITICAL STOCK ALERT*\n\n"
            f"Product: {product_name}\n"
            f"SKU: {sku}\n\n"
            f"Current Stock: {current_stock} units\n"
            f"Days to Stockout: {days_to_stockout} days\n"
            f"Recommended Order: {recommended_order} units\n\n"
            f"Action: Order immediately to avoid stockout"
        )
        return message
    
    def _format_daily_digest(self, digest_data: Dict) -> str:
        """Format daily digest message"""
        total_products = digest_data.get('total_products', 0)
        healthy_count = digest_data.get('healthy_count', 0)
        warning_count = digest_data.get('warning_count', 0)
        critical_count = digest_data.get('critical_count', 0)
        urgent_products = digest_data.get('urgent_products', [])
        
        message = (
            f"📊 *DAILY INVENTORY DIGEST*\n\n"
            f"Total Products: {total_products}\n"
            f"🟢 Healthy: {healthy_count}\n"
            f"🟡 Warning: {warning_count}\n"
            f"🔴 Critical: {critical_count}\n\n"
        )
        
        if urgent_products:
            message += "*Most Urgent Products:*\n"
            for i, product in enumerate(urgent_products[:5], 1):
                message += f"{i}. {product['name']} ({product['sku']}) - {product['days_to_stockout']} days left\n"
        
        message += "\n[Go to Dashboard](https://your-app-url.com/dashboard/)"
        return message
    
    def _format_weekly_report(self, report_data: Dict) -> str:
        """Format weekly report message"""
        total_products = report_data.get('total_products', 0)
        top_selling = report_data.get('top_selling_products', [])
        slow_moving = report_data.get('slow_moving_products', [])
        
        message = (
            f"📈 *WEEKLY INVENTORY REPORT*\n\n"
            f"Total Products Managed: {total_products}\n\n"
        )
        
        if top_selling:
            message += "*Top Selling Products:*\n"
            for i, product in enumerate(top_selling[:5], 1):
                message += f"{i}. {product['name']} ({product['sku']}) - {product['sold']} units sold\n"
        
        if slow_moving:
            message += "\n*Crawling Products:*\n"
            for i, product in enumerate(slow_moving[:5], 1):
                message += f"{i}. {product['name']} ({product['sku']}) - {product['stock']} units in stock\n"
        
        message += "\n[View Full Report](https://your-app-url.com/reports/weekly/)"
        return message
    
    def register_chat(self, user: User, chat_id: str) -> bool:
        """Register a Telegram chat ID for a user"""
        try:
            subscription, created = TelegramSubscription.objects.update_or_create(
                user=user,
                defaults={
                    'chat_id': chat_id,
                    'is_active': True
                }
            )
            logger.info(f"Telegram chat registered for user {user.email}: {chat_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to register Telegram chat for user {user.email}: {str(e)}")
            return False