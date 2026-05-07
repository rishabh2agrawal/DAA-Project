from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import pandas as pd
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictionRequest(BaseModel):
    rainfall: float
    humidity: float
    aqi: float

class HealthRiskRequest(BaseModel):
    temperature: float
    humidity: float
    aqi: float

# Load model
model_path = 'ai_models/temperature_model.pkl'
with open(model_path, 'rb') as f:
    model = pickle.load(f)

# Load data
data_path = 'data/processed/processed_weather_data.csv'
df = pd.read_csv(data_path)

@app.get("/weather")
def get_weather():
    # Return latest weather data
    latest = df.iloc[-1].to_dict()
    return latest

@app.post("/predict")
def predict_temperature(request: PredictionRequest):
    input_data = [[request.rainfall, request.humidity, request.aqi]]
    prediction = model.predict(input_data)[0]
    return {"predicted_temperature": float(prediction)}

@app.post("/health_risk")
def get_health_risk(request: HealthRiskRequest):
    risk = "Low"
    if request.aqi > 50:
        risk = "Moderate"
    if request.temperature > 30 or request.humidity > 70:
        risk = "High"
    return {"risk": risk}