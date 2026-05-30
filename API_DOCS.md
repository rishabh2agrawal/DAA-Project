# 📡 ClimateIQ API Documentation

The ClimateIQ backend is built with **FastAPI** (`backend/app.py`). It serves native ML predictions and data routing to the Streamlit frontend. 

### Base URL: `http://localhost:8000`

---

## 1. System & Data Endpoints

### `GET /weather`
Returns the most recent row of processed weather data from `data/processed/processed_weather_data.csv`.

**Response:**
```json
{
  "date": "2024-05-30",
  "temperature": 28.5,
  "humidity": 65.0,
  "rainfall": 1.2,
  "aqi": 80.0
}
```

---

## 2. Quantitative Prediction Routes
These routes expect the `BasicPredictionRequest` schema:
```json
{
  "temperature": 25.0,
  "humidity": 60.0,
  "rainfall": 0.0,
  "aqi": 50.0,
  "wind_speed": 5.0,
  "historical_rainfall": 0.0
}
```

### `POST /predict`
Predicts localized continuous temperature variations.
**Returns:** `{"predicted_temperature": 26.5}`

### `POST /predict_aqi`
Predicts the exact Air Quality Index measurement based on wind dispersion and precipitation.
**Returns:** `{"predicted_aqi": 84.1}`

### `POST /predict_rainfall`
Categorizes impending precipitation severity.
**Returns:** `{"category": "Moderate Rain"}` *(Options: No Rain, Light Rain, Moderate Rain, Heavy Rain, Extreme Rain)*

---

## 3. Human Hazard & Risk Endpoints
These routes take the same environmental request parameters and route them through localized Random Forest Classifier models.

### `POST /predict_heatwave`
**Returns:** `{"risk": "Moderate"}` *(Options: Low, Moderate, High, Severe)*

### `POST /predict_flood`
**Returns:** `{"risk": "Low"}` *(Options: Low, Medium, High)*

### `POST /predict_dengue`
Evaluates vector breeding capabilities based on standing water / humidity relationships.
**Returns:** `{"risk": "Medium"}` *(Options: Low, Moderate, High)*
