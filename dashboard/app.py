import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys
import os
import numpy as np
import geopandas as gpd
from shapely.geometry import Point

# ... (kode yang sudah ada sebelumnya)

# Judul aplikasi
st.title("🏞️ Dashboard Simulasi Kasus Lahan")

# Sidebar
st.sidebar.header("Konfigurasi")

# Tambahkan input untuk nilai tukar USD ke IDR
st.sidebar.subheader("Konfigurasi Mata Uang")
exchange_rate = st.sidebar.number_input(
    "Nilai Tukar USD ke IDR",
    min_value=1000,
    max_value=20000,
    value=14000,  # Nilai default
    step=100,
    help="Masukkan nilai tukar USD ke Rupiah"
)

# Fungsi untuk konversi mata uang
def format_currency(amount, currency="USD"):
    if currency == "IDR":
        return f"Rp {amount * exchange_rate:,.0f}"
    else:
        return f"${amount:,.2f}"

# Load data dengan error handling yang lebih baik
@st.cache_data
def load_data():
    # ... (kode yang sudah ada sebelumnya)

gdf_clean, config = load_data()

if gdf_clean is not None:
    # Tampilkan metrik dengan opsi mata uang
    col1, col2, col3, col4 = st.columns(4)
    
    # Tambahkan toggle untuk mata uang
    show_idr = st.sidebar.checkbox("Tampilkan dalam Rupiah", value=False)
    currency = "IDR" if show_idr else "USD"
    
    col1.metric("Jumlah Data", len(gdf_clean))
    col2.metric("Nilai Rata-rata", format_currency(gdf_clean['value'].mean(), currency))
    col3.metric("Nilai Minimum", format_currency(gdf_clean['value'].min(), currency))
    col4.metric("Nilai Maksimum", format_currency(gdf_clean['value'].max(), currency))

    # Tab untuk berbagai visualisasi
    tab1, tab2, tab3, tab4 = st.tabs(["Peta Interaktif", "Analisis Statistik", "Data", "Simulasi"])

    with tab1:
        st.header("Peta Interaktif Nilai Lahan")
        # ... (kode yang sudah ada sebelumnya)

    with tab2:
        st.header("Analisis Statistik")
        # ... (kode yang sudah ada sebelumnya)
        
        # Tampilkan statistik dengan mata uang yang dipilih
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

    with tab4:
        st.header("Simulasi Nilai Lahan")
        
        st.subheader("Kalkulator Konversi Mata Uang")
        col1, col2 = st.columns(2)
        
        with col1:
            usd_value = st.number_input("Nilai dalam USD", min_value=0.0, value=100000.0, step=1000.0)
        
        with col2:
            st.metric("Nilai dalam IDR", format_currency(usd_value, "IDR"))
        
        st.subheader("Simulasi Kenaikan Nilai")
        annual_increase = st.slider("Kenaikan Tahunan (%)", min_value=0.0, max_value=20.0, value=5.0, step=0.5)
        years = st.slider("Jumlah Tahun", min_value=1, max_value=10, value=5)
        
        future_value = usd_value * (1 + annual_increase/100) ** years
        st.metric("Nilai Masa Depan", format_currency(future_value, "IDR" if show_idr else "USD"))

# ... (kode yang sudah ada sebelumnya)