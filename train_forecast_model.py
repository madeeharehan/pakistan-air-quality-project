import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pickle
import os
import warnings
warnings.filterwarnings('ignore')

class SimpleForecastModel:
    """Simple forecasting model using moving averages and trend."""
    def __init__(self):
        self.history = None
        self.last_date = None
        self.trend = None
        self.seasonal_avg = None
        
    def fit(self, df):
        """Fit the model to historical data."""
        df = df.sort_values('ds').copy()
        df['datetime'] = df['ds']
        df['hour'] = pd.to_datetime(df['datetime']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['datetime']).dt.dayofweek
        
        self.history = df.copy()
        self.last_date = pd.to_datetime(df['ds']).max()
        
        # Calculate trend (slope)
        if len(df) > 1:
            x = np.arange(len(df))
            y = df['y'].values
            self.trend = np.polyfit(x, y, 1)[0]
        else:
            self.trend = 0
        
        # Calculate hourly averages for seasonality
        self.seasonal_avg = df.groupby('hour')['y'].mean().to_dict()
        self.base_value = df['y'].iloc[-1] if len(df) > 0 else df['y'].mean()
        
    def predict(self, future_df):
        """Predict future values."""
        predictions = []
        future_df = future_df.copy()
        future_df['datetime'] = pd.to_datetime(future_df['ds'])
        future_df['hour'] = future_df['datetime'].dt.hour
        
        for _, row in future_df.iterrows():
            hour = row['hour']
            
            # Base prediction: last value
            base = self.base_value
            
            # Add seasonal component (hourly pattern)
            seasonal = self.seasonal_avg.get(hour, base)
            
            # Add trend component
            hours_ahead = (row['datetime'] - self.last_date).total_seconds() / 3600
            trend_component = self.trend * (hours_ahead / 168)  # Scale trend per week
            
            # Combine predictions (weighted average)
            pred = base * 0.5 + seasonal * 0.3 + trend_component * 0.2
            
            # Add uncertainty bounds (10% of prediction)
            uncertainty = abs(pred) * 0.15
            
            predictions.append({
                'yhat': max(0, pred),
                'yhat_lower': max(0, pred - uncertainty),
                'yhat_upper': max(0, pred + uncertainty)
            })
        
        result_df = future_df.copy()
        result_df['yhat'] = [p['yhat'] for p in predictions]
        result_df['yhat_lower'] = [p['yhat_lower'] for p in predictions]
        result_df['yhat_upper'] = [p['yhat_upper'] for p in predictions]
        
        return result_df
    
    def make_future_dataframe(self, periods, freq='H'):
        """Create future dataframe for prediction (Prophet-compatible)."""
        last_date = pd.to_datetime(self.last_date)
        future_dates = pd.date_range(start=last_date + timedelta(hours=1), 
                                      periods=periods, freq=freq)
        return pd.DataFrame({'ds': future_dates})

def load_labeled_data(file_path='pakistan_pm25_labeled.csv'):
    """Load the labeled AQI data."""
    df = pd.read_csv(file_path, parse_dates=['datetime'])
    return df

def prepare_time_series_data(df, city):
    """Prepare time series data for a specific city."""
    city_data = df[df['city'] == city].copy()
    city_data = city_data.sort_values('datetime')
    
    # Aggregate to hourly (in case of duplicates)
    city_data = city_data.groupby('datetime').agg({
        'pm25_value': 'mean',
        'aqi_value': 'mean'
    }).reset_index()
    
    # Create Prophet format: ds (datetime) and y (target)
    prophet_df = pd.DataFrame({
        'ds': city_data['datetime'],
        'y': city_data['pm25_value']
    })
    
    return prophet_df, city_data

def train_prophet_model(prophet_df, city):
    """Train forecasting model for a city (Prophet-compatible function name)."""
    model = SimpleForecastModel()
    model.fit(prophet_df)
    return model

def forecast_next_days(model, days=7):
    """Forecast next N days."""
    future = model.make_future_dataframe(periods=days*24, freq='H')
    forecast = model.predict(future)
    
    # Get only future predictions
    last_date = pd.to_datetime(model.last_date)
    forecast['ds_datetime'] = pd.to_datetime(forecast['ds'])
    forecast_future = forecast[forecast['ds_datetime'] > last_date].copy()
    forecast_future = forecast_future.drop('ds_datetime', axis=1)
    
    return forecast_future

