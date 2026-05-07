# 🌍 AI-Powered Climate Risk Prediction System for Bengaluru

An intelligent web application that predicts temperature, analyzes climate risks, and visualizes weather patterns for Bengaluru using machine learning and real historical weather data.

## 📋 Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Project](#running-the-project)
- [Libraries Used](#libraries-used)
- [Usage Guide](#usage-guide)

## ✨ Features

- **📊 Climate Dashboard**: View historical temperature trends, humidity distribution, and feature correlations
- **🤖 AI Temperature Prediction**: Predict future temperatures based on rainfall, humidity, and AQI
- **⚠️ Health Risk Assessment**: Evaluate health risks based on current climate conditions
- **📈 Analytics & Statistics**: Monthly and seasonal climate analysis with detailed insights
- **💾 Real-time Data Processing**: Works with actual Bengaluru weather dataset (6,695+ records from 2014-2024)

## 📁 Project Structure

```
DAA-project/
├── data/
│   ├── raw/
│   │   └── bengaluru_weather.csv       # Raw weather data
│   └── processed/
│       └── processed_weather_data.csv  # Processed data
├── ai_models/
│   ├── train.py                        # Model training script
│   └── temperature_model.pkl           # Trained model
├── backend/
│   └── app.py                          # FastAPI backend server
├── frontend/
│   └── app.py                          # Streamlit web interface
├── data_processing.py                  # Data preprocessing script
├── requirements.txt                    # Python dependencies
└── README.md                           # This file
```

## 🔧 Prerequisites

- **Python 3.8+** (tested on Python 3.10+)
- **pip** (Python package manager)
- **Terminal/Command Prompt** (Windows PowerShell, Terminal, or bash)
- **4GB RAM** minimum (for model training)

## 📥 Installation

### Step 1: Clone/Download the Project
```bash
# Clone the repository or download the project
cd DAA-project
```

### Step 2: Create Virtual Environment
```powershell
python -m venv .venv
```

### Step 3: Activate Virtual Environment
```powershell
# For Windows PowerShell
.venv\Scripts\Activate.ps1

# For Mac/Linux
source .venv/bin/activate

# If you get an execution policy error on Windows, run:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

## 🚀 Running the Project

### Complete Workflow (First Time)

#### 1. **Process the Data** (Terminal 1)
```powershell
.venv\Scripts\Activate.ps1
python data_processing.py
```
Output: Loads 6,695 records from bengaluru_weather.csv and saves processed data

#### 2. **Train the Model** (Terminal 1)
```powershell
python ai_models/train.py
```
Output: Trains RandomForest model with MSE metric

#### 3. **Start Backend API** (Terminal 2)
```powershell
.venv\Scripts\Activate.ps1
uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```
✅ Backend running at: `http://localhost:8000`

#### 4. **Start Frontend Dashboard** (Terminal 3)
```powershell
.venv\Scripts\Activate.ps1
streamlit run frontend/app.py
```
✅ Dashboard running at: `http://localhost:8502`

### Quick Start (After Initial Setup)

Just run steps 3 & 4 in two separate terminals - the trained model is already saved!

## 📚 Libraries Used

| Library | Version | Purpose |
|---------|---------|---------|
| **fastapi** | 0.104.1 | Backend API framework |
| **uvicorn** | 0.24.0 | ASGI web server |
| **streamlit** | 1.28.1 | Frontend web interface |
| **pandas** | 2.1.3 | Data processing & analysis |
| **scikit-learn** | 1.3.2 | Machine learning models |
| **plotly** | 5.17.0 | Interactive visualizations |
| **requests** | 2.31.0 | HTTP client for API calls |
| **xgboost** | 2.0.0 | Gradient boosting (optional) |
| **folium** | 0.15.1 | Map visualizations |
| **streamlit-folium** | 0.13.0 | Folium integration for Streamlit |
| **pymongo** | 4.6.0 | MongoDB support (optional) |
| **python-dotenv** | 1.0.0 | Environment variables |

## 📖 Usage Guide

### 🎯 Dashboard Tab
- View summary statistics (temperature, humidity, rainfall, AQI)
- Analyze temperature trends over time
- Check humidity distribution
- Explore feature correlations

### 🤖 AI Prediction Tab
- Use sliders to set rainfall, humidity, and AQI
- Click "🔮 Predict Temperature" button
- Get predicted temperature based on ML model
- Compare with historical average

### ⚠️ Health Risk Tab
- Set current environmental conditions
- Click "📋 Check Health Risk" button
- Get risk level (Low/Moderate/High)
- View specific risk factors

### 📈 Analytics Tab
- View monthly climate statistics table
- Analyze seasonal patterns
- See key insights (warmest/coldest/wettest seasons)
- Download data if needed

## 🔌 API Endpoints

### Backend Endpoints (http://localhost:8000)

**GET /weather**
- Returns latest weather data
- Response: JSON with temperature, humidity, rainfall, AQI

**POST /predict**
```json
{
  "rainfall": 0.5,
  "humidity": 60,
  "aqi": 50
}
```
- Returns: `{"predicted_temperature": 26.5}`

**POST /health_risk**
```json
{
  "temperature": 28.0,
  "humidity": 70,
  "aqi": 100
}
```
- Returns: `{"risk": "Moderate"}`

## 🐛 Troubleshooting

### Issue: ModuleNotFoundError
**Solution**: Make sure virtual environment is activated
```powershell
.venv\Scripts\Activate.ps1
```

### Issue: Port already in use
**Solution**: Change port numbers in commands:
```powershell
# For backend (use different port, e.g., 8001)
uvicorn backend.app:app --reload --host 127.0.0.1 --port 8001
```

### Issue: Data processing fails
**Solution**: Ensure bengaluru_weather.csv is in `data/raw/` directory

### Issue: Model prediction fails
**Solution**: Re-train the model
```powershell
python ai_models/train.py
```

## 📊 Data Information

**Dataset**: Bengaluru Historical Weather Data
- **Time Period**: 2014-2024 (10 years)
- **Records**: 6,695 observations
- **Features**: 
  - Temperature (Celsius)
  - Humidity (%)
  - Rainfall (inches)
  - AQI (Air Quality Index)
  - Date

## 🎓 Model Details

- **Algorithm**: Random Forest Regressor
- **Target Variable**: Temperature (°C)
- **Features**: Rainfall, Humidity, AQI
- **Test Size**: 20%
- **Model Accuracy**: MSE = 7.3

## 📝 Notes

- Temperature is displayed in **Celsius** throughout the application
- All data is cached to prevent flickering and improve performance
- Backend auto-reloads on code changes (when `--reload` flag is used)
- Frontend auto-reloads on file changes (Streamlit default)

## 🔐 Data Privacy

- No sensitive data is stored
- All processing is local to your machine
- No external API calls (except weather data import)

## 📞 Support

If you encounter issues:
1. Ensure virtual environment is activated
2. Verify port 8000 and 8502 are not in use
3. Check that all dependencies are installed: `pip install -r requirements.txt --upgrade`
4. Verify the dataset file `bengaluru_weather.csv` is in `data/raw/` directory
5. Re-train the model if predictions fail: `python ai_models/train.py`
6. Check Python version: `python --version` (should be 3.8+)

## 📄 License

This project is for educational purposes.

---

**Happy Climate Forecasting! 🌡️📊**
