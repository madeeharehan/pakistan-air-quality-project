import pandas as pd
import os

def pm25_to_aqi_label(pm25):
    """
    Convert PM2.5 concentration (µg/m³) to AQI health category.
    Based on US EPA Air Quality Index standards for PM2.5.
    
    Args:
        pm25: PM2.5 concentration in µg/m³
        
    Returns:
        str: AQI category label
    """
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
    """
    Convert PM2.5 concentration (µg/m³) to AQI numeric value.
    Based on US EPA formula.
    
    Args:
        pm25: PM2.5 concentration in µg/m³
        
    Returns:
        float: AQI value (0-500+)
    """
    if pd.isna(pm25) or pm25 < 0:
        return None
    
    # AQI breakpoints for PM2.5 (24-hour average)
    # Format: (PM2.5_low, PM2.5_high, AQI_low, AQI_high)
    breakpoints = [
        (0.0, 12.0, 0, 50),          # Good
        (12.1, 35.4, 51, 100),       # Moderate
        (35.5, 55.4, 101, 150),      # Unhealthy for Sensitive Groups
        (55.5, 150.4, 151, 200),     # Unhealthy
        (150.5, 250.4, 201, 300),    # Very Unhealthy
        (250.5, 500.4, 301, 500),    # Hazardous
    ]
    
    for pm25_low, pm25_high, aqi_low, aqi_high in breakpoints:
        if pm25_low <= pm25 <= pm25_high:
            aqi = ((aqi_high - aqi_low) / (pm25_high - pm25_low)) * (pm25 - pm25_low) + aqi_low
            return round(aqi)
    
    # For values above 500.4, extrapolate or cap at 500+
    if pm25 > 500.4:
        return 500
    
    return None

def label_aqi_data(input_file, output_file=None, pm25_column='pm25_value'):
    """
    Add AQI labels and values to a dataset with PM2.5 measurements.
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file (optional, defaults to input_file with '_labeled' suffix)
        pm25_column: Name of the PM2.5 column in the dataset
        
    Returns:
        pd.DataFrame: DataFrame with AQI labels and values added
    """
    # Load the data
    if not os.path.exists(input_file):
        print(f"❌ Error: File '{input_file}' not found.")
        return None
    
    print(f"📂 Loading data from: {input_file}")
    df = pd.read_csv(input_file)
    
    # Check if PM2.5 column exists
    if pm25_column not in df.columns:
        print(f"❌ Error: Column '{pm25_column}' not found in the dataset.")
        print(f"Available columns: {list(df.columns)}")
        return None
    
    print(f"✅ Loaded {len(df)} rows")
    
    # Convert PM2.5 to numeric if needed
    df[pm25_column] = pd.to_numeric(df[pm25_column], errors='coerce')
    
    # Add AQI labels
    print("🏷️  Adding AQI labels...")
    df['aqi_category'] = df[pm25_column].apply(pm25_to_aqi_label)
    
    # Add AQI numeric values
    print("🔢 Calculating AQI values...")
    df['aqi_value'] = df[pm25_column].apply(pm25_to_aqi_value)
    
    # Save the labeled data
    if output_file is None:
        base_name = os.path.splitext(input_file)[0]
        output_file = f"{base_name}_labeled.csv"
    
    df.to_csv(output_file, index=False)
    print(f"✅ Labeled data saved to: {output_file}")
    
    # Print summary statistics
    print("\n" + "="*60)
    print("AQI CATEGORY SUMMARY")
    print("="*60)
    category_counts = df['aqi_category'].value_counts().sort_index()
    for category, count in category_counts.items():
        percentage = (count / len(df)) * 100
        print(f"{category:35s}: {count:6d} ({percentage:5.1f}%)")
    
    # Summary by city if city column exists
    if 'city' in df.columns:
        print("\n" + "="*60)
        print("AQI CATEGORY SUMMARY BY CITY")
        print("="*60)
        city_summary = df.groupby(['city', 'aqi_category']).size().unstack(fill_value=0)
        print(city_summary.to_string())
        
        print("\n" + "="*60)
        print("AVERAGE AQI VALUES BY CITY")
        print("="*60)
        city_avg = df.groupby('city').agg({
            'aqi_value': 'mean',
            pm25_column: 'mean'
        }).round(2)
        city_avg.columns = ['Avg AQI', 'Avg PM2.5 (µg/m³)']
        print(city_avg.to_string())
    
    return df

if __name__ == "__main__":
    # Default input file (adjust as needed)
    INPUT_FILE = "pakistan_pm25_cleaned.csv"
    OUTPUT_FILE = "pakistan_pm25_labeled.csv"
    
    # Label the data
    labeled_df = label_aqi_data(INPUT_FILE, OUTPUT_FILE)
    
    if labeled_df is not None:
        print("\n✅ AQI labeling completed successfully!")
    else:
        print("\n❌ AQI labeling failed. Please check the error messages above.")