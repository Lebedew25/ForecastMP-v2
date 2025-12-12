from django.http import JsonResponse
from django.contrib.auth import logout as django_logout, authenticate, login as django_login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
import json
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    """
    Login a user with username and password.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({
                'success': False,
                'error': 'Username and password are required'
            }, status=400)
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Login the user
            django_login(request, user)
            logger.info(f"User {username} logged in successfully. Session key: {request.session.session_key}")
            logger.info(f"Session data: {dict(request.session.items())}")
            
            response = JsonResponse({
                'success': True,
                'message': 'Logged in successfully'
            })
            # Ensure session cookie is set
            request.session.save()
            logger.info(f"Session saved. Cookie domain: {request.session.get_session_cookie_age()}")
            return response
        else:
            return JsonResponse({
                'success': False,
                'error': 'Invalid credentials'
            }, status=401)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)


@ensure_csrf_cookie
@require_http_methods(["GET"])
def current_user(request):
    """
    Get current authenticated user information.
    Returns user data if authenticated, 401 if not.
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': 'Not authenticated'
        }, status=401)
    
    user = request.user
    
    # Prepare company data
    company_data = None
    if user.company:
        company_data = {
            'id': str(user.company.id),
            'name': user.company.name,
            'tax_id': getattr(user.company, 'tax_id', ''),
            'currency': getattr(user.company, 'currency', 'USD'),
            'timezone': getattr(user.company, 'timezone', 'UTC'),
            'created_at': user.company.created_at.isoformat() if hasattr(user.company, 'created_at') else None,
        }
    
    # Return user data
    return JsonResponse({
        'id': str(user.id),
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'company': company_data,
        'is_superuser': user.is_superuser,
    })


@login_required
@require_http_methods(["POST"])
def logout_view(request):
    """
    Logout the current user.
    """
    django_logout(request)
    return JsonResponse({
        'success': True,
        'message': 'Logged out successfully'
    })
