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

# CSS custom untuk judul yang di-center dan freeze
st.markdown(
    """
    <style>
    .main-header {
        text-align: center;
        position: sticky;
        top: 0;
        background-color: white;
        z-index: 1000;
        padding: 10px;
        margin-bottom: 20px;
        border-bottom: 2px solid #f0f2f6;
    }
    .stApp {
        margin-top: 60px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Judul aplikasi dengan CSS custom
st.markdown('<div class="main-header"><h1>🏞️ Dashboard Simulasi Kasus Lahan</h1></div>', unsafe_allow_html=True)

# Sidebar
st.sidebar.header("Konfigurasi")

# Konfigurasi Mata Uang dalam expander (tersembunyi secara default)
with st.sidebar.expander("⚙️ Konfigurasi Mata Uang (Opsional)", expanded=False):
    exchange_rate = st.number_input(
        "Nilai Tukar USD ke IDR",
        min_value=1000.0,
        max_value=20000.0,
        value=14000.0,
        step=100.0,
        help="Masukkan nilai tukar USD ke Rupiah"
    )
    
    show_idr = st.checkbox("Tampilkan dalam Rupiah", value=False)

# Fungsi untuk format mata uang dengan penanganan digit yang lebih baik
def format_currency(amount, currency="USD"):
    try:
        if currency == "IDR":
            # Format Rupiah tanpa desimal, dengan pemisah ribuan
            nilai_idr = amount * exchange_rate
            if nilai_idr >= 1_000_000_000_000:  # Triliun
                return f"Rp {nilai_idr/1_000_000_000_000:.2f} T"
            elif nilai_idr >= 1_000_000_000:  # Miliar
                return f"Rp {nilai_idr/1_000_000_000:.2f} M"
            elif nilai_idr >= 1_000_000:  # Juta
                return f"Rp {nilai_idr/1_000_000:.2f} Jt"
            elif nilai_idr >= 1_000:  # Ribu
                return f"Rp {nilai_idr/1_000:.2f} Rb"
            else:
                return f"Rp {nilai_idr:,.0f}".replace(",", ".")
        else:
            # Format USD dengan 2 desimal
            if amount >= 1_000_000_000:  # Billion
                return f"${amount/1_000_000_000:.2f}B"
            elif amount >= 1_000_000:  # Million
                return f"${amount/1_000_000:.2f}M"
            elif amount >= 1_000:  # Thousand
                return f"${amount/1_000:.2f}K"
            else:
                return f"${amount:,.2f}"
    except:
        return f"${amount:,.2f}"  # Fallback format

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
    # Tampilkan metrik dengan opsi mata uang
    col1, col2, col3, col4 = st.columns(4)
    currency = "IDR" if show_idr else "USD"
    
    col1.metric("Jumlah Data", len(gdf_clean))
    col2.metric("Nilai Rata-rata", format_currency(gdf_clean['value'].mean(), currency))
    col3.metric("Nilai Minimum", format_currency(gdf_clean['value'].min(), currency))
    col4.metric("Nilai Maksimum", format_currency(gdf_clean['value'].max(), currency))

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
        stats = gdf_clean['value'].describe()
        if show_idr:
            stats_formatted = stats.apply(lambda x: format_currency(x, "IDR"))
        else:
            stats_formatted = stats.apply(lambda x: format_currency(x, "USD"))
        st.dataframe(stats_formatted)

    with tab3:
        st.header("Data")
        
        # Format kolom value berdasarkan mata uang yang dipilih
        display_data = gdf_clean.drop(columns=['geometry']).copy()
        if show_idr:
            display_data['value'] = display_data['value'].apply(lambda x: format_currency(x, "IDR"))
        else:
            display_data['value'] = display_data['value'].apply(lambda x: format_currency(x, "USD"))
        
        st.dataframe(display_data)
else:
    st.error("Tidak dapat memuat data. Pastikan data sampel telah dibuat dengan menjalankan 'python scripts/create_sample_data.py'")

# Informasi tambahan
st.sidebar.subheader("Informasi")
st.sidebar.info(
    "Dashboard ini menampilkan analisis data lahan simulasi. "
    "Gunakan opsi konfigurasi mata uang untuk menampilkan nilai dalam Rupiah."
)