import openaq
import pandas as pd
from datetime import datetime, timezone
import time
import os

# API Configuration
API_KEY = "31489434b8c7b38d9a93a71ba92d2be5871b7493445254fd195865951d00cb2c"
client = openaq.OpenAQ(api_key=API_KEY)

# Target cities in Pakistan
CITIES = ["Lahore", "Karachi", "Islamabad", "Peshawar", "Faisalabad", "Multan", "Rawalpindi", "Quetta"]

# Air quality parameters to fetch (parameter IDs from OpenAQ)
# Common parameters: PM2.5=2, PM10=1, O3=3, NO2=4, SO2=5, CO=6
PARAMETERS = {
    'pm25': 2,
    'pm10': 1,
    'o3': 3,
    'no2': 4,
    'so2': 5,
    'co': 6
}

# Time range configuration
DAYS_BACK = 90
OUTPUT_FOLDER = "hourly_data"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def fetch_hourly_data_for_city(city_name, days_back=DAYS_BACK):
    """
    Fetch hourly air quality data for a specific city in Pakistan.
    Returns a DataFrame with hourly aggregated data.
    """
    print(f"\n{'='*60}")
    print(f"Fetching hourly data for {city_name}")
    print(f"{'='*60}")
    
    end_date = datetime.now(timezone.utc)
    start_date = end_date - pd.Timedelta(days=days_back)
    
    all_data = []
    
    # Fetch locations for each parameter
    for param_name, param_id in PARAMETERS.items():
        print(f"\n  → Fetching {param_name.upper()} data...")
        
        try:
            # Get all locations in Pakistan for this parameter
            locations_resp = client.locations.list(
                countries_id=109,  # Pakistan country ID
                parameters_id=param_id,
                limit=1000
            )
            
            locations = locations_resp.results
            print(f"    Found {len(locations)} locations with {param_name.upper()} sensors")
            
            for loc in locations:
                loc_name = loc.name
                loc_city = getattr(loc, 'city', "") or getattr(loc, 'locality', "") or "Unknown"
                
                # Match to target city
                if city_name.lower() not in loc_city.lower() and city_name.lower() not in loc_name.lower():
                    continue
                
                # Find sensor for this parameter
                sensor = next((s for s in loc.sensors if s.parameter.name == param_name), None)
                if not sensor:
                    continue
                
                sensor_id = sensor.id
                print(f"    Processing: {loc_name} (Sensor: {sensor_id})")
                
                # Fetch measurements with pagination
                page = 1
                measurements = []
                
                while True:
                    try:
                        meas_resp = client.measurements.list(
                            sensors_id=sensor_id,
                            datetime_from=start_date,
                            datetime_to=end_date,
                            limit=1000,
                            page=page
                        )
                        
                        results = meas_resp.results
                        if not results:
                            break
                        
                        for m in results:
                            measurements.append({
                                'datetime': m.period.datetime_from.utc,
                                'value': m.value,
                                'location': loc_name,
                                'parameter': param_name,
                                'unit': m.parameter.unit if hasattr(m.parameter, 'unit') else "µg/m³"
                            })
                        
                        if len(results) < 1000:
                            break
                        
                        page += 1
                        time.sleep(0.2)  # Rate limiting
                        
                    except Exception as e:
                        print(f"      Error fetching page {page}: {e}")
                        break
                
                if measurements:
                    all_data.extend(measurements)
                    print(f"      Collected {len(measurements)} {param_name.upper()} records")
                
                time.sleep(0.3)  # Rate limiting between locations
                
        except Exception as e:
            print(f"    Error fetching {param_name.upper()} data: {e}")
            continue
    
    if not all_data:
        print(f"\n  ⚠ No data found for {city_name}")
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['datetime', 'location', 'parameter'])
    
    # Aggregate by hour (take mean of values within the same hour)
    df['datetime_hour'] = df['datetime'].dt.floor('H')
    
    # Create pivot table: datetime_hour x parameter
    hourly_data = []
    
    for hour in df['datetime_hour'].unique():
        hour_data = {'datetime': hour, 'city': city_name}
        
        for param in df['parameter'].unique():
            param_data = df[(df['datetime_hour'] == hour) & (df['parameter'] == param)]
            if not param_data.empty:
                hour_data[f'{param}_value'] = param_data['value'].mean()
                hour_data[f'{param}_unit'] = param_data['unit'].iloc[0]
                hour_data[f'{param}_locations'] = param_data['location'].nunique()
        
        hourly_data.append(hour_data)
    
    hourly_df = pd.DataFrame(hourly_data)
    
    if not hourly_df.empty:
        # Sort by datetime
        hourly_df = hourly_df.sort_values('datetime').reset_index(drop=True)
        
        # Reorder columns: datetime, city, then parameters
        cols = ['datetime', 'city'] + [c for c in hourly_df.columns if c not in ['datetime', 'city']]
        hourly_df = hourly_df[cols]
        
        print(f"\n  ✓ Successfully aggregated {len(hourly_df)} hourly records for {city_name}")
        print(f"    Date range: {hourly_df['datetime'].min()} to {hourly_df['datetime'].max()}")
        
        return hourly_df
    else:
        print(f"\n  ⚠ No hourly data could be aggregated for {city_name}")
        return None


def main():
    """Main function to fetch hourly data for all cities and save to CSV files."""
    print(f"\n{'='*60}")
    print("PAKISTAN AIR QUALITY - HOURLY DATA COLLECTOR")
    print(f"{'='*60}")
    print(f"Fetching data for last {DAYS_BACK} days")
    print(f"Target cities: {', '.join(CITIES)}")
    print(f"Output folder: {OUTPUT_FOLDER}\n")
    
    all_cities_data = []
    
    # Fetch data for each city
    for city in CITIES:
        city_df = fetch_hourly_data_for_city(city, DAYS_BACK)
        
        if city_df is not None and not city_df.empty:
            # Save individual city CSV
            filename = os.path.join(OUTPUT_FOLDER, f"{city.lower()}_hourly.csv")
            city_df.to_csv(filename, index=False)
            print(f"  💾 Saved: {filename}")
            
            all_cities_data.append(city_df)
        
        time.sleep(1)  # Rate limiting between cities
    
    # Save combined file
    if all_cities_data:
        combined_df = pd.concat(all_cities_data, ignore_index=True)
        combined_filename = os.path.join(OUTPUT_FOLDER, "pakistan_all_cities_hourly.csv")
        combined_df.to_csv(combined_filename, index=False)
        
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        print(f"Total cities processed: {len(all_cities_data)}")
        print(f"Total hourly records: {len(combined_df):,}")
        print(f"Date range: {combined_df['datetime'].min()} to {combined_df['datetime'].max()}")
        print(f"\nIndividual city files saved in: {OUTPUT_FOLDER}/")
        print(f"Combined file saved: {combined_filename}")
        print(f"\n✓ Data collection completed successfully!")
    else:
        print(f"\n⚠ No data was collected for any city.")
    
    client.close()


if __name__ == "__main__":
    main()


