import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "processed" / "processed_weather_data.csv"
MODEL_DIR = BASE_DIR / "ai_models" / "saved_models"
METRICS_PATH = MODEL_DIR / "model_metrics.json"

app = FastAPI(title="ClimateIQ API", version="3.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BasicPredictionRequest(BaseModel):
    temperature: float = 25.0
    humidity: float
    rainfall: float
    aqi: float
    wind_speed: float = 5.0
    historical_rainfall: float = 0.0
    NDVI: float = 0.3
    NDBI: float = 0.35
    NDWI: float = 0.25
    heat_index: float | None = None
    rainfall_anomaly: float = 0.0
    uhi_score: float = 3.0


class HybridPredictionRequest(BaseModel):
    rainfall: float
    humidity: float
    aqi: float
    LST: float = 0.0
    NDVI: float = 0.0
    NDBI: float = 0.0
    NDWI: float = 0.0
    temperature_avg: float


def load_pickle(path):
    try:
        with open(path, "rb") as file:
            return pickle.load(file)
    except Exception as exc:
        print(f"Warning: model unavailable at {path}: {exc}")
        return None


def load_data():
    try:
        df = pd.read_csv(DATA_PATH).replace(-999, np.nan)
        if "temperature" not in df.columns and "temperature_avg" in df.columns:
            df["temperature"] = df["temperature_avg"]
        return df
    except Exception as exc:
        print(f"Warning: processed data unavailable: {exc}")
        return None


def load_metrics():
    try:
        with open(METRICS_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {"message": "Model metrics unavailable. Run python ai_models/train_extended.py."}


df = load_data()
temperature_model = load_pickle(MODEL_DIR / "temperature_model.pkl")
aqi_model = load_pickle(MODEL_DIR / "aqi_model.pkl")
rainfall_model = load_pickle(MODEL_DIR / "rainfall_model.pkl")
flood_model = load_pickle(MODEL_DIR / "flood_model.pkl")
dengue_model = load_pickle(MODEL_DIR / "dengue_model.pkl")
heatwave_model = load_pickle(MODEL_DIR / "heatwave_model.pkl")
human_risk_model = load_pickle(MODEL_DIR / "human_risk_model.pkl")


def heat_index(temp_c, humidity):
    return temp_c + (humidity / 10)


def model_input(req, fields):
    values = {
        "temperature": req.temperature,
        "humidity": req.humidity,
        "rainfall": req.rainfall,
        "wind_speed": req.wind_speed,
        "aqi": req.aqi,
        "heat_index": req.heat_index if req.heat_index is not None else heat_index(req.temperature, req.humidity),
        "historical_rainfall": req.historical_rainfall,
        "NDVI": req.NDVI,
        "NDBI": req.NDBI,
        "NDWI": req.NDWI,
        "rainfall_anomaly": req.rainfall_anomaly,
        "uhi_score": req.uhi_score,
    }
    return pd.DataFrame([{field: values[field] for field in fields}])


def classify_temperature(value):
    if value < 25:
        return "Normal"
    if value < 30:
        return "Hot"
    if value < 35:
        return "Very Hot"
    return "Heat-wave-like"


def classify_aqi(value):
    if value <= 50:
        return "Good"
    if value <= 100:
        return "Moderate"
    if value <= 200:
        return "Poor"
    return "Very Poor"


def risk_fallback(req):
    score = 0
    if req.aqi > 200:
        score += 3
    elif req.aqi > 150:
        score += 2
    elif req.aqi > 100:
        score += 1
    if req.temperature + (req.humidity / 10) > 40:
        score += 2
    if req.rainfall > 50:
        score += 2
    return "Severe" if score >= 5 else "High" if score >= 3 else "Moderate" if score >= 1 else "Low"


@app.get("/weather")
def get_weather():
    if df is None or df.empty:
        return {"error": "Data unavailable"}
    clean_df = df.replace(-999, np.nan)
    required = [col for col in ["temperature", "rainfall", "humidity", "aqi"] if col in clean_df.columns]
    valid_df = clean_df.dropna(subset=required)
    latest = (valid_df.iloc[-1] if not valid_df.empty else clean_df.iloc[-1]).to_dict()
    for key, value in list(latest.items()):
        if pd.isna(value):
            latest[key] = None
    latest["method_note"] = "Weather is from the accessible NASA POWER-style project dataset; satellite/AQI fields may be proxy-generated."
    return latest


@app.get("/model_metrics")
def get_model_metrics():
    return load_metrics()


@app.get("/climate_summary")
def get_climate_summary():
    if df is None or df.empty:
        return {"error": "Data unavailable"}
    clean = df.dropna(subset=["temperature", "rainfall", "aqi"])
    first = clean.iloc[0]
    latest = clean.iloc[-1]
    return {
        "date_range": {"start": str(first["date"]), "end": str(latest["date"]), "rows": int(len(clean))},
        "temperature_change_c": round(float(latest["temperature"] - first["temperature"]), 2),
        "avg_temperature_c": round(float(clean["temperature"].mean()), 2),
        "avg_aqi": round(float(clean["aqi"].mean()), 2),
        "total_rainfall": round(float(clean["rainfall"].sum()), 2),
        "method_note": "2005-2026 environmental-change narrative remains proxy/simulation in v1 unless official LULC/raster data is added.",
    }


@app.post("/predict_temperature")
def predict_temperature(req: BasicPredictionRequest):
    fields = ["temperature", "humidity", "rainfall", "wind_speed", "aqi", "heat_index", "uhi_score"]
    if temperature_model:
        pred = float(temperature_model.predict(model_input(req, fields))[0])
    else:
        pred = req.temperature + (req.humidity * 0.02) - (req.rainfall * 0.08)
    return {"predicted_temperature": round(pred, 2), "temperature_class": classify_temperature(pred), "horizon": "next-day estimate"}


@app.post("/predict")
def predict_temperature_alias(req: BasicPredictionRequest):
    return predict_temperature(req)


@app.post("/predict_aqi")
def predict_aqi(req: BasicPredictionRequest):
    fields = ["temperature", "humidity", "rainfall", "wind_speed", "NDVI", "NDBI", "NDWI", "uhi_score"]
    if aqi_model:
        pred = float(aqi_model.predict(model_input(req, fields))[0])
    else:
        pred = req.aqi + np.random.uniform(-8, 8)
    pred = max(0, min(500, pred))
    return {"predicted_aqi": round(pred, 1), "aqi_class": classify_aqi(pred), "horizon": "next-day estimate"}


@app.post("/predict_rainfall")
def predict_rainfall(req: BasicPredictionRequest):
    mapping = {0: "No Rain", 1: "Light", 2: "Moderate", 3: "Heavy", 4: "Extreme"}
    if rainfall_model:
        idx = int(rainfall_model.predict(model_input(req, ["temperature", "humidity", "aqi", "wind_speed", "rainfall_anomaly"]))[0])
        category = mapping.get(idx, "Unknown")
    else:
        category = "Extreme" if req.rainfall >= 50 else "Heavy" if req.rainfall >= 20 else "Moderate" if req.rainfall >= 5 else "Light" if req.rainfall > 0.1 else "No Rain"
    return {"category": category, "horizon": "next-day class estimate"}


@app.post("/predict_heatwave")
def predict_heatwave(req: BasicPredictionRequest):
    mapping = {0: "Low", 1: "Moderate", 2: "High", 3: "Severe"}
    if heatwave_model:
        idx = int(heatwave_model.predict(model_input(req, ["temperature", "humidity", "heat_index", "uhi_score"]))[0])
        risk = mapping.get(idx, "Unknown")
    else:
        risk = "Severe" if heat_index(req.temperature, req.humidity) > 42 else "High" if heat_index(req.temperature, req.humidity) > 37 else "Moderate" if heat_index(req.temperature, req.humidity) > 32 else "Low"
    return {"risk": risk}


@app.post("/predict_flood")
def predict_flood(req: BasicPredictionRequest):
    mapping = {0: "Low", 1: "Moderate", 2: "High", 3: "Severe"}
    if flood_model:
        idx = int(flood_model.predict(model_input(req, ["rainfall", "historical_rainfall", "humidity", "rainfall_anomaly", "NDWI"]))[0])
        risk = mapping.get(idx, "Unknown")
    else:
        risk = "Severe" if req.rainfall > 80 else "High" if req.rainfall > 50 else "Moderate" if req.rainfall > 20 else "Low"
    return {"risk": risk}


@app.post("/predict_dengue")
def predict_dengue(req: BasicPredictionRequest):
    mapping = {0: "Low", 1: "Moderate", 2: "High", 3: "Severe"}
    if dengue_model:
        idx = int(dengue_model.predict(model_input(req, ["temperature", "humidity", "rainfall", "historical_rainfall", "NDWI"]))[0])
        risk = mapping.get(idx, "Unknown")
    else:
        risk = "High" if req.humidity > 75 and req.historical_rainfall > 35 else "Moderate" if req.humidity > 65 and req.rainfall > 1 else "Low"
    return {"risk": risk}


@app.post("/predict_human_risk")
def predict_human_risk(req: BasicPredictionRequest):
    mapping = {0: "Low", 1: "Moderate", 2: "High", 3: "Severe"}
    if human_risk_model:
        idx = int(human_risk_model.predict(model_input(req, ["temperature", "humidity", "rainfall", "aqi", "heat_index", "uhi_score"]))[0])
        risk = mapping.get(idx, "Unknown")
    else:
        risk = risk_fallback(req)
    return {"risk": risk, "method_note": "Risk is an ML/rule estimate for awareness, not medical advice."}


@app.post("/health_risk")
def health_risk_alias(req: BasicPredictionRequest):
    return predict_human_risk(req)


@app.post("/predict_risk")
def predict_risk_alias(req: HybridPredictionRequest):
    basic = BasicPredictionRequest(
        temperature=req.temperature_avg,
        humidity=req.humidity,
        rainfall=req.rainfall,
        aqi=req.aqi,
        NDVI=req.NDVI,
        NDBI=req.NDBI,
        NDWI=req.NDWI,
        uhi_score=max(0, req.LST - req.temperature_avg),
    )
    result = predict_human_risk(basic)
    return {"human_risk": result["risk"], "method_note": result["method_note"]}
