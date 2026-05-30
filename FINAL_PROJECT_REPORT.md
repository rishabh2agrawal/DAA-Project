# ClimateIQ Bengaluru Final Project Report

## Problem Statement

Bengaluru is experiencing increasing climate stress due to urban expansion, loss of green cover, lake and water-body degradation, pollution, urban heat-island effects, and unstable rainfall patterns. Citizens and planners need localized climate-risk awareness that combines weather, pollution, environmental indicators, maps, and health-risk warnings.

## Objectives

- Build a working climate intelligence dashboard for Bengaluru.
- Predict next-day temperature, AQI, rainfall category, and risk classes using classical ML.
- Visualize seasonal and long-term climate patterns.
- Show proxy spatial heatmaps for heat, pollution, flood, dengue, and urban heat-island risk.
- Clearly separate real accessible weather data from proxy/generated indicators.

## Dataset Sources

- Main weather source: `data/raw/nasa_power_bengaluru.csv`.
- Processed dataset: `data/processed/processed_weather_data.csv`.
- Proxy indicators generated in preprocessing:
  - NDVI for vegetation.
  - NDBI for built-up intensity.
  - NDWI for water/moisture.
  - LST for land-surface temperature.
  - UHI score for urban heat-island intensity.
  - AQI proxy when no official pollution file is supplied.

## Preprocessing

The preprocessing pipeline:

- Converts dates and numeric fields.
- Removes `-999` sentinels.
- Clips invalid negative rainfall.
- Interpolates or fills missing weather values.
- Creates seasonal labels.
- Computes heat index, rainfall anomaly, AQI class, rainfall class, temperature class, and risk labels.

## Feature Engineering

Final model/dashboard features include:

- Temperature, rainfall, humidity, wind speed, AQI.
- Heat index.
- NDVI, NDBI, NDWI, LST.
- Rainfall anomaly.
- UHI score.
- Temperature, rainfall, AQI, heatwave, flood, dengue, and human-risk classes.

## Model Methodology

The project-ready v1 uses classical ML:

- Random Forest regression for next-day temperature.
- Random Forest regression for next-day AQI.
- Random Forest classification for rainfall class.
- Random Forest classification for heatwave, flood, dengue, and human health risk.

Model results are saved in:

- `MODEL_RESULTS.md`
- `ai_models/saved_models/model_metrics.json`

## Dashboard Outputs

The Streamlit dashboard includes:

- Climate Risk Dashboard.
- Seasonal Analytics.
- Climate Trend Analysis.
- Future Forecast Simulator.
- Spatial Heatmaps.
- Environmental Change Analysis.

## Limitations

- This is a project-ready implementation, not a publication-grade climate model.
- Satellite-style indicators are proxy-generated, not extracted from Sentinel/Landsat rasters.
- AQI is proxy-generated unless replaced with official CPCB/OpenCity/Zenodo data.
- Spatial maps are simulated/proxy surfaces, not ward-certified risk maps.
- Health-risk outputs are awareness estimates and not medical diagnosis.

## Future Work

- Integrate official IMD gridded rainfall and temperature data.
- Add ERA5/ERA5-Land reanalysis variables.
- Add CPCB or OpenCity air-quality observations.
- Extract NDVI, NDBI, NDWI, and LST from Sentinel/Landsat imagery.
- Add Bengaluru ward boundaries and demographic/road-density features.
- Add LSTM/GRU or Transformer models for stronger sequence forecasting.
- Add ConvLSTM/CNN-LSTM for true spatial-temporal satellite modeling.
- Add Graph Neural Networks for ward-to-ward risk spread.
