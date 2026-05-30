import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report

# Load processed data
data_path = 'data/processed/processed_weather_data.csv'
df = pd.read_csv(data_path)

# Features and multi-class target
features = ['rainfall', 'humidity', 'aqi', 'LST', 'NDVI', 'NDBI', 'temperature_avg']
target = 'human_risk'

# Encode target
target_mapping = {'Low': 0, 'Moderate': 1, 'High': 2}
df['target_encoded'] = df[target].map(target_mapping)

X = df[features]
y = df['target_encoded']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Multi-Modal Hybrid Ensembles (XGBoost)
model = XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
model.fit(X_train, y_train)

# Evaluate
predictions = model.predict(X_test)
acc = accuracy_score(y_test, predictions)
print(f'Accuracy: {acc:.4f}')
print(classification_report(y_test, predictions, target_names=['Low', 'Moderate', 'High']))

# Save model
with open('ai_models/hybrid_risk_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print('Advanced Risk Model trained and saved.')
