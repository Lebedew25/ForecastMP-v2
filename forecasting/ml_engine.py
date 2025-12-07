"""
ML Engine for demand forecasting using XGBoost
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit


class FeatureEngineer:
    """Feature engineering pipeline for sales forecasting"""
    
    def __init__(self):
        self.lag_days = [1, 7, 14, 30]
        self.rolling_windows = [7, 14, 30]
    
    def create_lag_features(self, df: pd.DataFrame, column: str = 'quantity') -> pd.DataFrame:
        """Create lag features for time series"""
        for lag in self.lag_days:
            df[f'{column}_lag_{lag}'] = df[column].shift(lag)
        return df
    
    def create_rolling_features(self, df: pd.DataFrame, column: str = 'quantity') -> pd.DataFrame:
        """Create rolling statistics features"""
        for window in self.rolling_windows:
            df[f'{column}_rolling_mean_{window}'] = df[column].rolling(window=window).mean()
            df[f'{column}_rolling_std_{window}'] = df[column].rolling(window=window).std()
            df[f'{column}_rolling_max_{window}'] = df[column].rolling(window=window).max()
            df[f'{column}_rolling_min_{window}'] = df[column].rolling(window=window).min()
        return df
    
    def create_calendar_features(self, df: pd.DataFrame, date_column: str = 'date') -> pd.DataFrame:
        """Create calendar-based features"""
        df['day_of_week'] = pd.to_datetime(df[date_column]).dt.dayofweek
        df['day_of_month'] = pd.to_datetime(df[date_column]).dt.day
        df['week_of_year'] = pd.to_datetime(df[date_column]).dt.isocalendar().week
        df['month'] = pd.to_datetime(df[date_column]).dt.month
        df['quarter'] = pd.to_datetime(df[date_column]).dt.quarter
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_month_start'] = pd.to_datetime(df[date_column]).dt.is_month_start.astype(int)
        df['is_month_end'] = pd.to_datetime(df[date_column]).dt.is_month_end.astype(int)
        return df
    
    def create_trend_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create trend and growth features"""
        df['days_since_start'] = (pd.to_datetime(df['date']) - pd.to_datetime(df['date'].min())).dt.days
        
        # Calculate growth rate
        df['growth_rate_7d'] = df['quantity'].pct_change(periods=7)
        df['growth_rate_30d'] = df['quantity'].pct_change(periods=30)
        
        return df
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Complete feature engineering pipeline"""
        df = df.copy()
        df = df.sort_values('date')
        
        # Create all features
        df = self.create_lag_features(df)
        df = self.create_rolling_features(df)
        df = self.create_calendar_features(df)
        df = self.create_trend_features(df)
        
        # Drop NaN rows created by lag/rolling features
        df = df.dropna()
        
        return df


class DemandForecaster:
    """XGBoost-based demand forecasting model"""
    
    def __init__(self, horizon: int = 30):
        """
        Args:
            horizon: Number of days to forecast ahead
        """
        self.horizon = horizon
        self.model = None
        self.feature_engineer = FeatureEngineer()
        self.feature_columns = []
        self.model_version = "v1.0"
    
    def prepare_training_data(
        self, 
        sales_history: pd.DataFrame,
        target_column: str = 'quantity'
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare data for training"""
        
        # Engineer features
        df = self.feature_engineer.engineer_features(sales_history)
        
        # Define feature columns (exclude target and date)
        exclude_cols = [target_column, 'date', 'id', 'product_id', 'company_id']
        self.feature_columns = [col for col in df.columns if col not in exclude_cols]
        
        X = df[self.feature_columns]
        y = df[target_column]
        
        return X, y
    
    def train(
        self,
        sales_history: pd.DataFrame,
        params: Dict = None
    ) -> Dict:
        """Train XGBoost model"""
        
        if params is None:
            params = {
                'objective': 'reg:squarederror',
                'max_depth': 6,
                'learning_rate': 0.1,
                'n_estimators': 100,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42
            }
        
        X, y = self.prepare_training_data(sales_history)
        
        # Time series cross-validation
        tscv = TimeSeriesSplit(n_splits=3)
        cv_scores = []
        
        for train_idx, val_idx in tscv.split(X):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            
            model = xgb.XGBRegressor(**params)
            model.fit(X_train, y_train)
            
            score = model.score(X_val, y_val)
            cv_scores.append(score)
        
        # Train final model on all data
        self.model = xgb.XGBRegressor(**params)
        self.model.fit(X, y)
        
        return {
            'mean_cv_score': np.mean(cv_scores),
            'std_cv_score': np.std(cv_scores),
            'feature_importance': dict(zip(self.feature_columns, self.model.feature_importances_))
        }
    
    def predict(
        self,
        sales_history: pd.DataFrame,
        forecast_days: int = None
    ) -> pd.DataFrame:
        """Generate forecast for future days"""
        
        if self.model is None:
            raise ValueError("Model must be trained before prediction")
        
        if forecast_days is None:
            forecast_days = self.horizon
        
        # Prepare historical data
        df = self.feature_engineer.engineer_features(sales_history.copy())
        
        forecasts = []
        last_date = pd.to_datetime(df['date'].max())
        
        # Iterative forecasting for multiple days ahead
        for day_ahead in range(1, forecast_days + 1):
            forecast_date = last_date + timedelta(days=day_ahead)
            
            # Get last known features
            last_row = df.iloc[-1:][self.feature_columns]
            
            # Predict
            prediction = self.model.predict(last_row)[0]
            prediction = max(0, int(prediction))  # Ensure non-negative integer
            
            # Calculate prediction intervals (simplified)
            # In production, use quantile regression or similar
            std_dev = df['quantity'].std()
            confidence_lower = max(0, prediction - 1.96 * std_dev)
            confidence_upper = prediction + 1.96 * std_dev
            
            forecasts.append({
                'forecast_date': forecast_date,
                'predicted_quantity': prediction,
                'confidence_lower': confidence_lower,
                'confidence_upper': confidence_upper,
                'confidence_score': min(95.0, 100.0 - abs(std_dev / (prediction + 1) * 100))
            })
            
            # Update dataframe with prediction for next iteration
            new_row = df.iloc[-1:].copy()
            new_row['date'] = forecast_date
            new_row['quantity'] = prediction
            df = pd.concat([df, new_row], ignore_index=True)
            df = self.feature_engineer.engineer_features(df)
        
        return pd.DataFrame(forecasts)
    
    def evaluate(
        self,
        test_data: pd.DataFrame
    ) -> Dict:
        """Evaluate model performance"""
        
        X, y_true = self.prepare_training_data(test_data)
        y_pred = self.model.predict(X)
        
        # Calculate metrics
        mae = np.mean(np.abs(y_true - y_pred))
        mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1))) * 100
        rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
        
        return {
            'mae': mae,
            'mape': mape,
            'rmse': rmse
        }
