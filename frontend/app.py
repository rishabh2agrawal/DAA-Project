import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os

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
        df = pd.read_csv(data_path)
        df['date'] = pd.to_datetime(df['date'])
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
        3: 'Spring', 4: 'Spring', 5: 'Spring',
        6: 'Summer', 7: 'Summer', 8: 'Summer',
        9: 'Fall', 10: 'Fall', 11: 'Fall'
    })
    
    seasonal_data = df_copy.groupby('season').agg({
        'temperature': ['mean', 'std'],
        'humidity': 'mean',
        'rainfall': 'mean'
    }).round(2)
    
    # Flatten column names for better readability
    seasonal_data.columns = ['Avg Temp (°C)', 'Std Dev Temp', 'Avg Humidity (%)', 'Avg Rainfall (in)']
    
    # Reorder seasons properly
    season_order = ['Winter', 'Spring', 'Summer', 'Fall']
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
page = st.sidebar.radio("", ["📊 Dashboard", "🤖 AI Prediction", "⚠️ Health Risk", "📈 Analytics"], index=0)

if page == "📊 Dashboard":
    st.markdown('<div class="section-title">Climate Dashboard</div>', unsafe_allow_html=True)
    
    if df is not None:
        avg_temp = df['temperature'].mean()
        avg_humidity = df['humidity'].mean()
        total_rain = df['rainfall'].sum()
        avg_aqi = df['aqi'].mean()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(
                f"""
<div class="metric-card">
  <div class="metric-label">🌡️ Avg Temp</div>
  <div class="metric-value">{avg_temp:.1f}°C</div>
  <div class="metric-sub">Range: {df['temperature'].min():.1f}° - {df['temperature'].max():.1f}°</div>
</div>
""",
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
<div class="metric-card">
  <div class="metric-label">💧 Humidity</div>
  <div class="metric-value">{avg_humidity:.1f}%</div>
  <div class="metric-sub">Range: {df['humidity'].min():.1f}% - {df['humidity'].max():.1f}%</div>
</div>
""",
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                f"""
<div class="metric-card">
  <div class="metric-label">🌧️ Rainfall</div>
  <div class="metric-value">{total_rain:.2f} in</div>
  <div class="metric-sub">Max: {df['rainfall'].max():.2f} in</div>
</div>
""",
                unsafe_allow_html=True,
            )

        with col4:
            st.markdown(
                f"""
<div class="metric-card">
  <div class="metric-label">🌫️ AQI</div>
  <div class="metric-value">{avg_aqi:.0f}</div>
  <div class="metric-sub">Range: {df['aqi'].min():.0f} - {df['aqi'].max():.0f}</div>
</div>
""",
                unsafe_allow_html=True,
            )
        
        st.divider()

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

        st.markdown('<div class="section-title">🔗 Feature Correlations</div>', unsafe_allow_html=True)
        corr_matrix = df[['temperature', 'rainfall', 'humidity', 'aqi']].corr()
        fig_corr = go.Figure(
            data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale=[
                    [0.0, '#00D4FF'],
                    [0.5, '#1E2A3A'],
                    [1.0, '#FFB830'],
                ],
                text=corr_matrix.values.round(2),
                texttemplate='%{text}',
                textfont={"size": 12, "color": "#E6E8EF"},
            )
        )
        fig_corr.update_layout(
            height=380,
            margin=dict(l=10, r=10, t=20, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E6E8EF'),
        )
        st.plotly_chart(fig_corr, use_container_width=True, config={"displayModeBar": False})

elif page == "🤖 AI Prediction":
    st.markdown('<div class="section-title">AI Temperature Prediction</div>', unsafe_allow_html=True)

    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        rainfall = st.slider("Rainfall (inches)", 0.0, 5.0, 0.5, step=0.1)

    with col2:
        humidity = st.slider("Humidity (%)", 0, 100, 60)

    with col3:
        aqi = st.slider("AQI (Air Quality Index)", 0, 500, 50)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🔮 Predict Temperature", use_container_width=True):
        try:
            response = requests.post(
                f"{backend_url}/predict",
                json={"rainfall": rainfall, "humidity": humidity, "aqi": aqi},
                timeout=5,
            )
            if response.status_code == 200:
                pred = response.json()
                predicted_temp = pred['predicted_temperature']
                historical_avg = df['temperature'].mean() if df is not None else predicted_temp

                st.markdown(
                    f"""
<div class="result-card">
  <div class="metric-label">🌡️ Predicted Temperature</div>
  <div class="metric-value" style="color: var(--cyan);">{predicted_temp:.1f}°C</div>
  <div class="metric-sub">vs historical average {historical_avg:.1f}°C</div>
</div>
""",
                    unsafe_allow_html=True,
                )

                gauge_min = 10
                gauge_max = 45
                fig_gauge = go.Figure(
                    go.Indicator(
                        mode="gauge+number",
                        value=predicted_temp,
                        number={"suffix": "°C", "font": {"color": "#E6E8EF"}},
                        gauge={
                            "axis": {"range": [gauge_min, gauge_max], "tickcolor": "#A8B2C1"},
                            "bar": {"color": "#00D4FF"},
                            "bgcolor": "rgba(0,0,0,0)",
                            "steps": [
                                {"range": [gauge_min, 25], "color": "rgba(0,212,255,0.12)"},
                                {"range": [25, 35], "color": "rgba(57,255,20,0.12)"},
                                {"range": [35, gauge_max], "color": "rgba(255,184,48,0.18)"},
                            ],
                        },
                    )
                )
                fig_gauge.update_layout(
                    height=300,
                    margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#E6E8EF'),
                )
                st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

                fig_compare = go.Figure()
                fig_compare.add_trace(
                    go.Bar(
                        x=['Predicted'],
                        y=[predicted_temp],
                        marker_color='#00D4FF',
                        name='Predicted',
                    )
                )
                fig_compare.add_hline(
                    y=historical_avg,
                    line_dash="dash",
                    line_color="#FFB830",
                    annotation_text="Historical Avg",
                    annotation_font_color="#FFB830",
                )
                fig_compare.update_layout(
                    height=280,
                    margin=dict(l=10, r=10, t=20, b=10),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.08)', title='Temperature (°C)'),
                    font=dict(color='#E6E8EF'),
                    showlegend=False,
                )
                st.plotly_chart(fig_compare, use_container_width=True, config={"displayModeBar": False})

                with st.expander("Input Parameters"):
                    st.write(f"- **Rainfall**: {rainfall} inches")
                    st.write(f"- **Humidity**: {humidity}%")
                    st.write(f"- **AQI**: {aqi}")
            else:
                st.error(f"Error: {response.status_code}")
        except Exception as e:
            st.error(f"Connection error: {e}")

elif page == "⚠️ Health Risk":
    st.markdown('<div class="section-title">Health Risk Assessment</div>', unsafe_allow_html=True)

    st.markdown('<div class="control-panel">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        temp_risk = st.slider("Temperature (°C)", 15.0, 40.0, 24.0)

    with col2:
        humidity_risk = st.slider("Humidity (%)", 0, 100, 60)

    with col3:
        aqi_risk = st.slider("AQI", 0, 500, 50)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("📋 Check Health Risk", use_container_width=True):
        try:
            response = requests.post(
                f"{backend_url}/health_risk",
                json={"temperature": temp_risk, "humidity": humidity_risk, "aqi": aqi_risk},
                timeout=5,
            )
            if response.status_code == 200:
                risk = response.json()
                risk_level = risk.get('risk', 'Moderate')

                if 'Low' in risk_level:
                    risk_class = "risk-low"
                    risk_icon = "✅"
                elif 'Moderate' in risk_level:
                    risk_class = "risk-moderate"
                    risk_icon = "⚠️"
                else:
                    risk_class = "risk-high"
                    risk_icon = "🚨"

                st.markdown(
                    f"""
<div class="risk-card {risk_class}">
  {risk_icon} Health Risk: {risk_level}
</div>
""",
                    unsafe_allow_html=True,
                )

                risk_factors = []
                if temp_risk > 32:
                    risk_factors.append("🌡️ High temperature")
                if humidity_risk > 80:
                    risk_factors.append("💧 High humidity")
                if aqi_risk > 150:
                    risk_factors.append("💨 Poor air quality")

                st.markdown('<div class="section-title">Risk Factors</div>', unsafe_allow_html=True)
                if risk_factors:
                    chips = "".join([f"<span class=\"chip\">{item}</span>" for item in risk_factors])
                    st.markdown(chips, unsafe_allow_html=True)
                else:
                    st.markdown('<div class="glass-card">No significant risk factors detected.</div>', unsafe_allow_html=True)
            else:
                st.error(f"Error: {response.status_code}")
        except Exception as e:
            st.error(f"Connection error: {e}")

elif page == "📈 Analytics":
    st.markdown('<div class="section-title">Data Analytics</div>', unsafe_allow_html=True)

    if df is not None:
        st.markdown('<div class="section-title">📊 Monthly Climate Statistics</div>', unsafe_allow_html=True)

        monthly_stats = calculate_monthly_stats(df)
        fig_monthly = go.Figure()
        fig_monthly.add_trace(
            go.Bar(
                x=monthly_stats['Month'],
                y=monthly_stats['Avg Temp'],
                name='Avg Temp (°C)',
                marker_color='#00D4FF',
            )
        )
        fig_monthly.add_trace(
            go.Bar(
                x=monthly_stats['Month'],
                y=monthly_stats['Avg Humidity'],
                name='Avg Humidity (%)',
                marker_color='#39FF14',
            )
        )
        fig_monthly.add_trace(
            go.Bar(
                x=monthly_stats['Month'],
                y=monthly_stats['Total Rain'],
                name='Total Rain (in)',
                marker_color='#FFB830',
            )
        )
        fig_monthly.update_layout(
            barmode='group',
            height=420,
            margin=dict(l=10, r=10, t=20, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.08)'),
            font=dict(color='#E6E8EF'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        )
        st.plotly_chart(fig_monthly, use_container_width=True, config={"displayModeBar": False})

        st.divider()

        st.markdown('<div class="section-title">🌡️ Seasonal Patterns</div>', unsafe_allow_html=True)
        seasonal_data = calculate_seasonal_stats(df)

        seasons = seasonal_data.index.tolist()
        fig_radar = go.Figure()
        fig_radar.add_trace(
            go.Scatterpolar(
                r=seasonal_data['Avg Temp (°C)'],
                theta=seasons,
                fill='toself',
                name='Avg Temp (°C)',
                line_color='#00D4FF',
            )
        )
        fig_radar.add_trace(
            go.Scatterpolar(
                r=seasonal_data['Avg Humidity (%)'],
                theta=seasons,
                fill='toself',
                name='Avg Humidity (%)',
                line_color='#39FF14',
            )
        )
        fig_radar.add_trace(
            go.Scatterpolar(
                r=seasonal_data['Avg Rainfall (in)'],
                theta=seasons,
                fill='toself',
                name='Avg Rainfall (in)',
                line_color='#FFB830',
            )
        )
        fig_radar.update_layout(
            height=420,
            polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(gridcolor='rgba(255,255,255,0.08)', tickfont_color='#A8B2C1')),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E6E8EF'),
            legend=dict(orientation='h', yanchor='bottom', y=1.05, xanchor='right', x=1),
        )
        st.plotly_chart(fig_radar, use_container_width=True, config={"displayModeBar": False})

        st.markdown('<div class="section-title">📌 Key Insights</div>', unsafe_allow_html=True)
        warmest = seasonal_data['Avg Temp (°C)'].idxmax()
        coldest = seasonal_data['Avg Temp (°C)'].idxmin()
        wettest = seasonal_data['Avg Rainfall (in)'].idxmax()
        st.markdown(
            f"""
<div class="callout">🔥 Warmest: {warmest} ({seasonal_data.loc[warmest, 'Avg Temp (°C)']:.1f}°C)</div>
<div class="callout">❄️ Coldest: {coldest} ({seasonal_data.loc[coldest, 'Avg Temp (°C)']:.1f}°C)</div>
<div class="callout">💧 Wettest: {wettest} ({seasonal_data.loc[wettest, 'Avg Rainfall (in)']:.3f} in)</div>
""",
            unsafe_allow_html=True,
        )