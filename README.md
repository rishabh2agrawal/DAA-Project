# 🌍 ClimateIQ Bengaluru: Spatio-Temporal Climate Prediction Platform

An intelligent web application and analytics platform designed to predict urban climate metrics, analyze multi-dimensional environmental health risks, and visualize decadal weather patterns and geospatial heatmaps for Bengaluru using Machine Learning.

## 📋 Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation & Prerequisites](#installation--prerequisites)
- [Running the Project](#running-the-project)
- [Deployment Guide](#deployment-guide)

## ✨ Features

- **🌍 Climate Risk Dashboard**: Live evaluation of environmental metrics paired with real-time risk indicators (Flood, Heatwave, Dengue, Pollution).
- **🗓️ Seasonal Analytics**: Deep-dive into aggregate seasons (Winter, Summer, Monsoon, Post-Monsoon) displaying comparative Plotly radar charts.
- **📈 Climate Trend Analysis**: Correlation heatmaps, distribution violins, and time-series line charts for weather variables.
- **🔮 Future Forecast Simulator**: Unified control center executing 5 simultaneous predictive models using Scikit-Learn (Random Forest) for predictive temperature, rain categorization, and specific hazard risks.
- **🗺️ Spatial Heatmaps**: Interactive topological mapping representing urban heat islands and flood-prone zones via Folium and GeoPandas.
- **🌱 Environmental Change Analysis**: AI-generated insights analyzing structural decadal changes, comparing urbanization, deforestation, and atmospheric degradation.

## 📁 Project Structure

```
DAA-project/
├── ai_models/
│   ├── saved_models/      (Generated .pkl predictive models)
│   ├── train.py           (Base predictive modeling)
│   └── train_extended.py  (Complete ML pipeline for risk classifiers)
├── analytics/
│   └── climate_change_analysis.py (Synthetic decadal analysis & plotly charts)
├── backend/
│   └── app.py             (FastAPI service & inference endpoints)
├── data/
│   ├── processed/         (Cleaned CSV data)
│   └── raw/               (Raw climate/NASA CSV datasets)
├── frontend/
│   └── app.py             (Streamlit UI/UX platform)
├── maps/
│   ├── geo_utils.py       (GeoPandas mock data generation layer)
│   └── heatmap_generator.py (Folium interactive heatmap wrappers)
├── data_processing.py     (Data normalization & scrubbing)
├── API_DOCS.md            (Comprehensive API interface specifications)
├── DEPLOYMENT.md          (End-to-End deployment strategies)
└── requirements.txt       (Pip dependencies)
```

## 🛠️ Installation & Prerequisites

**Prerequisites:** Python 3.9+ 

1. **Clone & Environment Setup:**
   ```bash
   python -m venv .venv
   source .venv/Scripts/activate  # Or .venv/bin/activate on Mac/Linux
   ```
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Data Processing & Training:**
   ```bash
   python data_processing.py
   python ai_models/train_extended.py
   ```

## 🚀 Running the Project

You must run the **Backend API** and the **Frontend Dashboard** simultaneously in separate terminals.

**Terminal 1 (Backend):**
```bash
uvicorn backend.app:app --reload
```

**Terminal 2 (Frontend):**
```bash
streamlit run frontend/app.py
```