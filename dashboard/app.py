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
# --- FILTER DATA ---
st.sidebar.subheader("Filter Data")

# 1. Filter berdasarkan range nilai
min_val = float(gdf_clean['value'].min())
max_val = float(gdf_clean['value'].max())
value_range = st.sidebar.slider(
    "Rentang Nilai Lahan",
    min_val,
    max_val,
    (min_val, max_val),
    help="Pilih rentang nilai lahan yang ingin ditampilkan"
)

# 2. Filter berdasarkan jumlah data
sample_size = st.sidebar.slider(
    "Jumlah Data yang Ditampilkan",
    min_value=10,
    max_value=len(gdf_clean),
    value=min(100, len(gdf_clean)),
    step=10,
    help="Batasi jumlah data yang ditampilkan untuk performa yang lebih baik"
)

# 3. Filter berdasarkan kriteria tambahan (opsional)
st.sidebar.subheader("Filter Lanjutan")
show_outliers = st.sidebar.checkbox(
    "Sertakan Outlier", 
    value=True,
    help="Tampilkan data yang merupakan outlier"
)

# 4. Filter berdasarkan zona/area (jika data memiliki informasi zona)
if 'zone' in gdf_clean.columns:
    zones = gdf_clean['zone'].unique()
    selected_zones = st.sidebar.multiselect(
        "Pilih Zona",
        options=zones,
        default=zones,
        help="Pilih zona yang ingin ditampilkan"
    )
    # Terapkan filter pada data
filtered_data = gdf_clean.copy()

# Filter berdasarkan range nilai
filtered_data = filtered_data[
    (filtered_data['value'] >= value_range[0]) & 
    (filtered_data['value'] <= value_range[1])
]

# Filter berdasarkan zona (jika ada)
if 'zone' in gdf_clean.columns and selected_zones:
    filtered_data = filtered_data[filtered_data['zone'].isin(selected_zones)]

# Filter outlier jika diperlukan
if not show_outliers:
    Q1 = filtered_data['value'].quantile(0.25)
    Q3 = filtered_data['value'].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    filtered_data = filtered_data[
        (filtered_data['value'] >= lower_bound) & 
        (filtered_data['value'] <= upper_bound)
    ]

