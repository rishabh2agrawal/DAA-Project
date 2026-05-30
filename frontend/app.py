import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from streamlit_folium import st_folium
try:
    from maps.geo_utils import generate_spatial_mock_data
    from maps.heatmap_generator import (
        generate_temperature_heatmap,
        generate_aqi_heatmap,
        generate_flood_heatmap,
        generate_dengue_heatmap
    )
except ImportError as e:
    st.error(f"Cannot load mapping modules: {e}")

try:
    from analytics.climate_change_analysis import (
        get_historical_climate_data,
        plot_temperature_trend,
        plot_rainfall_trend,
        plot_aqi_trend,
        plot_land_use_changes,
        generate_insights
    )
except ImportError as e:
    st.error(f"Cannot load analytics modules: {e}")

st.set_page_config(
        page_title="ClimateIQ Bengaluru",
        page_icon="🌍",
        layout="wide",
        initial_sidebar_state="expanded",
)

st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

:root {
    --bg: #0A0E1A;
    --panel: rgba(30, 42, 58, 0.55);
    --panel-strong: rgba(30, 42, 58, 0.75);
    --border: rgba(255, 255, 255, 0.08);
    --text: #E6E8EF;
    --muted: #A8B2C1;
    --cyan: #00D4FF;
    --green: #39FF14;
    --amber: #FFB830;
    --red: #FF4D4D;
}

html, body, [class*="css"], .stApp {
    background: var(--bg);
    color: var(--text);
    font-family: 'Inter', sans-serif;
}

header, footer, #MainMenu {
    visibility: hidden;
    height: 0;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0B1327 0%, #0A0E1A 100%);
    border-right: 1px solid var(--border);
}

.sidebar-title {
    font-size: 1.2rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    color: var(--text);
    margin-bottom: 0.5rem;
}

.hero {
    padding: 1.5rem 0 1rem 0;
}

.hero-title {
    font-size: 3rem;
    font-weight: 800;
    line-height: 1.05;
    background: linear-gradient(90deg, #00D4FF 0%, #39FF14 50%, #FFB830 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    margin-bottom: 0.25rem;
}

.hero-subtitle {
    color: var(--muted);
    font-size: 1.05rem;
}

.glass-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1rem 1.1rem;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
}

.metric-card {
    border-radius: 16px;
    padding: 1.1rem 1.2rem;
    border: 1px solid rgba(0, 212, 255, 0.25);
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.08), rgba(57, 255, 20, 0.04));
    box-shadow: 0 0 20px rgba(0, 212, 255, 0.15);
}

.metric-label {
    color: var(--muted);
    font-size: 0.9rem;
    margin-bottom: 0.25rem;
}

.metric-value {
    font-size: 1.8rem;
    font-weight: 700;
}

.metric-sub {
    color: var(--muted);
    font-size: 0.85rem;
}

.section-title {
    font-size: 1.3rem;
    font-weight: 700;
    margin: 0.5rem 0 0.75rem 0;
}

.control-panel {
    background: var(--panel-strong);
    border: 1px solid rgba(0, 212, 255, 0.25);
    border-radius: 18px;
    padding: 1rem 1.2rem 0.5rem 1.2rem;
    box-shadow: 0 0 24px rgba(0, 212, 255, 0.12);
}

.result-card {
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.08), rgba(255, 184, 48, 0.08));
    border: 1px solid rgba(0, 212, 255, 0.3);
    border-radius: 18px;
    padding: 1rem 1.2rem;
}

.risk-card {
    border-radius: 18px;
    padding: 1rem 1.2rem;
    font-weight: 700;
    text-align: left;
}

.risk-low {
    border: 1px solid rgba(57, 255, 20, 0.6);
    box-shadow: 0 0 20px rgba(57, 255, 20, 0.2);
    background: rgba(57, 255, 20, 0.08);
}

.risk-moderate {
    border: 1px solid rgba(255, 184, 48, 0.6);
    box-shadow: 0 0 20px rgba(255, 184, 48, 0.2);
    background: rgba(255, 184, 48, 0.08);
}

.risk-high {
    border: 1px solid rgba(255, 77, 77, 0.7);
    box-shadow: 0 0 24px rgba(255, 77, 77, 0.3);
    background: rgba(255, 77, 77, 0.1);
}

