"""
Debug middleware to log slow requests
"""
import time
import logging

logger = logging.getLogger(__name__)


class DebugSlowRequestMiddleware:
    """Log requests that take more than 1 second"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        
        response = self.get_response(request)
        
        duration = time.time() - start_time
        
        if duration > 1.0:
            logger.warning(
                f'Slow request: {request.method} {request.path} took {duration:.2f}s'
            )
        
        return response
