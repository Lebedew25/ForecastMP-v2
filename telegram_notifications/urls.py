"""
URL configuration for telegram_notifications app
"""
from django.urls import path
from . import views

app_name = 'telegram_notifications'

urlpatterns = [
    # Telegram bot webhook endpoint
    path('api/telegram/webhook/', views.telegram_webhook, name='telegram_webhook'),
    
    # User registration and preferences
    path('api/telegram/register/', views.register_telegram_chat, name='register_telegram'),
    path('api/telegram/preferences/', views.TelegramPreferencesView.as_view(), name='telegram_preferences'),
]