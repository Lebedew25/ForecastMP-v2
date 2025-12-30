from django.db.models import Q, Count, Case, When, IntegerField, F, Value, CharField
from django.db.models.functions import Cast
from django.core.paginator import Paginator
from django.core.cache import cache
from .models import ProcurementRecommendation
from products.models import Product


def get_buying_table_data(company, filters=None, page=1, page_size=50):
    """
    Get optimized buying table data with proper select_related and annotations
    """
    from datetime import date
    today = date.today()
    
    # Create cache key based on company, filters and pagination
    cache_key = f"buying_table_data_{company.id}_{today}_{str(filters)}_{page}_{page_size}"
    cache_key = cache_key.replace(' ', '_').replace('/', '_').replace('\\', '_')
    
    # Try to get from cache first
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    # Base queryset with optimized joins
    queryset = ProcurementRecommendation.objects.filter(
        product__company=company,
        analysis_date=today
    ).select_related(
        'product'
    ).annotate(
        # Pre-calculate forecast for 30 days to avoid template calculations
        forecast_30days=F('daily_burn_rate') * 30,
        # Format daily burn rate to avoid template formatting
        daily_burn_rate_formatted=Cast(F('daily_burn_rate'), CharField()),
        # Pre-calculate if product has category for template
        has_category=Case(
            When(product__category__isnull=False, then=Value(True)),
            default=Value(False),
            output_field=IntegerField()
        )
    ).order_by('-priority_score')
    
    # Apply filters
    if filters:
        category = filters.get('category')
        if category:
            queryset = queryset.filter(product__category=category)
        
        supplier = filters.get('supplier')
        if supplier:
            queryset = queryset.filter(
                product__attributes__supplier=supplier
            )
        
        health_status = filters.get('health_status')
        if health_status:
            queryset = queryset.filter(action_category=health_status)
        
        search = filters.get('search')
        if search:
            queryset = queryset.filter(
                Q(product__sku__icontains=search) |
                Q(product__name__icontains=search)
            )
    
    # Pagination
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)
    
    # Cache the result for 5 minutes
    cache.set(cache_key, page_obj, 300)
    
    return page_obj


def get_buying_table_summary(company, filters=None):
    """
    Get optimized summary data with single query
    """
    from datetime import date
    today = date.today()
    
    # Create cache key based on company and filters
    cache_key = f"buying_table_summary_{company.id}_{today}_{str(filters)}"
    cache_key = cache_key.replace(' ', '_').replace('/', '_').replace('\\', '_')
    
    # Try to get from cache first
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    # Base queryset
    queryset = ProcurementRecommendation.objects.filter(
        product__company=company,
        analysis_date=today
    )
    
    # Apply filters
    if filters:
        category = filters.get('category')
        if category:
            queryset = queryset.filter(product__category=category)
        
        supplier = filters.get('supplier')
        if supplier:
            queryset = queryset.filter(
                product__attributes__supplier=supplier
            )
        
        health_status = filters.get('health_status')
        if health_status:
            queryset = queryset.filter(action_category=health_status)
        
        search = filters.get('search')
        if search:
            queryset = queryset.filter(
                Q(product__sku__icontains=search) |
                Q(product__name__icontains=search)
            )
    
    # Calculate summary with single optimized query
    summary_result = queryset.aggregate(
        normal_count=Count(Case(When(action_category='NORMAL', then=1), output_field=IntegerField())),
        attention_count=Count(Case(When(action_category='ATTENTION_REQUIRED', then=1), output_field=IntegerField())),
        order_today_count=Count(Case(When(action_category='ORDER_TODAY', then=1), output_field=IntegerField())),
        already_ordered_count=Count(Case(When(action_category='ALREADY_ORDERED', then=1), output_field=IntegerField())),
    )
    
    # Cache the result for 5 minutes
    cache.set(cache_key, summary_result, 300)
    
    return summary_result


def get_buying_table_filters(company):
    """
    Get filter options with optimized queries
    """
    # Create cache key based on company
    cache_key = f"buying_table_filters_{company.id}"
    
    # Try to get from cache first
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    categories = Product.objects.filter(
        company=company,
        category__isnull=False
    ).values_list('category', flat=True).distinct().order_by('category')
    
    # Get suppliers from product attributes - need to check actual field name
    suppliers = Product.objects.filter(
        company=company,
        attributes__supplier__isnull=False
    ).values_list('attributes__supplier', flat=True).distinct().order_by('attributes__supplier')
    
    result = {
        'categories': list(categories),  # Convert to list for caching
        'suppliers': list(suppliers),
    }
    
    # Cache the result for 15 minutes
    cache.set(cache_key, result, 900)
    
    return result


def invalidate_buying_table_cache(company):
    """
    Invalidate all cached buying table data for a company
    """
    from datetime import date
    today = date.today()
    
    # Invalidate all cache keys related to this company
    cache.delete(f"buying_table_filters_{company.id}")
    
    # We can't easily delete all keys with pattern, so we'll need to use a different approach
    # For now, just invalidate the filters cache
    # In a real implementation, we'd want to use cache versioning or tags


def invalidate_recommendation_cache(company):
    """
    Invalidate all cached data when recommendations are updated
    """
    from django.core.cache import cache
    from datetime import date
    today = date.today()
    
    # Invalidate all cache keys related to this company
    cache.delete_pattern(f"buying_table_*_{company.id}_{today}_*")
    cache.delete(f"buying_table_filters_{company.id}")
    cache.delete(f"buying_table_summary_{company.id}_{today}_None")
    
    # For now, just invalidate the filters cache
    cache.delete(f"buying_table_filters_{company.id}")