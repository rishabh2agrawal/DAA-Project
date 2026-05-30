import pandas as pd
import numpy as np
import os
from datetime import datetime

def compute_heat_index(T_C, RH):
    T_F = T_C * 9/5 + 32
    HI_F = 0.5 * (T_F + 61.0 + ((T_F-68.0)*1.2) + (RH*0.094))
    if HI_F > 79:
        HI_F = -42.379 + 2.04901523*T_F + 10.14333127*RH - 0.22475541*T_F*RH - 0.00683783*T_F*T_F - 0.05481717*RH*RH + 0.00122874*T_F*T_F*RH + 0.00085282*T_F*RH*RH - 0.00000199*T_F*T_F*RH*RH
    return (HI_F - 32) * 5/9

def get_season(month):
    if month in [12, 1, 2]: return 'Winter'
    elif month in [3, 4, 5]: return 'Summer'
    elif month in [6, 7, 8, 9]: return 'Monsoon'
    else: return 'Post-monsoon'

def process_data():
    input_path = os.path.join('data', 'raw', 'nasa_power_bengaluru.csv')
    df = pd.read_csv(input_path)
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.month
    df['season'] = df['month'].apply(get_season)
    df['heat_index'] = df.apply(lambda row: compute_heat_index(row['temperature_avg'], row['humidity']), axis=1)
    df['rolling_rain_30d'] = df['rainfall'].rolling(window=30, min_periods=1).sum()
    df['NDVI'] = 0.2 + (df['rolling_rain_30d'] / 500).clip(0, 0.6) + np.random.normal(0, 0.05, len(df))
    df['NDVI'] = df['NDVI'].clip(0.1, 0.8)
    years_passed = df['date'].dt.year - df['date'].dt.year.min()
    df['NDBI'] = 0.3 + (years_passed * 0.02) + np.random.normal(0, 0.02, len(df))
    df['LST'] = df['temperature_avg'] + (df['NDBI'] * 5) - (df['NDVI'] * 3) + 2
    base_aqi = 100 + (years_passed * 5)
    aqi_weather_effect = (df['wind_speed'] * -5) + (df['rainfall'] * -2)
    df['aqi'] = (base_aqi + aqi_weather_effect + np.random.normal(0, 15, len(df))).clip(20, 500)
    conditions_temp = [df['temperature_max'] < 25, df['temperature_max'] < 30, df['temperature_max'] < 35]
    choices_temp = ['Normal', 'Warm', 'Hot']
    df['temp_class'] = np.select(conditions_temp, choices_temp, default='Very Hot')
    conditions_rain = [df['rainfall'] == 0, df['rainfall'] < 10, df['rainfall'] < 30, df['rainfall'] < 60]
    choices_rain = ['No Rain', 'Light', 'Moderate', 'Heavy']
    df['rain_class'] = np.select(conditions_rain, choices_rain, default='Extreme')
    def assess_risk(row):
        score = 0
        if row['aqi'] > 150: score += 2
        elif row['aqi'] > 100: score += 1
        if row['heat_index'] > 35: score += 2
        elif row['heat_index'] > 30: score += 1
        if row['rainfall'] > 50: score += 3
        if score >= 3: return 'High'
        elif score == 2: return 'Moderate'
        else: return 'Low'
    df['human_risk'] = df.apply(assess_risk, axis=1)
    df = df.dropna().drop(columns=['rolling_rain_30d'])
    out_path = os.path.join('data', 'processed', 'processed_weather_data.csv')
    df.to_csv(out_path, index=False)
    print(f'Processed data saved to {out_path}')

if __name__ == '__main__':
    process_data()
