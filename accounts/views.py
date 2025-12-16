from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.conf import settings

def user_login(request):
    """Custom login view for regular users"""
    # If user is already authenticated, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('home')
    
    # Handle POST request (login form submission)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if user is staff/admin
            if user.is_staff:
                # Redirect admin users to Django admin
                login(request, user)
                return redirect('/admin/')
            else:
                # Login regular users and redirect to home/dashboard
                login(request, user)
                return redirect('home')
        else:
            # Invalid credentials
            messages.error(request, 'Invalid username or password.')
    
    # Render login page for GET requests
    return render(request, 'account/login.html')

@login_required
def user_logout(request):
    """Custom logout view"""
    from django.contrib.auth import logout
    logout(request)
    
    # Redirect to appropriate login page based on user type
    if hasattr(request, 'user') and request.user.is_staff:
        return redirect('/admin/login/')
    else:
        return redirect('accounts:login')