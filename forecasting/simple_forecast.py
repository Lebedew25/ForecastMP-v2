"""
Simple forecasting engine using moving averages for MVP
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from django.db.models import Avg, Count
from sales.models import SalesHistory, DailySalesAggregate
from forecasting.models import Forecast
from products.models import Product


class SimpleForecaster:
    """Simple moving average forecasting for MVP"""
    
    def __init__(self):
        self.window_7 = 7
        self.window_14 = 14
    
    def calculate_moving_averages(self, sales_data: List[int]) -> Tuple[float, float]:
        """
        Calculate 7-day and 14-day moving averages
        
        Args:
            sales_data: List of daily sales quantities
            
        Returns:
            Tuple of (avg_7_day, avg_14_day)
        """
        if len(sales_data) == 0:
            return 0.0, 0.0
            
        # Calculate 7-day average (or use available data if less than 7 days)
        if len(sales_data) >= 7:
            avg_7 = np.mean(sales_data[-7:])
        else:
            avg_7 = np.mean(sales_data)
            
        # Calculate 14-day average (or use available data if less than 14 days)
        if len(sales_data) >= 14:
            avg_14 = np.mean(sales_data[-14:])
        else:
            avg_14 = np.mean(sales_data)
            
        return float(avg_7), float(avg_14)
    
    def calculate_volatility(self, sales_data: List[int]) -> float:
        """
        Calculate sales volatility using coefficient of variation
        
        Args:
            sales_data: List of daily sales quantities
            
        Returns:
            Volatility score (0-1, where 1 is high volatility)
        """
        if len(sales_data) < 2:
            return 0.0
            
        # Calculate coefficient of variation
        mean = np.mean(sales_data)
        if mean == 0:
            return 0.0
            
        std_dev = np.std(sales_data)
        cv = std_dev / mean
        
        # Normalize to 0-1 scale (assuming CV rarely exceeds 2)
        return min(1.0, cv / 2.0)
    
    def calculate_weighted_forecast(self, avg_7: float, avg_14: float, volatility: float) -> float:
        """
        Calculate weighted forecast based on volatility
        
        Args:
            avg_7: 7-day moving average
            avg_14: 14-day moving average
            volatility: Volatility measure (0-1)
            
        Returns:
            Weighted forecast value
        """
        # Higher volatility = more weight to longer term average
        if volatility < 0.3:  # Low volatility
            weight_7 = 0.6
            weight_14 = 0.4
        elif volatility < 0.7:  # Medium volatility
            weight_7 = 0.5
            weight_14 = 0.5
        else:  # High volatility
            weight_7 = 0.4
            weight_14 = 0.6
            
        return weight_7 * avg_7 + weight_14 * avg_14
    
    def get_product_sales_history(self, product_id: str, days: int = 60) -> List[int]:
        """
        Retrieve sales history for a product
        
        Args:
            product_id: Product UUID
            days: Number of days of history to retrieve
            
        Returns:
            List of daily sales quantities
        """
        cutoff_date = datetime.now().date() - timedelta(days=days)
        
        # Get daily sales from SalesHistory (preferred) or DailySalesAggregate
        sales_records = SalesHistory.objects.filter(
            product_id=product_id,
            date__gte=cutoff_date
        ).order_by('date')
        
        # If no SalesHistory data, fall back to DailySalesAggregate
        if not sales_records.exists():
            sales_records = DailySalesAggregate.objects.filter(
                product_id=product_id,
                date__gte=cutoff_date
            ).order_by('date')
            sales_data = [record.total_quantity for record in sales_records]
        else:
            sales_data = [record.quantity for record in sales_records]
            
        return sales_data
    
    def calculate_confidence_level(self, sales_data: List[int], forecast_value: float) -> str:
        """
        Determine forecast confidence level
        
        Args:
            sales_data: Historical sales data
            forecast_value: Calculated forecast value
            
        Returns:
            Confidence level: 'HIGH', 'MEDIUM', or 'LOW'
        """
        data_points = len(sales_data)
        
        # High confidence requires substantial history and low variance
        if data_points >= 30:
            return 'HIGH'
        elif data_points >= 14:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def generate_forecast_for_product(
        self, 
        product_id: str, 
        forecast_days: int = 14
    ) -> List[Dict]:
        """
        Generate forecast for a single product
        
        Args:
            product_id: Product UUID
            forecast_days: Number of days to forecast
            
        Returns:
            List of forecast dictionaries
        """
        # Get sales history
        sales_data = self.get_product_sales_history(product_id, days=60)
        
        # Handle edge cases
        if len(sales_data) == 0:
            # No sales history - forecast 0
            avg_7, avg_14 = 0.0, 0.0
            volatility = 0.0
            weighted_avg = 0.0
        else:
            # Calculate moving averages
            avg_7, avg_14 = self.calculate_moving_averages(sales_data)
            
            # Calculate volatility
            volatility = self.calculate_volatility(sales_data)
            
            # Calculate weighted forecast
            weighted_avg = self.calculate_weighted_forecast(avg_7, avg_14, volatility)
        
        # Generate daily forecasts for specified period
        forecasts = []
        today = datetime.now().date()
        
        for i in range(1, forecast_days + 1):
            forecast_date = today + timedelta(days=i)
            
            # Use the same forecast for all days (simple approach)
            forecast_value = max(0, round(weighted_avg))
            
            # Calculate confidence bounds (simplified)
            std_dev = np.std(sales_data) if len(sales_data) > 1 else 0
            confidence_lower = max(0, forecast_value - 1.96 * std_dev)
            confidence_upper = forecast_value + 1.96 * std_dev
            
            # Determine confidence level
            confidence_level = self.calculate_confidence_level(sales_data, forecast_value)
            
            forecasts.append({
                'forecast_date': forecast_date,
                'predicted_quantity': forecast_value,
                'confidence_lower': round(confidence_lower),
                'confidence_upper': round(confidence_upper),
                'confidence_level': confidence_level,
                'calculation_method': 'MOVING_AVERAGE'
            })
            
        return forecasts
    
    def generate_forecasts_for_company(self, company_id: str) -> Dict[str, List[Dict]]:
        """
        Generate forecasts for all active products in a company
        
        Args:
            company_id: Company UUID
            
        Returns:
            Dictionary mapping product IDs to forecast lists
        """
        from products.models import Product
        
        # Get all active products for company
        products = Product.objects.filter(
            company_id=company_id,
            is_active=True
        )
        
        forecasts = {}
        for product in products:
            try:
                product_forecasts = self.generate_forecast_for_product(str(product.id))
                forecasts[str(product.id)] = product_forecasts
            except Exception as e:
                print(f"Error generating forecast for product {product.sku}: {str(e)}")
                # Generate fallback forecast
                forecasts[str(product.id)] = [{
                    'forecast_date': datetime.now().date() + timedelta(days=i),
                    'predicted_quantity': 0,
                    'confidence_lower': 0,
                    'confidence_upper': 0,
                    'confidence_level': 'LOW',
                    'calculation_method': 'MOVING_AVERAGE'
                } for i in range(1, 15)]
                
        return forecasts
    
    def save_forecasts_to_db(self, product_id: str, forecasts: List[Dict]) -> None:
        """
        Save forecasts to database
        
        Args:
            product_id: Product UUID
            forecasts: List of forecast dictionaries
        """
        from products.models import Product
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ValueError(f"Product with ID {product_id} does not exist")
        
        # Save each forecast
        for forecast_data in forecasts:
            Forecast.objects.update_or_create(
                product=product,
                forecast_date=forecast_data['forecast_date'],
                defaults={
                    'predicted_quantity': forecast_data['predicted_quantity'],
                    'confidence_lower': forecast_data['confidence_lower'],
                    'confidence_upper': forecast_data['confidence_upper'],
                    'model_version': 'simple_ma_v1.0',
                    'confidence_score': 80.0 if forecast_data['confidence_level'] == 'HIGH' else 
                                       60.0 if forecast_data['confidence_level'] == 'MEDIUM' else 40.0,
                }
            )


# Convenience function for Celery tasks
def generate_simple_forecast_for_product(product_id: str, forecast_days: int = 14) -> bool:
    """
    Generate and save simple forecast for a single product
    
    Args:
        product_id: Product UUID
        forecast_days: Number of days to forecast
        
    Returns:
        True if successful, False otherwise
    """
    try:
        forecaster = SimpleForecaster()
        forecasts = forecaster.generate_forecast_for_product(product_id, forecast_days)
        forecaster.save_forecasts_to_db(product_id, forecasts)
        return True
    except Exception as e:
        print(f"Error generating forecast for product {product_id}: {str(e)}")
        return False


def generate_simple_forecasts_for_company(company_id: str) -> Dict[str, int]:
    """
    Generate forecasts for all products in a company
    
    Args:
        company_id: Company UUID
        
    Returns:
        Dictionary with success/failure counts
    """
    forecaster = SimpleForecaster()
    forecasts = forecaster.generate_forecasts_for_company(company_id)
    
    success_count = 0
    failure_count = 0
    
    for product_id, product_forecasts in forecasts.items():
        try:
            forecaster.save_forecasts_to_db(product_id, product_forecasts)
            success_count += 1
        except Exception as e:
            print(f"Error saving forecasts for product {product_id}: {str(e)}")
            failure_count += 1
    
    return {
        'success_count': success_count,
        'failure_count': failure_count
    }