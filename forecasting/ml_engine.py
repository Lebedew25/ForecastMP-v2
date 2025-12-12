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
        self.lag_days = [1, 7]  # Reduced from [1, 7, 14, 30] to avoid excessive data loss
        self.rolling_windows = [7]  # Reduced from [7, 14, 30] to avoid excessive data loss
    
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
        return df
    
    def create_calendar_features(self, df: pd.DataFrame, date_column: str = 'date') -> pd.DataFrame:
        """Create calendar-based features"""
        df['day_of_week'] = pd.to_datetime(df[date_column]).dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        return df
    
    def create_trend_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create trend and growth features"""
        df['days_since_start'] = (pd.to_datetime(df['date']) - pd.to_datetime(df['date'].min())).dt.days
        
        # Calculate growth rate with smaller periods to avoid excessive NaN
        df['growth_rate_3d'] = df['quantity'].pct_change(periods=3)
        
        return df
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Complete feature engineering pipeline with data preservation"""
        df = df.copy()
        df = df.sort_values('date')
        
        original_rows = len(df)
        
        # Create all features
        df = self.create_lag_features(df)
        df = self.create_rolling_features(df)
        df = self.create_calendar_features(df)
        df = self.create_trend_features(df)
        
        # Instead of dropping all NaN rows, let's be more selective
        # Keep rows that have at least some features (not all NaN)
        feature_cols = [col for col in df.columns if col not in ['quantity', 'date', 'id', 'product_id', 'company_id']]
        df['feature_null_count'] = df[feature_cols].isnull().sum(axis=1)
        
        # Keep rows where less than 50% of features are null
        threshold = len(feature_cols) // 2
        df = df[df['feature_null_count'] <= threshold]
        
        # Remove the helper column
        df = df.drop('feature_null_count', axis=1)
        
        # Replace inf / -inf with NaN
        df = df.replace([np.inf, -np.inf], np.nan)
        
        # Fill NaN values with appropriate defaults instead of dropping them
        # For lag features, fill with the original quantity
        for col in df.columns:
            if 'lag_' in col:
                df[col] = df[col].fillna(df['quantity'])
            elif 'rolling_' in col:
                # For rolling stats, fill with the original quantity or 0
                if 'std' in col:
                    df[col] = df[col].fillna(0)
                else:
                    df[col] = df[col].fillna(df['quantity'])
            elif 'growth_rate' in col:
                # For growth rates, fill with 0 (no growth)
                df[col] = df[col].fillna(0)
        
        # For calendar features, forward fill or use reasonable defaults
        df['day_of_week'] = df['day_of_week'].fillna(method='ffill').fillna(0)
        df['is_weekend'] = df['is_weekend'].fillna(method='ffill').fillna(0)
        df['days_since_start'] = df['days_since_start'].fillna(0)
        
        final_rows = len(df)
        print(f"Feature engineering: {original_rows} -> {final_rows} rows (preserved {final_rows/original_rows*100:.1f}% of data)")
        
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
        """Train XGBoost model with data validation"""
        
        if params is None:
            params = {
                'objective': 'reg:squarederror',
                'max_depth': 4,  # Reduced from 6 to prevent overfitting on small datasets
                'learning_rate': 0.1,
                'n_estimators': 50,  # Reduced from 100 for faster training
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42
            }
        
        X, y = self.prepare_training_data(sales_history)
        
        # Check if we have enough data
        if len(X) < 10:
            raise ValueError(f"Insufficient training data: only {len(X)} samples available, need at least 10")
        
        # Check for empty feature set
        if X.empty or len(X.columns) == 0:
            raise ValueError("No features available for training")
        
        # Time series cross-validation with reduced splits for small datasets
        n_splits = min(3, len(X) // 5)  # Reduce splits for small datasets
        if n_splits < 2:
            # Fall back to simple train/validation split
            split_idx = len(X) * 4 // 5
            if split_idx < 1:
                raise ValueError("Dataset too small for training")
            
            X_train, X_val = X.iloc[:split_idx], X.iloc[split_idx:]
            y_train, y_val = y.iloc[:split_idx], y.iloc[split_idx:]
            
            model = xgb.XGBRegressor(**params)
            model.fit(X_train, y_train)
            
            score = model.score(X_val, y_val)
            cv_scores = [score]
        else:
            tscv = TimeSeriesSplit(n_splits=n_splits)
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
            'mean_cv_score': np.mean(cv_scores) if cv_scores else 0.0,
            'std_cv_score': np.std(cv_scores) if len(cv_scores) > 1 else 0.0,
            'feature_importance': dict(zip(self.feature_columns, self.model.feature_importances_)) if hasattr(self.model, 'feature_importances_') else {},
            'samples_used': len(X)
        }
    
    def predict(
        self,
        sales_history: pd.DataFrame,
        forecast_days: int = None
    ) -> pd.DataFrame:
        """Generate forecast for future days with error handling"""
        
        if self.model is None:
            raise ValueError("Model must be trained before prediction")
        
        if forecast_days is None:
            forecast_days = self.horizon
        
        # Prepare historical data
        df = self.feature_engineer.engineer_features(sales_history.copy())
        
        # Check if we have data to work with
        if len(df) == 0:
            raise ValueError("No data available after feature engineering")
        
        # Ensure date is Timestamp for consistent operations
        df['date'] = pd.to_datetime(df['date'])
        
        forecasts = []
        last_date = df['date'].max()
        
        # Iterative forecasting for multiple days ahead
        for day_ahead in range(1, forecast_days + 1):
            forecast_date = last_date + timedelta(days=day_ahead)
            
            # Get last known features
            if len(df) > 0:
                last_row = df.iloc[-1:][self.feature_columns]
                
                # Check if we have features to predict on
                if not last_row.empty and len(last_row.columns) > 0:
                    # Predict
                    try:
                        prediction = self.model.predict(last_row)[0]
                        prediction = max(0, int(prediction))  # Ensure non-negative integer
                    except Exception as e:
                        # Fallback to simple average if prediction fails
                        prediction = int(df['quantity'].mean()) if len(df) > 0 else 0
                        prediction = max(0, prediction)
                else:
                    # Fallback to simple average if no features
                    prediction = int(df['quantity'].mean()) if len(df) > 0 else 0
                    prediction = max(0, prediction)
            else:
                # Fallback to 0 if no data
                prediction = 0
            
            # Calculate prediction intervals (simplified)
            # In production, use quantile regression or similar
            if len(df) > 1:
                std_dev = df['quantity'].std()
                confidence_lower = max(0, prediction - 1.96 * std_dev)
                confidence_upper = prediction + 1.96 * std_dev
            else:
                confidence_lower = prediction
                confidence_upper = prediction
            
            forecasts.append({
                'forecast_date': forecast_date.date(),
                'predicted_quantity': prediction,
                'confidence_lower': confidence_lower,
                'confidence_upper': confidence_upper,
                'confidence_score': min(95.0, 100.0 - (std_dev / (prediction + 1) * 100 if 'std_dev' in locals() else 50.0))
            })
            
            # Update dataframe with prediction for next iteration
            if len(df) > 0:
                new_row = df.iloc[-1:].copy()
                new_row['date'] = forecast_date
                new_row['quantity'] = prediction
                df = pd.concat([df, new_row], ignore_index=True)
                df = self.feature_engineer.engineer_features(df)
                df['date'] = pd.to_datetime(df['date'])
        
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
