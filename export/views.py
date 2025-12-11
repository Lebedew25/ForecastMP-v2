"""
Export views for procurement order exports
"""
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging
from .services import ExportService
from .tasks import generate_procurement_export
from procurement.models import ProcurementRecommendation
from products.models import Product

logger = logging.getLogger(__name__)


class ExportOrderView(View):
    """API endpoint for generating procurement order exports"""
    
    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        """Generate procurement order export"""
        try:
            # Parse JSON data
            data = json.loads(request.body.decode('utf-8'))
            
            # Extract parameters
            export_format = data.get('format', 'excel').upper()
            notes = data.get('notes', '')
            filters = data.get('filters', {})
            
            # Validate format
            if export_format not in ['EXCEL', 'CSV', 'PDF']:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid format. Supported formats: excel, csv, pdf'
                }, status=400)
            
            # Get products with recommended quantities
            products = self._get_recommended_products(request.user.company, filters)
            
            if not products:
                return JsonResponse({
                    'success': False,
                    'error': 'No products found for export'
                }, status=404)
            
            # Generate export using the service
            service = ExportService(request.user.company.name)
            
            if export_format == 'EXCEL':
                file_content = service.generate_excel_export(products, notes)
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                file_extension = 'xlsx'
            elif export_format == 'CSV':
                file_content = service.generate_csv_export(products, notes)
                content_type = 'text/csv'
                file_extension = 'csv'
            elif export_format == 'PDF':
                file_content = service.generate_pdf_export(products, notes)
                content_type = 'application/pdf'
                file_extension = 'pdf'
            
            # Generate filename
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y-%m-%d')
            filename = f"procurement_order_{request.user.company.name}_{timestamp}.{file_extension}"
            
            # Return file as download
            response = HttpResponse(file_content, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f"Export generation error: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)
    
    def _get_recommended_products(self, company, filters):
        """Get products with procurement recommendations"""
        try:
            # Build query for recommendations
            recommendations = ProcurementRecommendation.objects.filter(
                product__company=company,
                product__is_active=True,
                recommended_quantity__gt=0
            ).select_related('product')
            
            # Apply filters if provided
            if filters.get('product_ids'):
                recommendations = recommendations.filter(product_id__in=filters['product_ids'])
            
            if filters.get('categories'):
                recommendations = recommendations.filter(product__category__in=filters['categories'])
            
            if filters.get('min_priority'):
                recommendations = recommendations.filter(priority_score__gte=filters['min_priority'])
            
            # Convert to export format
            products = []
            for rec in recommendations:
                products.append({
                    'sku': rec.product.sku,
                    'name': rec.product.name,
                    'current_stock': getattr(rec, 'current_stock', 0),
                    'recommended_quantity': rec.recommended_quantity,
                    'notes': f"Priority: {rec.priority_score}"
                })
            
            return products
            
        except Exception as e:
            logger.error(f"Error getting recommended products: {str(e)}")
            return []


class ExportStatusView(View):
    """API endpoint for checking export status"""
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, export_id):
        """Get export status - placeholder for async exports"""
        # In a real implementation with async processing, this would check the status
        # For now, we're generating exports synchronously
        return JsonResponse({
            'success': True,
            'export_id': export_id,
            'status': 'completed',
            'message': 'Exports are generated synchronously in this implementation'
        })