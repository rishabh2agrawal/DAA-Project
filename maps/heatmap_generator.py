import folium
from folium.plugins import HeatMap
import geopandas as gpd
from .geo_utils import generate_spatial_mock_data

BENGALURU_COORDS = [12.9716, 77.5946]

def get_base_map():
    """Returns a base Folium map centered on Bengaluru."""
    return folium.Map(location=BENGALURU_COORDS, zoom_start=11, tiles="CartoDB positron")

def generate_temperature_heatmap(gdf: gpd.GeoDataFrame):
    """
    Generates a Temperature Heatmap.
    Green = Low, Yellow = Medium, Red = High.
    """
    m = get_base_map()
    
    # Normalize temperature somewhat for standard heatmap weights (e.g., 20-45 -> 0-1)
    heat_data = [[row.latitude, row.longitude, row.temperature] for index, row in gdf.iterrows()]
    
    # Custom gradient for Temp
    gradient = {0.2: 'green', 0.6: 'yellow', 1.0: 'red'}
    
    HeatMap(
        heat_data,
        gradient=gradient,
        min_opacity=0.3,
        max_val=45.0, # Max reference temperature
        radius=25,
        blur=15
    ).add_to(m)
    
    return m

def generate_aqi_heatmap(gdf: gpd.GeoDataFrame):
    """
    Generates an AQI Heatmap.
    Based on AQI categories (Good..Severe)
    """
    m = get_base_map()
    
    heat_data = [[row.latitude, row.longitude, row.aqi] for index, row in gdf.iterrows()]
    
    # Custom gradient for AQI: Green -> Yellow -> Orange -> Red -> Purple -> Maroon
    gradient = {
        0.1: '#00e400', # Good
        0.3: '#ffff00', # Moderate
        0.5: '#ff7e00', # Unhealthy for Sensitive
        0.7: '#ff0000', # Unhealthy
        0.9: '#8f3f97', # Very Unhealthy
        1.0: '#7e0023'  # Hazardous
    }
    
    HeatMap(
        heat_data,
        gradient=gradient,
        min_opacity=0.3,
        max_val=400.0, # AQI max reference
        radius=25,
        blur=15
    ).add_to(m)
    
    return m

def generate_flood_heatmap(gdf: gpd.GeoDataFrame):
    """
    Generates a Flood Risk Heatmap.
    High risk = Blues/Cyans
    """
    m = get_base_map()
    
    # flood_risk is 0.0 to 1.0
    heat_data = [[row.latitude, row.longitude, row.flood_risk] for index, row in gdf.iterrows()]
    
    gradient = {0.2: 'lightblue', 0.6: 'blue', 1.0: 'darkblue'}
    
    HeatMap(
        heat_data,
        gradient=gradient,
        min_opacity=0.3,
        max_val=1.0,
        radius=30,
        blur=20
    ).add_to(m)
    
    return m

def generate_dengue_heatmap(gdf: gpd.GeoDataFrame):
    """
    Generates a Dengue Risk Heatmap.
    Highlight mosquito-risk zones (typically Greens/Purples/Reds)
    """
    m = get_base_map()
    
    heat_data = [[row.latitude, row.longitude, row.dengue_risk] for index, row in gdf.iterrows()]
    
    gradient = {0.2: '#ffffb2', 0.5: '#fd8d3c', 0.8: '#f03b20', 1.0: '#bd0026'}
    
    HeatMap(
        heat_data,
        gradient=gradient,
        min_opacity=0.3,
        max_val=1.0,
        radius=25,
        blur=15
    ).add_to(m)
    
    return m
