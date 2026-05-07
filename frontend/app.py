import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os

st.set_page_config(page_title="Climate Risk Prediction", layout="wide")

st.title("🌍 AI-Powered Climate Risk Prediction System for Bengaluru")

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

# Load processed data for visualization
df = load_data()
if df is None:
    st.warning("Processed data not found. Please run data_processing.py first.")

# Sidebar for navigation
page = st.sidebar.radio("Navigation", ["📊 Dashboard", "🤖 AI Prediction", "⚠️ Health Risk", "📈 Analytics"])

if page == "📊 Dashboard":
    st.header("Climate Dashboard")
    
    if df is not None:
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Avg Temperature (°C)", f"{df['temperature'].mean():.1f}°C", 
                     f"Range: {df['temperature'].min():.1f}° - {df['temperature'].max():.1f}°")
        
        with col2:
            st.metric("Avg Humidity (%)", f"{df['humidity'].mean():.1f}%",
                     f"Range: {df['humidity'].min():.1f}% - {df['humidity'].max():.1f}%")
        
        with col3:
            st.metric("Total Rainfall (in)", f"{df['rainfall'].sum():.2f} in",
                     f"Max: {df['rainfall'].max():.2f} in")
        
        with col4:
            st.metric("Avg AQI", f"{df['aqi'].mean():.0f}",
                     f"Range: {df['aqi'].min():.0f} - {df['aqi'].max():.0f}")
        
        st.divider()
        
        # Temperature trends
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Temperature Trend Over Time")
            fig_temp = px.line(df, x='date', y='temperature', 
                             title='Historical Temperature Pattern',
                             labels={'temperature': 'Temperature (°C)', 'date': 'Date'},
                             color_discrete_sequence=['#FF6B6B'])
            fig_temp.update_layout(height=400)
            st.plotly_chart(fig_temp, use_container_width=True)
        
        with col2:
            st.subheader("💧 Humidity Distribution")
            fig_humidity = px.histogram(df, x='humidity', nbins=50,
                                       title='Humidity Distribution',
                                       labels={'humidity': 'Humidity (%)'},
                                       color_discrete_sequence=['#4ECDC4'])
            fig_humidity.update_layout(height=400)
            st.plotly_chart(fig_humidity, use_container_width=True)
        
        # Correlation heatmap
        st.subheader("🔗 Feature Correlations")
        corr_matrix = df[['temperature', 'rainfall', 'humidity', 'aqi']].corr()
        fig_corr = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 12}
        ))
        fig_corr.update_layout(height=400, width=500)
        st.plotly_chart(fig_corr, use_container_width=True)

