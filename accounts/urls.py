from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('settings/', views.settings_view, name='settings'),
    path('subscription/', views.subscription_view, name='subscription'),
    path('pricing/', views.pricing_view, name='pricing'),
]