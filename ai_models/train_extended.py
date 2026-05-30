import json
import os
import pickle

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, classification_report, mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


DATA_PATH = "data/processed/processed_weather_data.csv"
MODEL_DIR = "ai_models/saved_models"
METRICS_PATH = os.path.join(MODEL_DIR, "model_metrics.json")
REPORT_PATH = "MODEL_RESULTS.md"
RANDOM_STATE = 42

CLASS_MAPPINGS = {
    "rain_class": {0: "No Rain", 1: "Light", 2: "Moderate", 3: "Heavy", 4: "Extreme"},
    "heatwave_risk": {0: "Low", 1: "Moderate", 2: "High", 3: "Severe"},
    "flood_risk": {0: "Low", 1: "Moderate", 2: "High", 3: "Severe"},
    "dengue_risk": {0: "Low", 1: "Moderate", 2: "High", 3: "Severe"},
    "human_risk": {0: "Low", 1: "Moderate", 2: "High", 3: "Severe"},
}


def clean_training_data(df):
    df = df.replace(-999, np.nan).copy()
    if "temperature" not in df.columns and "temperature_avg" in df.columns:
        df["temperature"] = df["temperature_avg"]

    numeric_cols = [
        "temperature",
        "temperature_avg",
        "rainfall",
        "humidity",
        "wind_speed",
        "aqi",
        "heat_index",
        "NDVI",
        "NDBI",
        "NDWI",
        "LST",
        "rainfall_anomaly",
        "uhi_score",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["rainfall"] = df["rainfall"].clip(lower=0).fillna(0)
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())
    return df


def encode_risk(series):
    order = {"Low": 0, "Moderate": 1, "Medium": 1, "High": 2, "Severe": 3}
    return series.map(order).fillna(0).astype(int)


def encode_rain(series):
    order = {"No Rain": 0, "Light": 1, "Light Rain": 1, "Moderate": 2, "Moderate Rain": 2, "Heavy": 3, "Heavy Rain": 3, "Extreme": 4, "Extreme Rain": 4}
    return series.map(order).fillna(0).astype(int)


def save_model(name, model):
    with open(os.path.join(MODEL_DIR, name), "wb") as file:
        pickle.dump(model, file)


def regression_metrics(y_true, y_pred):
    return {
        "mae": round(float(mean_absolute_error(y_true, y_pred)), 3),
        "rmse": round(float(mean_squared_error(y_true, y_pred, squared=False)), 3),
        "r2": round(float(r2_score(y_true, y_pred)), 3),
    }


def classifier_metrics(y_true, y_pred, mapping):
    labels = sorted(mapping)
    target_names = [mapping[label] for label in labels]
    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 3),
        "classification_report": classification_report(
            y_true,
            y_pred,
            labels=labels,
            target_names=target_names,
            zero_division=0,
            output_dict=True,
        ),
    }


def fit_classifier(df, name, features, target, mapping, model_path):
    X = df[features]
    y = df[target]
    stratify = y if y.value_counts().min() >= 2 and y.nunique() > 1 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=stratify,
    )
    model = RandomForestClassifier(n_estimators=120, max_depth=8, class_weight="balanced", random_state=RANDOM_STATE)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    save_model(model_path, model)
    return model, classifier_metrics(y_test, y_pred, mapping)


def write_metrics_report(metrics):
    lines = [
        "# ClimateIQ Model Results",
        "",
        "These metrics are generated from the project-ready v1 classical ML pipeline.",
        "Forecast targets use next-day shifted labels where practical; proxy climate features are not a substitute for official satellite or health datasets.",
        "",
        "## Metrics Summary",
        "",
    ]
    for name, data in metrics.items():
        lines.append(f"### {name}")
        if "accuracy" in data:
            lines.append(f"- Accuracy: {data['accuracy']}")
        if "mae" in data:
            lines.append(f"- MAE: {data['mae']}")
            lines.append(f"- RMSE: {data['rmse']}")
            lines.append(f"- R2: {data['r2']}")
        lines.append("")

    with open(REPORT_PATH, "w", encoding="utf-8") as file:
        file.write("\n".join(lines))


