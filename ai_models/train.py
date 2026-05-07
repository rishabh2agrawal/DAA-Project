import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

# Load processed data
data_path = 'data/processed/processed_weather_data.csv'
df = pd.read_csv(data_path)

# Features and target (predict temperature)
features = ['rainfall', 'humidity', 'aqi']
target = 'temperature'

X = df[features]
y = df[target]

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestRegressor(n_estimators=10, random_state=42)
model.fit(X_train, y_train)

# Evaluate
predictions = model.predict(X_test)
mse = mean_squared_error(y_test, predictions)
print(f'MSE: {mse}')

# Save model
with open('ai_models/temperature_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("Model trained and saved.")