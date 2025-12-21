from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# Create a custom view that checks authentication
@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'dashboard/dashboard.html'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', DashboardView.as_view(), name='home'),
    path('accounts/', include('accounts.urls')),
    path('onboarding/', include('onboarding.urls')),
    path('dashboard/', include('procurement.urls')),
    path('sales/', include('sales.urls')),
    path('telegram/', include('telegram_notifications.urls')),
    path('export/', include('export.urls')),
    path('api/', include('dashboard.urls')),
    path('forecasting/', include('forecasting.urls')),
]