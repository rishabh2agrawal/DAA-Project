# ClimateIQ Bengaluru

ClimateIQ Bengaluru is a project-ready climate intelligence platform for Bengaluru. It combines accessible daily weather data, proxy environmental indicators, classical machine-learning models, FastAPI prediction services, Streamlit dashboards, and interactive heatmaps.

The project is designed for academic presentation: it is working end-to-end, clearly explains its data methodology, and separates real accessible data from proxy/simulated features.

## Features

- Climate risk dashboard with latest temperature, rainfall, humidity, AQI, and modeled risk indicators.
- Seasonal analytics for Winter, Summer, Monsoon, and Post-Monsoon.
- Climate trend charts for temperature, AQI, rainfall anomaly, and feature correlations.
- Future forecast simulator for next-day temperature, AQI, rainfall class, heatwave risk, flood risk, dengue risk, and human health risk.
- Spatial heatmaps for proxy temperature, AQI, flood risk, dengue risk, and urban heat-island score.
- Environmental change analysis narrative for 2005-2026 with explicit proxy/simulation labeling.
- FastAPI backend with model metrics and climate summary endpoints.

## Data Methodology

The current v1 uses `data/raw/nasa_power_bengaluru.csv` as the main accessible weather dataset.

Generated project-ready proxy fields:

- `NDVI`: vegetation/green-cover proxy.
- `NDBI`: built-up intensity proxy.
- `NDWI`: water-body/moisture proxy.
- `LST`: land surface temperature proxy.
- `uhi_score`: urban heat-island proxy.
- `aqi`: generated AQI proxy if no official AQI file is supplied.

These proxy fields are useful for a working academic prototype, but they are not replacements for official satellite rasters, CPCB station data, IMD grids, or health records.

## ML Methodology

The primary v1 approach is classical ML:

- Random Forest regressor for next-day temperature.
- Random Forest regressor for next-day AQI.
- Random Forest classifiers for rainfall class, heatwave risk, flood risk, dengue risk, and human-risk class.

Metrics are saved to:

- `ai_models/saved_models/model_metrics.json`
- `MODEL_RESULTS.md`

Deep-learning models such as LSTM, Transformer, CNN-LSTM, ConvLSTM, and GNN are documented as future work.

## Project Structure

```text
DAA-project/
  ai_models/
    train_extended.py
    saved_models/
  analytics/
    climate_change_analysis.py
  backend/
    app.py
  data/
    raw/
    processed/
  frontend/
    app.py
  maps/
    geo_utils.py
    heatmap_generator.py
  data_processing.py
  API_DOCS.md
  DEPLOYMENT.md
  MODEL_RESULTS.md
```

## Run Locally

```bash
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe data_processing.py
.\.venv\Scripts\python.exe ai_models\train_extended.py
```

Terminal 1:

```bash
.\.venv\Scripts\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Terminal 2:

```bash
.\.venv\Scripts\streamlit.exe run frontend/app.py --server.address 127.0.0.1 --server.port 8501
```

Open:

- Frontend: http://127.0.0.1:8501
- Backend docs: http://127.0.0.1:8000/docs

## Limitations

- The current processed dataset starts from the available raw NASA-style data, not a full official 2005-2026 multi-source archive.
- Satellite and spatial indicators are proxy/generated in v1.
- AQI is proxy-generated unless replaced with official CPCB/OpenCity/Zenodo data.
- Health-risk outputs are awareness estimates, not medical advice.
- Official IMD, ERA5, CPCB, Bhuvan/NRSC, Sentinel/Landsat, hospital, and ward-level datasets are future-work integrations.