def pm25_to_aqi_category(pm25):
    """Convert PM2.5 to AQI category."""
    if pd.isna(pm25) or pm25 < 0:
        return 'Unknown'
    elif pm25 <= 12.0:
        return 'Good'
    elif pm25 <= 35.4:
        return 'Moderate'
    elif pm25 <= 55.4:
        return 'Unhealthy for Sensitive Groups'
    elif pm25 <= 150.4:
        return 'Unhealthy'
    elif pm25 <= 250.4:
        return 'Very Unhealthy'
    else:
        return 'Hazardous'

def pm25_to_aqi_value(pm25):
    """Convert PM2.5 to AQI value."""
    if pd.isna(pm25) or pm25 < 0:
        return None
    
    breakpoints = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 500.4, 301, 500),
    ]
    
    for pm25_low, pm25_high, aqi_low, aqi_high in breakpoints:
        if pm25_low <= pm25 <= pm25_high:
            aqi = ((aqi_high - aqi_low) / (pm25_high - pm25_low)) * (pm25 - pm25_low) + aqi_low
            return round(aqi)
    
    if pm25 > 500.4:
        return 500
    return None

def train_all_city_models(df, output_dir='models'):
    """Train models for all cities."""
    os.makedirs(output_dir, exist_ok=True)
    
    cities = df['city'].unique()
    models = {}
    
    print("="*60)
    print("TRAINING FORECASTING MODELS (Simple Model)")
    print("="*60)
    
    for city in cities:
        print(f"\n📊 Training model for {city}...")
        try:
            prophet_df, _ = prepare_time_series_data(df, city)
            
            if len(prophet_df) < 48:  # Need at least 48 hours of data
                print(f"⚠️  {city}: Insufficient data (need at least 48 hours)")
                continue
            
            model = train_prophet_model(prophet_df, city)
            models[city] = model
            
            # Save model
            model_file = os.path.join(output_dir, f'{city.lower()}_model.pkl')
            with open(model_file, 'wb') as f:
                pickle.dump(model, f)
            
            print(f"✅ {city}: Model trained and saved")
            
        except Exception as e:
            print(f"❌ {city}: Error - {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"\n✅ Training complete! {len(models)} models saved to {output_dir}/")
    return models

def generate_forecasts(models, days=7):
    """Generate forecasts for all cities."""
    forecasts = {}
    
    for city, model in models.items():
        forecast_df = forecast_next_days(model, days=days)
        
        # Add AQI calculations
        forecast_df['pm25_predicted'] = forecast_df['yhat'].clip(lower=0)
        forecast_df['pm25_lower'] = forecast_df['yhat_lower'].clip(lower=0)
        forecast_df['pm25_upper'] = forecast_df['yhat_upper'].clip(lower=0)
        forecast_df['aqi_predicted'] = forecast_df['pm25_predicted'].apply(pm25_to_aqi_value)
        forecast_df['aqi_category'] = forecast_df['pm25_predicted'].apply(pm25_to_aqi_category)
        
        # Keep only relevant columns
        forecast_df = forecast_df[['ds', 'pm25_predicted', 'pm25_lower', 'pm25_upper', 
                                   'aqi_predicted', 'aqi_category']].copy()
        forecast_df.rename(columns={'ds': 'datetime'}, inplace=True)
        
        forecasts[city] = forecast_df
    
    return forecasts

if __name__ == "__main__":
    # Load data
    print("📂 Loading data...")
    df = load_labeled_data()
    print(f"✅ Loaded {len(df)} rows")
    
    # Train models
    models = train_all_city_models(df)
    
    # Generate sample forecasts
    print("\n🔮 Generating sample forecasts (7 days)...")
    forecasts = generate_forecasts(models, days=7)
    
    # Save forecasts to CSV
    forecasts_dir = 'forecasts'
    os.makedirs(forecasts_dir, exist_ok=True)
    
    for city, forecast_df in forecasts.items():
        forecast_file = os.path.join(forecasts_dir, f'{city.lower()}_forecast.csv')
        forecast_df.to_csv(forecast_file, index=False)
        print(f"📊 {city}: Forecast saved to {forecast_file}")
    
    print("\n✅ All forecasts generated!")