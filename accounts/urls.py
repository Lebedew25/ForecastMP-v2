from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    path('settings/', views.settings_view, name='settings'),
    path('subscription/', views.subscription_view, name='subscription'),
    path('subscription/invoice/<int:invoice_idx>/', views.download_invoice, name='download_invoice'),
    path('pricing/', views.pricing_view, name='pricing'),
]
