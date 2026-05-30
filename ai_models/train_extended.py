import pandas as pd
import numpy as np
import pickle
import os
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

# Ensure directory exists for new models
os.makedirs('ai_models/saved_models', exist_ok=True)

# 1. Load Data
data_path = 'data/processed/processed_weather_data.csv'
try:
    df = pd.read_csv(data_path)
except FileNotFoundError:
    print(f"Data not found at {data_path}. Creating synthetic base data for training.")
    # Fallback to create synthetic data if running fresh
    dates = pd.date_range(start='2020-01-01', periods=1000)
    df = pd.DataFrame({
        'date': dates,
        'temperature': np.random.uniform(15, 40, size=1000),
        'humidity': np.random.uniform(30, 95, size=1000),
        'rainfall': np.random.exponential(scale=5, size=1000),
        'aqi': np.random.uniform(20, 300, size=1000)
    })

# 2. Feature Engineering & Target Generation (Synthetic logic for missing targets)
np.random.seed(42)

weather_cols = ['rainfall', 'temperature', 'temperature_avg', 'humidity', 'aqi']
for col in weather_cols:
    if col in df.columns:
        df[col] = df[col].replace(-999, np.nan)

df['rainfall'] = df['rainfall'].clip(lower=0).fillna(0)
if 'temperature' not in df.columns and 'temperature_avg' in df.columns:
    df['temperature'] = df['temperature_avg']
df['temperature'] = df['temperature'].fillna(df['temperature'].mean())
df['humidity'] = df['humidity'].fillna(df['humidity'].mean())
df['aqi'] = df['aqi'].fillna(df['aqi'].mean())

# Wind Speed (Random normal)
df['wind_speed'] = np.random.uniform(0, 20, size=len(df))
# Historical Rainfall (Rolling avg)
df['historical_rainfall'] = df['rainfall'].rolling(window=7, min_periods=1).mean().fillna(0)

# Target: Future AQI (Next day AQI proxy)
df['target_future_aqi'] = df['aqi'].shift(-1).fillna(df['aqi'].mean())

# Target: Rainfall Category
# Categories: 0: No Rain, 1: Light, 2: Moderate, 3: Heavy, 4: Extreme
bins = [-1, 0.1, 5, 20, 50, np.inf]
labels = [0, 1, 2, 3, 4]
df['target_rainfall_cat'] = pd.cut(df['rainfall'], bins=bins, labels=labels).astype(int)

# Target: Flood Risk (0: Low, 1: Medium, 2: High)
df['target_flood_risk'] = ((df['rainfall'] + df['historical_rainfall']) > 60).astype(int) + \
                          ((df['rainfall'] + df['historical_rainfall']) > 120).astype(int)

# Target: Dengue Risk (0: Low, 1: Moderate, 2: High)
# Higher risk with moderate temp (25-30), high humidity (> 70), and stagnant water (post rain)
dengue_conditions = ((df['temperature'].between(25, 30)) & (df['humidity'] > 70) & (df['historical_rainfall'] > 10))
df['target_dengue_risk'] = dengue_conditions.astype(int) * np.random.choice([1, 2], size=len(df), p=[0.7, 0.3])

# Target: Heatwave Risk (0: Low, 1: Moderate, 2: High, 3: Severe)
# Simplified Heat Index proxy: T + (H/10)
hi = df['temperature'] + (df['humidity'] / 10)
bins_hi = [-np.inf, 25, 35, 42, np.inf]
labels_hi = [0, 1, 2, 3]
df['target_heatwave_risk'] = pd.cut(hi, bins=bins_hi, labels=labels_hi).astype(int)


# ---------------------------------------------------------
# 3. Train Models
# ---------------------------------------------------------

print("Training AQI Prediction Model...")
X_aqi = df[['temperature', 'humidity', 'rainfall', 'wind_speed']]
y_aqi = df['target_future_aqi']
aqi_model = RandomForestRegressor(n_estimators=50, max_depth=8, random_state=42)
aqi_model.fit(X_aqi, y_aqi)
with open('ai_models/saved_models/aqi_model.pkl', 'wb') as f:
    pickle.dump(aqi_model, f)

print("Training Rainfall Category Model...")
X_rain = df[['temperature', 'humidity', 'aqi', 'wind_speed']]
y_rain = df['target_rainfall_cat']
rain_model = RandomForestClassifier(n_estimators=50, max_depth=6, random_state=42)
rain_model.fit(X_rain, y_rain)
with open('ai_models/saved_models/rainfall_model.pkl', 'wb') as f:
    pickle.dump(rain_model, f)

print("Training Flood Risk Model...")
X_flood = df[['rainfall', 'humidity', 'historical_rainfall']]
y_flood = df['target_flood_risk']
flood_model = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
flood_model.fit(X_flood, y_flood)
with open('ai_models/saved_models/flood_model.pkl', 'wb') as f:
    pickle.dump(flood_model, f)

print("Training Dengue Risk Model...")
X_dengue = df[['temperature', 'humidity', 'rainfall']]
y_dengue = df['target_dengue_risk']
dengue_model = RandomForestClassifier(n_estimators=50, max_depth=5, class_weight='balanced', random_state=42)
dengue_model.fit(X_dengue, y_dengue)
with open('ai_models/saved_models/dengue_model.pkl', 'wb') as f:
    pickle.dump(dengue_model, f)

print("Training Heatwave Risk Model...")
X_heatwave = df[['temperature', 'humidity']]
y_heatwave = df['target_heatwave_risk']
heatwave_model = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
heatwave_model.fit(X_heatwave, y_heatwave)
with open('ai_models/saved_models/heatwave_model.pkl', 'wb') as f:
    pickle.dump(heatwave_model, f)

print("All advanced models trained and saved to ai_models/saved_models/")
