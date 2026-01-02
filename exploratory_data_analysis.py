import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load your cleaned data CSV file (update the path as needed)
df = pd.read_csv('pakistan_pm25_cleaned.csv', parse_dates=['datetime'])

# Basic info
print("Data summary:")
print(df.info())
print(df.describe())

# Convert datetime to local timezone if needed (optional)
# df['datetime'] = df['datetime'].dt.tz_convert('Asia/Karachi')

# Extract date and hour for analysis
df['date'] = df['datetime'].dt.date
df['hour'] = df['datetime'].dt.hour
df['month'] = df['datetime'].dt.month

# 1. Daily average PM2.5 per city
daily_avg = df.groupby(['date', 'city'])['pm25_value'].mean().reset_index()

plt.figure(figsize=(14,6))
sns.lineplot(data=daily_avg, x='date', y='pm25_value', hue='city')
plt.title('Daily Average PM2.5 by City')
plt.xlabel('Date')
plt.ylabel('PM2.5 (µg/m³)')
plt.legend(title='City')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 2. Monthly average PM2.5 per city
monthly_avg = df.groupby(['month', 'city'])['pm25_value'].mean().reset_index()

plt.figure(figsize=(10,5))
sns.barplot(data=monthly_avg, x='month', y='pm25_value', hue='city')
plt.title('Monthly Average PM2.5 by City')
plt.xlabel('Month')
plt.ylabel('PM2.5 (µg/m³)')
plt.legend(title='City')
plt.tight_layout()
plt.show()

# 3. Average PM2.5 by hour of day (peak pollution hours)
hourly_avg = df.groupby(['hour', 'city'])['pm25_value'].mean().reset_index()

plt.figure(figsize=(14,6))
sns.lineplot(data=hourly_avg, x='hour', y='pm25_value', hue='city')
plt.title('Average PM2.5 by Hour of Day')
plt.xlabel('Hour')
plt.ylabel('PM2.5 (µg/m³)')
plt.legend(title='City')
plt.tight_layout()
plt.show()

# 4. Clean vs Polluted Days (threshold example: 35 µg/m³)
daily_avg['pollution_level'] = daily_avg['pm25_value'].apply(lambda x: 'Clean' if x <= 35 else 'Polluted')

plt.figure(figsize=(10,5))
sns.countplot(data=daily_avg, x='pollution_level', hue='city')
plt.title('Count of Clean vs Polluted Days by City')
plt.xlabel('Pollution Level')
plt.ylabel('Number of Days')
plt.legend(title='City')
plt.tight_layout()
plt.show()
