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
    }
    
    client_class = clients.get(marketplace)
    if not client_class:
        raise ValueError(f"Unknown marketplace: {marketplace}")
    
    client = client_class(api_key, api_secret)
    client.authenticate()
    return client
