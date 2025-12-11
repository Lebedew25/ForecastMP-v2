"""
Marketplace API clients
"""
import requests
from abc import ABC, abstractmethod
from typing import List, Dict
from datetime import datetime, date


class MarketplaceClient(ABC):
    """Base class for marketplace API clients"""
    
    def __init__(self, api_key: str, api_secret: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with marketplace API"""
        pass
    
    @abstractmethod
    def fetch_sales(self, start_date: date, end_date: date) -> List[Dict]:
        """Fetch sales transactions"""
        pass
    
    @abstractmethod
    def fetch_inventory(self) -> List[Dict]:
        """Fetch current inventory levels"""
        pass
    
    @abstractmethod
    def fetch_products(self) -> List[Dict]:
        """Fetch product catalog"""
        pass


class WildberriesClient(MarketplaceClient):
    """Wildberries API client"""
    
    BASE_URL = "https://suppliers-api.wildberries.ru"
    
    def authenticate(self) -> bool:
        """Wildberries uses API token authentication"""
        self.session.headers.update({
            'Authorization': self.api_key,
            'Content-Type': 'application/json'
        })
        return True
    
    def fetch_sales(self, start_date: date, end_date: date) -> List[Dict]:
        """Fetch sales from Wildberries"""
        # Simplified placeholder - actual implementation would call real API
        endpoint = f"{self.BASE_URL}/api/v1/supplier/reportDetailByPeriod"
        
        params = {
            'dateFrom': start_date.isoformat(),
            'dateTo': end_date.isoformat()
        }
        
        try:
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch Wildberries sales: {str(e)}")
    
    def fetch_inventory(self) -> List[Dict]:
        """Fetch inventory from Wildberries"""
        endpoint = f"{self.BASE_URL}/api/v1/supplier/stocks"
        
        try:
            response = self.session.get(endpoint, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch Wildberries inventory: {str(e)}")
    
    def fetch_products(self) -> List[Dict]:
        """Fetch products from Wildberries"""
        endpoint = f"{self.BASE_URL}/api/v1/supplier/cards"
        
        try:
            response = self.session.get(endpoint, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch Wildberries products: {str(e)}")



class WebsiteClient(MarketplaceClient):
    """Generic website/e-commerce platform client"""
    
    def __init__(self, api_endpoint: str, api_key: str = None, auth_method: str = 'API_KEY'):
        """
        Initialize website client
        
        Args:
            api_endpoint: Base API endpoint URL
            api_key: API key/token for authentication
            auth_method: Authentication method (API_KEY, BASIC_AUTH, OAUTH)
        """
        super().__init__(api_key)
        self.api_endpoint = api_endpoint.rstrip('/')
        self.auth_method = auth_method
        
        # Platform-specific settings
        self.platform_type = 'CUSTOM_API'
        self.supported_features = ['sales', 'inventory']
    
    def authenticate(self) -> bool:
        """Authenticate with website API"""
        if self.auth_method == 'API_KEY':
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            })
        elif self.auth_method == 'BASIC_AUTH' and self.api_secret:
            import base64
            credentials = base64.b64encode(f'{self.api_key}:{self.api_secret}'.encode()).decode()
            self.session.headers.update({
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/json'
            })
        elif self.auth_method == 'OAUTH':
            # OAuth would require more complex flow
            # This is a simplified placeholder
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            })
        
        return True
    
    def fetch_sales(self, start_date: date, end_date: date) -> List[Dict]:
        """Fetch sales from website API"""
        endpoint = f"{self.api_endpoint}/sales"
        
        params = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }
        
        try:
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Normalize data to internal format
            normalized_sales = []
            sales_data = data.get('sales', data.get('orders', data.get('data', [])))
            
            for sale in sales_data:
                # Extract required fields with fallbacks
                order_id = sale.get('order_id') or sale.get('id') or ''
                order_date = sale.get('order_date') or sale.get('date') or ''
                items = sale.get('items', [])
                
                # Handle single item vs multiple items
                if isinstance(items, dict):
                    items = [items]
                
                for item in items:
                    sku = item.get('sku') or item.get('product_sku') or item.get('product_id', '')
                    quantity = int(item.get('quantity', 0))
                    price = float(item.get('price', 0) or item.get('revenue', 0))
                    
                    if sku and quantity > 0:
                        normalized_sales.append({
                            'order_id': order_id,
                            'order_date': order_date,
                            'sku': sku,
                            'quantity': quantity,
                            'price': price
                        })
            
            return normalized_sales
            
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch website sales: {str(e)}")
    
    def fetch_inventory(self) -> List[Dict]:
        """Fetch inventory from website API"""
        endpoint = f"{self.api_endpoint}/inventory"
        
        try:
            response = self.session.get(endpoint, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Normalize data to internal format
            normalized_inventory = []
            inventory_data = data.get('inventory', data.get('stock', data.get('data', [])))
            
            for item in inventory_data:
                sku = item.get('sku') or item.get('product_sku') or item.get('product_id', '')
                quantity = int(item.get('quantity', 0) or item.get('stock', 0))
                
                if sku:
                    normalized_inventory.append({
                        'sku': sku,
                        'quantity': quantity
                    })
            
            return normalized_inventory
            
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch website inventory: {str(e)}")
    
    def fetch_products(self) -> List[Dict]:
        """Fetch products from website API"""
        endpoint = f"{self.api_endpoint}/products"
        
        try:
            response = self.session.get(endpoint, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Normalize data to internal format
            normalized_products = []
            products_data = data.get('products', data.get('data', []))
            
            for product in products_data:
                sku = product.get('sku') or product.get('product_sku') or product.get('id', '')
                name = product.get('name') or product.get('title', 'Unknown Product')
                price = float(product.get('price', 0) or product.get('selling_price', 0))
                
                if sku:
                    normalized_products.append({
                        'sku': sku,
                        'name': name,
                        'price': price
                    })
            
            return normalized_products
            
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch website products: {str(e)}")
    
    def update_inventory(self, updates: List[Dict]) -> bool:
        """Push inventory updates to website API"""
        endpoint = f"{self.api_endpoint}/inventory/bulk-update"
        
        try:
            payload = {
                'updates': updates
            }
            
            response = self.session.post(endpoint, json=payload, timeout=30)
            response.raise_for_status()
            
            return response.json().get('success', True)
            
        except requests.RequestException as e:
            raise Exception(f"Failed to update website inventory: {str(e)}")


class OzonClient(MarketplaceClient):
    """Ozon API client"""
    
    BASE_URL = "https://api-seller.ozon.ru"
    
    def authenticate(self) -> bool:
        """Ozon uses Client-Id and Api-Key authentication"""
        self.session.headers.update({
            'Client-Id': self.api_key,
            'Api-Key': self.api_secret,
            'Content-Type': 'application/json'
        })
        return True
    
    def fetch_sales(self, start_date: date, end_date: date) -> List[Dict]:
        """Fetch sales from Ozon"""
        endpoint = f"{self.BASE_URL}/v1/analytics/data"
        
        payload = {
            'date_from': start_date.isoformat(),
            'date_to': end_date.isoformat(),
            'metrics': ['revenue', 'ordered_units'],
            'dimension': ['sku'],
            'filters': []
        }
        
        try:
            response = self.session.post(endpoint, json=payload, timeout=30)
            response.raise_for_status()
            return response.json().get('result', {}).get('data', [])
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch Ozon sales: {str(e)}")
    
    def fetch_inventory(self) -> List[Dict]:
        """Fetch inventory from Ozon"""
        endpoint = f"{self.BASE_URL}/v2/products/stocks"
        
        payload = {
            'filter': {},
            'last_id': '',
            'limit': 1000
        }
        
        try:
            response = self.session.post(endpoint, json=payload, timeout=30)
            response.raise_for_status()
            return response.json().get('result', {}).get('items', [])
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch Ozon inventory: {str(e)}")
    
    def fetch_products(self) -> List[Dict]:
        """Fetch products from Ozon"""
        endpoint = f"{self.BASE_URL}/v2/product/list"
        
        payload = {
            'filter': {},
            'last_id': '',
            'limit': 1000
        }
        
        try:
            response = self.session.post(endpoint, json=payload, timeout=30)
            response.raise_for_status()
            return response.json().get('result', {}).get('items', [])
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch Ozon products: {str(e)}")


def get_client(marketplace: str, api_key: str, api_secret: str = None) -> MarketplaceClient:
    """Factory function to get marketplace client"""
    clients = {
        'WILDBERRIES': WildberriesClient,
        'OZON': OzonClient,
        'WEBSITE': WebsiteClient,
    }
    
    client_class = clients.get(marketplace)
    if not client_class:
        raise ValueError(f"Unknown marketplace: {marketplace}")
    
    client = client_class(api_key, api_secret)
    client.authenticate()
    return client
