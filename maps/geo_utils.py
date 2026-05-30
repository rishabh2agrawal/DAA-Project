import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

BENGALURU_BBOX = {
    'min_lat': 12.85,
    'max_lat': 13.15,
    'min_lon': 77.45,
    'max_lon': 77.75
}

def generate_spatial_mock_data(n_points=200):
    """
    Generates synthetic geospatial data for Bengaluru using GeoPandas.
    Returns a GeoDataFrame.
    """
    np.random.seed(42) # For reproducible spatial patterns
    
    lats = np.random.uniform(BENGALURU_BBOX['min_lat'], BENGALURU_BBOX['max_lat'], n_points)
    lons = np.random.uniform(BENGALURU_BBOX['min_lon'], BENGALURU_BBOX['max_lon'], n_points)
    
    # Simulate variations across the city
    # E.g., center of city (Lat 12.97, Lon 77.59) might have higher AQI, temp
    center_lat, center_lon = 12.97, 77.59
    dist_from_center = np.sqrt((lats - center_lat)**2 + (lons - center_lon)**2)
    
    # Temperature: Higher near center (Urban Heat Island)
    base_temp = 25.0
    temperatures = base_temp + (0.1 - dist_from_center) * 30 + np.random.normal(0, 1.5, n_points)
    temperatures = np.clip(temperatures, 20.0, 45.0)
    
    # AQI: Higher near center
    aqis = 50 + (0.2 - dist_from_center) * 800 + np.random.normal(0, 20, n_points)
    aqis = np.clip(aqis, 20, 450)
    
    # Flood Risk: Higher in certain low-lying areas (simulated by random clusters)
    # Let's make the south-east a bit more flood prone
    flood_risk = np.where((lats < 12.95) & (lons > 77.65), np.random.uniform(0.6, 1.0, n_points), np.random.uniform(0.0, 0.5, n_points))
    
    # Dengue Risk: Correlated somewhat with flood/water
    dengue_risk = flood_risk * 0.7 + np.random.uniform(0.0, 0.4, n_points)
    dengue_risk = np.clip(dengue_risk, 0.0, 1.0)
    
    df = pd.DataFrame({
        'latitude': lats,
        'longitude': lons,
        'temperature': temperatures,
        'aqi': aqis,
        'flood_risk': flood_risk,
        'dengue_risk': dengue_risk
    })
    
    geometry = [Point(xy) for xy in zip(df.longitude, df.latitude)]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    return gdf