def train_models():
    os.makedirs(MODEL_DIR, exist_ok=True)
    df = clean_training_data(pd.read_csv(DATA_PATH))

    df["historical_rainfall"] = df["rainfall"].rolling(window=7, min_periods=1).mean()
    df["target_next_temperature"] = df["temperature"].shift(-1).fillna(df["temperature"].median())
    df["target_next_aqi"] = df["aqi"].shift(-1).fillna(df["aqi"].median())
    df["target_next_rain_class"] = encode_rain(df["rain_class"].shift(-1).fillna(df["rain_class"]))
    df["target_heatwave_risk"] = encode_risk(df["heatwave_risk"].shift(-1).fillna(df["heatwave_risk"]))
    df["target_flood_risk"] = encode_risk(df["flood_risk"].shift(-1).fillna(df["flood_risk"]))
    df["target_dengue_risk"] = encode_risk(df["dengue_risk"].shift(-1).fillna(df["dengue_risk"]))
    df["target_human_risk"] = encode_risk(df["human_risk"].shift(-1).fillna(df["human_risk"]))

    metrics = {}

    temp_features = ["temperature", "humidity", "rainfall", "wind_speed", "aqi", "heat_index", "uhi_score"]
    X_train, X_test, y_train, y_test = train_test_split(
        df[temp_features],
        df["target_next_temperature"],
        test_size=0.2,
        random_state=RANDOM_STATE,
    )
    temp_model = RandomForestRegressor(n_estimators=120, max_depth=10, random_state=RANDOM_STATE)
    temp_model.fit(X_train, y_train)
    metrics["next_day_temperature_regressor"] = regression_metrics(y_test, temp_model.predict(X_test))
    save_model("temperature_model.pkl", temp_model)

    aqi_features = ["temperature", "humidity", "rainfall", "wind_speed", "NDVI", "NDBI", "NDWI", "uhi_score"]
    X_train, X_test, y_train, y_test = train_test_split(
        df[aqi_features],
        df["target_next_aqi"],
        test_size=0.2,
        random_state=RANDOM_STATE,
    )
    aqi_model = RandomForestRegressor(n_estimators=120, max_depth=10, random_state=RANDOM_STATE)
    aqi_model.fit(X_train, y_train)
    metrics["next_day_aqi_regressor"] = regression_metrics(y_test, aqi_model.predict(X_test))
    save_model("aqi_model.pkl", aqi_model)

    _, metrics["next_day_rainfall_classifier"] = fit_classifier(
        df,
        "rainfall",
        ["temperature", "humidity", "aqi", "wind_speed", "rainfall_anomaly"],
        "target_next_rain_class",
        CLASS_MAPPINGS["rain_class"],
        "rainfall_model.pkl",
    )
    _, metrics["heatwave_risk_classifier"] = fit_classifier(
        df,
        "heatwave",
        ["temperature", "humidity", "heat_index", "uhi_score"],
        "target_heatwave_risk",
        CLASS_MAPPINGS["heatwave_risk"],
        "heatwave_model.pkl",
    )
    _, metrics["flood_risk_classifier"] = fit_classifier(
        df,
        "flood",
        ["rainfall", "historical_rainfall", "humidity", "rainfall_anomaly", "NDWI"],
        "target_flood_risk",
        CLASS_MAPPINGS["flood_risk"],
        "flood_model.pkl",
    )
    _, metrics["dengue_risk_classifier"] = fit_classifier(
        df,
        "dengue",
        ["temperature", "humidity", "rainfall", "historical_rainfall", "NDWI"],
        "target_dengue_risk",
        CLASS_MAPPINGS["dengue_risk"],
        "dengue_model.pkl",
    )
    _, metrics["human_risk_classifier"] = fit_classifier(
        df,
        "human",
        ["temperature", "humidity", "rainfall", "aqi", "heat_index", "uhi_score"],
        "target_human_risk",
        CLASS_MAPPINGS["human_risk"],
        "human_risk_model.pkl",
    )

    with open(METRICS_PATH, "w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2)
    write_metrics_report(metrics)

    print(f"Trained models saved to {MODEL_DIR}")
    print(f"Metrics saved to {METRICS_PATH} and {REPORT_PATH}")


if __name__ == "__main__":
    train_models()
