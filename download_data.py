import openaq
import pandas as pd
from datetime import datetime, timezone
import time
import os

# Replace with your actual API key
API_KEY = "31489434b8c7b38d9a93a71ba92d2be5871b7493445254fd195865951d00cb2c"

client = openaq.OpenAQ(api_key=API_KEY)

# Target cities (case-insensitive match)
cities = ["Lahore", "Karachi", "Islamabad", "Peshawar", "Faisalabad"]

days_back = 90
end_date = datetime.now(timezone.utc)
start_date = end_date - pd.Timedelta(days=days_back)

output_folder = "pakistan_pm25_hourly"
os.makedirs(output_folder, exist_ok=True)

print(f"Fetching hourly PM2.5 data for Pakistan (last {days_back} days)...\n")

# 1. Fetch all locations in Pakistan that measure PM2.5
# Note: In V3, some arguments use singular/plural naming strictly
locations_resp = client.locations.list(
    countries_id=109,  # Pakistan country ID
    parameters_id=2,   # PM2.5 parameter ID
    limit=1000
)

locations = locations_resp.results
print(f"Found {len(locations)} potential locations in Pakistan.\n")

city_dfs = {}

for loc in locations:
    loc_id = loc.id
    loc_name = loc.name
    loc_city = getattr(loc, 'city', "") or getattr(loc, 'locality', "") or "Unknown"

    # Match to target city list
    matched_city = None
    for city in cities:
        if city.lower() in loc_city.lower() or city.lower() in loc_name.lower():
            matched_city = city
            break

    if not matched_city:
        continue

    # 2. Find the specific Sensor ID for PM2.5 at this location
    pm25_sensor = next((s for s in loc.sensors if s.parameter.name == 'pm25'), None)
    
    if not pm25_sensor:
        continue

    sensor_id = pm25_sensor.id
    print(f"Fetching data for {loc_name} (Sensor: {sensor_id})")

    # 3. Fetch measurements with pagination
    all_measurements = []
    page = 1
    
    try:
        while True:
            # FIXED: Changed date_from -> datetime_from and date_to -> datetime_to
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
                all_measurements.append({
                    'city': matched_city,
                    'location': loc_name,
                    'datetime': m.period.datetime_from.utc,
                    'pm25': m.value,
                    'unit': m.parameter.unit if hasattr(m.parameter, 'unit') else "µg/m³"
                })
            
            if len(all_measurements) >= 20000 or len(results) < 1000:
                break
                
            page += 1
            time.sleep(0.2)

        if all_measurements:
            df = pd.DataFrame(all_measurements)
            df = df.drop_duplicates(subset=['datetime', 'location'])
            
            if matched_city in city_dfs:
                city_dfs[matched_city] = pd.concat([city_dfs[matched_city], df])
            else:
                city_dfs[matched_city] = df
            print(f"  → Collected {len(df)} records")

    except Exception as e:
        print(f"  Error fetching {loc_name}: {e}")
    
    time.sleep(0.5)

# 4. Save to CSV
if city_dfs:
    all_dfs = []
    for city, df in city_dfs.items():
        df = df.sort_values('datetime').reset_index(drop=True)
        filename = os.path.join(output_folder, f"{city.lower()}_hourly_pm25.csv")
        df.to_csv(filename, index=False)
        all_dfs.append(df)

    combined = pd.concat(all_dfs, ignore_index=True)
    combined.to_csv(os.path.join(output_folder, "pakistan_all_cities_hourly_pm25.csv"), index=False)
    print(f"\nSuccess! Total records saved: {len(combined):,}")
else:
    print("\nNo data was collected. Please check if sensors have been active in the last 90 days.")

client.close()