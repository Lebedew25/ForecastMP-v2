from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.conf import settings
from urllib.parse import urlparse
from accounts.models import Company

def user_login(request):
    """Custom login view for regular users"""
    # If user is already authenticated, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('home')
    
    # Handle POST request (login form submission)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next', '')
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Login user
            login(request, user)
            
            # Check if user is staff/admin
            if user.is_staff:
                # If coming from admin login or explicitly going to admin, redirect to admin
                if 'admin' in next_url or '/admin/' in next_url:
                    return redirect('/admin/')
                else:
                    # Staff users from regular login go to home
                    return redirect('home')
            else:
                # Regular users always go to home
                return redirect('home')
        else:
            # Invalid credentials
            messages.error(request, 'Invalid username or password.')
    
    # Render login page for GET requests
    next_url = request.GET.get('next', '')
    context = {'next': next_url}
    return render(request, 'account/login.html', context)

def user_logout(request):
    """Custom logout view"""
    # Store user type before logout
    is_staff = False
    if hasattr(request, 'user') and request.user.is_authenticated:
        is_staff = request.user.is_staff
    
    from django.contrib.auth import logout
    logout(request)
    
    # Redirect to appropriate login page based on user type
    if is_staff:
        return redirect('/admin/login/')
    else:
        return redirect('accounts:login')


@login_required
def settings_view(request):
    """Settings page view"""
    company = request.user.company
    
    context = {
        'company': company,
    }
    
    return render(request, 'accounts/settings.html', context)


@login_required
def subscription_view(request):
    """Subscription page view"""
    company = request.user.company
    
    # Mock data for subscription info
    subscription = {
        'plan': 'PRO',
        'get_plan_display': 'Pro',
        'status': 'ACTIVE',
        'current_period_end': '2024-12-31',
        'trial_end': None,
    }
    
    # Mock data for plan limits
    plan_limits = {
        'max_skus': 2000,
        'max_integrations': None,  # Unlimited
        'max_warehouses': None,   # Unlimited
        'ai_forecasting': True,
        'telegram_notifications': True,
        'api_access': True,
        'white_label': True,
    }
    
    # Mock data for usage
    usage = {
        'sku_count': 1250,
        'integration_count': 3,
        'warehouse_count': 5,
    }
    
    # Mock data for invoices
    invoices = [
        {
            'invoice_date': '2023-11-01',
            'description': 'Pro Plan (November 2023)',
            'amount': '14990',
            'status': 'PAID',
        },
        {
            'invoice_date': '2023-10-01',
            'description': 'Pro Plan (October 2023)',
            'amount': '14990',
            'status': 'PAID',
        }
    ]
    
    context = {
        'company': company,
        'subscription': subscription,
        'plan_limits': plan_limits,
        'usage': usage,
        'invoices': invoices,
    }
    
    return render(request, 'accounts/subscription.html', context)


def pricing_view(request):
    """Pricing page view for public access"""
    return render(request, 'pricing.html')
