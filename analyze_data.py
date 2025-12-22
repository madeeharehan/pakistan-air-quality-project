import pandas as pd
import os

def get_aqi_label(pm25):
    """Returns the health category based on PM2.5 concentration (µg/m³)."""
    if pm25 <= 9.0:
        return 'Good'
    elif pm25 <= 35.4:
        return 'Moderate'
    elif pm25 <= 55.4:
        return 'Unhealthy for Sensitive Groups'
    elif pm25 <= 125.4:
        return 'Unhealthy'
    elif pm25 <= 225.4:
        return 'Very Unhealthy'
    else:
        return 'Hazardous'

# Load the file you just created
input_file = "pakistan_pm25_hourly/pakistan_all_cities_hourly_pm25.csv"
output_file = "pakistan_pm25_hourly/pakistan_analyzed_pm25.csv"

if os.path.exists(input_file):
    df = pd.read_csv(input_file)
    
    # Apply the labeling
    df['health_category'] = df['pm25'].apply(get_aqi_label)
    
    # Save the updated file
    df.to_csv(output_file, index=False)
    print(f"Success! Analyzed data saved to: {output_file}")
    
    # Show a quick summary
    print("\n--- Health Summary by City ---")
    summary = df.groupby(['city', 'health_category']).size().unstack(fill_value=0)
    print(summary)
else:
    print("Source file not found. Please run the download script first.")