# Project Alignment & Missing Features Analysis

Based on the research notes for "Spatio-Temporal Climate Prediction and Human Risk Assessment for Bengaluru Using Multi-Source Environmental Data from 2005–2026", here is an evaluation of the current project and a roadmap of missing features needed to align it with the required methodology.

## 1. Current Project State
* **Data Sources:** Uses a single basic weather CSV (`bengaluru_weather.csv`).
* **Variables:** Only uses basic temperature, rainfall, humidity, and a rudimentary proxy for AQI.
* **Preprocessing:** Minimal cleaning and imputation.
* **Feature Engineering:** Missing advanced indicators (e.g., NDVI, LST, Heat Index).
* **Modeling:** Uses a basic `RandomForestRegressor` to predict continuous temperature based on rainfall, humidity, and proxy AQI.
* **Outputs:** Only predicts numerical temperature.

---

## 2. Missing Features & Required Additions

### Step 1: Data Collection Expansion
Currently, the project lacks multi-modal data sources. 
**To Add:**
* **Meteorological Data:** Integrate IMD Gridded Rainfall Data, NASA POWER API data, or ERA5 reanalysis data for historical precision.
* **Satellite Data:** Integrate Landsat / Sentinel data to extract LST, NDVI, NDBI, and NDWI.
* **Air Pollution Data:** Add genuine CPCB or OpenCity AQI data (PM2.5, PM10, NO₂, SO₂, CO, O₃).
* **Urban & Health Data:** Add ward-level demographic data, road density, built-up area statistics, and health incident data (dengue cases, heat stress).

### Step 2: Advanced Preprocessing
Currently, data processing only does basic NaN filling.
**To Add:**
* Spatial alignment: Map data to specific Bengaluru grid/ward coordinates.
* Temporal alignment: Ensure data spans 2005–2026 and aggregate properly on daily/monthly scales.
* Seasonal labeling: Categorize data points into Winter, Summer/Pre-monsoon, Southwest Monsoon, and Post-monsoon.

### Step 3: Feature Engineering
Current features are just `['rainfall', 'humidity', 'aqi']`.
**To Add:**
* **Satellite Indices:** `NDVI` (Green cover), `NDBI` (Built-up intensity), `NDWI` (Water-body presence).
* **Climate Indices:** `LST` (Land Surface Temperature), `Heat Index` (Human-perceived heat stress).
* **Anomalies & Scores:** Rainfall anomalies, accurate AQI categories, and Urban Heat Island (UHI) scores.

### Step 4: Upgrading Prediction Models
Current model is a basic `RandomForestRegressor`.
**To Add (Hybrid Multi-Modal Framework):**
* Replace or supplement RF with Deep Learning models for time-series forecasting: **LSTM / GRU** or **Transformers**.
* Add Spatial Modeling: Use **CNN-LSTM** or **ConvLSTM** to process satellite imagery mixed with climate time-series.
* Add Network Modeling: Implement **Graph Neural Networks (GNN)** to model ward-to-ward climate transitions.
* **Target Architectures:** Use an ensemble approach like **CNN + Transformer + XGBoost** for robust predictions.

### Step 5: Expanding Prediction Outputs
Currently only predicting continuous temperature.
**To Add (Classification Targets):**
* **Temperature Class:** Normal, hot, very hot, heat-wave-like.
* **Rainfall Class:** No rain, light, moderate, heavy, extreme.
* **Air Quality Class:** Good, moderate, poor, very poor.
* **Human Risk Class:** Low, moderate, high, severe.
* **Environmental Risks:** Flood risk and Dengue/mosquito risk levels (Low, medium, high).

## 3. Recommended Implementation Roadmap
1. **Directory Structure Updates:** Create folders for `data/satellite`, `data/pollution`, `data/urban`.
2. **API Integrations:** Write scripts to fetch NASA POWER and CPCB data automatically.
3. **Spatial Processing:** Integrate `geopandas` and `rasterio` into `data_processing.py` to handle spatial grids and compute NDVI/NDBI/LST.
4. **Model Restructuring:** Refactor `ai_models/train.py` to support PyTorch/TensorFlow for deep learning architectures, building pipelines for LSTM/Transformer and CNN models.
5. **API & UI Refactor:** Update `backend/app.py` and `frontend/app.py` to expose the new prediction classes (Heat risk, Flood risk, Dengue risk) and visualize them spatially on a map of Bengaluru.
