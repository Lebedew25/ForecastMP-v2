from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from urllib.parse import urlparse
from accounts.models import Company, Subscription
from datetime import date, timedelta

User = get_user_model()


def register(request):
    """Public registration for a new company and user"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        company_name = (request.POST.get('company_name') or '').strip()
        email = (request.POST.get('email') or '').strip().lower()
        first_name = (request.POST.get('first_name') or '').strip()
        last_name = (request.POST.get('last_name') or '').strip()
        password1 = request.POST.get('password1') or ''
        password2 = request.POST.get('password2') or ''

        if not company_name or not email or not password1:
            messages.error(request, 'Company name, email, and password are required.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'User with this email already exists.')
        else:
            try:
                validate_password(password1)
            except ValidationError as exc:
                messages.error(request, ' '.join(exc.messages))
            else:
                with transaction.atomic():
                    company = Company.objects.create(name=company_name)
                    user = User.objects.create_user(
                        email=email,
                        password=password1,
                        first_name=first_name,
                        last_name=last_name,
                        company=company,
                        role='ADMIN'
                    )
                    today = date.today()
                    Subscription.objects.create(
                        company=company,
                        status='TRIAL',
                        trial_start_date=today,
                        trial_end_date=today + timedelta(days=14)
                    )
                login(request, user)
                return redirect('onboarding:wizard')

    return render(request, 'account/register.html')

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
