import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import os
from pathlib import Path

def create_sample_data():
    # Buat direktori jika belum ada
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    
    # Buat data sampel
    np.random.seed(42)
    num_points = 100
    latitudes = np.random.uniform(-6.2, -6.1, num_points)
    longitudes = np.random.uniform(106.7, 106.8, num_points)
    values = np.random.uniform(100000, 500000, num_points)
    
    # Buat GeoDataFrame
    geometry = [Point(xy) for xy in zip(longitudes, latitudes)]
    gdf = gpd.GeoDataFrame({
        'id': range(num_points),
        'value': values,
        'geometry': geometry
    })
    
    # Simpan sebagai shapefile
    gdf.to_file("data/raw/sample_land_data.shp")
    return True

if __name__ == "__main__":
    create_sample_data()
    print("Data sampel berhasil dibuat!")