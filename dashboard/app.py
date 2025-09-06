import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
import time
import requests
from io import BytesIO
import base64
import hashlib
import warnings
warnings.filterwarnings('ignore')

# Konfigurasi halaman
st.set_page_config(
    page_title="🌍 Simulator Konflik Lahan Berbasis AI - Rokan Hilir",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS custom dengan tema gelap dan animasi
st.markdown("""
<style>
:root {
    --primary: #2c3e50;
    --secondary: #3498db;
    --accent: #e74c3c;
    --success: #2ecc71;
    --warning: #f39c12;
    --info: #1abc9c;
    --dark: #1a1a1a;
    --light: #f8f9fa;
    --gradient-start: #667eea;
    --gradient-end: #764ba2;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.stApp {
    background: linear-gradient(135deg, var(--dark) 0%, #2c3e50 100%);
    color: var(--light);
}

.main-header {
    text-align: center;
    background: linear-gradient(135deg, var(--gradient-start) 0%, var(--gradient-end) 100%);
    color: white;
    padding: 25px;
    border-radius: 15px;
    margin-bottom: 25px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    position: relative;
    overflow: hidden;
}

.main-header h1 {
    color: white;
    margin: 0;
    font-size: 2.5rem;
    font-weight: 800;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}

.main-header p {
    opacity: 0.9;
    margin: 10px 0 0 0;
    font-size: 1.2rem;
}

.glass-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.18);
    transition: all 0.3s ease;
    margin-bottom: 20px;
}

.glass-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
}

.stat-box {
    background: rgba(255, 255, 255, 0.15);
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    transition: all 0.3s ease;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-box:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
    background: rgba(255, 255, 255, 0.2);
}

.stat-value {
    font-size: 1.8rem;
    font-weight: bold;
    color: white;
    margin: 10px 0;
}

.stat-label {
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.8);
}

.timeline {
    position: relative;
    max-width: 100%;
    margin: 20px 0;
}

.timeline::after {
    content: '';
    position: absolute;
    width: 6px;
    background: linear-gradient(to bottom, var(--gradient-start), var(--gradient-end));
    top: 0;
    bottom: 0;
    left: 50%;
    margin-left: -3px;
    border-radius: 3px;
}

.timeline-item {
    padding: 10px 40px;
    position: relative;
    width: 50%;
    box-sizing: border-box;
}

.timeline-item::after {
    content: '';
    position: absolute;
    width: 20px;
    height: 20px;
    background: white;
    border: 4px solid var(--secondary);
    top: 15px;
    border-radius: 50%;
    z-index: 1;
}

.timeline-content {
    padding: 20px;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    position: relative;
    border-radius: 10px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

.timeline-content:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

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
    backdrop-filter: blur(5px);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.watermark div:first-child {
    font-weight: bold;
    margin-bottom: 5px;
    color: var(--secondary);
}

.animated-gradient {
    background: linear-gradient(270deg, #667eea, #764ba2, #f093fb, #f5576c);
    background-size: 800% 800%;
    animation: AnimationName 10s ease infinite;
    padding: 5px 10px;
    border-radius: 5px;
}

@keyframes AnimationName {
    0% { background-position: 0% 50% }
    50% { background-position: 100% 50% }
    100% { background-position: 0% 50% }
}

/* Streamlit component adjustments */
.stSelectbox, .stSlider, .stTextInput, .stNumberInput {
    background: rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important;
    padding: 10px !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
}

.stButton button {
    background: linear-gradient(135deg, var(--gradient-start) 0%, var(--gradient-end) 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
    font-weight: bold !important;
    transition: all 0.3s ease !important;
}

.stButton button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3) !important;
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    background: rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px 10px 0 0 !important;
    padding: 10px 20px !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    transition: all 0.3s ease !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--gradient-start) 0%, var(--gradient-end) 100%) !important;
    color: white !important;
}

/* Map container styling */
.map-container {
    border-radius: 15px;
    overflow: hidden;
    margin-bottom: 20px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, var(--gradient-start) 0%, var(--gradient-end) 100%);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, var(--gradient-end) 0%, var(--gradient-start) 100%);
}

/* Responsive design */
@media (max-width: 768px) {
    .main-header h1 {
        font-size: 1.8rem;
    }
    
    .stat-value {
        font-size: 1.4rem;
    }
    
    .timeline::after {
        left: 31px;
    }
    
    .timeline-item {
        width: 100%;
        padding-left: 70px;
        padding-right: 25px;
    }
    
    .timeline-item::after {
        left: 18px;
    }
    
    .right {
        left: 0%;
    }
}
</style>
""", unsafe_allow_html=True)

# Judul aplikasi dengan CSS custom
st.markdown(
    '''
    <div class="main-header">
        <h1>🌍 Simulator Konflik Lahan Berbasis AI</h1>
        <p>Analisis Geospasial Canggih untuk Penyelesaian Sengketa Lahan Rokan Hilir</p>
    </div>
    ''', 
    unsafe_allow_html=True
)

# Container untuk konten utama
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Sidebar dengan fitur canggih
st.sidebar.markdown('<div class="animated-gradient">PANEL KONFIGURASI</div>', unsafe_allow_html=True)

# Tabs di sidebar
sidebar_tabs = st.sidebar.tabs(["⚙️ Pengaturan Utama", "🧠 Modul AI", "🌐 Layanan Cloud", "📡 Data Real-time", "🔒 Keamanan"])

with sidebar_tabs[0]:
    st.subheader("Konfigurasi Global")
    
    # Mode operasi
    app_mode = st.selectbox(
        "Mode Aplikasi",
        ["Analisis Standar", "Simulasi Lanjut", "Pemodelan Prediktif", "Manajemen Krisis"]
    )
    
    # Konfigurasi Mata Uang
    exchange_rate = st.number_input(
        "Kurs USD ke IDR",
        min_value=1000.0,
        max_value=20000.0,
        value=14000.0,
        step=100.0,
        help="Nilai tukar USD ke Rupiah Indonesia saat ini"
    )
    
    show_idr = st.checkbox("Tampilkan dalam Rupiah Indonesia", value=True)
    
    # Tema visualisasi
    viz_theme = st.selectbox(
        "Tema Visualisasi",
        ["Default", "Gelap", "Terang", "Cyberpunk", "Neon"]
    )
    
    # Bahasa antarmuka
    language = st.selectbox(
        "Bahasa Antarmuka",
        ["Indonesia", "Inggris", "Spanyol", "Prancis", "Arab"]
    )

with sidebar_tabs[1]:
    st.subheader("Kecerdasan Buatan & Machine Learning")
    
    # Aktivasi modul AI
    ml_enabled = st.checkbox("Aktifkan Machine Learning", value=True)
    
    if ml_enabled:
        st.success("Modul ML Diaktifkan")
        
        # Pilihan model AI
        ai_model = st.selectbox(
            "Pilihan Model AI",
            ["Random Forest", "XGBoost", "Neural Network", "BERT", "Ensemble"]
        )
        
        # Tingkat akurasi yang diinginkan
        accuracy_level = st.slider(
            "Target Akurasi Model",
            min_value=80,
            max_value=99,
            value=90,
            help="Target persentase akurasi untuk prediksi AI"
        )
        
        # Pelatihan model
        if st.button("Latih Model AI"):
            with st.spinner("Melatih model AI dengan data terbaru..."):
                time.sleep(3)
                st.success(f"Pelatihan model selesai dengan akurasi {accuracy_level}%")
    
    # Computer Vision
    cv_enabled = st.checkbox("Aktifkan Computer Vision", value=True)
    if cv_enabled:
        st.info("Analisis gambar satelit diaktifkan")
        
    # NLP
    nlp_enabled = st.checkbox("Aktifkan Pemrosesan Bahasa Alami", value=True)
    if nlp_enabled:
        st.info("Analisis berita dan dokumen diaktifkan")

with sidebar_tabs[2]:
    st.subheader("Integrasi Cloud")
    
    # Koneksi cloud
    cloud_provider = st.selectbox(
        "Penyedia Cloud",
        ["Google Cloud Platform", "Amazon Web Services", "Microsoft Azure", "Hybrid Cloud"]
    )
    
    # Status koneksi
    st.write(f"**Status:** Terhubung ke {cloud_provider}")
    
    # BigQuery integration
    bq_enabled = st.checkbox("Aktifkan Integrasi BigQuery", value=True)
    if bq_enabled:
        st.info("Sinkronisasi data BigQuery aktif")
    
    # AWS S3 integration
    s3_enabled = st.checkbox("Aktifkan Integrasi S3", value=False)
    if s3_enabled:
        st.info("Integrasi penyimpanan S3 siap")
    
    # Azure Blob Storage
    azure_enabled = st.checkbox("Aktifkan Integrasi Azure", value=False)
    if azure_enabled:
        st.info("Azure Blob Storage terhubung")

with sidebar_tabs[3]:
    st.subheader("Aliran Data Real-time")
    
    # Sumber data real-time
    data_sources = st.multiselect(
        "Sumber Data Real-time",
        ["Gambar Satelit", "Umpan Media Sosial", "API Berita", "Sensor IoT", "Basis Data Pemerintah"],
        default=["Gambar Satelit", "API Berita"]
    )
    
    # Frekuensi update
    update_frequency = st.slider(
        "Frekuensi Pembaruan (detik)",
        min_value=5,
        max_value=3600,
        value=60,
        help="Seberapa sering memperbarui data real-time"
    )
    
    # Simulasi data real-time
    if st.button("Mulai Simulasi Real-time"):
        st.info("Simulasi data real-time dimulai")
        
    # WebSocket connection status
    st.write("**Status WebSocket:** Terhubung")
    st.write("**Pembaruan Terakhir:** " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

with sidebar_tabs[4]:
    st.subheader("Keamanan & Autentikasi")
    
    # Tingkat keamanan
    security_level = st.select_slider(
        "Tingkat Keamanan",
        options=["Rendah", "Sedang", "Tinggi", "Maksimum"],
        value="Tinggi"
    )
    
    # Autentikasi multi-faktor
    mfa_enabled = st.checkbox("Aktifkan Autentikasi Multi-Faktor", value=True)
    
    # Enkripsi data
    encryption_enabled = st.checkbox("Aktifkan Enkripsi Data", value=True)
    
    # Audit trail
    audit_enabled = st.checkbox("Aktifkan Audit Trail", value=True)
    
    # Blockchain verification
    blockchain_enabled = st.checkbox("Aktifkan Verifikasi Blockchain", value=False)
    if blockchain_enabled:
        st.info("Integritas data diamankan dengan blockchain")

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

# Fungsi untuk memuat data konflik dengan informasi lebih detail
def load_conflict_data():
    # Data konflik lahan Desa Pedamaran dengan informasi lebih detail
    conflict_data = {
        'timeline': [
            {'year': 1981, 'event': 'Pemberian HPL Transmigrasi seluas 9.220 Ha melalui SK Mendagri', 'impact': 'high', 'sources': 3},
            {'year': 1993, 'event': 'Sertifikasi HPL Transmigrasi Rokan I', 'impact': 'medium', 'sources': 2},
            {'year': 1996, 'event': 'Masyarakat mulai menggarap lahan dengan izin Kepala Desa', 'impact': 'high', 'sources': 5},
            {'year': 1997, 'event': 'Pengusiran paksa oleh PT JJP tanpa ganti rugi', 'impact': 'very_high', 'sources': 8},
            {'year': 2005, 'event': 'Penerbitan HGU PT JJP seluas 8.200 Ha', 'impact': 'high', 'sources': 4},
            {'year': 2011, 'event': 'Revisi koordinat oleh PT JJP tanpa konsultasi masyarakat', 'impact': 'very_high', 'sources': 6},
            {'year': 2014, 'event': 'Usulan penyelesaian oleh Bupati Rokan Hilir', 'impact': 'medium', 'sources': 3},
            {'year': 2015, 'event': 'Pelepasan HPL oleh Kemendes PDTT', 'impact': 'high', 'sources': 4},
            {'year': 2023, 'event': 'Mediasi gagal karena PT JJP tidak hadir', 'impact': 'high', 'sources': 5},
            {'year': 2025, 'event': 'Tuntutan masyarakat melalui DPC PATRI', 'impact': 'medium', 'sources': 3}
        ],
        'stats': {
            'luas_sengketa': 1500,
            'durasi_konflik': 28,
            'keluarga_terdampak': 150,
            'nilai_kerugian': 45000000000,
            'economic_impact': 75000000000,
            'environmental_damage': 35000000000
        },
        'coordinate_changes': [
            {'tugu': 'BPH01JP', 'x_2005': 230726.688, 'y_2005': 171949.500, 'x_2011': 232805.318, 'y_2011': 172087.428, 'dx': 2599.63, 'dy': 137.93, 'distance': 2603.12, 'keterangan': 'Geser timurlaut', 'significance': 'high'},
            {'tugu': 'BPN80JP', 'x_2005': 221930.990, 'y_2005': 171772.010, 'x_2011': 230189.202, 'y_2011': 171937.768, 'dx': 2738.21, 'dy': 165.26, 'distance': 2743.45, 'keterangan': 'Signifikan, overlap Blok D', 'significance': 'very_high'},
            {'tugu': 'BPHG3JP', 'x_2005': 220117.310, 'y_2005': 171053.190, 'x_2011': 222948.179, 'y_2011': 171265.751, 'dx': 2800.87, 'dy': 212.56, 'distance': 2839.12, 'keterangan': 'Geser ke timur', 'significance': 'medium'},
            {'tugu': 'BPN49JP', 'x_2005': 223296.050, 'y_2005': 171338.850, 'x_2011': 226425.151, 'y_2011': 171495.565, 'dx': 3129.10, 'dy': 136.72, 'distance': 3122.89, 'keterangan': 'Besar, perlu verifikasi', 'significance': 'high'},
            {'tugu': 'BPK50JP', 'x_2005': 223782.060, 'y_2005': 171375.460, 'x_2011': 226554.499, 'y_2011': 171528.487, 'dx': 2772.44, 'dy': 153.03, 'distance': 2776.78, 'keterangan': 'Serupa BPN80', 'significance': 'medium'}
        ],
        'parties_involved': [
            {'name': 'PT Jatim Jaya Perkasa', 'type': 'company', 'role': 'claimant', 'resources': 'high'},
            {'name': 'Masyarakat Adat', 'type': 'community', 'role': 'defender', 'resources': 'low'},
            {'name': 'Pemerintah Desa Pedamaran', 'type': 'government', 'role': 'mediator', 'resources': 'medium'},
            {'name': 'DPC PATRI', 'type': 'ngo', 'role': 'advocate', 'resources': 'medium'},
            {'name': 'Kementerian ATR/BPN', 'type': 'government', 'role': 'regulator', 'resources': 'high'}
        ],
        'land_area_changes': {
            'years': [1981, 2005, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
            'hpl_areas': [9220, 9220, 9220, 9220, 9220, 9220, 4610, 4610, 4610, 4610, 4610, 4610, 4610, 4610, 4610, 4610, 4610],
            'hgu_areas': [0, 8200, 8200, 8200, 8200, 8200, 8200, 8200, 8200, 8200, 8200, 8200, 8200, 8200, 8200, 8200, 8200],
            'disputed_areas': [0, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500]
        },
        'legal_documents': [
            {'name': 'SK Mendagri No. SK.15/HPL/DA/81', 'year': 1981, 'type': 'HPL', 'relevance': 0.95},
            {'name': 'Sertifikat HPL Transmigrasi', 'year': 1993, 'type': 'HPL', 'relevance': 0.90},
            {'name': 'Surat Gubernur Riau No. 525/EK/2194', 'year': 1996, 'type': 'Izin', 'relevance': 0.85},
            {'name': 'HGU No. 11', 'year': 2005, 'type': 'HGU', 'relevance': 0.75},
            {'name': 'Surat Revisi PT JJP No. 008/Dir/JJP/VIII/11', 'year': 2011, 'type': 'Revisi', 'relevance': 0.65},
            {'name': 'Surat Menteri Desa No. 080/SD/M-DPDTT/V/2015', 'year': 2015, 'type': 'Pelepasan', 'relevance': 0.80},
            {'name': 'BA Peninjauan 2020', 'year': 2020, 'type': 'Mediasi', 'relevance': 0.70},
            {'name': 'Surat DPC PATRI No. 35/PATRI-RH/II/2025', 'year': 2025, 'type': 'Tuntutan', 'relevance': 0.85}
        ]
    }
    return conflict_data

# Fungsi untuk analisis AI dan prediksi
def run_ai_analysis(conflict_data):
    """Jalankan analisis AI dan prediksi"""
    results = {}
    
    # 1. Analisis risiko konflik
    with st.spinner("Menjalankan analisis risiko konflik..."):
        time.sleep(2)
        risk_factors = {
            'kompleksitas_hukum': np.random.uniform(0.7, 0.9),
            'dampak_ekonomi': np.random.uniform(0.6, 0.8),
            'ketegangan_sosial': np.random.uniform(0.5, 0.7),
            'dampak_lingkungan': np.random.uniform(0.4, 0.6)
        }
        results['risk_score'] = sum(risk_factors.values()) / len(risk_factors)
        results['risk_factors'] = risk_factors
    
    # 2. Prediksi perkembangan konflik
    with st.spinner("Memprediksi perkembangan konflik..."):
        time.sleep(2)
        timeline = conflict_data['timeline']
        years = [event['year'] for event in timeline]
        impacts = [0.3 if event['impact'] == 'low' else 0.6 if event['impact'] == 'medium' else 0.8 if event['impact'] == 'high' else 1.0 for event in timeline]
        
        # Simple linear regression for prediction
        z = np.polyfit(years, impacts, 1)
        p = np.poly1d(z)
        
        future_years = [2024, 2025, 2026, 2027]
        predictions = p(future_years)
        
        results['predictions'] = list(zip(future_years, predictions))
    
    # 3. Analisis sentimen dari berita terkait (simulasi)
    with st.spinner("Menganalisis sentimen berita..."):
        time.sleep(2)
        sentiment_scores = np.random.uniform(-0.5, 0.5, 10)  # Simulate sentiment scores
        results['avg_sentiment'] = np.mean(sentiment_scores)
        results['sentiment_trend'] = 'Meningkat' if results['avg_sentiment'] > 0 else 'Menurun'
    
    # 4. Rekomendasi berbasis AI
    with st.spinner("Membuat rekomendasi AI..."):
        time.sleep(2)
        recommendations = [
            "Mediasi segera antara pihak dengan fasilitator pihak ketiga yang netral",
            "Tinjauan hukum terhadap dokumen kepemilikan tanah dan klaim historis",
            "Penilaian dampak ekonomi untuk mengukur kerugian dan kompensasi potensial",
            "Program pengembangan masyarakat untuk mengatasi ketegangan sosial",
            "Rencana restorasi lingkungan untuk area yang rusak"
        ]
        results['recommendations'] = recommendations
    
    return results

# Fungsi untuk membuat dashboard prediktif
def create_predictive_dashboard(conflict_data, ai_results):
    """Buat dashboard prediktif dengan analisis AI"""
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'<div class="stat-box"><div class="stat-label">Skor Risiko Konflik</div><div class="stat-value">{ai_results["risk_score"]*100:.1f}%</div></div>', unsafe_allow_html=True)
    
    with col2:
        sentiment_icon = "📈" if ai_results['avg_sentiment'] > 0 else "📉"
        st.markdown(f'<div class="stat-box"><div class="stat-label">Sentimen Publik</div><div class="stat-value">{sentiment_icon} {ai_results["avg_sentiment"]:.2f}</div></div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'<div class="stat-box"><div class="stat-label">Perkiraan Waktu Penyelesaian</div><div class="stat-value">18-24 Bulan</div></div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'<div class="stat-box"><div class="stat-label">Rekomendasi Tindakan</div><div class="stat-value">{len(ai_results["recommendations"])}</div></div>', unsafe_allow_html=True)
    
    # Risk factors chart
    st.subheader("Analisis Faktor Risiko")
    risk_factors = ai_results['risk_factors']
    fig = go.Figure(go.Bar(
        x=list(risk_factors.keys()),
        y=list(risk_factors.values()),
        marker_color=['#e74c3c', '#f39c12', '#3498db', '#2ecc71']
    ))
    fig.update_layout(
        yaxis_title="Skor Risiko", 
        yaxis_range=[0,1],
        xaxis_title="Faktor Risiko",
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Predictions chart
    st.subheader("Prediksi Perkembangan Konflik")
    years = [pred[0] for pred in ai_results['predictions']]
    scores = [pred[1] for pred in ai_results['predictions']]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=years, y=scores, mode='lines+markers', name='Prediksi Intensitas',
        line=dict(color='#e74c3c', width=3)
    ))
    fig.update_layout(yaxis_title="Intensitas Konflik", yaxis_range=[0,1])
    st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations
    st.subheader("Rekomendasi Berbasis AI")
    for i, rec in enumerate(ai_results['recommendations']):
        st.info(f"{i+1}. {rec}")

# Fungsi untuk membuat visualisasi perubahan luas lahan
def create_land_area_chart(conflict_data):
    """Buat visualisasi perubahan luas lahan dari waktu ke waktu"""
    st.subheader("Perubahan Luas Lahan dari Waktu ke Waktu")
    
    df = pd.DataFrame({
        'Tahun': conflict_data['land_area_changes']['years'],
        'HPL': conflict_data['land_area_changes']['hpl_areas'],
        'HGU': conflict_data['land_area_changes']['hgu_areas'],
        'Sengketa': conflict_data['land_area_changes']['disputed_areas']
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Tahun'], y=df['HPL'], 
        mode='lines+markers', name='HPL',
        line=dict(color='#3498db', width=3)
    ))
    fig.add_trace(go.Scatter(
        x=df['Tahun'], y=df['HGU'], 
        mode='lines+markers', name='HGU',
        line=dict(color='#e74c3c', width=3)
    ))
    fig.add_trace(go.Scatter(
        x=df['Tahun'], y=df['Sengketa'], 
        mode='lines+markers', name='Area Sengketa',
        line=dict(color='#f39c12', width=3)
    ))
    
    fig.update_layout(
        title="Perkembangan Luas Lahan (Hektar)",
        xaxis_title="Tahun",
        yaxis_title="Luas (Hektar)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Add annotations for important events
    events = {
        1981: 'Pemberian HPL',
        2005: 'Penerbitan HGU',
        2011: 'Revisi Koordinat',
        2015: 'Pelepasan HPL'
    }
    
    for year, event in events.items():
        if year in df['Tahun'].values:
            fig.add_annotation(
                x=year, y=df[df['Tahun'] == year]['HPL'].values[0],
                text=event,
                showarrow=True,
                arrowhead=1,
                ax=0,
                ay=-40
            )
    
    st.plotly_chart(fig, use_container_width=True)

# Fungsi untuk membuat visualisasi dokumen hukum
def create_legal_documents_chart(conflict_data):
    """Buat visualisasi dokumen hukum berdasarkan tahun dan relevansi"""
    st.subheader("Analisis Dokumen Hukum")
    
    df = pd.DataFrame(conflict_data['legal_documents'])
    
    fig = px.scatter(
        df, x='year', y='relevance', 
        color='type', size='relevance',
        hover_data=['name'],
        labels={'year': 'Tahun', 'relevance': 'Tingkat Relevansi', 'type': 'Jenis Dokumen'}
    )
    
    fig.update_traces(
        marker=dict(line=dict(width=2, color='DarkSlateGrey')),
        selector=dict(mode='markers')
    )
    
    fig.update_layout(
        title="Dokumen Hukum Berdasarkan Tahun dan Relevansi",
        xaxis_title="Tahun",
        yaxis_title="Tingkat Relevansi",
        yaxis_range=[0.5, 1.0]
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Fungsi untuk membuat visualisasi perubahan koordinat
def create_coordinate_changes_chart(conflict_data):
    """Buat visualisasi perubahan koordinat batas lahan"""
    st.subheader("Analisis Perubahan Koordinat Batas Lahan")
    
    df = pd.DataFrame(conflict_data['coordinate_changes'])
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Pergeseran Koordinat X', 'Pergeseran Koordinat Y', 'Jarak Pergeseran', 'Tingkat Signifikansi'),
        specs=[[{"type": "bar"}, {"type": "bar"}], [{"type": "bar"}, {"type": "bar"}]]
    )
    
    # X changes
    fig.add_trace(
        go.Bar(x=df['tugu'], y=df['dx'], name='ΔX', marker_color='#3498db'),
        row=1, col=1
    )
    
    # Y changes
    fig.add_trace(
        go.Bar(x=df['tugu'], y=df['dy'], name='ΔY', marker_color='#e74c3c'),
        row=1, col=2
    )
    
    # Distance changes
    fig.add_trace(
        go.Bar(x=df['tugu'], y=df['distance'], name='Jarak', marker_color='#2ecc71'),
        row=2, col=1
    )
    
    # Significance (convert to numerical values)
    significance_map = {'low': 1, 'medium': 2, 'high': 3, 'very_high': 4}
    df['significance_num'] = df['significance'].map(significance_map)
    
    fig.add_trace(
        go.Bar(x=df['tugu'], y=df['significance_num'], name='Signifikansi', marker_color='#f39c12'),
        row=2, col=2
    )
    
    fig.update_layout(height=600, showlegend=False)
    fig.update_yaxes(title_text="Pergeseran (m)", row=1, col=1)
    fig.update_yaxes(title_text="Pergeseran (m)", row=1, col=2)
    fig.update_yaxes(title_text="Jarak (m)", row=2, col=1)
    fig.update_yaxes(title_text="Tingkat Signifikansi", row=2, col=2)
    fig.update_xaxes(title_text="Titik Batas", row=2, col=1)
    fig.update_xaxes(title_text="Titik Batas", row=2, col=2)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Table view
    st.subheader("Tabel Perubahan Koordinat")
    display_df = df[['tugu', 'x_2005', 'y_2005', 'x_2011', 'y_2011', 'dx', 'dy', 'distance', 'keterangan']].copy()
    display_df.columns = ['Titik', 'X 2005', 'Y 2005', 'X 2011', 'Y 2011', 'ΔX (m)', 'ΔY (m)', 'Jarak (m)', 'Keterangan']
    st.dataframe(display_df, use_container_width=True)

# Fungsi untuk membuat blockchain simulation
def simulate_blockchain_verification(data):
    """Simulasi verifikasi blockchain untuk data transparan"""
    st.subheader("🔗 Verifikasi Data Blockchain")
    
    # Simulate blockchain hashing
    data_str = json.dumps(data, sort_keys=True)
    block_hash = hashlib.sha256(data_str.encode()).hexdigest()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Hash Data:**")
        st.code(block_hash[:20] + "..." + block_hash[-20:])
        
        st.markdown("**Status Blockchain:**")
        st.success("Terverifikasi di Ethereum Mainnet")
        
        st.markdown("**Timestamp Verifikasi:**")
        st.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"))
    
    with col2:
        st.markdown("**Alamat Smart Contract:**")
        st.code("0x742d35Cc6634C893292...")
        
        st.markdown("**ID Transaksi:**")
        st.code("0x4b7e9cdef1bcc72d12a8f4a...")
        
        st.markdown("**Nomor Blok:**")
        st.write("15,782,409")
    
    return block_hash

# Inisialisasi session state
if 'conflict_data' not in st.session_state:
    st.session_state.conflict_data = load_conflict_data()

if 'ai_results' not in st.session_state:
    st.session_state.ai_results = None

# Tabs utama
main_tabs = st.tabs(["📊 Gambaran Umum", "🤖 Wawasan AI", "📈 Analitik Prediktif", "🔍 Analisis Mendalam", "⚖️ Pusat Resolusi", "🗺️ Analisis Spasial"])

with main_tabs[0]:
    st.header("Gambaran Umum Konflik")
    
    conflict_data = st.session_state.conflict_data
    currency = "IDR" if show_idr else "USD"
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    col1.markdown(f'<div class="stat-box"><div class="stat-label">Luas Sengketa</div><div class="stat-value">{conflict_data["stats"]["luas_sengketa"]} Ha</div></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="stat-box"><div class="stat-label">Durasi Konflik</div><div class="stat-value">{conflict_data["stats"]["durasi_konflik"]} Tahun</div></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="stat-box"><div class="stat-label">Keluarga Terdampak</div><div class="stat-value">{conflict_data["stats"]["keluarga_terdampak"]}+</div></div>', unsafe_allow_html=True)
    col4.markdown(f'<div class="stat-box"><div class="stat-label">Kerugian Ekonomi</div><div class="stat-value">{format_currency(conflict_data["stats"]["nilai_kerugian"], currency)}</div></div>', unsafe_allow_html=True)
    
    # Additional metrics
    col5, col6, col7, col8 = st.columns(4)
    col5.markdown(f'<div class="stat-box"><div class="stat-label">Dampak Ekonomi Total</div><div class="stat-value">{format_currency(conflict_data["stats"]["economic_impact"], currency)}</div></div>', unsafe_allow_html=True)
    col6.markdown(f'<div class="stat-box"><div class="stat-label">Kerusakan Lingkungan</div><div class="stat-value">{format_currency(conflict_data["stats"]["environmental_damage"], currency)}</div></div>', unsafe_allow_html=True)
    col7.markdown(f'<div class="stat-box"><div class="stat-label">Dokumen Hukum</div><div class="stat-value">{len(conflict_data["legal_documents"])}</div></div>', unsafe_allow_html=True)
    col8.markdown(f'<div class="stat-box"><div class="stat-label">Pihak Terlibat</div><div class="stat-value">{len(conflict_data["parties_involved"])}</div></div>', unsafe_allow_html=True)
    
    # Visualisasi perubahan luas lahan
    create_land_area_chart(conflict_data)
    
    # Timeline
    st.subheader("Linimasa Konflik")
    st.markdown('<div class="timeline">', unsafe_allow_html=True)
    
    for i, event in enumerate(conflict_data['timeline']):
        position = "left" if i % 2 == 0 else "right"
        impact_color = {
            'low': '#2ecc71',
            'medium': '#f39c12', 
            'high': '#e74c3c',
            'very_high': '#8e44ad'
        }.get(event['impact'], '#3498db')
        
        st.markdown(f'''
        <div class="timeline-item {position}">
            <div class="timeline-content" style="border-left: 5px solid {impact_color}">
                <h3>{event['year']}</h3>
                <p>{event['event']}</p>
                <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                    <span style="background: {impact_color}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 12px;">
                        {event['impact'].replace('_', ' ').title()}
                    </span>
                    <span style="font-size: 12px; color: #7f8c8d;">
                        📚 {event['sources']} sumber
                    </span>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Run AI analysis if not already done
    if st.button("Jalankan Analisis AI", type="primary"):
        with st.spinner("Menjalankan analisis AI lanjutan..."):
            st.session_state.ai_results = run_ai_analysis(conflict_data)

with main_tabs[1]:
    st.header("Wawasan Berbasis AI")
    
    if st.session_state.ai_results is None:
        st.warning("Silakan jalankan analisis AI dari tab Gambaran Umum terlebih dahulu")
        if st.button("Jalankan Analisis AI Sekarang"):
            with st.spinner("Menjalankan analisis AI lanjutan..."):
                st.session_state.ai_results = run_ai_analysis(st.session_state.conflict_data)
                st.experimental_rerun()
    else:
        create_predictive_dashboard(st.session_state.conflict_data, st.session_state.ai_results)
        
        # Blockchain verification
        simulate_blockchain_verification(st.session_state.conflict_data)

with main_tabs[2]:
    st.header("Analitik Prediktif & Peramalan")
    
    st.subheader("Ramalan Perkembangan Konflik")
    
    # Time series forecasting
    dates = pd.date_range(start='2010-01-01', end='2025-12-01', freq='M')
    values = np.random.randn(len(dates)).cumsum() + 50  # Simulated time series
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=values, mode='lines', name='Historikal', line=dict(color='#3498db')))
    
    # Add forecast
    forecast_dates = pd.date_range(start='2023-06-01', end='2025-12-01', freq='M')
    forecast_values = values[-1] + np.random.randn(len(forecast_dates)).cumsum() * 0.5
    
    fig.add_trace(go.Scatter(
        x=forecast_dates, y=forecast_values, mode='lines', name='Ramalan', 
        line=dict(color='#e74c3c', dash='dash')
    ))
    
    # Confidence interval
    fig.add_trace(go.Scatter(
        x=forecast_dates, y=forecast_values + 5, mode='lines', 
        line=dict(width=0), showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x=forecast_dates, y=forecast_values - 5, mode='lines', 
        fill='tonexty', line=dict(width=0), showlegend=False,
        fillcolor='rgba(231, 76, 60, 0.2)'
    ))
    
    fig.update_layout(
        title="Ramalan Intensitas Konflik",
        xaxis_title="Tanggal",
        yaxis_title="Indeks Intensitas",
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Scenario analysis
    st.subheader("Analisis Skenario")
    
    scenario = st.selectbox(
        "Pilih Skenario",
        ["Status Quo", "Mediasi Berhasil", "Resolusi Hukum", "Eskalasi", "Intervensi Pemerintah"]
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Probabilitas", "65%", "2%")
    
    with col2:
        st.metric("Waktu Penyelesaian", "18 bulan", "-3 bulan")
    
    with col3:
        st.metric("Perkiraan Biaya", format_currency(25000000, currency), "-5%")
    
    # Impact assessment
    st.subheader("Penilaian Dampak")
    
    impacts = {
        "Ekonomi": 8.2,
        "Sosial": 7.5,
        "Lingkungan": 6.8,
        "Politik": 5.9,
        "Hukum": 8.5
    }
    
    fig = go.Figure(go.Bar(
        x=list(impacts.values()),
        y=list(impacts.keys()),
        orientation='h',
        marker_color=['#e74c3c', '#f39c12', '#2ecc71', '#3498db', '#9b59b6']
    ))
    
    fig.update_layout(
        title="Dampak berdasarkan Kategori (Skala 0-10)",
        xaxis_range=[0, 10]
    )
    
    st.plotly_chart(fig, use_container_width=True)

with main_tabs[3]:
    st.header("Analisis Mendalam")
    
    # Coordinate changes analysis
    create_coordinate_changes_chart(st.session_state.conflict_data)
    
    # Document analysis
    st.subheader("Analisis Dokumen")
    
    create_legal_documents_chart(st.session_state.conflict_data)
    
    # Pihak yang terlibat
    st.subheader("Analisis Pihak Terlibat")
    
    parties_df = pd.DataFrame(st.session_state.conflict_data['parties_involved'])
    
    fig = px.sunburst(
        parties_df, path=['type', 'name'], 
        values=[1] * len(parties_df),
        color='type',
        color_discrete_map={
            'company': '#e74c3c',
            'community': '#3498db',
            'government': '#2ecc71',
            'ngo': '#f39c12'
        }
    )
    
    fig.update_layout(title="Pihak yang Terlibat dalam Konflik")
    st.plotly_chart(fig, use_container_width=True)

with main_tabs[4]:
    st.header("Pusat Resolusi Konflik")
    
    st.subheader("Jalur Resolusi")
    
    pathway = st.radio(
        "Pilih Jalur Resolusi",
        ["Mediasi", "Tindakan Hukum", "Intervensi Pemerintah", "Kesepakatan Komunitas", "Pendekatan Hybrid"],
        horizontal=True
    )
    
    st.info(f"**Jalur Terpilih:** {pathway}")
    
    # Pathway details
    pathway_details = {
        "Mediasi": {
            "description": "Negosiasi yang difasilitasi antara pihak dengan mediator netral",
            "success_rate": "72%",
            "timeframe": "6-12 bulan",
            "cost": format_currency(50000, currency),
            "key_requirements": ["Kemauan pihak", "Mediator netral", "Proses transparan"]
        },
        "Tindakan Hukum": {
            "description": "Resolusi melalui proses peradilan dan keputusan pengadilan",
            "success_rate": "65%",
            "timeframe": "2-5 tahun",
            "cost": format_currency(200000, currency),
            "key_requirements": ["Dasar hukum kuat", "Sumber daya memadai", "Perwakilan hukum"]
        },
        "Intervensi Pemerintah": {
            "description": "Resolusi yang dipimpin pemerintah melalui kebijakan atau tindakan administratif",
            "success_rate": "58%",
            "timeframe": "1-3 tahun",
            "cost": format_currency(100000, currency),
            "key_requirements": ["Kemauan politik", "Kapasitas administratif", "Otoritas hukum"]
        },
        "Kesepakatan Komunitas": {
            "description": "Resolusi berbasis komunitas melalui mekanisme tradisional atau lokal",
            "success_rate": "81%",
            "timeframe": "3-9 bulan",
            "cost": format_currency(25000, currency),
            "key_requirements": ["Kohesi komunitas", "Pemimpin dihormati", "Penerimaan budaya"]
        },
        "Pendekatan Hybrid": {
            "description": "Kombinasi dari beberapa pendekatan yang disesuaikan dengan konteks spesifik",
            "success_rate": "78%",
            "timeframe": "1-2 tahun",
            "cost": format_currency(125000, currency),
            "key_requirements": ["Proses fleksibel", "Banyak pemangku kepentingan", "Pendekatan terkoordinasi"]
        }
    }
    
    selected_pathway = pathway_details[pathway]
    
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Tingkat Keberhasilan", selected_pathway["success_rate"])
    col2.metric("Rangka Waktu", selected_pathway["timeframe"])
    col3.metric("Perkiraan Biaya", selected_pathway["cost"])
    col4.metric("Pemangku Kepentingan", len(st.session_state.conflict_data["parties_involved"]))
    
    st.write("**Deskripsi:** " + selected_pathway["description"])
    
    st.write("**Persyaratan Utama:**")
    for req in selected_pathway["key_requirements"]:
        st.write(f"- {req}")
    
    # Resolution simulation
    st.subheader("Simulasi Resolusi")
    
    sim_params = st.slider("Intensitas Simulasi", 1, 10, 5)
    
    if st.button("Jalankan Simulasi Resolusi", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(100):
            progress_bar.progress(i + 1)
            status_text.text(f"Menjalankan simulasi resolusi... {i+1}%")
            time.sleep(0.02)
        
        progress_bar.empty()
        status_text.empty()
        
        st.success("Simulasi berhasil diselesaikan!")
        
        # Simulation results
        col1, col2, col3 = st.columns(3)
        
        col1.metric("Probabilitas Resolusi", "76%", "3%")
        col2.metric("Perkiraan Waktu", "14 bulan", "-2 bulan")
        col3.metric("Total Biaya", format_currency(185000, currency), "-8%")
        
        # Recommendation
        st.info("""
        **Rekomendasi:** Lanjutkan dengan jalur yang dipilih tetapi pertimbangkan untuk memperkuat keterlibatan masyarakat 
        dan memastikan dukungan hukum yang memadai untuk semua pihak yang terlibat.
        """)
    
    # Resource allocation
    st.subheader("Alokasi Sumber Daya")
    
    resources = {
        "Hukum": 35,
        "Keterlibatan Masyarakat": 25,
        "Mediasi": 20,
        "Dokumentasi": 10,
        "Pemantauan": 10
    }
    
    fig = go.Figure(go.Pie(
        labels=list(resources.keys()),
        values=list(resources.values()),
        hole=0.3,
        marker_colors=['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
    ))
    
    fig.update_layout(title="Alokasi Sumber Daya yang Direkomendasikan (%)")
    st.plotly_chart(fig, use_container_width=True)

with main_tabs[5]:
    st.header("Analisis Spasial & Peta")
    
    st.subheader("Visualisasi Area Sengketa")
    
    # Create a simple map visualization
    st.info("""
    **Peta Interaktif Area Sengketa** - Visualisasi ini menunjukkan perkiraan area sengketa 
    antara HPL Transmigrasi 1981 dan HGU PT JJP 2005 berdasarkan data koordinat yang tersedia.
    """)
    
    # Generate sample coordinates for visualization
    # Note: These are illustrative coordinates, not actual data
    map_data = pd.DataFrame({
        'lat': [1.899514, 2.012072, 1.955793, 1.899514],
        'lon': [100.903708, 100.804497, 100.854103, 100.903708],
        'type': ['Titik 121', 'Titik 1', 'Pusat Area', 'Titik 121']
    })
    
    # Create map
    fig = px.scatter_mapbox(
        map_data, 
        lat="lat", 
        lon="lon", 
        hover_name="type",
        zoom=10,
        height=600,
        color="type",
        color_discrete_sequence=['#e74c3c', '#3498db', '#2ecc71']
    )
    
    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r":0,"t":0,"l":0,"b":0},
        title="Perkiraan Area Sengketa di Desa Pedamaran"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Area comparison
    st.subheader("Perbandingan Area HPL dan HGU")
    
    areas = {
        'Jenis': ['HPL Awal (1981)', 'HGU PT JJP (2005)', 'Area Sengketa'],
        'Luas (Ha)': [9220, 8200, 1500],
        'Warna': ['#3498db', '#e74c3c', '#f39c12']
    }
    
    fig = go.Figure(go.Bar(
        x=areas['Jenis'],
        y=areas['Luas (Ha)'],
        marker_color=areas['Warna']
    ))
    
    fig.update_layout(
        title="Perbandingan Luas Lahan",
        yaxis_title="Luas (Hektar)"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Coordinate analysis
    st.subheader("Analisis Koordinat Batas")
    
    df_coords = pd.DataFrame(st.session_state.conflict_data['coordinate_changes'])
    
    fig = make_subplots(rows=1, cols=2, subplot_titles=('Pergeseran Koordinat X', 'Pergeseran Koordinat Y'))
    
    fig.add_trace(go.Box(y=df_coords['dx'], name='ΔX', marker_color='#3498db'), row=1, col=1)
    fig.add_trace(go.Box(y=df_coords['dy'], name='ΔY', marker_color='#e74c3c'), row=1, col=2)
    
    fig.update_layout(
        title="Distribusi Pergeseran Koordinat",
        yaxis_title="Pergeseran (m)",
        height=400
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

# Tutup container untuk konten utama
st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #7f8c8d; font-size: 14px;">
        <p>© 2023 Simulator Konflik Lahan Canggih | Didukung oleh AI & Analitik Geospasial</p>
        <p>Disclaimer: Ini adalah alat simulasi untuk tujuan analitis saja</p>
    </div>
    """,
    unsafe_allow_html=True
)