"""
Celery tasks for export functionality
"""
from celery import shared_task
import logging
import os
import tempfile
from typing import List, Dict, Any
from django.conf import settings
from .services import ExportService

logger = logging.getLogger(__name__)


@shared_task
def generate_procurement_export(export_id: str, company_name: str, products: List[Dict[str, Any]], 
                               export_format: str, notes: str = '') -> Dict[str, Any]:
    """Generate procurement export in specified format"""
    try:
        # Initialize export service
        service = ExportService(company_name)
        
        # Generate export based on format
        if export_format.upper() == 'EXCEL':
            file_content = service.generate_excel_export(products, notes)
            file_extension = '.xlsx'
        elif export_format.upper() == 'CSV':
            file_content = service.generate_csv_export(products, notes)
            file_extension = '.csv'
        elif export_format.upper() == 'PDF':
            file_content = service.generate_pdf_export(products, notes)
            file_extension = '.pdf'
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
        
        # Generate filename
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y-%m-%d')
        filename = f"procurement_order_{company_name}_{timestamp}{file_extension}"
        
        # For now, we'll return the file content directly
        # In a real implementation, you might save this to a file storage system
        # and return a URL or file path
        
        return {
            'success': True,
            'export_id': export_id,
            'filename': filename,
            'content': file_content,
            'format': export_format.lower(),
            'size': len(file_content)
        }
        
    except Exception as e:
        logger.error(f"Failed to generate procurement export: {str(e)}")
        return {
            'success': False,
            'export_id': export_id,
            'error': str(e)
        }