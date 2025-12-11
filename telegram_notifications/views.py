"""
Telegram notifications views
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging
from .services import TelegramNotificationService
from accounts.models import TelegramSubscription

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def telegram_webhook(request):
    """Handle incoming Telegram bot messages"""
    try:
        # Parse JSON data
        data = json.loads(request.body.decode('utf-8'))
        
        # Check if this is a message
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            
            # Handle /start command
            if text == '/start':
                # Extract user ID from the message if possible
                # For now, we'll just acknowledge the subscription
                logger.info(f"Telegram bot started by chat {chat_id}")
                
                # Send welcome message
                service = TelegramNotificationService()
                # Note: We don't have the bot token here, so we can't send a message back
                # This would typically be handled by storing the chat_id for later use
                
                return JsonResponse({'status': 'ok'})
        
        return JsonResponse({'status': 'ok'})
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Telegram webhook error: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@login_required
@require_http_methods(["POST"])
def register_telegram_chat(request):
    """Register a Telegram chat ID for the current user"""
    try:
        # Parse JSON data
        data = json.loads(request.body.decode('utf-8'))
        chat_id = data.get('chat_id')
        
        if not chat_id:
            return JsonResponse({'error': 'Missing chat_id'}, status=400)
        
        # Register the chat ID for the current user
        service = TelegramNotificationService()
        success = service.register_chat(request.user, chat_id)
        
        if success:
            return JsonResponse({'status': 'registered'})
        else:
            return JsonResponse({'error': 'Failed to register chat'}, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"Telegram registration error: {str(e)}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


class TelegramPreferencesView(View):
    """API endpoint for managing Telegram notification preferences"""
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request):
        """Get current Telegram notification preferences"""
        try:
            subscription = TelegramSubscription.objects.get(user=request.user)
            
            return JsonResponse({
                'success': True,
                'preferences': {
                    'critical_alerts_enabled': subscription.critical_alerts_enabled,
                    'daily_digest_enabled': subscription.daily_digest_enabled,
                    'weekly_report_enabled': subscription.weekly_report_enabled,
                    'digest_time': subscription.digest_time.strftime('%H:%M') if subscription.digest_time else '08:00',
                }
            })
        except TelegramSubscription.DoesNotExist:
            return JsonResponse({
                'success': True,
                'preferences': {
                    'critical_alerts_enabled': True,
                    'daily_digest_enabled': True,
                    'weekly_report_enabled': True,
                    'digest_time': '08:00',
                }
            })
        except Exception as e:
            logger.error(f"Telegram preferences error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)
    
    def post(self, request):
        """Update Telegram notification preferences"""
        try:
            # Parse JSON data
            data = json.loads(request.body.decode('utf-8'))
            
            # Get or create subscription
            subscription, created = TelegramSubscription.objects.get_or_create(
                user=request.user,
                defaults={
                    'chat_id': '',  # Will be set when user registers
                    'is_active': True
                }
            )
            
            # Update preferences
            if 'critical_alerts_enabled' in data:
                subscription.critical_alerts_enabled = data['critical_alerts_enabled']
            
            if 'daily_digest_enabled' in data:
                subscription.daily_digest_enabled = data['daily_digest_enabled']
            
            if 'weekly_report_enabled' in data:
                subscription.weekly_report_enabled = data['weekly_report_enabled']
            
            if 'digest_time' in data:
                # Parse time string (HH:MM format)
                from datetime import datetime
                try:
                    time_obj = datetime.strptime(data['digest_time'], '%H:%M').time()
                    subscription.digest_time = time_obj
                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid digest_time format. Use HH:MM'
                    }, status=400)
            
            subscription.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Preferences updated successfully'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Telegram preferences update error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)