import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import os

# Set style
sns.set_theme(style="whitegrid")
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 300

# AQI Category colors (standard EPA colors)
AQI_COLORS = {
    'Good': '#00E400',                    # Green
    'Moderate': '#FFFF00',                # Yellow
    'Unhealthy for Sensitive Groups': '#FF7E00',  # Orange
    'Unhealthy': '#FF0000',               # Red
    'Very Unhealthy': '#8F3F97',          # Purple
    'Hazardous': '#7E0023',               # Maroon
    'Unknown': '#808080'                  # Gray
}

# Category order for consistent plotting
CATEGORY_ORDER = [
    'Good',
    'Moderate', 
    'Unhealthy for Sensitive Groups',
    'Unhealthy',
    'Very Unhealthy',
    'Hazardous'
]

def load_labeled_data(file_path='pakistan_pm25_labeled.csv'):
    """Load the labeled AQI data."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' not found. Please run label_aqi.py first.")
    
    df = pd.read_csv(file_path, parse_dates=['datetime'])
    print(f"✅ Loaded {len(df)} rows from {file_path}")
    return df

def plot_aqi_timeseries_by_category(df, city=None, output_dir='visualizations'):
    """
    Plot time series of AQI values colored by category.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    plot_df = df.copy()
    if city:
        plot_df = plot_df[plot_df['city'] == city]
        title_city = f" - {city}"
        filename_city = f"_{city.lower()}"
    else:
        title_city = " - All Cities"
        filename_city = "_all_cities"
    
    # Sort by datetime
    plot_df = plot_df.sort_values('datetime')
    
    fig, axes = plt.subplots(2, 1, figsize=(16, 10))
    
    # Plot 1: Scatter plot colored by category
    ax1 = axes[0]
    for category in CATEGORY_ORDER:
        if category in plot_df['aqi_category'].values:
            category_data = plot_df[plot_df['aqi_category'] == category]
            ax1.scatter(
                category_data['datetime'], 
                category_data['aqi_value'],
                c=AQI_COLORS.get(category, '#808080'),
                label=category,
                alpha=0.6,
                s=20
            )
    
    ax1.set_xlabel('Date', fontsize=12)
    ax1.set_ylabel('AQI Value', fontsize=12)
    ax1.set_title(f'AQI Time Series by Category{title_city}', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper left', fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # Add category threshold lines
    ax1.axhline(50, color='green', linestyle='--', alpha=0.3, linewidth=1)
    ax1.axhline(100, color='yellow', linestyle='--', alpha=0.3, linewidth=1)
    ax1.axhline(150, color='orange', linestyle='--', alpha=0.3, linewidth=1)
    ax1.axhline(200, color='red', linestyle='--', alpha=0.3, linewidth=1)
    ax1.axhline(300, color='purple', linestyle='--', alpha=0.3, linewidth=1)
    
    # Plot 2: Line plot by city (if multiple cities)
    if not city and 'city' in plot_df.columns:
        ax2 = axes[1]
        for city_name in plot_df['city'].unique():
            city_data = plot_df[plot_df['city'] == city_name].sort_values('datetime')
            ax2.plot(city_data['datetime'], city_data['aqi_value'], 
                    label=city_name, alpha=0.7, linewidth=1.5)
        
        ax2.set_xlabel('Date', fontsize=12)
        ax2.set_ylabel('AQI Value', fontsize=12)
        ax2.set_title(f'AQI Trends by City', fontsize=14, fontweight='bold')
        ax2.legend(loc='upper left', fontsize=9)
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_file = os.path.join(output_dir, f'aqi_timeseries{filename_city}.png')
    plt.savefig(output_file, bbox_inches='tight')
    print(f"📊 Saved: {output_file}")
    plt.close()

def plot_aqi_distribution_by_city(df, output_dir='visualizations'):
    """Plot distribution of AQI categories by city."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Prepare data
    category_counts = df.groupby(['city', 'aqi_category']).size().unstack(fill_value=0)
    category_counts = category_counts.reindex(columns=[c for c in CATEGORY_ORDER if c in category_counts.columns], fill_value=0)
    
    # Calculate percentages
    category_pct = category_counts.div(category_counts.sum(axis=1), axis=0) * 100
    
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    # Plot 1: Stacked bar chart (counts)
    ax1 = axes[0]
    category_counts.plot(kind='bar', stacked=True, ax=ax1, 
                        color=[AQI_COLORS.get(c, '#808080') for c in category_counts.columns],
                        edgecolor='white', linewidth=0.5)
    ax1.set_xlabel('City', fontsize=12)
    ax1.set_ylabel('Count', fontsize=12)
    ax1.set_title('AQI Category Distribution by City (Counts)', fontsize=14, fontweight='bold')
    ax1.legend(title='AQI Category', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45, ha='right')
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Plot 2: Stacked bar chart (percentages)
    ax2 = axes[1]
    category_pct.plot(kind='bar', stacked=True, ax=ax2,
                     color=[AQI_COLORS.get(c, '#808080') for c in category_pct.columns],
                     edgecolor='white', linewidth=0.5)
    ax2.set_xlabel('City', fontsize=12)
    ax2.set_ylabel('Percentage (%)', fontsize=12)
    ax2.set_title('AQI Category Distribution by City (Percentages)', fontsize=14, fontweight='bold')
    ax2.legend(title='AQI Category', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')
    ax2.set_ylim(0, 100)
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    output_file = os.path.join(output_dir, 'aqi_distribution_by_city.png')
    plt.savefig(output_file, bbox_inches='tight')
    print(f"📊 Saved: {output_file}")
    plt.close()

def plot_aqi_heatmap_by_hour(df, output_dir='visualizations'):
    """Create heatmap showing AQI patterns by hour of day and city."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract hour
    df['hour'] = df['datetime'].dt.hour
    
    # Create pivot table: average AQI by city and hour
    pivot_data = df.pivot_table(values='aqi_value', index='city', columns='hour', aggfunc='mean')
    
    fig, ax = plt.subplots(figsize=(14, 6))
    sns.heatmap(pivot_data, annot=True, fmt='.0f', cmap='RdYlGn_r', 
                cbar_kws={'label': 'Average AQI'}, ax=ax, linewidths=0.5)
    ax.set_title('Average AQI by City and Hour of Day', fontsize=14, fontweight='bold')
    ax.set_xlabel('Hour of Day', fontsize=12)
    ax.set_ylabel('City', fontsize=12)
    
    plt.tight_layout()
    output_file = os.path.join(output_dir, 'aqi_heatmap_by_hour.png')
    plt.savefig(output_file, bbox_inches='tight')
    print(f"📊 Saved: {output_file}")
    plt.close()

def plot_aqi_category_heatmap(df, output_dir='visualizations'):
    """Create heatmap showing percentage of time in each AQI category by city."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Calculate percentage of time in each category for each city
    category_pct = df.groupby(['city', 'aqi_category']).size().unstack(fill_value=0)
    category_pct = category_pct.reindex(columns=[c for c in CATEGORY_ORDER if c in category_pct.columns], fill_value=0)
    category_pct_pct = category_pct.div(category_pct.sum(axis=1), axis=0) * 100
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Create custom colormap based on AQI categories
    sns.heatmap(category_pct_pct, annot=True, fmt='.1f', cmap='YlOrRd',
                cbar_kws={'label': 'Percentage of Time (%)'}, ax=ax, linewidths=0.5)
    ax.set_title('Percentage of Time in Each AQI Category by City', fontsize=14, fontweight='bold')
    ax.set_xlabel('AQI Category', fontsize=12)
    ax.set_ylabel('City', fontsize=12)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    output_file = os.path.join(output_dir, 'aqi_category_heatmap.png')
    plt.savefig(output_file, bbox_inches='tight')
    print(f"📊 Saved: {output_file}")
    plt.close()

def plot_aqi_summary_statistics(df, output_dir='visualizations'):
    """Create summary statistics visualization."""
    os.makedirs(output_dir, exist_ok=True)
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Average AQI by city
    ax1 = axes[0, 0]
    city_avg = df.groupby('city')['aqi_value'].mean().sort_values(ascending=False)
    bars = ax1.barh(city_avg.index, city_avg.values, 
                    color=['#FF0000' if x > 150 else '#FF7E00' if x > 100 else '#FFFF00' if x > 50 else '#00E400' 
                           for x in city_avg.values])
    ax1.set_xlabel('Average AQI', fontsize=12)
    ax1.set_title('Average AQI by City', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='x')
    # Add value labels
    for i, (city, value) in enumerate(city_avg.items()):
        ax1.text(value, i, f' {value:.0f}', va='center', fontweight='bold')
    
    # 2. Worst AQI values by city
    ax2 = axes[0, 1]
    city_max = df.groupby('city')['aqi_value'].max().sort_values(ascending=False)
    bars = ax2.barh(city_max.index, city_max.values,
                    color=['#7E0023' if x > 300 else '#8F3F97' if x > 200 else '#FF0000' 
                           for x in city_max.values])
    ax2.set_xlabel('Maximum AQI', fontsize=12)
    ax2.set_title('Worst AQI Recorded by City', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='x')
    for i, (city, value) in enumerate(city_max.items()):
        ax2.text(value, i, f' {value:.0f}', va='center', fontweight='bold')
    
    # 3. Category counts (overall)
    ax3 = axes[1, 0]
    category_counts = df['aqi_category'].value_counts()
    category_counts = category_counts.reindex([c for c in CATEGORY_ORDER if c in category_counts.index])
    colors = [AQI_COLORS.get(c, '#808080') for c in category_counts.index]
    bars = ax3.bar(range(len(category_counts)), category_counts.values, color=colors)
    ax3.set_xticks(range(len(category_counts)))
    ax3.set_xticklabels(category_counts.index, rotation=45, ha='right')
    ax3.set_ylabel('Count', fontsize=12)
    ax3.set_title('Overall AQI Category Distribution', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    # 4. Days with unhealthy air (AQI > 100) by city
    ax4 = axes[1, 1]
    df['date'] = df['datetime'].dt.date
    unhealthy_days = df[df['aqi_value'] > 100].groupby(['city', 'date']).size().reset_index()
    unhealthy_days_count = unhealthy_days.groupby('city').size().sort_values(ascending=False)
    bars = ax4.barh(unhealthy_days_count.index, unhealthy_days_count.values, color='#FF0000')
    ax4.set_xlabel('Number of Days with Unhealthy Air (AQI > 100)', fontsize=12)
    ax4.set_title('Days with Unhealthy Air by City', fontsize=13, fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='x')
    for i, (city, value) in enumerate(unhealthy_days_count.items()):
        ax4.text(value, i, f' {value}', va='center', fontweight='bold')
    
    plt.tight_layout()
    output_file = os.path.join(output_dir, 'aqi_summary_statistics.png')
    plt.savefig(output_file, bbox_inches='tight')
    print(f"📊 Saved: {output_file}")
    plt.close()

def main():
    """Main function to generate all visualizations."""
    print("="*60)
    print("AQI VISUALIZATION GENERATOR")
    print("="*60)
    
    # Load data
    df = load_labeled_data()
    
    # Create output directory
    output_dir = 'visualizations'
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n📊 Generating visualizations...\n")
    
    # Generate all visualizations
    plot_aqi_timeseries_by_category(df, output_dir=output_dir)
    plot_aqi_timeseries_by_category(df, city='Lahore', output_dir=output_dir)
    plot_aqi_timeseries_by_category(df, city='Karachi', output_dir=output_dir)
    plot_aqi_distribution_by_city(df, output_dir=output_dir)
    plot_aqi_heatmap_by_hour(df, output_dir=output_dir)
    plot_aqi_category_heatmap(df, output_dir=output_dir)
    plot_aqi_summary_statistics(df, output_dir=output_dir)
    
    print("\n" + "="*60)
    print("✅ All visualizations generated successfully!")
    print(f"📁 Output directory: {output_dir}/")
    print("="*60)

if __name__ == "__main__":
    main()