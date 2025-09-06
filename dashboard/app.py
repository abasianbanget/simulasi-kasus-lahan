import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import sqlite3

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

# Fungsi untuk membuat peta
def create_map():
    m = folium.Map(location=[2.1667, 100.8000], zoom_start=12)
    folium.Marker(
        [2.1667, 100.8000],
        popup='Desa Pedamaran',
        tooltip='Area Konflik Utama'
    ).add_to(m)
    folium.Polygon(
        locations=[[2.18, 100.79], [2.18, 100.81], [2.15, 100.81], [2.15, 100.79]],
        color='red',
        fill=True,
        fillColor='red',
        fillOpacity=0.2,
        popup='Area Sengketa ±1.500 Ha'
    ).add_to(m)
    return m

# Fungsi database
def init_db():
    conn = sqlite3.connect('conflict_data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS conflicts
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         year INTEGER,
         event TEXT,
         impact_level INTEGER)
    ''')
    conn.commit()
    conn.close()

def add_conflict(year, event, impact_level):
    conn = sqlite3.connect('conflict_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO conflicts (year, event, impact_level) VALUES (?, ?, ?)",
              (year, event, impact_level))
    conn.commit()
    conn.close()

def get_conflicts():
    conn = sqlite3.connect('conflict_data.db')
    df = pd.read_sql_query("SELECT * FROM conflicts", conn)
    conn.close()
    return df

init_db()

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
        }
    }

conflict_data = load_conflict_data()

# Form tambah data di sidebar
with st.sidebar:
    st.subheader("Tambah Data Konflik Baru")
    with st.form("tambah_data_form"):
        year = st.number_input("Tahun", min_value=1980, max_value=2030, value=2023)
        event = st.text_input("Peristiwa")
        impact = st.slider("Tingkat Dampak", 1, 5, 3)
        submitted = st.form_submit_button("Tambah")
        if submitted:
            add_conflict(year, event, impact)
            st.success("Data berhasil ditambahkan!")

# Buat tabs
tab1, tab2, tab3 = st.tabs(["Overview", "Peta", "Analisis"])

with tab1:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Luas Sengketa", "1,500 Ha")
    col2.metric("Durasi Konflik", "28 Tahun")
    col3.metric("Keluarga Terdampak", "150+")
    col4.metric("Nilai Kerugian", "Rp 45 M" if show_idr else "$3.21M")

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

    for event in conflict_data['timeline']:
        with st.expander(f"{event['year']}: {event['event']}"):
            st.write(event['event'])

with tab2:
    st.subheader("Peta Interaktif Konflik Lahan")
    map_obj = create_map()
    st_folium(map_obj, width=700, height=500)

with tab3:
    st.subheader("Analisis Data")
    
    data = pd.DataFrame({
        'Tahun': [1981, 1993, 1996, 2005, 2011, 2014, 2015, 2023, 2025],
        'Luas_Sengketa': [9220, 9220, 9220, 11074, 10730, 10730, 1500, 1500, 1500],
        'Intensitas_Konflik': [1, 1, 2, 3, 4, 3, 4, 5, 5]
    })
    
    fig1 = px.line(data, x='Tahun', y='Luas_Sengketa', title='Perkembangan Luas Sengketa')
    st.plotly_chart(fig1, use_container_width=True)
    
    fig2 = px.bar(data, x='Tahun', y='Intensitas_Konflik', title='Intensitas Konflik per Tahun')
    st.plotly_chart(fig2, use_container_width=True)
    
    st.subheader("Simulasi Prediksi Konflik")
    tahun_prediksi = st.slider("Tahun Prediksi", 2025, 2030, 2027)
    trend = 0.5
    intensitas_terakhir = 5
    tahun_terakhir = 2025
    prediksi = intensitas_terakhir + (tahun_prediksi - tahun_terakhir) * trend
    st.metric("Prediksi Intensitas Konflik", f"{prediksi:.1f}/5.0")
    if prediksi < 3:
        st.success("Kemungkinan konflik rendah")
    elif prediksi < 4:
        st.warning("Kemungkinan konflik sedang")
    else:
        st.error("Kemungkinan konflik tinggi")
    
    st.subheader("Data Konflik dari Database")
    df = get_conflicts()
    st.dataframe(df)

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