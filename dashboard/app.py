import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import json

# Konfigurasi halaman
st.set_page_config(
    page_title="Simulator Konflik Lahan - Rohil",
    page_icon="🌍",
    layout="wide"
)

# CSS custom
st.markdown("""
<style>
.watermark {
    position: fixed;
    bottom: 20px;
    right: 20px;
    opacity: 0.8;
    color: white;
    font-size: 14px;
    z-index: 1000;
    text-align: right;
    background: rgba(0, 0, 0, 0.5);
    padding: 10px 15px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# Judul aplikasi
st.title("🌍 Simulator Konflik Lahan")
st.markdown("**Desa Pedamaran, Kabupaten Rokan Hilir - PT Jatim Jaya Perkasa vs Masyarakat**")

# Sidebar
st.sidebar.header("Konfigurasi")
show_idr = st.sidebar.checkbox("Tampilkan dalam Rupiah", value=True)
exchange_rate = st.sidebar.number_input("Nilai Tukar USD ke IDR", value=14000.0) if show_idr else 14000.0

# Data konflik
def load_conflict_data():
    return {
        'timeline': [
            {'year': 1981, 'event': 'Pemberian HPL Transmigrasi seluas 9.220 Ha melalui SK Mendagri'},
            {'year': 1993, 'event': 'Sertifikasi HPL Transmigrasi Rokan I'},
            {'year': 1996, 'event': 'Masyarakat mulai menggarap lahan dengan izin Kepala Desa'},
            {'year': 1997, 'event': 'Pengusiran paksa oleh PT JJP tanpa ganti rugi'},
            {'year': 2005, 'event': 'Penerbitan HGU PT JJP seluas 8.200 Ha'},
            {'year': 2011, 'event': 'Revisi koordinat oleh PT JJP tanpa konsultasi masyarakat'},
            {'year': 2014, 'event': 'Usulan penyelesaian oleh Bupati Rokan Hilir'},
            {'year': 2015, 'event': 'Pelepasan HPL oleh Kemendes PDTT'},
            {'year': 2023, 'event': 'Mediasi gagal karena PT JJP tidak hadir'},
            {'year': 2025, 'event': 'Tuntutan masyarakat melalui DPC PATRI'}
        ],
        'stats': {
            'luas_sengketa': 1500,
            'durasi_konflik': 28,
            'keluarga_terdampak': 150,
            'nilai_kerugian': 45000000000
        },
        'coordinates': [2.1667, 100.8000]  # Koordinat Desa Pedamaran
    }

conflict_data = load_conflict_data()

# Tampilkan metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Luas Sengketa", "1,500 Ha")
col2.metric("Durasi Konflik", "28 Tahun")
col3.metric("Keluarga Terdampak", "150+")
col4.metric("Nilai Kerugian", "Rp 45 M" if show_idr else "$3.21M")

# Tab untuk organisasi konten
tab1, tab2, tab3 = st.tabs(["Kronologi", "Peta Interaktif", "Analisis"])

with tab1:
    # Grafik timeline
    st.subheader("Kronologi Konflik")
    years = [event['year'] for event in conflict_data['timeline']]
    events = [event['event'] for event in conflict_data['timeline']]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years,
        y=[1] * len(years),
        mode='markers+text',
        marker=dict(size=15, color='red'),
        text=[str(year) for year in years],
        textposition="top center",
        name="Tahun"
    ))

    fig.update_layout(
        title="Timeline Konflik Lahan",
        xaxis_title="Tahun",
        yaxis=dict(showticklabels=False, showgrid=False),
        height=400,
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # Tampilkan detail timeline
    for event in conflict_data['timeline']:
        with st.expander(f"{event['year']}: {event['event']}"):
            st.write(event['event'])

with tab2:
    st.subheader("Peta Interaktif Konflik Lahan")
    
    # Buat peta dengan Folium
    m = folium.Map(location=conflict_data['coordinates'], zoom_start=12)
    
    # Tambahkan marker untuk area konflik
    folium.Marker(
        conflict_data['coordinates'],
        popup="Desa Pedamaran: Area Konflik Lahan",
        tooltip="Klik untuk detail"
    ).add_to(m)
    
    # Tambahkan area sekitar sebagai polygon (contoh)
    folium.Rectangle(
        bounds=[[2.15, 100.78], [2.18, 100.82]],
        popup="Perkiraan Area Sengketa",
        color="#ff7800",
        fill=True,
        fill_color="#ffff00",
        fill_opacity=0.2
    ).add_to(m)
    
    # Tampilkan peta
    st_folium(m, width=700, height=500)

with tab3:
    st.subheader("Analisis Konflik Lahan")
    
    # Data untuk analisis sederhana
    st.write("### Distribusi Penggunaan Lahan")
    land_use_data = pd.DataFrame({
        'Jenis Lahan': ['Perkebunan', 'Pertanian', 'Pemukiman', 'Hutan', 'Lainnya'],
        'Luas (Ha)': [800, 400, 200, 100, 100]
    })
    
    fig = px.pie(land_use_data, values='Luas (Ha)', names='Jenis Lahan', title='Distribusi Penggunaan Lahan')
    st.plotly_chart(fig, use_container_width=True)
    
    # Grafik batang untuk nilai lahan
    st.write("### Perkembangan Nilai Lahan")
    years = [2010, 2015, 2020, 2023]
    land_values = [50000000, 75000000, 100000000, 150000000]  # dalam Rupiah per Ha
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=years,
        y=land_values,
        name='Nilai Lahan per Ha',
        marker_color='indianred'
    ))
    
    fig.update_layout(
        title='Perkembangan Nilai Lahan per Hektar',
        xaxis_title='Tahun',
        yaxis_title='Nilai (Rupiah)',
        yaxis_tickformat = ',.0f'
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Watermark
st.markdown(
    """
    <div class="watermark">
        <div>Powered By Agung Basuki</div>
        <div>Didukung oleh LSM Bismi</div>
    </div>
    """,
    unsafe_allow_html=True
)