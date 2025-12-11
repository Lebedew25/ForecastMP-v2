"""
Celery tasks for product import processing
"""
from celery import shared_task
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import logging
import uuid
import os
from .importer import import_products_from_file

logger = logging.getLogger(__name__)


@shared_task
def process_product_import(file_path: str, company_id: str, filename: str) -> dict:
    """
    Process uploaded product file asynchronously
    
    Args:
        file_path: Path to uploaded file in storage
        company_id: Company UUID string
        filename: Original filename
        
    Returns:
        Dictionary with import results
    """
    try:
        # Open file from storage
        with default_storage.open(file_path, 'rb') as f:
            # Create a temporary file-like object
            from django.core.files.uploadedfile import SimpleUploadedFile
            
            # Read file content
            file_content = f.read()
            
            # Create SimpleUploadedFile to mimic uploaded file
            uploaded_file = SimpleUploadedFile(
                name=filename,
                content=file_content,
                content_type='text/csv' if filename.endswith('.csv') else 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
            # Process import
            result = import_products_from_file(company_id, uploaded_file)
            
            # Clean up temporary file
            if default_storage.exists(file_path):
                default_storage.delete(file_path)
            
            return {
                'status': 'success',
                'result': result
            }
            
    except Exception as e:
        logger.error(f"Product import failed: {str(e)}")
        
        # Clean up temporary file even on error
        if default_storage.exists(file_path):
            default_storage.delete(file_path)
        
        return {
            'status': 'error',
            'error': str(e)
        }


@shared_task
def process_large_product_import(file_paths: list, company_id: str) -> dict:
    """
    Process multiple uploaded files (for large imports split into chunks)
    
    Args:
        file_paths: List of paths to uploaded files
        company_id: Company UUID string
        
    Returns:
        Dictionary with combined import results
    """
    total_imported = 0
    total_errors = 0
    all_errors = []
    all_warnings = []
    
    try:
        for file_path, filename in file_paths:
            try:
                # Process each file
                result = process_product_import(file_path, company_id, filename)
                
                if result['status'] == 'success':
                    total_imported += result['result']['imported_count']
                    all_errors.extend(result['result'].get('errors', []))
                    all_warnings.extend(result['result'].get('warnings', []))
                else:
                    total_errors += 1
                    all_errors.append(f"File {filename}: {result['error']}")
                    
            except Exception as e:
                total_errors += 1
                all_errors.append(f"File {filename}: {str(e)}")
        
        return {
            'status': 'completed',
            'total_imported': total_imported,
            'total_errors': total_errors,
            'errors': all_errors,
            'warnings': all_warnings
        }
        
    except Exception as e:
        logger.error(f"Large product import failed: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }


def save_uploaded_file_temporarily(uploaded_file) -> str:
    """
    Save uploaded file to temporary storage for async processing
    
    Args:
        uploaded_file: Django UploadedFile object
        
    Returns:
        Path to saved file
    """
    # Generate unique filename
    ext = os.path.splitext(uploaded_file.name)[1]
    unique_filename = f"temp_import_{uuid.uuid4().hex}{ext}"
    
    # Save to temporary location
    path = default_storage.save(
        f"temp_imports/{unique_filename}",
        ContentFile(uploaded_file.read())
    )
    
    return path


# Convenience function for easier usage
def queue_product_import(uploaded_file, company_id: str) -> str:
    """
    Queue product import task
    
    Args:
        uploaded_file: Django UploadedFile object
        company_id: Company UUID string
        
    Returns:
        Celery task ID
    """
    # Save file temporarily
    file_path = save_uploaded_file_temporarily(uploaded_file)
    
    # Queue processing task
    task = process_product_import.delay(file_path, company_id, uploaded_file.name)
    
    return task.id