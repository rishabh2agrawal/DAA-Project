# ClimateIQ Model Results

These metrics are generated from the project-ready v1 classical ML pipeline.
Forecast targets use next-day shifted labels where practical; proxy climate features are not a substitute for official satellite or health datasets.

## Metrics Summary

### next_day_temperature_regressor
- MAE: 0.643
- RMSE: 0.841
- R2: 0.909

### next_day_aqi_regressor
- MAE: 12.35
- RMSE: 15.85
- R2: 0.343

### next_day_rainfall_classifier
- Accuracy: 0.638

### heatwave_risk_classifier
- Accuracy: 0.95

### flood_risk_classifier
- Accuracy: 0.941

### dengue_risk_classifier
- Accuracy: 0.889

### human_risk_classifier
- Accuracy: 0.705
