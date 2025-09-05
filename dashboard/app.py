import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys
import os
import numpy as np
import geopandas as gpd
from shapely.geometry import Point

# Tambahkan path ke src
current_dir = Path(__file__).parent
project_root = current_dir.parent
src_path = os.path.join(project_root, 'src')

if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from data_ingestion import load_config, read_shapefile
    from data_processing import clean_geospatial_data
    from visualization import create_interactive_map, create_static_map
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# Konfigurasi halaman
st.set_page_config(
    page_title="Simulasi Kasus Lahan",
    page_icon="🏞️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Judul aplikasi
st.title("🏞️ Dashboard Simulasi Kasus Lahan")

# Sidebar
st.sidebar.header("Konfigurasi")

# Fungsi untuk membuat data sampel
def create_sample_data():
    try:
        # Buat direktori jika belum ada
        os.makedirs('data/raw', exist_ok=True)
        
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
    except Exception as e:
        st.error(f"Gagal membuat data sampel: {e}")
        return False

# Load data dengan error handling yang lebih baik
@st.cache_data
def load_data():
    try:
        config = load_config()
        data_path = 'data/raw/sample_land_data.shp'
        
        # Periksa apakah file data ada
        if not os.path.exists(data_path):
            st.warning("File data tidak ditemukan. Membuat data sampel...")
            if create_sample_data():
                st.success("Data sampel berhasil dibuat!")
            else:
                return None, None
            
        gdf = read_shapefile(data_path)
        
        # Periksa apakah data berhasil dibaca
        if gdf is None or gdf.empty:
            st.error("Gagal membaca data atau data kosong")
            return None, None
            
        gdf_clean = clean_geospatial_data(gdf, config['project_settings']['default_crs'])
        return gdf_clean, config
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

# Pemanggilan fungsi load_data - TIDAK di-indentasi
gdf_clean, config = load_data()

# ... sisa kode aplikasi Anda