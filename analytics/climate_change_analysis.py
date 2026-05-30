import pandas as pd
import numpy as np
import plotly.graph_objects as go

def get_historical_climate_data():
    """Generates synthetic historical climate data for Bengaluru (2005-2026)."""
    np.random.seed(42)
    years = np.arange(2005, 2027)
    
    # Simulate realistic climate change trends
    temp = 23.5 + np.linspace(0, 1.8, len(years)) + np.random.normal(0, 0.2, len(years))
    rain = 950 - np.linspace(0, 150, len(years)) + np.random.normal(0, 40, len(years))
    aqi = 65 + np.linspace(0, 85, len(years)) + np.random.normal(0, 8, len(years))
    
    urban_growth = 28 + np.linspace(0, 32, len(years)) # 28% to 60%
    green_cover = 45 - np.linspace(0, 25, len(years)) # 45% to 20%
    water_bodies = 12 - np.linspace(0, 7, len(years)) # 12% to 5%
    
    return pd.DataFrame({
        'Year': years,
        'Temperature_C': temp,
        'Rainfall_mm': rain,
        'AQI': aqi,
        'Urban_Area_wt': urban_growth,
        'Green_Cover_wt': green_cover,
        'Water_Bodies_wt': water_bodies
    })

def plot_temperature_trend(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Year'], y=df['Temperature_C'], mode='lines+markers', 
                             name='Avg Temp', line=dict(color='#FF5733', width=3)))
    fig.update_layout(
        title="Yearly Temperature Rise", 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', 
        font=dict(color='#E6E8EF'), 
        yaxis_title="Temperature (°C)",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def plot_rainfall_trend(df):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['Year'], y=df['Rainfall_mm'], name='Rainfall', marker_color='#00D4FF'))
    fig.update_layout(
        title="Rainfall Variation (mm)", 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', 
        font=dict(color='#E6E8EF'), 
        yaxis_title="Rainfall (mm)",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def plot_aqi_trend(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Year'], y=df['AQI'], fill='tozeroy', 
                             name='AQI Trend', line=dict(color='#FFB830', width=2)))
    fig.update_layout(
        title="Air Quality Index (AQI) Deterioration", 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', 
        font=dict(color='#E6E8EF'), 
        yaxis_title="AQI",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def plot_land_use_changes(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Year'], y=df['Urban_Area_wt'], mode='lines', name='Urban Growth (%)', line=dict(color='#A8B2C1', width=3)))
    fig.add_trace(go.Scatter(x=df['Year'], y=df['Green_Cover_wt'], mode='lines', name='Green Cover (%)', line=dict(color='#39FF14', width=3)))
    fig.add_trace(go.Scatter(x=df['Year'], y=df['Water_Bodies_wt'], mode='lines', name='Water Bodies (%)', line=dict(color='#00D4FF', width=3)))
    fig.update_layout(
        title="Land Use Changes (2005-2026)", 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', 
        font=dict(color='#E6E8EF'), 
        yaxis_title="Percentage Area (%)",
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

def generate_insights(df):
    dFirst = df.iloc[0]
    dLast = df.iloc[-1]
    
    temp_diff = dLast['Temperature_C'] - dFirst['Temperature_C']
    rain_diff = dFirst['Rainfall_mm'] - dLast['Rainfall_mm'] 
    aqi_diff = dLast['AQI'] - dFirst['AQI']
    urban_diff = dLast['Urban_Area_wt'] - dFirst['Urban_Area_wt']
    green_diff = dFirst['Green_Cover_wt'] - dLast['Green_Cover_wt']
    water_diff = dFirst['Water_Bodies_wt'] - dLast['Water_Bodies_wt']
    
    insights = [
        f"🌡️ **Temperature Rise**: Average temperature increased by **{temp_diff:.1f}°C** between 2005 and 2026.",
        f"🌧️ **Rainfall Deficit**: Annual rainfall volume decreased by **{rain_diff:.0f} mm** over the last 2 decades.",
        f"🌫️ **Pollution Spike**: AQI levels deteriorated, increasing by **{aqi_diff:.0f} points**.",
        f"🏙️ **Urbanization**: Urban built-up area expanded by **{urban_diff:.1f}%**, replacing critical natural habitats.",
        f"🌳 **Deforestation**: Green cover reduced drastically by **{green_diff:.1f}%**.",
        f"💧 **Water Scarcity**: Water bodies shrunk by **{water_diff:.1f}%**, contributing to recent urban flood vulnerabilities."
    ]
    return insights
