import os
import sys

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
from streamlit_folium import st_folium

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

try:
    from maps.geo_utils import generate_spatial_mock_data
    from maps.heatmap_generator import (
        generate_aqi_heatmap,
        generate_dengue_heatmap,
        generate_flood_heatmap,
        generate_temperature_heatmap,
        generate_uhi_heatmap,
    )
except ImportError as exc:
    st.error(f"Cannot load mapping modules: {exc}")

try:
    from analytics.climate_change_analysis import (
        generate_insights,
        get_historical_climate_data,
        plot_aqi_trend,
        plot_land_use_changes,
        plot_rainfall_trend,
        plot_temperature_trend,
    )
except ImportError as exc:
    st.error(f"Cannot load analytics modules: {exc}")


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="ClimateIQ Bengaluru", page_icon="CI", layout="wide", initial_sidebar_state="expanded")
st.markdown(
    """
<style>
:root {
    --bg: #0A0E1A;
    --panel: rgba(30, 42, 58, 0.62);
    --border: rgba(255, 255, 255, 0.1);
    --text: #E6E8EF;
    --muted: #A8B2C1;
    --cyan: #00D4FF;
    --green: #39FF14;
    --amber: #FFB830;
    --red: #FF4D4D;
}
html, body, .stApp { background: var(--bg); color: var(--text); }
header, footer, #MainMenu { visibility: hidden; height: 0; }
[data-testid="stSidebar"] { background: #0B1327; border-right: 1px solid var(--border); }
.hero { padding: 1.3rem 0 0.8rem 0; }
.hero-title { font-size: 2.6rem; font-weight: 800; color: var(--text); margin-bottom: 0.15rem; }
.hero-subtitle { color: var(--muted); font-size: 1rem; }
.section-title { font-size: 1.25rem; font-weight: 700; margin: 0.7rem 0 0.75rem 0; }
.glass-card, .metric-card, .result-card, .callout {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.1rem;
    box-shadow: 0 8px 24px rgba(0,0,0,0.25);
}
.metric-card { border-color: rgba(0, 212, 255, 0.25); min-height: 116px; }
.metric-label { color: var(--muted); font-size: 0.88rem; margin-bottom: 0.25rem; }
.metric-value { font-size: 1.65rem; font-weight: 700; }
.metric-sub { color: var(--muted); font-size: 0.84rem; }
.callout { border-left: 4px solid var(--cyan); margin-bottom: 0.8rem; color: var(--muted); }
.control-panel { background: rgba(30,42,58,0.78); border: 1px solid rgba(0,212,255,0.25); border-radius: 10px; padding: 1rem; }
.stButton>button { background: var(--cyan); color: #06101A; border: 0; border-radius: 8px; font-weight: 700; }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    path = os.path.join("data", "processed", "processed_weather_data.csv")
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path).replace(-999, pd.NA)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    text_cols = ["date", "season", "temp_class", "rain_class", "aqi_class", "human_risk", "flood_risk", "dengue_risk", "heatwave_risk"]
    numeric_cols = df.columns.difference(text_cols)
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
    if "temperature" not in df.columns and "temperature_avg" in df.columns:
        df["temperature"] = df["temperature_avg"]
    return df.dropna(subset=["date", "temperature", "rainfall", "humidity", "aqi"])


@st.cache_data
def seasonal_stats(df):
    order = ["Winter", "Summer", "Monsoon", "Post-Monsoon"]
    grouped = df.groupby("season").agg(
        avg_temp=("temperature", "mean"),
        avg_aqi=("aqi", "mean"),
        avg_rain=("rainfall", "mean"),
        dominant_risk=("human_risk", lambda x: x.mode().iloc[0] if not x.mode().empty else "Low"),
    )
    return grouped.reindex(order).round(2)


@st.cache_data(ttl=60)
def api_get(path):
    try:
        response = requests.get(f"{BACKEND_URL}{path}", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        return None
    return None


def api_post(path, payload):
    response = requests.post(f"{BACKEND_URL}{path}", json=payload, timeout=8)
    response.raise_for_status()
    return response.json()


def method_note(text):
    st.markdown(f'<div class="callout"><b>Data Source / Method:</b> {text}</div>', unsafe_allow_html=True)


def metric_card(label, value, sub=""):
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-sub">{sub}</div></div>',
        unsafe_allow_html=True,
    )


def risk_color(risk):
    if risk in ["Low", "Good", "Normal"]:
        return "rgba(57,255,20,0.12)"
    if risk in ["Moderate", "Medium", "Hot"]:
        return "rgba(255,184,48,0.16)"
    return "rgba(255,77,77,0.2)"


df = load_data()
weather = api_get("/weather")

st.markdown(
    """
<div class="hero">
  <div class="hero-title">ClimateIQ Bengaluru</div>
  <div class="hero-subtitle">Project-ready climate prediction, risk analytics, and proxy spatial intelligence for Bengaluru.</div>
</div>
""",
    unsafe_allow_html=True,
)

st.sidebar.markdown("### Live Weather Snapshot")
if weather:
    st.sidebar.markdown(
        f"""
<div class="glass-card">
  <div class="metric-label">Temperature</div><div class="metric-value">{weather.get('temperature', 0):.1f} C</div>
  <div class="metric-label">Humidity</div><div class="metric-value">{weather.get('humidity', 0):.0f}%</div>
  <div class="metric-label">Rainfall</div><div class="metric-value">{weather.get('rainfall', 0):.2f} in</div>
  <div class="metric-label">AQI</div><div class="metric-value">{weather.get('aqi', 0):.0f}</div>
</div>
""",
        unsafe_allow_html=True,
    )
else:
    st.sidebar.warning("Weather service offline.")

page = st.sidebar.radio(
    "View",
    [
        "Climate Risk Dashboard",
        "Seasonal Analytics",
        "Climate Trend",
        "Future Forecast",
        "Spatial Heatmaps",
        "Environmental Change Analysis",
    ],
    label_visibility="collapsed",
)

if df is None:
    st.error("Processed data not found. Run: python data_processing.py")
    st.stop()

if page == "Climate Risk Dashboard":
    st.markdown('<div class="section-title">Current Conditions and Risk Indicators</div>', unsafe_allow_html=True)
    method_note("Weather data comes from the accessible NASA POWER-style dataset. NDVI, NDBI, NDWI, LST, UHI, and AQI are project-ready proxy/generated indicators unless replaced with official external datasets.")
    latest = weather or df.iloc[-1].to_dict()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Temperature", f"{latest.get('temperature', 0):.1f} C", latest.get("temp_class", ""))
    with c2:
        metric_card("AQI", f"{latest.get('aqi', 0):.0f}", latest.get("aqi_class", ""))
    with c3:
        metric_card("Humidity", f"{latest.get('humidity', 0):.1f}%", "current")
    with c4:
        metric_card("Rainfall", f"{latest.get('rainfall', 0):.2f} in", latest.get("rain_class", ""))

    st.markdown('<div class="section-title">Risk Indicators</div>', unsafe_allow_html=True)
    r1, r2, r3, r4 = st.columns(4)
    risk_items = [
        ("Heatwave", latest.get("heatwave_risk", "Low")),
        ("Flood", latest.get("flood_risk", "Low")),
        ("Dengue", latest.get("dengue_risk", "Low")),
        ("Human Health", latest.get("human_risk", "Low")),
    ]
    for col, (label, risk) in zip([r1, r2, r3, r4], risk_items):
        with col:
            st.markdown(f'<div class="result-card" style="background:{risk_color(risk)}"><b>{label}</b><br>{risk}</div>', unsafe_allow_html=True)

elif page == "Seasonal Analytics":
    st.markdown('<div class="section-title">Seasonal Analytics</div>', unsafe_allow_html=True)
    method_note("Seasons are derived from month: Winter, Summer, Monsoon, and Post-Monsoon. Dominant risk is the most frequent modeled human-risk class in that season.")
    stats = seasonal_stats(df)
    cols = st.columns(4)
    for col, season in zip(cols, stats.index):
        row = stats.loc[season]
        with col:
            metric_card(season, f"{row['avg_temp']:.1f} C", f"AQI {row['avg_aqi']:.0f} | Rain {row['avg_rain']:.2f} in | Risk {row['dominant_risk']}")

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=stats["avg_temp"], theta=stats.index, fill="toself", name="Temp C", line_color="#00D4FF"))
    fig.add_trace(go.Scatterpolar(r=stats["avg_aqi"] / 5, theta=stats.index, fill="toself", name="AQI scaled", line_color="#FFB830"))
    fig.add_trace(go.Scatterpolar(r=stats["avg_rain"], theta=stats.index, fill="toself", name="Rainfall", line_color="#39FF14"))
    fig.update_layout(height=430, paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#E6E8EF"))
    st.plotly_chart(fig, use_container_width=True)

elif page == "Climate Trend":
    st.markdown('<div class="section-title">Climate Trend Analysis</div>', unsafe_allow_html=True)
    method_note("Trend charts use the processed daily Bengaluru dataset. Rainfall anomaly is calculated against the month-wise average rainfall.")
    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure(go.Scatter(x=df["date"], y=df["temperature"], mode="lines", line=dict(color="#00D4FF")))
        fig.update_layout(title="Temperature Trend", height=360, paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#E6E8EF"))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = go.Figure(go.Scatter(x=df["date"], y=df["aqi"], mode="lines", line=dict(color="#FFB830")))
        fig.update_layout(title="AQI Trend", height=360, paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#E6E8EF"))
        st.plotly_chart(fig, use_container_width=True)
    c3, c4 = st.columns(2)
    with c3:
        fig = go.Figure(go.Bar(x=df["date"], y=df["rainfall_anomaly"], marker_color="#39FF14"))
        fig.update_layout(title="Rainfall Anomaly", height=360, paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#E6E8EF"))
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        corr = df[["temperature", "rainfall", "humidity", "aqi", "NDVI", "NDBI", "NDWI", "uhi_score"]].corr()
        fig = go.Figure(go.Heatmap(z=corr.values, x=corr.columns, y=corr.columns, colorscale="RdBu", zmid=0, text=corr.round(2).values, texttemplate="%{text}"))
        fig.update_layout(title="Feature Correlation", height=360, paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#E6E8EF"))
        st.plotly_chart(fig, use_container_width=True)

elif page == "Future Forecast":
    st.markdown('<div class="section-title">Future Forecast Simulator</div>', unsafe_allow_html=True)
    method_note("Forecasts are next-day/class estimates from classical Random Forest models. They are awareness estimates, not official warnings.")
    metrics = api_get("/model_metrics")
    if metrics:
        with st.expander("Model evaluation summary"):
            for name, vals in metrics.items():
                if isinstance(vals, dict):
                    score = vals.get("accuracy", vals.get("r2", "n/a"))
                    st.write(f"{name}: {score}")

    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        f_temp = st.slider("Temperature (C)", 10.0, 50.0, 28.0)
    with c2:
        f_hum = st.slider("Humidity (%)", 0, 100, 65)
    with c3:
        f_rain = st.slider("Rainfall (in)", 0.0, 100.0, 2.0)
    with c4:
        f_aqi = st.slider("Current AQI", 0, 500, 100)
    c5, c6, c7, c8 = st.columns(4)
    with c5:
        f_wind = st.slider("Wind (km/h)", 0.0, 50.0, 8.0)
    with c6:
        f_hist = st.slider("7-day rain (in)", 0.0, 100.0, 5.0)
    with c7:
        f_uhi = st.slider("Proxy UHI score", 0.0, 10.0, 3.0)
    with c8:
        f_ndwi = st.slider("Proxy NDWI", 0.0, 1.0, 0.25)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Generate Complete Forecast", use_container_width=True):
        payload = {
            "temperature": f_temp,
            "humidity": f_hum,
            "rainfall": f_rain,
            "aqi": f_aqi,
            "wind_speed": f_wind,
            "historical_rainfall": f_hist,
            "NDWI": f_ndwi,
            "uhi_score": f_uhi,
            "heat_index": f_temp + (f_hum / 10),
        }
        try:
            temp = api_post("/predict_temperature", payload)
            aqi = api_post("/predict_aqi", payload)
            rain = api_post("/predict_rainfall", payload)
            heat = api_post("/predict_heatwave", payload)
            flood = api_post("/predict_flood", payload)
            dengue = api_post("/predict_dengue", payload)
            human = api_post("/predict_human_risk", payload)
            cards = [
                ("Temperature", f"{temp['predicted_temperature']:.1f} C", temp["temperature_class"]),
                ("AQI", f"{aqi['predicted_aqi']:.0f}", aqi["aqi_class"]),
                ("Rainfall", rain["category"], "next-day class"),
                ("Heatwave", heat["risk"], "risk"),
                ("Flood", flood["risk"], "risk"),
                ("Dengue", dengue["risk"], "risk"),
                ("Human Health", human["risk"], "risk"),
            ]
            cols = st.columns(4)
            for i, (label, value, sub) in enumerate(cards):
                with cols[i % 4]:
                    metric_card(label, value, sub)
        except Exception as exc:
            st.error(f"Forecast service error: {exc}")

elif page == "Spatial Heatmaps":
    st.markdown('<div class="section-title">Spatial Heatmaps</div>', unsafe_allow_html=True)
    method_note("Maps are simulated/proxy spatial risk surfaces for v1. They show how the final system would visualize ward/grid risk once official spatial datasets are added.")
    if "geo_df" not in st.session_state:
        st.session_state.geo_df = generate_spatial_mock_data(n_points=300)
    layer = st.radio("Select Heatmap Layer", ["Temperature", "AQI", "Flood Risk", "Dengue Risk", "UHI Score"], horizontal=True)
    if layer == "Temperature":
        fmap = generate_temperature_heatmap(st.session_state.geo_df)
    elif layer == "AQI":
        fmap = generate_aqi_heatmap(st.session_state.geo_df)
    elif layer == "Flood Risk":
        fmap = generate_flood_heatmap(st.session_state.geo_df)
    elif layer == "Dengue Risk":
        fmap = generate_dengue_heatmap(st.session_state.geo_df)
    else:
        fmap = generate_uhi_heatmap(st.session_state.geo_df)
    st_folium(fmap, width=1100, height=520)

elif page == "Environmental Change Analysis":
    st.markdown('<div class="section-title">Environmental Change Analysis (2005-2026 narrative)</div>', unsafe_allow_html=True)
    method_note("This section is a proxy/simulation narrative for project-ready v1. Official Bhuvan/NRSC, Landsat/Sentinel, IMD, and CPCB datasets are documented as future work.")
    st.markdown(
        """
<div class="callout">
Bengaluru climate risk is driven by combined urban expansion, loss of green cover, lake/water-body stress,
vehicle and industrial pollution, urban heat-island formation, and unstable rainfall patterns.
</div>
""",
        unsafe_allow_html=True,
    )
    hist_df = get_historical_climate_data()
    for insight in generate_insights(hist_df):
        st.markdown(f"- {insight}")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(plot_temperature_trend(hist_df), use_container_width=True)
    with c2:
        st.plotly_chart(plot_aqi_trend(hist_df), use_container_width=True)
    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(plot_rainfall_trend(hist_df), use_container_width=True)
    with c4:
        st.plotly_chart(plot_land_use_changes(hist_df), use_container_width=True)
