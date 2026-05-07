import pandas as pd
import os

# Load raw data - updated for Bengaluru weather dataset
raw_data_path = os.path.join('data', 'raw', 'bengaluru_weather.csv')
df = pd.read_csv(raw_data_path)

# Map dataset columns to our format
df_processed = pd.DataFrame()
df_processed['date'] = pd.to_datetime(df['Date time'], format='%m/%d/%Y', errors='coerce')

# Convert Temperature from Fahrenheit to Celsius
df_processed['temperature'] = ((df['Temperature'].astype(float) - 32) * 5/9).round(2)

df_processed['rainfall'] = df['Precipitation'].fillna(0).astype(float)
df_processed['humidity'] = df['Relative Humidity'].astype(float)

# For AQI - estimate based on visibility and cloud cover (proxy for air quality)
# Lower visibility + high cloud cover = higher AQI (worse air quality)
df_processed['aqi'] = 50 + ((100 - df['Visibility'].fillna(6)) * 5) + (df['Cloud Cover'].fillna(50) / 2)
df_processed['aqi'] = df_processed['aqi'].clip(0, 500).astype(float)

# Remove any rows with missing critical values
df_processed = df_processed.dropna(subset=['date', 'temperature', 'humidity'])

# Handle remaining missing values with forward fill, then backward fill
df_processed = df_processed.ffill()
df_processed = df_processed.bfill()

# Sort by date
df_processed = df_processed.sort_values('date').reset_index(drop=True)

print(f"Loaded {len(df_processed)} records from Bengaluru weather dataset")
print(f"\nData Summary:")
print(df_processed.describe())

# Save processed data
processed_path = os.path.join('data', 'processed', 'processed_weather_data.csv')
df_processed.to_csv(processed_path, index=False)

print(f"\nData processed and saved to {processed_path}")