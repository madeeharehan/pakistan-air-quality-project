import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# 1. Load the analyzed data
file_path = "pakistan_pm25_hourly/pakistan_analyzed_pm25.csv"
if not os.path.exists(file_path):
    print("Error: Analyzed data file not found. Run analyze_data.py first!")
    exit()

df = pd.read_csv(file_path)
df['datetime'] = pd.to_datetime(df['datetime'])

# 2. Prepare data for a 'Weekly Profile'
# We extract the 'Hour of Day' to see the rush hour effect
df['hour'] = df['datetime'].dt.hour

# 3. Create the Visualization
plt.figure(figsize=(14, 7))
sns.set_theme(style="whitegrid")

# Create a line plot showing the average PM2.5 for each hour of the day
sns.lineplot(data=df, x='hour', y='pm25', hue='city', linewidth=2.5, marker='o')

# Add a 'Danger Zone' threshold (WHO 24h limit is 15, but let's mark 55 for 'Unhealthy')
plt.axhline(55, ls='--', color='red', alpha=0.6, label='Unhealthy Threshold (55 µg/m³)')

# Formatting the chart
plt.title("Hourly Air Quality Profile: Major Cities in Pakistan", fontsize=16, fontweight='bold')
plt.xlabel("Hour of Day (24h Format)", fontsize=12)
plt.ylabel("Average PM2.5 Concentration (µg/m³)", fontsize=12)
plt.xticks(range(0, 24))
plt.legend(title="City", loc='upper left')

# 4. Save and Show
output_img = "pakistan_pm25_hourly/hourly_trends_comparison.png"
plt.savefig(output_img)
print(f"Graph saved as: {output_img}")
plt.show()