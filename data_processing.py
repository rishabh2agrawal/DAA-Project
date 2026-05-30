import os

import numpy as np
import pandas as pd


RAW_PATH = os.path.join("data", "raw", "nasa_power_bengaluru.csv")
OUT_PATH = os.path.join("data", "processed", "processed_weather_data.csv")
CORE_NUMERIC_COLUMNS = [
    "temperature_avg",
    "temperature_max",
    "temperature_min",
    "rainfall",
    "humidity",
    "wind_speed",
]


def compute_heat_index(temp_c, humidity):
    temp_f = temp_c * 9 / 5 + 32
    heat_index_f = 0.5 * (temp_f + 61.0 + ((temp_f - 68.0) * 1.2) + (humidity * 0.094))
    if heat_index_f > 79:
        heat_index_f = (
            -42.379
            + 2.04901523 * temp_f
            + 10.14333127 * humidity
            - 0.22475541 * temp_f * humidity
            - 0.00683783 * temp_f * temp_f
            - 0.05481717 * humidity * humidity
            + 0.00122874 * temp_f * temp_f * humidity
            + 0.00085282 * temp_f * humidity * humidity
            - 0.00000199 * temp_f * temp_f * humidity * humidity
        )
    return (heat_index_f - 32) * 5 / 9


def get_season(month):
    if month in [12, 1, 2]:
        return "Winter"
    if month in [3, 4, 5]:
        return "Summer"
    if month in [6, 7, 8, 9]:
        return "Monsoon"
    return "Post-Monsoon"


def classify_temperature(temp_max):
    if temp_max < 25:
        return "Normal"
    if temp_max < 30:
        return "Hot"
    if temp_max < 35:
        return "Very Hot"
    return "Heat-wave-like"


def classify_rainfall(rainfall):
    if rainfall <= 0.1:
        return "No Rain"
    if rainfall < 5:
        return "Light"
    if rainfall < 20:
        return "Moderate"
    if rainfall < 50:
        return "Heavy"
    return "Extreme"


def classify_aqi(aqi):
    if aqi <= 50:
        return "Good"
    if aqi <= 100:
        return "Moderate"
    if aqi <= 200:
        return "Poor"
    return "Very Poor"


def risk_from_score(score):
    if score >= 5:
        return "Severe"
    if score >= 3:
        return "High"
    if score >= 1:
        return "Moderate"
    return "Low"


def process_data():
    np.random.seed(42)
    df = pd.read_csv(RAW_PATH)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.replace(-999, np.nan)

    for col in CORE_NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["rainfall"] = df["rainfall"].clip(lower=0).fillna(0)
    for col in ["temperature_avg", "temperature_max", "temperature_min", "humidity", "wind_speed"]:
        df[col] = df[col].interpolate(limit_direction="both").fillna(df[col].median())

    df["humidity"] = df["humidity"].clip(0, 100)
    df["wind_speed"] = df["wind_speed"].clip(lower=0)
    df["temperature"] = df["temperature_avg"]
    df["month"] = df["date"].dt.month
    df["season"] = df["month"].apply(get_season)
    df["heat_index"] = df.apply(lambda row: compute_heat_index(row["temperature"], row["humidity"]), axis=1)

    rolling_rain_30d = df["rainfall"].rolling(window=30, min_periods=1).sum()
    years_passed = df["date"].dt.year - df["date"].dt.year.min()

    # Proxy satellite-style indices for project-ready v1. Replace with raster-derived values in research-grade work.
    df["NDVI"] = (0.25 + (rolling_rain_30d / 500).clip(0, 0.45) - (years_passed * 0.012) + np.random.normal(0, 0.035, len(df))).clip(0.08, 0.78)
    df["NDBI"] = (0.28 + (years_passed * 0.018) + np.random.normal(0, 0.018, len(df))).clip(0.15, 0.75)
    df["NDWI"] = (0.32 + (rolling_rain_30d / 650).clip(0, 0.35) - (years_passed * 0.01) + np.random.normal(0, 0.03, len(df))).clip(0.03, 0.7)
    df["LST"] = df["temperature"] + (df["NDBI"] * 5) - (df["NDVI"] * 3) - (df["NDWI"] * 1.5) + 2
    df["uhi_score"] = ((df["LST"] - df["temperature"]) + (df["NDBI"] * 8) - (df["NDVI"] * 4) - (df["NDWI"] * 3)).clip(0, 10)

    monthly_rain_mean = df.groupby("month")["rainfall"].transform("mean")
    df["rainfall_anomaly"] = df["rainfall"] - monthly_rain_mean

    base_aqi = 92 + (years_passed * 4.5)
    aqi_weather_effect = (df["wind_speed"] * -4.2) + (df["rainfall"] * -1.7) + (df["NDBI"] * 25) - (df["NDVI"] * 10)
    df["aqi"] = (base_aqi + aqi_weather_effect + np.random.normal(0, 12, len(df))).clip(20, 500)

    df["temp_class"] = df["temperature_max"].apply(classify_temperature)
    df["rain_class"] = df["rainfall"].apply(classify_rainfall)
    df["aqi_class"] = df["aqi"].apply(classify_aqi)

    heat_score = np.select([df["heat_index"] > 40, df["heat_index"] > 35, df["heat_index"] > 30], [3, 2, 1], default=0)
    flood_score = np.select([df["rainfall"] > 80, df["rainfall"] > 50, df["rainfall"] > 20], [3, 2, 1], default=0)
    pollution_score = np.select([df["aqi"] > 200, df["aqi"] > 150, df["aqi"] > 100], [3, 2, 1], default=0)
    dengue_score = np.select(
        [
            (df["humidity"] > 78) & (rolling_rain_30d > 80),
            (df["humidity"] > 70) & (rolling_rain_30d > 35),
            (df["humidity"] > 65) & (rolling_rain_30d > 15),
        ],
        [3, 2, 1],
        default=0,
    )

    df["heatwave_risk"] = [risk_from_score(score) for score in heat_score]
    df["flood_risk"] = [risk_from_score(score) for score in flood_score]
    df["dengue_risk"] = [risk_from_score(score) for score in dengue_score]
    df["human_risk"] = [risk_from_score(score) for score in (heat_score + pollution_score + flood_score)]

    final_columns = [
        "date",
        "temperature",
        "temperature_avg",
        "temperature_max",
        "temperature_min",
        "rainfall",
        "humidity",
        "wind_speed",
        "month",
        "season",
        "heat_index",
        "NDVI",
        "NDBI",
        "NDWI",
        "LST",
        "rainfall_anomaly",
        "uhi_score",
        "aqi",
        "temp_class",
        "rain_class",
        "aqi_class",
        "human_risk",
        "flood_risk",
        "dengue_risk",
        "heatwave_risk",
    ]
    df = df.dropna(subset=["date", "temperature", "rainfall", "humidity", "wind_speed", "aqi"])
    df = df[final_columns].sort_values("date")

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    df.to_csv(OUT_PATH, index=False)
    print(f"Processed {len(df)} rows saved to {OUT_PATH}")
    print("Proxy fields: NDVI, NDBI, NDWI, LST, uhi_score, AQI if no external AQI file is supplied.")


if __name__ == "__main__":
    process_data()