elif page == "🤖 AI Prediction":
    st.header("AI Temperature Prediction")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        rainfall = st.slider("Rainfall (inches)", 0.0, 5.0, 0.5, step=0.1)
    
    with col2:
        humidity = st.slider("Humidity (%)", 0, 100, 60)
    
    with col3:
        aqi = st.slider("AQI (Air Quality Index)", 0, 500, 50)
    
    if st.button("🔮 Predict Temperature", use_container_width=True):
        try:
            response = requests.post(f"{backend_url}/predict", 
                                   json={"rainfall": rainfall, "humidity": humidity, "aqi": aqi},
                                   timeout=5)
            if response.status_code == 200:
                pred = response.json()
                predicted_temp = pred['predicted_temperature']
                
                st.success(f"### 🌡️ Predicted Temperature: **{predicted_temp:.1f}°C**")
                
                # Show input summary
                with st.expander("Input Parameters"):
                    st.write(f"- **Rainfall**: {rainfall} inches")
                    st.write(f"- **Humidity**: {humidity}%")
                    st.write(f"- **AQI**: {aqi}")
                
                # Visualization
                fig = go.Figure(data=[
                    go.Bar(x=['Predicted'], y=[predicted_temp], name='Temperature',
                          marker_color='indianred')
                ])
                fig.add_hline(y=df['temperature'].mean(), annotation_text="Historical Avg",
                            line_dash="dash", line_color="blue")
                fig.update_layout(title="Prediction vs Historical Average",
                                yaxis_title="Temperature (°C)", height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(f"Error: {response.status_code}")
        except Exception as e:
            st.error(f"Connection error: {e}")

elif page == "⚠️ Health Risk":
    st.header("Health Risk Assessment")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        temp_risk = st.slider("Temperature (°C)", 15.0, 40.0, 24.0)
    
    with col2:
        humidity_risk = st.slider("Humidity (%)", 0, 100, 60)
    
    with col3:
        aqi_risk = st.slider("AQI", 0, 500, 50)
    
    if st.button("📋 Check Health Risk", use_container_width=True):
        try:
            response = requests.post(f"{backend_url}/health_risk",
                                   json={"temperature": temp_risk, "humidity": humidity_risk, "aqi": aqi_risk},
                                   timeout=5)
            if response.status_code == 200:
                risk = response.json()
                risk_level = risk.get('risk', 'Moderate')
                
                # Color code the risk level
                if 'Low' in risk_level:
                    st.success(f"### ✅ Health Risk: **{risk_level}**")
                elif 'Moderate' in risk_level:
                    st.warning(f"### ⚠️ Health Risk: **{risk_level}**")
                else:
                    st.error(f"### 🚨 Health Risk: **{risk_level}**")
                
                # Risk factors
                st.subheader("Risk Factors:")
                if temp_risk > 32:
                    st.warning("🌡️ High temperature - Heat stress risk")
                if humidity_risk > 80:
                    st.warning("💧 High humidity - Reduced cooling capacity")
                if aqi_risk > 150:
                    st.warning("💨 Poor air quality - Respiratory concerns")
            else:
                st.error(f"Error: {response.status_code}")
        except Exception as e:
            st.error(f"Connection error: {e}")

elif page == "📈 Analytics":
    st.header("Data Analytics")
    
    if df is not None:
        st.subheader("📊 Monthly Climate Statistics")
        
        # Get cached monthly stats
        monthly_stats = calculate_monthly_stats(df)
        st.dataframe(
            monthly_stats.head(20),
            use_container_width=True,
            height=400,
            column_config={
                "Avg Temp": st.column_config.NumberColumn(format="%.2f °C"),
                "Max Temp": st.column_config.NumberColumn(format="%.2f °C"),
                "Min Temp": st.column_config.NumberColumn(format="%.2f °C"),
                "Avg Humidity": st.column_config.NumberColumn(format="%.1f %%"),
                "Total Rain": st.column_config.NumberColumn(format="%.2f in"),
                "Avg AQI": st.column_config.NumberColumn(format="%.0f"),
            }
        )
        
        st.divider()
        
        # Seasonal analysis
        st.subheader("🌡️ Seasonal Patterns")
        seasonal_data = calculate_seasonal_stats(df)
        
        # Format and display with styling
        col1, col2 = st.columns([2, 1])
        with col1:
            st.dataframe(
                seasonal_data,
                use_container_width=True,
                height=300,
                column_config={
                    "Avg Temp (°C)": st.column_config.NumberColumn(format="%.2f °C"),
                    "Std Dev Temp": st.column_config.NumberColumn(format="%.2f"),
                    "Avg Humidity (%)": st.column_config.NumberColumn(format="%.1f %%"),
                    "Avg Rainfall (in)": st.column_config.NumberColumn(format="%.3f in"),
                }
            )
        
        with col2:
            # Quick summary
            st.markdown("### 📌 Key Insights")
            warmest = seasonal_data['Avg Temp (°C)'].idxmax()
            coldest = seasonal_data['Avg Temp (°C)'].idxmin()
            wettest = seasonal_data['Avg Rainfall (in)'].idxmax()
            
            st.markdown(f"🔥 **Warmest**: {warmest} ({seasonal_data.loc[warmest, 'Avg Temp (°C)']:.1f}°C)")
            st.markdown(f"❄️ **Coldest**: {coldest} ({seasonal_data.loc[coldest, 'Avg Temp (°C)']:.1f}°C)")
            st.markdown(f"💧 **Wettest**: {wettest} ({seasonal_data.loc[wettest, 'Avg Rainfall (in)']:.3f} in)")