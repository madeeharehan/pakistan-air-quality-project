import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = 'http://localhost:5000/api';

const AQI_COLORS = {
  'Good': '#10b981',
  'Moderate': '#fbbf24',
  'Unhealthy for Sensitive Groups': '#f97316',
  'Unhealthy': '#ef4444',
  'Very Unhealthy': '#a855f7',
  'Hazardous': '#991b1b'
};

const AQI_GRADIENTS = {
  'Good': 'from-emerald-500 to-green-600',
  'Moderate': 'from-yellow-400 to-amber-500',
  'Unhealthy for Sensitive Groups': 'from-orange-400 to-orange-600',
  'Unhealthy': 'from-red-500 to-red-700',
  'Very Unhealthy': 'from-purple-500 to-purple-700',
  'Hazardous': 'from-red-900 to-red-950'
};

function App() {
  const [cities, setCities] = useState([]);
  const [selectedCity, setSelectedCity] = useState(null);
  const [currentAQI, setCurrentAQI] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [forecastError, setForecastError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchCities();
  }, []);

  const fetchCities = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/cities`);
      const data = await response.json();
      setCities(data.cities);
      if (data.cities.length > 0 && !selectedCity) {
        setSelectedCity(data.cities[0]);
      }
    } catch (error) {
      console.error('Error fetching cities:', error);
    }
  };

  const fetchCityData = async (city) => {
    if (!city) return;
    
    setLoading(true);
    setForecastError(null);
    setForecast(null);
    
    try {
      const currentRes = await fetch(`${API_BASE_URL}/current/${city}`);
      if (!currentRes.ok) {
        throw new Error(`Failed to fetch current AQI: ${currentRes.statusText}`);
      }
      const currentData = await currentRes.json();
      setCurrentAQI(currentData);

      const forecastRes = await fetch(`${API_BASE_URL}/forecast/${city}?days=7`);
      if (!forecastRes.ok) {
        const errorData = await forecastRes.json();
        setForecastError(errorData.error || 'Failed to load forecast');
      } else {
        const forecastData = await forecastRes.json();
        setForecast(forecastData);
        setForecastError(null);
      }
    } catch (error) {
      console.error('Error fetching city data:', error);
      setForecastError(error.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (selectedCity) {
      fetchCityData(selectedCity);
    }
  }, [selectedCity]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-lg border-b border-slate-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg">
                <span className="text-2xl">🌬️</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-slate-900">Pakistan Air Quality</h1>
                <p className="text-sm text-slate-600">Real-time monitoring & forecasts</p>
              </div>
            </div>
            
            {/* City Selector */}
            <div className="flex items-center gap-3 bg-white px-4 py-2.5 rounded-xl shadow-md border border-slate-200">
              <span className="text-xl">📍</span>
              <select 
                value={selectedCity || ''} 
                onChange={(e) => setSelectedCity(e.target.value)}
                className="bg-transparent border-none outline-none text-slate-900 font-medium text-base cursor-pointer"
              >
                {cities.map(city => (
                  <option key={city} value={city}>{city}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent"></div>
          </div>
        )}

        {/* Current AQI Card */}
        {currentAQI && !loading && (
          <div className="mb-8 animate-fadeIn">
            <div className={`relative overflow-hidden rounded-3xl shadow-2xl bg-gradient-to-br ${AQI_GRADIENTS[currentAQI.aqi_category] || 'from-slate-500 to-slate-700'} p-8 text-white`}>
              <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full -mr-32 -mt-32"></div>
              <div className="absolute bottom-0 left-0 w-48 h-48 bg-black/10 rounded-full -ml-24 -mb-24"></div>
              
              <div className="relative z-10">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xl">📍</span>
                      <h2 className="text-2xl font-bold">{currentAQI.city}</h2>
                    </div>
                    <p className="text-white/90 text-sm">
                      {new Date(currentAQI.datetime).toLocaleString('en-US', {
                        weekday: 'long',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
                  <div>
                    <div className="text-7xl font-bold mb-2">{Math.round(currentAQI.aqi_value)}</div>
                    <div className="text-2xl font-semibold mb-4">{currentAQI.aqi_category}</div>
                    <div className="inline-flex items-center gap-2 bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full">
                      <span className="text-lg">🌬️</span>
                      <span className="text-sm font-medium">Air Quality Index</span>
                    </div>
                  </div>

                  <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 border border-white/20">
                    <h3 className="text-lg font-semibold mb-4 text-white">Current Readings</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-white/90">PM2.5 Level</span>
                        <span className="text-xl font-bold text-white">{currentAQI.pm25_value.toFixed(1)} µg/m³</span>
                      </div>
                      <div className="h-px bg-white/20"></div>
                      <div className="flex justify-between items-center">
                        <span className="text-white/90">Status</span>
                        <span className="text-xl font-bold text-white">{currentAQI.aqi_category}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Forecast Section */}
        <div className="bg-white rounded-3xl shadow-xl p-8 border border-slate-200">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center">
              <span className="text-xl">📈</span>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-slate-900">7-Day Forecast</h2>
              <p className="text-sm text-slate-600">Predicted air quality trends</p>
            </div>
          </div>

          {forecastError && (
            <div className="bg-amber-50 border-l-4 border-amber-500 rounded-xl p-6 mb-6">
              <div className="flex items-start gap-3">
                <span className="text-2xl">⚠️</span>
                <div className="flex-1">
                  <p className="text-amber-900 font-medium mb-2">{forecastError}</p>
                  <p className="text-sm text-amber-800">
                    To enable forecasts, train the models by running: 
                    <code className="ml-2 bg-amber-100 px-2 py-1 rounded text-xs font-mono">
                      python train_forecast_model.py
                    </code>
                  </p>
                </div>
              </div>
            </div>
          )}

          {forecast && forecast.data && forecast.data.length > 0 ? (
            <>
              <div className="flex items-center gap-2 mb-6 text-slate-600">
                <span className="text-lg">📅</span>
                <p className="text-sm">
                  Showing {forecast.count} hourly predictions for the next {forecast.forecast_days} days
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {forecast.data
                  .filter((_, idx) => idx % 6 === 0)
                  .map((item, index) => (
                    <div 
                      key={index} 
                      className="group relative overflow-hidden bg-gradient-to-br from-slate-50 to-slate-100 rounded-2xl p-5 border-2 transition-all duration-300 hover:shadow-lg hover:scale-105"
                      style={{ 
                        borderColor: AQI_COLORS[item.aqi_category] || '#94a3b8'
                      }}
                    >
                      <div className="absolute top-0 right-0 w-20 h-20 rounded-full opacity-10 -mr-10 -mt-10"
                        style={{ backgroundColor: AQI_COLORS[item.aqi_category] }}
                      ></div>
                      
                      <div className="relative z-10">
                        <div className="text-xs font-medium text-slate-600 mb-3">
                          {new Date(item.datetime).toLocaleString('en-US', {
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </div>
                        
                        <div 
                          className="text-4xl font-bold mb-2"
                          style={{ color: AQI_COLORS[item.aqi_category] || '#475569' }}
                        >
                          {Math.round(item.aqi_predicted)}
                        </div>
                        
                        <div className="text-sm font-semibold text-slate-700 mb-3">
                          {item.aqi_category}
                        </div>
                        
                        <div className="flex items-center gap-1.5 text-xs text-slate-600">
                          <span className="text-sm">🌬️</span>
                          <span>PM2.5: {item.pm25_predicted.toFixed(1)} µg/m³</span>
                        </div>
                      </div>
                    </div>
                  ))}
              </div>
            </>
          ) : !forecastError && !loading && (
            <div className="bg-blue-50 border border-blue-200 rounded-2xl p-8 text-center">
              <span className="text-5xl inline-block mb-3">ℹ️</span>
              <p className="text-blue-900 font-medium">No forecast data available</p>
              <p className="text-sm text-blue-700 mt-1">Check back later for predictions</p>
            </div>
          )}
        </div>
      </main>

      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        .animate-fadeIn {
          animation: fadeIn 0.6s ease-out;
        }
      `}</style>
    </div>
  );
}

export default App;