from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import pickle
import os
from datetime import datetime, timedelta
import numpy as np

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Import forecasting functions AND the model class
from train_forecast_model import (
    load_labeled_data, 
    prepare_time_series_data,
    train_prophet_model,
    forecast_next_days,
    pm25_to_aqi_category,
    pm25_to_aqi_value,
    SimpleForecastModel  # Import the class so pickle can load it
)

MODELS_DIR = 'models'
DATA_FILE = 'pakistan_pm25_labeled.csv'

# Load data once at startup
try:
    df = load_labeled_data(DATA_FILE)
    print("✅ Data loaded successfully")
except Exception as e:
    print(f"❌ Error loading data: {e}")
    df = None

def load_model(city):
    """Load saved model for a city."""
    model_file = os.path.join(MODELS_DIR, f'{city.lower()}_model.pkl')
    if os.path.exists(model_file):
        with open(model_file, 'rb') as f:
            return pickle.load(f)
    return None

@app.route('/api/cities', methods=['GET'])
def get_cities():
    """Get list of available cities."""
    if df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    cities = sorted(df['city'].unique().tolist())
    return jsonify({'cities': cities})

@app.route('/api/current/<city>', methods=['GET'])
def get_current_aqi(city):
    """Get current AQI for a city (latest reading)."""
    if df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    city_data = df[df['city'] == city].copy()
    if city_data.empty:
        return jsonify({'error': f'No data for {city}'}), 404
    
    latest = city_data.sort_values('datetime').iloc[-1]
    
    return jsonify({
        'city': city,
        'datetime': str(latest['datetime']),
        'pm25_value': float(latest['pm25_value']),
        'aqi_value': float(latest['aqi_value']),
        'aqi_category': latest['aqi_category']
    })

@app.route('/api/history/<city>', methods=['GET'])
def get_history(city):
    """Get historical AQI data for a city."""
    if df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    city_data = df[df['city'] == city].copy()
    if city_data.empty:
        return jsonify({'error': f'No data for {city}'}), 404
    
    # Get optional parameters
    hours = request.args.get('hours', default=168, type=int)  # Default 7 days
    limit = request.args.get('limit', default=1000, type=int)
    
    # Filter by time
    latest_date = city_data['datetime'].max()
    start_date = latest_date - timedelta(hours=hours)
    city_data = city_data[city_data['datetime'] >= start_date]
    
    # Sort and limit
    city_data = city_data.sort_values('datetime').tail(limit)
    
    # Convert to list of dicts
    history = city_data[['datetime', 'pm25_value', 'aqi_value', 'aqi_category']].to_dict('records')
    
    # Convert datetime to string and numpy types to native Python types
    for record in history:
        record['datetime'] = str(record['datetime'])
        record['pm25_value'] = float(record['pm25_value'])
        record['aqi_value'] = float(record['aqi_value'])
    
    return jsonify({
        'city': city,
        'count': len(history),
        'data': history
    })

@app.route('/api/forecast/<city>', methods=['GET'])
def get_forecast(city):
    """Get forecast for a city."""
    model = load_model(city)
    if model is None:
        return jsonify({'error': f'No model found for {city}. Please train models first.'}), 404
    
    # Get forecast days (default 7)
    days = request.args.get('days', default=7, type=int)
    
    try:
        forecast_df = forecast_next_days(model, days=days)
        
        # Add AQI calculations
        forecast_df['pm25_predicted'] = forecast_df['yhat'].clip(lower=0)
        forecast_df['pm25_lower'] = forecast_df['yhat_lower'].clip(lower=0)
        forecast_df['pm25_upper'] = forecast_df['yhat_upper'].clip(lower=0)
        forecast_df['aqi_predicted'] = forecast_df['pm25_predicted'].apply(pm25_to_aqi_value)
        forecast_df['aqi_category'] = forecast_df['pm25_predicted'].apply(pm25_to_aqi_category)
        
        # Prepare response
        forecast_list = []
        for _, row in forecast_df.iterrows():
            forecast_list.append({
                'datetime': str(row['ds']),
                'pm25_predicted': float(row['pm25_predicted']),
                'pm25_lower': float(row['pm25_lower']),
                'pm25_upper': float(row['pm25_upper']),
                'aqi_predicted': float(row['aqi_predicted']) if pd.notna(row['aqi_predicted']) else None,
                'aqi_category': row['aqi_category']
            })
        
        return jsonify({
            'city': city,
            'forecast_days': days,
            'count': len(forecast_list),
            'data': forecast_list
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats/<city>', methods=['GET'])
def get_stats(city):
    """Get statistics for a city."""
    if df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    city_data = df[df['city'] == city].copy()
    if city_data.empty:
        return jsonify({'error': f'No data for {city}'}), 404
    
    stats = {
        'city': city,
        'avg_aqi': float(city_data['aqi_value'].mean()),
        'max_aqi': float(city_data['aqi_value'].max()),
        'min_aqi': float(city_data['aqi_value'].min()),
        'avg_pm25': float(city_data['pm25_value'].mean()),
        'max_pm25': float(city_data['pm25_value'].max()),
        'min_pm25': float(city_data['pm25_value'].min()),
        'total_readings': int(len(city_data)),
        'category_distribution': city_data['aqi_category'].value_counts().to_dict()
    }
    
    return jsonify(stats)

@app.route('/api/all-current', methods=['GET'])
def get_all_current():
    """Get current AQI for all cities."""
    if df is None:
        return jsonify({'error': 'Data not loaded'}), 500
    
    cities = df['city'].unique()
    results = []
    
    for city in cities:
        city_data = df[df['city'] == city].copy()
        latest = city_data.sort_values('datetime').iloc[-1]
        results.append({
            'city': city,
            'datetime': str(latest['datetime']),
            'pm25_value': float(latest['pm25_value']),
            'aqi_value': float(latest['aqi_value']),
            'aqi_category': latest['aqi_category']
        })
    
    return jsonify({'cities': results})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    model_count = 0
    if os.path.exists(MODELS_DIR):
        model_count = len([f for f in os.listdir(MODELS_DIR) if f.endswith('.pkl')])
    
    return jsonify({
        'status': 'healthy',
        'data_loaded': df is not None,
        'models_available': model_count
    })

if __name__ == '__main__':
    # Ensure models directory exists
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    print("🚀 Starting Air Quality API Server...")
    print("📡 API will be available at http://localhost:5000")
    print("📚 API Endpoints:")
    print("   GET /api/cities - List all cities")
    print("   GET /api/current/<city> - Current AQI for a city")
    print("   GET /api/history/<city>?hours=168&limit=1000 - Historical data")
    print("   GET /api/forecast/<city>?days=7 - Forecast for a city")
    print("   GET /api/stats/<city> - Statistics for a city")
    print("   GET /api/all-current - Current AQI for all cities")
    print("   GET /api/health - Health check")
    
    app.run(debug=True, host='0.0.0.0', port=5000)