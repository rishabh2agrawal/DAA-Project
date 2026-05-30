from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import pandas as pd
import numpy as np

app = FastAPI(title="ClimateIQ API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Request Models
class HybridPredictionRequest(BaseModel):
    rainfall: float
    humidity: float
    aqi: float
    LST: float = 0.0
    NDVI: float = 0.0
    NDBI: float = 0.0
    temperature_avg: float

class BasicPredictionRequest(BaseModel):
    rainfall: float
    humidity: float
    aqi: float
    wind_speed: float = 5.0
    temperature: float = 25.0
    historical_rainfall: float = 0.0

# ---------------------------------------------------------
# Load models safely
# ---------------------------------------------------------
def load_pickle(path):
    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        print(f"Warning: Model at {path} not found. ({e})")
        return None

risk_model = load_pickle('ai_models/hybrid_risk_model.pkl')
aqi_model = load_pickle('ai_models/saved_models/aqi_model.pkl')
rainfall_model = load_pickle('ai_models/saved_models/rainfall_model.pkl')
flood_model = load_pickle('ai_models/saved_models/flood_model.pkl')
dengue_model = load_pickle('ai_models/saved_models/dengue_model.pkl')
heatwave_model = load_pickle('ai_models/saved_models/heatwave_model.pkl')

# Load data
data_path = 'data/processed/processed_weather_data.csv'
try:
    df = pd.read_csv(data_path)
except:
    df = None

@app.get('/weather')
def get_weather():
    if df is None: return {"error": "Data unavailable"}
    clean_df = df.replace(-999, np.nan)
    required_cols = ['temperature_avg', 'rainfall', 'humidity', 'aqi']
    valid_df = clean_df.dropna(subset=[col for col in required_cols if col in clean_df.columns])
    latest = (valid_df.iloc[-1] if not valid_df.empty else clean_df.iloc[-1]).to_dict()
    for k, v in latest.items():
        if pd.isna(v): latest[k] = None
    if latest.get('temperature') is None and latest.get('temperature_avg') is not None:
        latest['temperature'] = latest['temperature_avg']
    return latest

# ---------------------------------------------------------
# Forecasting API Routes (AI Prediction Page)
# ---------------------------------------------------------
@app.post('/predict')
def predict_temperature(request: BasicPredictionRequest):
    # Fallback heuristic if no Temp model exists
    pred_temp = request.temperature + (request.humidity * 0.02) - (request.rainfall * 0.1)
    return {"predicted_temperature": round(pred_temp, 2)}

@app.post('/predict_aqi')
def predict_aqi(req: BasicPredictionRequest):
    if not aqi_model: return {"predicted_aqi": req.aqi + np.random.uniform(-10, 10)}
    input_data = pd.DataFrame([{'temperature': req.temperature, 'humidity': req.humidity, 'rainfall': req.rainfall, 'wind_speed': req.wind_speed}])
    return {"predicted_aqi": round(float(aqi_model.predict(input_data)[0]), 1)}

@app.post('/predict_rainfall')
def predict_rainfall(req: BasicPredictionRequest):
    if not rainfall_model: return {"category": "Light Rain"}
    input_data = pd.DataFrame([{'temperature': req.temperature, 'humidity': req.humidity, 'aqi': req.aqi, 'wind_speed': req.wind_speed}])
    idx = rainfall_model.predict(input_data)[0]
    mapping = {0: 'No Rain', 1: 'Light Rain', 2: 'Moderate Rain', 3: 'Heavy Rain', 4: 'Extreme Rain'}
    return {"category": mapping.get(idx, 'Unknown')}

# ---------------------------------------------------------
# Health & Risk Assessment API Routes (Health Risk Page)
# ---------------------------------------------------------
@app.post('/health_risk')
def health_risk(req: BasicPredictionRequest):
    # Legacy health risk handling
    score = (req.temperature * 1.5) + (req.aqi * 0.8) + (req.humidity * 0.5)
    r = "Low" if score < 100 else "Moderate" if score < 180 else "High"
    return {"risk": r}

@app.post('/predict_flood')
def predict_flood(req: BasicPredictionRequest):
    if not flood_model: return {"risk": "Low"}
    input_data = pd.DataFrame([{'rainfall': req.rainfall, 'humidity': req.humidity, 'historical_rainfall': req.historical_rainfall}])
    idx = flood_model.predict(input_data)[0]
    mapping = {0: 'Low', 1: 'Medium', 2: 'High'}
    return {"risk": mapping.get(idx, 'Unknown')}

@app.post('/predict_dengue')
def predict_dengue(req: BasicPredictionRequest):
    if not dengue_model: return {"risk": "Low"}
    input_data = pd.DataFrame([{'temperature': req.temperature, 'humidity': req.humidity, 'rainfall': req.rainfall}])
    idx = dengue_model.predict(input_data)[0]
    mapping = {0: 'Low', 1: 'Moderate', 2: 'High'}
    return {"risk": mapping.get(idx, 'Unknown')}

@app.post('/predict_heatwave')
def predict_heatwave(req: BasicPredictionRequest):
    if not heatwave_model: return {"risk": "Low"}
    input_data = pd.DataFrame([{'temperature': req.temperature, 'humidity': req.humidity}])
    idx = heatwave_model.predict(input_data)[0]
    mapping = {0: 'Low', 1: 'Moderate', 2: 'High', 3: 'Severe'}
    return {"risk": mapping.get(idx, 'Unknown')}

@app.post('/predict_risk')
def predict_risk(request: HybridPredictionRequest):
    if not risk_model:
        return {'error': 'Model not loaded'}
    # (Original predict_risk logic preserved)
    features = ['rainfall', 'humidity', 'aqi', 'LST', 'NDVI', 'NDBI', 'temperature_avg']
    input_data = pd.DataFrame([{
        'rainfall': request.rainfall,
        'humidity': request.humidity,
        'aqi': request.aqi,
        'LST': request.LST,
        'NDVI': request.NDVI,
        'NDBI': request.NDBI,
        'temperature_avg': request.temperature_avg
    }])[features]
    prediction_idx = risk_model.predict(input_data)[0]
    mapping = {0: 'Low', 1: 'Moderate', 2: 'High'}
    risk_level = mapping.get(prediction_idx, 'Unknown')
    
    return {
        'human_risk': risk_level
    }
