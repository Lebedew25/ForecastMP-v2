"""
Product importer for CSV/XLSX files
"""
import csv
import io
import pandas as pd
from typing import Dict, List, Tuple, Any
from django.db import transaction
from django.core.files.uploadedfile import UploadedFile
from products.models import Product, ProductAttributes
from sales.models import InventorySnapshot
import logging

logger = logging.getLogger(__name__)


class ProductImporter:
    """Handles importing products from CSV/XLSX files"""
    
    # Required columns that must be present
    REQUIRED_COLUMNS = ['sku', 'name']
    
    # Optional columns with their expected data types
    OPTIONAL_COLUMNS = {
        'category': str,
        'description': str,
        'cost_price': float,
        'selling_price': float,
        'weight': float,
        'length': float,
        'width': float,
        'height': float,
        'initial_stock': int,
        'warehouse': str,
    }
    
    def __init__(self, company_id: str):
        """
        Initialize importer for a specific company
        
        Args:
            company_id: Company UUID string
        """
        self.company_id = company_id
        self.errors = []
        self.warnings = []
        
    def detect_file_format(self, file: UploadedFile) -> str:
        """
        Detect if file is CSV or Excel format
        
        Args:
            file: Uploaded file object
            
        Returns:
            'csv' or 'excel'
        """
        filename = file.name.lower()
        if filename.endswith('.csv'):
            return 'csv'
        elif filename.endswith(('.xlsx', '.xls')):
            return 'excel'
        else:
            # Try to read as CSV first
            try:
                file.seek(0)
                sample = file.read(1024).decode('utf-8')
                file.seek(0)
                sniffer = csv.Sniffer()
                sniffer.sniff(sample)
                return 'csv'
            except:
                return 'excel'
    
    def read_csv_file(self, file: UploadedFile) -> pd.DataFrame:
        """
        Read CSV file into pandas DataFrame
        
        Args:
            file: Uploaded CSV file
            
        Returns:
            DataFrame with file contents
        """
        try:
            # Reset file pointer
            file.seek(0)
            
            # Read file content
            content = file.read().decode('utf-8')
            file.seek(0)
            
            # Use pandas to read CSV
            df = pd.read_csv(io.StringIO(content))
            
            # Clean column names
            df.columns = [col.strip().lower() for col in df.columns]
            
            return df
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {str(e)}")
    
    def read_excel_file(self, file: UploadedFile) -> pd.DataFrame:
        """
        Read Excel file into pandas DataFrame
        
        Args:
            file: Uploaded Excel file
            
        Returns:
            DataFrame with file contents
        """
        try:
            # Reset file pointer
            file.seek(0)
            
            # Read Excel file
            df = pd.read_excel(file, engine='openpyxl')
            
            # Clean column names
            df.columns = [col.strip().lower() for col in df.columns]
            
            return df
        except Exception as e:
            raise ValueError(f"Error reading Excel file: {str(e)}")
    
    def validate_columns(self, df: pd.DataFrame) -> bool:
        """
        Validate that required columns are present
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if valid, False otherwise
        """
        columns = df.columns.tolist()
        
        # Check required columns
        missing_required = []
        for col in self.REQUIRED_COLUMNS:
            if col not in columns:
                missing_required.append(col)
        
        if missing_required:
            self.errors.append(f"Missing required columns: {', '.join(missing_required)}")
            return False
        
        # Check for unknown columns
        known_columns = self.REQUIRED_COLUMNS + list(self.OPTIONAL_COLUMNS.keys())
        unknown_columns = [col for col in columns if col not in known_columns]
        
        if unknown_columns:
            self.warnings.append(f"Unknown columns ignored: {', '.join(unknown_columns)}")
        
        return True
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and normalize data in DataFrame
        
        Args:
            df: Raw DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        df = df.copy()
        
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Strip whitespace from string columns
        string_columns = ['sku', 'name', 'category', 'description', 'warehouse']
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        
        # Handle numeric columns
        numeric_columns = ['cost_price', 'selling_price', 'weight', 'length', 'width', 'height', 'initial_stock']
        for col in numeric_columns:
            if col in df.columns:
                # Convert to numeric, replacing invalid values with NaN
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def validate_row(self, row: pd.Series, row_index: int) -> Tuple[bool, List[str]]:
        """
        Validate a single row of data
        
        Args:
            row: DataFrame row
            row_index: Row index (for error reporting)
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate SKU
        if pd.isna(row['sku']) or str(row['sku']).strip() == '':
            errors.append("SKU is required")
        elif len(str(row['sku'])) > 100:
            errors.append("SKU must be 100 characters or less")
        
        # Validate name
        if pd.isna(row['name']) or str(row['name']).strip() == '':
            errors.append("Name is required")
        elif len(str(row['name'])) > 500:
            errors.append("Name must be 500 characters or less")
        
        # Validate numeric fields
        numeric_fields = {
            'cost_price': (0, 999999),
            'selling_price': (0, 999999),
            'weight': (0, 999999),
            'length': (0, 999999),
            'width': (0, 999999),
            'height': (0, 999999),
            'initial_stock': (0, 999999999)
        }
        
        for field, (min_val, max_val) in numeric_fields.items():
            if field in row and not pd.isna(row[field]):
                try:
                    value = float(row[field])
                    if value < min_val or value > max_val:
                        errors.append(f"{field} must be between {min_val} and {max_val}")
                except (ValueError, TypeError):
                    errors.append(f"{field} must be a valid number")
        
        # Validate warehouse if specified
        if 'warehouse' in row and not pd.isna(row['warehouse']):
            warehouse_name = str(row['warehouse']).strip()
            if len(warehouse_name) > 255:
                errors.append("Warehouse name must be 255 characters or less")
        
        return len(errors) == 0, errors
    
    def import_products(self, file: UploadedFile) -> Dict[str, Any]:
        """
        Main import function - reads file and imports products
        
        Args:
            file: Uploaded file object
            
        Returns:
            Dictionary with import results
        """
        try:
            # Detect file format
            file_format = self.detect_file_format(file)
            
            # Read file into DataFrame
            if file_format == 'csv':
                df = self.read_csv_file(file)
            else:
                df = self.read_excel_file(file)
            
            # Validate columns
            if not self.validate_columns(df):
                return {
                    'success': False,
                    'errors': self.errors,
                    'warnings': self.warnings,
                    'imported_count': 0,
                    'failed_rows': []
                }
            
            # Clean data
            df = self.clean_data(df)
            
            # Process rows
            imported_count = 0
            failed_rows = []
            
            # Process each row in transaction
            with transaction.atomic():
                for index, row in df.iterrows():
                    row_number = index + 2  # +1 for header, +1 for 0-based index
                    
                    # Validate row
                    is_valid, row_errors = self.validate_row(row, row_number)
                    
                    if not is_valid:
                        failed_rows.append({
                            'row_number': row_number,
                            'errors': row_errors,
                            'data': row.to_dict()
                        })
                        continue
                    
                    # Import product
                    try:
                        self.create_or_update_product(row)
                        imported_count += 1
                    except Exception as e:
                        failed_rows.append({
                            'row_number': row_number,
                            'errors': [str(e)],
                            'data': row.to_dict()
                        })
            
            return {
                'success': True,
                'errors': self.errors,
                'warnings': self.warnings,
                'imported_count': imported_count,
                'failed_rows': failed_rows
            }
            
        except Exception as e:
            logger.error(f"Import failed: {str(e)}")
            return {
                'success': False,
                'errors': [f"Import failed: {str(e)}"],
                'warnings': self.warnings,
                'imported_count': 0,
                'failed_rows': []
            }
    
    def create_or_update_product(self, row: pd.Series) -> Product:
        """
        Create or update a product from row data
        
        Args:
            row: DataFrame row with product data
            
        Returns:
            Product instance
        """
        from accounts.models import Company
        
        # Get company
        company = Company.objects.get(id=self.company_id)
        
        # Create or update product
        product, created = Product.objects.update_or_create(
            company=company,
            sku=str(row['sku']).strip(),
            defaults={
                'name': str(row['name']).strip(),
                'category': str(row.get('category', '')).strip() if not pd.isna(row.get('category')) else '',
                'description': str(row.get('description', '')).strip() if not pd.isna(row.get('description')) else '',
                'is_active': True
            }
        )
        
        # Update product attributes if any provided
        attrs_updated = False
        attrs_defaults = {}
        
        if 'cost_price' in row and not pd.isna(row['cost_price']):
            attrs_defaults['cost_price'] = row['cost_price']
            attrs_updated = True
            
        if 'selling_price' in row and not pd.isna(row['selling_price']):
            attrs_defaults['selling_price'] = row['selling_price']
            attrs_updated = True
            
        if 'weight' in row and not pd.isna(row['weight']):
            attrs_defaults['weight'] = row['weight']
            attrs_updated = True
            
        if 'length' in row and not pd.isna(row['length']):
            attrs_defaults['length'] = row['length']
            attrs_updated = True
            
        if 'width' in row and not pd.isna(row['width']):
            attrs_defaults['width'] = row['width']
            attrs_updated = True
            
        if 'height' in row and not pd.isna(row['height']):
            attrs_defaults['height'] = row['height']
            attrs_updated = True
        
        if attrs_updated:
            ProductAttributes.objects.update_or_create(
                product=product,
                defaults=attrs_defaults
            )
        
        # Handle initial stock if specified
        if 'initial_stock' in row and not pd.isna(row['initial_stock']):
            initial_stock = int(row['initial_stock'])
            
            # If warehouse specified, try to find it
            warehouse = None
            if 'warehouse' in row and not pd.isna(row['warehouse']):
                from sales.models import Warehouse
                try:
                    warehouse = Warehouse.objects.get(
                        company=company,
                        name=str(row['warehouse']).strip()
                    )
                except Warehouse.DoesNotExist:
                    # Log warning but continue
                    self.warnings.append(f"Warehouse '{row['warehouse']}' not found for product {row['sku']}")
            
            # Create inventory snapshot
            if initial_stock >= 0:
                InventorySnapshot.objects.create(
                    product=product,
                    snapshot_date=pd.Timestamp.now().date(),
                    quantity_available=initial_stock,
                    quantity_reserved=0,
                    warehouse=warehouse,
                    legacy_warehouse_id=warehouse.name if warehouse else ''
                )
        
        return product


# Convenience function for easier usage
def import_products_from_file(company_id: str, file: UploadedFile) -> Dict[str, Any]:
    """
    Import products from uploaded file
    
    Args:
        company_id: Company UUID string
        file: Uploaded file object
        
    Returns:
        Dictionary with import results
    """
    importer = ProductImporter(company_id)
    return importer.import_products(file)