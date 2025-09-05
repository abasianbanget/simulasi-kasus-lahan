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

# Pemanggilan fungsi load_data
gdf_clean, config = load_data()

if gdf_clean is not None:
    # Tampilkan metrik
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Jumlah Data", len(gdf_clean))
    col2.metric("Nilai Rata-rata", f"${gdf_clean['value'].mean():.2f}")
    col3.metric("Nilai Minimum", f"${gdf_clean['value'].min():.2f}")
    col4.metric("Nilai Maksimum", f"${gdf_clean['value'].max():.2f}")

    # Tab untuk berbagai visualisasi
    tab1, tab2, tab3 = st.tabs(["Peta Interaktif", "Analisis Statistik", "Data"])

    with tab1:
        st.header("Peta Interaktif Nilai Lahan")
        try:
            fig = create_interactive_map(gdf_clean, 'value', 'Distribusi Nilai Lahan')
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating interactive map: {e}")
            st.info("Menggunakan static map sebagai alternatif...")
            fig = create_static_map(gdf_clean, 'value', 'Distribusi Nilai Lahan')
            st.pyplot(fig)

    with tab2:
        st.header("Analisis Statistik")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Distribusi Nilai")
            fig_hist, ax_hist = plt.subplots()
            ax_hist.hist(gdf_clean['value'], bins=20, edgecolor='black', alpha=0.7)
            ax_hist.set_xlabel('Nilai')
            ax_hist.set_ylabel('Frekuensi')
            st.pyplot(fig_hist)
        
        with col2:
            st.subheader("Box Plot")
            fig_box, ax_box = plt.subplots()
            ax_box.boxplot(gdf_clean['value'])
            ax_box.set_ylabel('Nilai')
            st.pyplot(fig_box)
        
        # Tampilkan statistik
        st.subheader("Statistik Deskriptif")
        st.dataframe(gdf_clean['value'].describe())

    with tab3:
        st.header("Data")
        st.dataframe(gdf_clean.drop(columns=['geometry']))
else:
    st.error("Tidak dapat memuat data. Pastikan data sampel telah dibuat dengan menjalankan 'python scripts/create_sample_data.py'")

# Informasi tambahan
st.sidebar.subheader("Informasi")
st.sidebar.info(
    "Dashboard ini menampilkan analisis data lahan simulasi."
)