.chip {
    display: inline-block;
    padding: 0.3rem 0.6rem;
    border-radius: 999px;
    background: rgba(0, 212, 255, 0.12);
    border: 1px solid rgba(0, 212, 255, 0.35);
    color: var(--text);
    margin-right: 0.4rem;
    margin-bottom: 0.4rem;
    font-size: 0.85rem;
}

.callout {
    padding: 0.8rem 1rem;
    border-left: 4px solid var(--cyan);
    background: rgba(30, 42, 58, 0.6);
    border-radius: 12px;
    margin-bottom: 0.6rem;
}

.stButton>button {
    background: linear-gradient(90deg, #00D4FF 0%, #39FF14 100%);
    color: #0A0E1A;
    border: none;
    border-radius: 999px;
    padding: 0.6rem 1.2rem;
    font-weight: 700;
    box-shadow: 0 8px 18px rgba(0, 212, 255, 0.25);
}

.stButton>button:hover {
    filter: brightness(1.05);
    box-shadow: 0 10px 24px rgba(0, 212, 255, 0.35);
}

[data-baseweb="slider"] .rc-slider-track {
    background: var(--cyan);
}

[data-baseweb="slider"] .rc-slider-handle {
    border: solid 2px var(--cyan);
    background: var(--bg);
    box-shadow: 0 0 10px rgba(0, 212, 255, 0.6);
}

.stPlotlyChart > div {
    background: transparent !important;
}
</style>
""",
        unsafe_allow_html=True,
)

# Backend URL
backend_url = "http://localhost:8000"

# Cache functions to prevent flickering
@st.cache_data
def load_data():
    data_path = os.path.join('data', 'processed', 'processed_weather_data.csv')
    if os.path.exists(data_path):
        df = pd.read_csv(data_path).replace(-999, pd.NA)
        df['date'] = pd.to_datetime(df['date'])
        numeric_cols = df.columns.difference(['date', 'season', 'temp_class', 'rain_class', 'human_risk'])
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
        if 'temperature' not in df.columns and 'temperature_avg' in df.columns:
            df['temperature'] = df['temperature_avg']
        return df
    return None

@st.cache_data
def calculate_monthly_stats(df):
    df_copy = df.copy()
    df_copy['month'] = df_copy['date'].dt.to_period('M')
    monthly_stats = df_copy.groupby('month').agg({
        'temperature': ['mean', 'max', 'min'],
        'humidity': 'mean',
        'rainfall': 'sum',
        'aqi': 'mean'
    }).reset_index()
    
    monthly_stats.columns = ['Month', 'Avg Temp', 'Max Temp', 'Min Temp', 'Avg Humidity', 'Total Rain', 'Avg AQI']
    monthly_stats['Month'] = monthly_stats['Month'].astype(str)
    return monthly_stats

@st.cache_data
def calculate_seasonal_stats(df):
    df_copy = df.copy()
    df_copy['season'] = df_copy['date'].dt.month.map({
        12: 'Winter', 1: 'Winter', 2: 'Winter',
        3: 'Summer', 4: 'Summer', 5: 'Summer',
        6: 'Monsoon', 7: 'Monsoon', 8: 'Monsoon', 9: 'Monsoon',
        10: 'Post-Monsoon', 11: 'Post-Monsoon'
    })
    
    seasonal_data = df_copy.groupby('season').agg({
        'temperature': 'mean',
        'aqi': 'mean',
        'rainfall': 'mean'
    }).round(2)
    
    seasonal_data.columns = ['Avg Temp (°C)', 'Avg AQI', 'Avg Rainfall (in)']
    season_order = ['Winter', 'Summer', 'Monsoon', 'Post-Monsoon']
    seasonal_data = seasonal_data.reindex(season_order)
    return seasonal_data

@st.cache_data(ttl=60)
def fetch_weather():
    try:
        response = requests.get(f"{backend_url}/weather", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

# Load processed data for visualization
df = load_data()
if df is None:
    st.warning("Processed data not found. Please run data_processing.py first.")

st.markdown(
    """
<div class="hero">
  <div class="hero-title">🌍 ClimateIQ Bengaluru</div>
  <div class="hero-subtitle">AI-powered climate intelligence for risk, resilience, and health planning.</div>
</div>
""",
    unsafe_allow_html=True,
)

weather = fetch_weather()

st.sidebar.markdown('<div class="sidebar-title">Live Weather Snapshot</div>', unsafe_allow_html=True)
if weather:
    st.sidebar.markdown(
        f"""
<div class="glass-card">
  <div class="metric-label">Temperature</div>
  <div class="metric-value">{weather.get('temperature', 0):.1f}°C</div>
  <div class="metric-label">Humidity</div>
  <div class="metric-value">{weather.get('humidity', 0):.0f}%</div>
  <div class="metric-label">Rainfall</div>
  <div class="metric-value">{weather.get('rainfall', 0):.2f} in</div>
  <div class="metric-label">AQI</div>
  <div class="metric-value">{weather.get('aqi', 0):.0f}</div>
</div>
""",
        unsafe_allow_html=True,
    )
else:
    st.sidebar.markdown(
        '<div class="glass-card">Weather service offline.</div>',
        unsafe_allow_html=True,
    )

st.sidebar.markdown("---")
page = st.sidebar.radio(
    "View",
    ["🌍 Climate Risk Dashboard", "🗓️ Seasonal Analytics", "📈 Climate Trend", "🔮 Future Forecast", "🗺️ Spatial Heatmaps", "🌱 Env Change Analysis"],
    index=0,
    label_visibility="collapsed",
)

if page == "🌍 Climate Risk Dashboard":
    st.markdown('<div class="section-title">Current Conditions & Risk Indicators</div>', unsafe_allow_html=True)
    
    if df is not None and weather is not None:
        curr_temp = weather.get('temperature', 0)
        curr_humidity = weather.get('humidity', 0)
        curr_rain = weather.get('rainfall', 0)
        curr_aqi = weather.get('aqi', 0)

        # Section A: Current Conditions
        st.markdown('<div class="section-title">A. Current Conditions</div>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">🌡️ Temperature</div><div class="metric-value">{curr_temp:.1f}°C</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><div class="metric-label">🌫️ AQI</div><div class="metric-value">{curr_aqi:.0f}</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><div class="metric-label">💧 Humidity</div><div class="metric-value">{curr_humidity:.1f}%</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card"><div class="metric-label">🌧️ Rainfall</div><div class="metric-value">{curr_rain:.2f} in</div></div>', unsafe_allow_html=True)
        
        st.divider()

        # Fetch live risks based on current weather
        try:
            hw_res = requests.post(f"{backend_url}/predict_heatwave", json={"temperature": curr_temp, "humidity": curr_humidity, "aqi": curr_aqi, "rainfall": curr_rain}, timeout=5).json().get('risk', 'Low')
            fl_res = requests.post(f"{backend_url}/predict_flood", json={"temperature": curr_temp, "humidity": curr_humidity, "aqi": curr_aqi, "rainfall": curr_rain}, timeout=5).json().get('risk', 'Low')
            dg_res = requests.post(f"{backend_url}/predict_dengue", json={"temperature": curr_temp, "humidity": curr_humidity, "aqi": curr_aqi, "rainfall": curr_rain}, timeout=5).json().get('risk', 'Low')
            pl_res = "Severe" if curr_aqi > 200 else "High" if curr_aqi > 150 else "Moderate" if curr_aqi > 100 else "Low"
        except:
            hw_res = fl_res = dg_res = pl_res = "Unknown"

        # Section B: Risk Indicators
        st.markdown('<div class="section-title">B. Risk Indicators</div>', unsafe_allow_html=True)
        r1, r2, r3, r4 = st.columns(4)
        
        def risk_color(risk):
            if risk in ['Low', 'Normal']: return 'rgba(57,255,20,0.1)'
            elif risk in ['Medium', 'Moderate']: return 'rgba(255,184,48,0.2)'
            else: return 'rgba(255,77,77,0.3)'

        with r1: st.markdown(f'<div class="result-card" style="background: {risk_color(hw_res)}; height: 100%;">🔥 Heatwave Risk<br><b>{hw_res}</b></div>', unsafe_allow_html=True)
        with r2: st.markdown(f'<div class="result-card" style="background: {risk_color(fl_res)}; height: 100%;">🌊 Flood Risk<br><b>{fl_res}</b></div>', unsafe_allow_html=True)
        with r3: st.markdown(f'<div class="result-card" style="background: {risk_color(dg_res)}; height: 100%;">🦟 Dengue Risk<br><b>{dg_res}</b></div>', unsafe_allow_html=True)
        with r4: st.markdown(f'<div class="result-card" style="background: {risk_color(pl_res)}; height: 100%;">🌫️ Pollution Risk<br><b>{pl_res}</b></div>', unsafe_allow_html=True)

    else:
        st.error("Data unavailable to generate climate risk dashboard.")

elif page == "🗓️ Seasonal Analytics":
    st.markdown('<div class="section-title">C. Seasonal Analysis</div>', unsafe_allow_html=True)
    if df is not None:
        seasonal_data = calculate_seasonal_stats(df)
        cols = st.columns(4)
        
        for i, season in enumerate(['Winter', 'Summer', 'Monsoon', 'Post-Monsoon']):
            if season in seasonal_data.index:
                row = seasonal_data.loc[season]
                avg_t = row['Avg Temp (°C)']
                avg_a = row['Avg AQI']
                avg_r = row['Avg Rainfall (in)']
                
                # Heuristic risk summary for season overview
                summary = []
                if avg_t > 30: summary.append("Heat")
                if avg_a > 120: summary.append("Pollution")
                if avg_r > 50: summary.append("Flood")
                risk_str = ", ".join(summary) if summary else "Stable"

                with cols[i]:
                    st.markdown(f"""
                    <div class="glass-card" style="margin-bottom: 1rem; text-align: center;">
                        <h3 style="color: var(--cyan); margin-top: 0;">{season}</h3>
                        <div style="font-size: 0.9rem; color: var(--muted); margin: 4px 0;">🌡️ {avg_t:.1f}°C</div>
                        <div style="font-size: 0.9rem; color: var(--muted); margin: 4px 0;">🌫️ AQI {avg_a:.0f}</div>
                        <div style="font-size: 0.9rem; color: var(--muted); margin: 4px 0;">🌧️ {avg_r:.1f} in</div>
                        <div style="margin-top: 10px; font-weight: bold; font-size: 0.9rem; color: var(--amber);">⚠️ Risks: {risk_str}</div>
                    </div>""", unsafe_allow_html=True)
        
        st.divider()
        st.markdown('<div class="section-title">🌡️ Seasonal Radar</div>', unsafe_allow_html=True)
        seasons = seasonal_data.index.tolist()
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=seasonal_data['Avg Temp (°C)'], theta=seasons, fill='toself', name='Temp (°C)', line_color='#00D4FF'))
        fig_radar.add_trace(go.Scatterpolar(r=seasonal_data['Avg AQI']/5, theta=seasons, fill='toself', name='AQI (scaled)', line_color='#FFB830'))
        fig_radar.add_trace(go.Scatterpolar(r=seasonal_data['Avg Rainfall (in)'], theta=seasons, fill='toself', name='Rainfall (in)', line_color='#39FF14'))
        fig_radar.update_layout(height=420, polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(gridcolor='rgba(255,255,255,0.08)', tickfont_color='#A8B2C1')), paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#E6E8EF'))
        st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})
        
elif page == "📈 Climate Trend":
    st.markdown('<div class="section-title">Data Trends & Analytics</div>', unsafe_allow_html=True)
    
    if df is not None:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="section-title">📈 Temperature Trend</div>', unsafe_allow_html=True)
            fig_temp = go.Figure()
            fig_temp.add_trace(
                go.Scatter(
                    x=df['date'],
                    y=df['temperature'],
                    mode='lines',
                    line=dict(color='#00D4FF', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(0, 212, 255, 0.15)',
                )
            )
            fig_temp.update_layout(
                height=380,
                margin=dict(l=10, r=10, t=20, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.08)', title=''),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.08)', title='Temperature (°C)'),
                font=dict(color='#E6E8EF'),
            )
            st.plotly_chart(fig_temp, use_container_width=True, config={"displayModeBar": False})

        with col2:
            st.markdown('<div class="section-title">💧 Humidity Profile</div>', unsafe_allow_html=True)
            fig_humidity = go.Figure()
            fig_humidity.add_trace(
                go.Violin(
                    y=df['humidity'],
                    line_color='#39FF14',
                    fillcolor='rgba(57, 255, 20, 0.2)',
                    box_visible=True,
                    meanline_visible=True,
                )
            )
            fig_humidity.update_layout(
                height=380,
                margin=dict(l=10, r=10, t=20, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.08)', title='Humidity (%)'),
                font=dict(color='#E6E8EF'),
                showlegend=False,
            )
            st.plotly_chart(fig_humidity, use_container_width=True, config={"displayModeBar": False})

        st.markdown('<div class="section-title">🔗 Feature Correlations (Temp, Rain, Hum, AQI)</div>', unsafe_allow_html=True)
        corr_matrix = df[['temperature', 'rainfall', 'humidity', 'aqi']].corr()
        fig_corr = go.Figure(
            data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale=[[0.0, '#00D4FF'], [0.5, '#1E2A3A'], [1.0, '#FFB830']],
                text=corr_matrix.values.round(2),
                texttemplate='%{text}',
                textfont={"size": 12, "color": "#E6E8EF"},
            )
        )
        fig_corr.update_layout(
            height=380, margin=dict(l=10, r=10, t=20, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#E6E8EF'),
        )
        st.plotly_chart(fig_corr, use_container_width=True, config={"displayModeBar": False})

elif page == "🔮 Future Forecast":
    st.markdown('<div class="section-title">D. Future Forecast Simulator</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-sub" style="margin-bottom: 1rem;">Simulate environmental variables to generate multi-dimensional climate forecasts and risk alerts.</div>', unsafe_allow_html=True)

    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: f_temp = st.slider("Temperature (°C)", 10.0, 50.0, 25.0)
    with c2: f_hum = st.slider("Humidity (%)", 0, 100, 60)
    with c3: f_rain = st.slider("Rainfall (in)", 0.0, 15.0, 1.0)
    with c4: f_aqi = st.slider("Current AQI", 0, 500, 50)
    
    c5, c6, c7, c8 = st.columns(4)
    with c5: f_wind = st.slider("Wind (km/h)", 0.0, 50.0, 10.0)
    with c6: f_hist = st.slider("Hist. Rain (in)", 0.0, 50.0, 5.0)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🔮 Generate Complete Forecast", use_container_width=True):
        with st.spinner("Processing massive-scale climate models..."):
            try:
                req_data = {
                    "temperature": f_temp, "humidity": f_hum, "rainfall": f_rain, 
                    "aqi": f_aqi, "wind_speed": f_wind, "historical_rainfall": f_hist
                }
                
                p_temp = requests.post(f"{backend_url}/predict", json=req_data, timeout=5).json().get('predicted_temperature', 0)
                p_aqi = requests.post(f"{backend_url}/predict_aqi", json=req_data, timeout=5).json().get('predicted_aqi', 0)
                p_rain = requests.post(f"{backend_url}/predict_rainfall", json=req_data, timeout=5).json().get('category', 'Unknown')
                
                r_hw = requests.post(f"{backend_url}/predict_heatwave", json=req_data, timeout=5).json().get('risk', 'Low')
                r_fl = requests.post(f"{backend_url}/predict_flood", json=req_data, timeout=5).json().get('risk', 'Low')
                r_dg = requests.post(f"{backend_url}/predict_dengue", json=req_data, timeout=5).json().get('risk', 'Low')

                st.markdown('<div class="section-title" style="margin-top: 2rem;">Forecast Outcomes</div>', unsafe_allow_html=True)
                o1, o2, o3 = st.columns(3)
                with o1: st.markdown(f'<div class="metric-card"><div class="metric-label">🌡️ Expected Temp</div><div class="metric-value" style="color:var(--cyan)">{p_temp:.1f}°C</div></div>', unsafe_allow_html=True)
                with o2: st.markdown(f'<div class="metric-card"><div class="metric-label">🌫️ Expected AQI</div><div class="metric-value" style="color:var(--amber)">{p_aqi:.0f}</div></div>', unsafe_allow_html=True)
                with o3: st.markdown(f'<div class="metric-card"><div class="metric-label">🌧️ Rainfall Category</div><div class="metric-value" style="color:var(--green)">{p_rain}</div></div>', unsafe_allow_html=True)

                st.markdown('<div class="section-title">Predicted Risk Levels</div>', unsafe_allow_html=True)
                r1, r2, r3 = st.columns(3)
                def rc(risk): return 'rgba(57,255,20,0.1)' if risk in ['Low'] else 'rgba(255,184,48,0.2)' if risk in ['Medium', 'Moderate'] else 'rgba(255,77,77,0.3)'
                
                with r1: st.markdown(f'<div class="result-card" style="background: {rc(r_hw)}">🔥 Heatwave: <b>{r_hw}</b></div>', unsafe_allow_html=True)
                with r2: st.markdown(f'<div class="result-card" style="background: {rc(r_fl)}">🌊 Flood: <b>{r_fl}</b></div>', unsafe_allow_html=True)
                with r3: st.markdown(f'<div class="result-card" style="background: {rc(r_dg)}">🦟 Dengue: <b>{r_dg}</b></div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error communicating with AI models: {e}")

elif page == "🗺️ Spatial Heatmaps":
    st.markdown('<div class="section-title">E. Geospatial Climate Visualization</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-sub" style="margin-bottom: 1rem;">Explore simulated risk and feature heatmaps across the Bengaluru region overlayed on live maps.</div>', unsafe_allow_html=True)

    try:
        if 'geo_df' not in st.session_state:
            st.session_state.geo_df = generate_spatial_mock_data(n_points=300)
    except NameError:
        st.warning("Mapping modules not available. Make sure geopandas and folium are installed.")
    else:
        map_type = st.radio(
            "Select Heatmap Layer:",
            ["🌡️ Temperature", "🌫️ AQI", "🌊 Flood Risk", "🦟 Dengue Risk"],
            horizontal=True
        )

        st.markdown('<div class="glass-card" style="padding: 10px; margin-top: 10px;">', unsafe_allow_html=True)
        
        with st.spinner("Generating Map Layer..."):
            if map_type == "🌡️ Temperature":
                m = generate_temperature_heatmap(st.session_state.geo_df)
                st.caption("Temperature Gradient: Green (Cooler) ➔ Yellow (Warm) ➔ Red (Hot / Heat island)")
            elif map_type == "🌫️ AQI":
                m = generate_aqi_heatmap(st.session_state.geo_df)
                st.caption("AQI Gradient: Green (Good) ➔ Yellow (Moderate) ➔ Red/Purple (Unhealthy/Severe)")
            elif map_type == "🌊 Flood Risk":
                m = generate_flood_heatmap(st.session_state.geo_df)
                st.caption("Flood Risk Gradient: Light Blue (Safe) ➔ Dark Blue (High PRone Area)")
            else:
                m = generate_dengue_heatmap(st.session_state.geo_df)
                st.caption("Dengue Risk Gradient: Yellow (Low) ➔ Orange (Medium) ➔ Red (High Mosquito Zone)")

            st_data = st_folium(m, width=1000, height=500)
            
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "🌱 Env Change Analysis":
    st.markdown('<div class="section-title">Environmental Change Analysis (2005-2026)</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-sub" style="margin-bottom: 1rem;">Analyzing decades of climate variations and urban transformation in Bengaluru highlighting the impact of rapid development.</div>', unsafe_allow_html=True)

    try:
        hist_df = get_historical_climate_data()
        insights = generate_insights(hist_df)
        
        st.markdown('<div class="glass-card" style="padding: 20px; margin-bottom: 25px;">', unsafe_allow_html=True)
        st.markdown('#### 💡 Key Automated Insights')
        for insight in insights:
            st.markdown(f"- {insight}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">Decadal Trend Charts</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(plot_temperature_trend(hist_df), use_container_width=True, config={"displayModeBar": False})
        with c2:
            st.plotly_chart(plot_aqi_trend(hist_df), use_container_width=True, config={"displayModeBar": False})
            
        c3, c4 = st.columns(2)
        with c3:
            st.plotly_chart(plot_rainfall_trend(hist_df), use_container_width=True, config={"displayModeBar": False})
        with c4:
            st.plotly_chart(plot_land_use_changes(hist_df), use_container_width=True, config={"displayModeBar": False})
            
    except NameError:
        st.error("Historical analytics libraries could not be loaded.")