# Ambil sampel data sesuai dengan jumlah yang dipilih
if sample_size < len(filtered_data):
    filtered_data = filtered_data.sample(n=sample_size, random_state=42)

    with tab1:
    st.header("Peta Interaktif Nilai Lahan")
    
    # Tambahkan opsi untuk memilih kolom yang ditampilkan di peta
    map_value_column = st.selectbox(
        "Pilih nilai yang ditampilkan di peta",
        options=['value', 'log_value'] if 'log_value' in filtered_data.columns else ['value'],
        help="Pilih kolom nilai yang ingin ditampilkan di peta"
    )
    
    # Tambahkan opsi untuk mengubah style peta
    map_style = st.selectbox(
        "Pilih style peta",
        options=['open-street-map', 'carto-positron', 'carto-darkmatter', 'stamen-terrain', 'stamen-toner'],
        help="Pilih style peta yang diinginkan"
    )
    
    try:
        fig = create_interactive_map(filtered_data, map_value_column, 'Distribusi Nilai Lahan')
        fig.update_layout(mapbox_style=map_style)
        st.plotly_chart(fig, use_container_width=True)
        
        # Tambahkan fitur download data dari peta
        st.download_button(
            label="Download Data Peta (CSV)",
            data=filtered_data.drop(columns=['geometry']).to_csv(index=False),
            file_name="filtered_land_data.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"Error creating interactive map: {e}")
        st.info("Menggunakan static map sebagai alternatif...")
        fig = create_static_map(filtered_data, map_value_column, 'Distribusi Nilai Lahan')
        st.pyplot(fig)

        with tab2:
    st.header("Analisis Statistik")
    
    # Tambahkan opsi untuk mengubah jumlah bins histogram
    bins = st.slider(
        "Jumlah Bins Histogram",
        min_value=5,
        max_value=50,
        value=20,
        help="Atur jumlah bins untuk histogram"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribusi Nilai")
        fig_hist, ax_hist = plt.subplots()
        ax_hist.hist(filtered_data['value'], bins=bins, edgecolor='black', alpha=0.7)
        ax_hist.set_xlabel('Nilai (USD)')
        ax_hist.set_ylabel('Frekuensi')
        
        # Tambahkan garis untuk mean dan median
        mean_val = filtered_data['value'].mean()
        median_val = filtered_data['value'].median()
        ax_hist.axvline(mean_val, color='red', linestyle='dashed', linewidth=1, label=f'Mean: ${mean_val:,.2f}')
        ax_hist.axvline(median_val, color='green', linestyle='dashed', linewidth=1, label=f'Median: ${median_val:,.2f}')
        ax_hist.legend()
        
        st.pyplot(fig_hist)
    
    with col2:
        st.subheader("Box Plot")
        fig_box, ax_box = plt.subplots()
        ax_box.boxplot(filtered_data['value'])
        ax_box.set_ylabel('Nilai (USD)')
        
        # Tambahkan titik untuk mean
        ax_box.plot(1, mean_val, 'ro', label=f'Mean: ${mean_val:,.2f}')
        ax_box.legend()
        
        st.pyplot(fig_box)
    
    # Tambahkan opsi untuk menampilkan statistik deskriptif
    show_stats = st.checkbox("Tampilkan Statistik Deskriptif Lengkap", value=True)
    if show_stats:
        st.subheader("Statistik Deskriptif")
        stats = filtered_data['value'].describe()
        if show_idr:
            stats_formatted = stats.apply(lambda x: format_currency(x, "IDR"))
        else:
            stats_formatted = stats.apply(lambda x: format_currency(x, "USD"))
        st.dataframe(stats_formatted)

        with tab3:
    st.header("Data")
    
    # Tambahkan opsi untuk mengatur jumlah baris yang ditampilkan
    rows_per_page = st.selectbox("Baris per halaman", [10, 25, 50, 100])
    
    # Tambahkan fitur pencarian
    search_term = st.text_input("Cari data", "")
    if search_term:
        display_data = filtered_data[filtered_data.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
    else:
        display_data = filtered_data.copy()
    
    # Hitung jumlah halaman
    total_pages = max(1, len(display_data) // rows_per_page + (1 if len(display_data) % rows_per_page > 0 else 0))
    
    # Tambahkan navigasi halaman
    page_number = st.number_input("Halaman", min_value=1, max_value=total_pages, value=1)
    
    # Tampilkan data untuk halaman tertentu
    start_idx = (page_number - 1) * rows_per_page
    end_idx = min(start_idx + rows_per_page, len(display_data))
    
    # Format kolom value berdasarkan mata uang yang dipilih
    display_data = display_data.drop(columns=['geometry']).copy()
    if show_idr:
        display_data['value'] = display_data['value'].apply(lambda x: format_currency(x, "IDR"))
    else:
        display_data['value'] = display_data['value'].apply(lambda x: format_currency(x, "USD"))
    
    st.dataframe(display_data.iloc[start_idx:end_idx])
    
    # Tampilkan informasi halaman
    st.write(f"Menampilkan {start_idx + 1} - {end_idx} dari {len(display_data)} baris")
    
    # Tambahkan fitur ekspor data
    st.subheader("Ekspor Data")
    export_format = st.selectbox("Format ekspor", ["CSV", "Excel"])
    
    if st.button("Ekspor Data"):
        if export_format == "CSV":
            csv_data = display_data.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="filtered_land_data.csv",
                mime="text/csv"
            )
        elif export_format == "Excel":
            # Untuk ekspor Excel, kita perlu library tambahan
            try:
                import io
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    display_data.to_excel(writer, index=False, sheet_name='Data Lahan')
                st.download_button(
                    label="Download Excel",
                    data=buffer.getvalue(),
                    file_name="filtered_land_data.xlsx",
                    mime="application/vnd.ms-excel"
                )
            except ImportError:
                st.error("Library openpyxl tidak tersedia. Silakan tambahkan ke requirements.txt")

   # Di bagian bawah sidebar, tambahkan tombol reset
st.sidebar.markdown("---")
if st.sidebar.button("Reset Semua Filter"):
    # Reset semua nilai filter ke default
    st.experimental_set_query_params()
    st.experimental_rerun()
    
                 