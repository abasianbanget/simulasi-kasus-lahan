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

# Initialize session state for theme
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'
if 'map_style' not in st.session_state:
    st.session_state.map_style = "open-street-map"
if 'show_overlap' not in st.session_state:
    st.session_state.show_overlap = True
if 'show_displacement' not in st.session_state:
    st.session_state.show_displacement = True
if 'show_animation' not in st.session_state:
    st.session_state.show_animation = False

# Function to toggle theme
def toggle_theme():
    if st.session_state.theme == 'dark':
        st.session_state.theme = 'light'
    else:
        st.session_state.theme = 'dark'

# Function to change map style
def change_map_style(style):
    st.session_state.map_style = style

# CSS custom dengan tema yang dapat diubah
def get_theme_css(theme):
    if theme == 'dark':
        return """
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
            --bg-gradient: linear-gradient(135deg, var(--dark) 0%, #2c3e50 100%);
            --card-bg: rgba(255, 255, 255, 0.1);
            --card-border: 1px solid rgba(255, 255, 255, 0.18);
            --text-color: var(--light);
            --stat-box-bg: rgba(255, 255, 255, 0.15);
            --input-bg: rgba(255, 255, 255, 0.1);
            --input-border: 1px solid rgba(255, 255, 255, 0.2);
            --font-size-sm: 14px;
            --font-size-md: 16px;
            --font-size-lg: 18px;
            --font-size-xl: 20px;
        }
        </style>
        """
    else:
        return """
        <style>
        :root {
            --primary: #2c3e50;
            --secondary: #3498db;
            --accent: #e74c3c;
            --success: #2ecc71;
            --warning: #f39c12;
            --info: #1abc9c;
            --dark: #f8f9fa;
            --light: #1a1a1a;
            --gradient-start: #667eea;
            --gradient-end: #764ba2;
            --bg-gradient: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            --card-bg: rgba(255, 255, 255, 0.9);
            --card-border: 1px solid rgba(0, 0, 0, 0.1);
            --text-color: #2c3e50;
            --stat-box-bg: rgba(52, 152, 219, 0.15);
            --input-bg: rgba(255, 255, 255, 0.9);
            --input-border: 1px solid rgba(0, 0, 0, 0.1);
            --font-size-sm: 14px;
            --font-size-md: 16px;
            --font-size-lg: 18px;
            --font-size-xl: 20px;
        }
        </style>
        """

# Apply theme CSS
st.markdown(get_theme_css(st.session_state.theme), unsafe_allow_html=True)

# Common CSS dengan perbaikan
st.markdown(f"""
<style>
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}}

.stApp {{
    background: var(--bg-gradient);
    color: var(--text-color);
    font-size: var(--font-size-md);
}}

.main-header {{
    text-align: center;
    background: linear-gradient(135deg, var(--gradient-start) 0%, var(--gradient-end) 100%);
    color: white;
    padding: 25px;
    border-radius: 15px;
    margin-bottom: 25px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    position: relative;
    overflow: hidden;
}}

.main-header h1 {{
    color: white;
    margin: 0;
    font-size: 2.5rem;
    font-weight: 800;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}}

.main-header p {{
    opacity: 0.9;
    margin: 10px 0 0 0;
    font-size: 1.2rem;
}}

.glass-card {{
    background: var(--card-bg);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    border: var(--card-border);
    transition: all 0.3s ease;
    margin-bottom: 20px;
}}

.glass-card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
}}

.stat-box {{
    background: var(--stat-box-bg);
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    transition: all 0.3s ease;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    border: var(--card-border);
}}

.stat-box:hover {{
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
    background: rgba(255, 255, 255, 0.2);
}}

.stat-value {{
    font-size: 1.8rem;
    font-weight: bold;
    color: var(--text-color);
    margin: 10px 0;
}}

.stat-label {{
    font-size: 0.9rem;
    color: rgba(0, 0, 0, 0.8);
}}

.timeline {{
    position: relative;
    max-width: 100%;
    margin: 20px 0;
}}

.timeline::after {{
    content: '';
    position: absolute;
    width: 6px;
    background: linear-gradient(to bottom, var(--gradient-start), var(--gradient-end));
    top: 0;
    bottom: 0;
    left: 50%;
    margin-left: -3px;
    border-radius: 3px;
}}

.timeline-item {{
    padding: 10px 40px;
    position: relative;
    width: 50%;
    box-sizing: border-box;
}}

.timeline-item::after {{
    content: '';
    position: absolute;
    width: 20px;
    height: 20px;
    background: white;
    border: 4px solid var(--secondary);
    top: 15px;
    border-radius: 50%;
    z-index: 1;
}}

.timeline-content {{
    padding: 20px;
    background: var(--card-bg);
    backdrop-filter: blur(10px);
    position: relative;
    border-radius: 10px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}}

.timeline-content:hover {{
    transform: translateY(-3px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}}

.watermark {{
    position: fixed;
    bottom: 20px;
    right: 20px;
    opacity: 0.7;
    color: var(--text-color);
    font-size: 12px;
    z-index: 1000;
    text-align: right;
    background: var(--card-bg);
    padding: 10px 15px;
    border-radius: 8px;
    backdrop-filter: blur(5px);
    border: var(--card-border);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}}

.watermark div:first-child {{
    font-weight: bold;
    margin-bottom: 3px;
    color: var(--secondary);
    font-size: 11px;
    letter-spacing: 0.5px;
}}

.watermark div:last-child {{
    font-size: 10px;
    opacity: 0.8;
}}

.animated-gradient {{
    background: linear-gradient(270deg, #667eea, #764ba2, #f093fb, #f5576c);
    background-size: 800% 800%;
    animation: AnimationName 10s ease infinite;
    padding: 5px 10px;
    border-radius: 5px;
    color: white;
    font-weight: bold;
}}

@keyframes AnimationName {{
    0% {{ background-position: 0% 50% }}
    50% {{ background-position: 100% 50% }}
    100% {{ background-position: 0% 50% }}
}}

/* Streamlit component adjustments */
.stSelectbox, .stSlider, .stTextInput, .stNumberInput {{
    background: var(--input-bg) !important;
    border-radius: 10px !important;
    padding: 10px !important;
    border: var(--input-border) !important;
}}

.stButton button {{
    background: linear-gradient(135deg, var(--gradient-start) 0%, var(--gradient-end) 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 20px !important;
    font-weight: bold !important;
    transition: all 0.3s ease !important;
}}

.stButton button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3) !important;
}}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {{
    gap: 8px;
}}

.stTabs [data-baseweb="tab"] {{
    background: var(--input-bg) !important;
    border-radius: 10px 10px 0 0 !important;
    padding: 10px 20px !important;
    border: var(--input-border) !important;
    transition: all 0.3s ease !important;
    font-size: var(--font-size-md);
}}

.stTabs [aria-selected="true"] {{
    background: linear-gradient(135deg, var(--gradient-start) 0%, var(--gradient-end) 100%) !important;
    color: white !important;
}}

/* Map container styling */
.map-container {{
    border-radius: 15px;
    overflow: hidden;
    margin-bottom: 20px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    border: var(--card-border);
    height: 600px;
    position: relative;
}}

/* Panel styling */
.config-panel {{
    background: var(--card-bg);
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 15px;
    border: var(--card-border);
}}

.config-panel h3 {{
    margin-top: 0;
    color: var(--secondary);
    border-bottom: 1px solid rgba(0,0,0,0.1);
    padding-bottom: 10px;
}}

/* Custom scrollbar */
::-webkit-scrollbar {{
    width: 8px;
}}

::-webkit-scrollbar-track {{
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
}}

::-webkit-scrollbar-thumb {{
    background: linear-gradient(135deg, var(--gradient-start) 0%, var(--gradient-end) 100%);
    border-radius: 10px;
}}

::-webkit-scrollbar-thumb:hover {{
    background: linear-gradient(135deg, var(--gradient-end) 0%, var(--gradient-start) 100%);
}}

/* Responsive design */
@media (max-width: 768px) {{
    .main-header h1 {{
        font-size: 1.8rem;
    }}
    
    .stat-value {{
        font-size: 1.4rem;
    }}
    
    .timeline::after {{
        left: 31px;
    }}
    
    .timeline-item {{
        width: 100%;
        padding-left: 70px;
        padding-right: 25px;
    }}
    
    .timeline-item::after {{
        left: 18px;
    }}
    
    .right {{
        left: 0%;
    }}
}}

/* Map controls styling - dipindahkan ke sidebar */
.map-controls-sidebar {{
    background: var(--card-bg);
    border-radius: 12px;
    padding: 15px;
    margin-bottom: 15px;
    border: var(--card-border);
}}

.map-controls-sidebar h3 {{
    margin-top: 0;
    color: var(--secondary);
    border-bottom: 1px solid rgba(0,0,0,0.1);
    padding-bottom: 10px;
}}

/* Sidebar scroll optimization */
.sidebar .sidebar-content {{
    overflow-y: auto;
    max-height: calc(100vh - 100px);
}}

.sidebar .sidebar-content::-webkit-scrollbar {{
    width: 6px;
}}

.sidebar .sidebar-content::-webkit-scrollbar-thumb {{
    background: rgba(255, 255, 255, 0.3);
    border-radius: 3px;
}}

/* Expander styling */
.streamlit-expanderHeader {{
    font-weight: 600;
    color: var(--secondary);
    font-size: var(--font-size-md);
}}

/* Compact form elements */
.stSelectbox, .stSlider, .stTextInput, .stNumberInput {{
    margin-bottom: 0.5rem;
}}

/* Label styling */
label {{
    font-weight: 500;
    margin-bottom: 0.25rem;
    display: block;
}}

/* Analysis card styling */
.analysis-card {{
    background: var(--card-bg);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    border: var(--card-border);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}}

.analysis-card h3 {{
    color: var(--secondary);
    margin-top: 0;
    border-bottom: 1px solid rgba(0,0,0,0.1);
    padding-bottom: 10px;
    font-size: var(--font-size-lg);
}}

/* Chart container styling */
.chart-container {{
    background: var(--card-bg);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    border: var(--card-border);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}}

/* Professional legend styling */
.professional-legend {{
    background: var(--card-bg);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    border: var(--card-border);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}}

.professional-legend h4 {{
    color: var(--secondary);
    margin-top: 0;
    border-bottom: 1px solid rgba(0,0,0,0.1);
    padding-bottom: 10px;
    font-size: var(--font-size-lg);
    font-weight: 600;
}}

.legend-item {{
    display: flex;
    align-items: center;
    margin-bottom: 12px;
}}

.legend-color {{
    width: 20px;
    height: 20px;
    border-radius: 3px;
    margin-right: 10px;
    border: 1px solid rgba(0,0,0,0.2);
}}

.legend-label {{
    font-size: var(--font-size-md);
    color: var(--text-color);
    font-weight: 500;
}}

/* Improved sidebar section headers */
.sidebar-section {{
    background: linear-gradient(135deg, var(--gradient-start) 0%, var(--gradient-end) 100%);
    color: white;
    padding: 12px 15px;
    border-radius: 8px;
    margin-bottom: 15px;
    font-weight: 600;
    font-size: var(--font-size-md);
    text-align: center;
}}

/* Global standard form elements */
.global-form .stSelectbox, 
.global-form .stSlider, 
.global-form .stTextInput, 
.global-form .stNumberInput {{
    margin-bottom: 15px;
}}

.global-form label {{
    font-size: var(--font-size-md);
    font-weight: 500;
    margin-bottom: 8px;
    color: var(--text-color);
}}

/* Footer styling */
.footer {{
    text-align: center;
    color: #7f8c8d;
    font-size: var(--font-size-sm);
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid rgba(0,0,0,0.1);
}}

.footer p {{
    margin: 5px 0;
}}

/* Tab content styling */
.tab-content {{
    font-size: var(--font-size-md);
}}

.tab-content h1, .tab-content h2, .tab-content h3, .tab-content h4 {{
    color: var(--secondary);
}}

.tab-content h1 {{
    font-size: 2rem;
    margin-bottom: 1rem;
}}

.tab-content h2 {{
    font-size: 1.5rem;
    margin-bottom: 0.8rem;
}}

.tab-content h3 {{
    font-size: 1.2rem;
    margin-bottom: 0.6rem;
}}

.tab-content p {{
    margin-bottom: 1rem;
    line-height: 1.6;
}}

/* Dashboard specific styling */
.dashboard-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-bottom: 20px;
}}

.dashboard-card {{
    background: var(--card-bg);
    border-radius: 12px;
    padding: 20px;
    border: var(--card-border);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}}

.dashboard-card h3 {{
    color: var(--secondary);
    margin-top: 0;
    margin-bottom: 15px;
    font-size: var(--font-size-lg);
}}

/* Data table styling */
.data-table {{
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-size: var(--font-size-sm);
}}

.data-table th, .data-table td {{
    padding: 12px 15px;
    text-align: left;
    border-bottom: 1px solid rgba(0,0,0,0.1);
}}

.data-table th {{
    background-color: var(--stat-box-bg);
    color: var(--secondary);
    font-weight: 600;
}}

.data-table tr:hover {{
    background-color: rgba(0,0,0,0.05);
}}

/* Responsive table */
.table-container {{
    overflow-x: auto;
}}

/* Custom mapbox styles */
.mapbox-style-container {{
    margin-bottom: 20px;
}}

.mapbox-style-container label {{
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: var(--text-color);
}}

/* Improved chart styling */
.plotly-chart {{
    border-radius: 12px;
    overflow: hidden;
}}
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

# Sidebar dengan fitur canggih - Dioptimalkan untuk mengurangi scroll
st.sidebar.markdown('<div class="sidebar-section">KONFIGURASI SIMULATOR</div>', unsafe_allow_html=True)

# Theme selector
with st.sidebar.expander("🎨 TEMA DAN TAMPILAN", expanded=False):
    theme_options = {"Gelap": "dark", "Terang": "light"}
    current_theme = st.radio("Pilih Tema", list(theme_options.keys()), 
                                     index=list(theme_options.values()).index(st.session_state.theme),
                                     key="theme_selector",
                                     on_change=toggle_theme)

# Kontrol Peta dipindahkan ke sidebar
with st.sidebar.expander("🗺️ KONTROL PETA", expanded=False):
    st.markdown("### Gaya Peta")
    map_style_options = {
        "OpenStreetMap": "open-street-map",
        "Satellite": "satellite", 
        "Light": "carto-positron",
        "Dark": "carto-darkmatter",
        "Terrain": "stamen-terrain"
    }
    
    map_style = st.radio(
        "Pilih Gaya Peta",
        list(map_style_options.keys()),
        index=0,
        key="map_style_selector"
    )
    
    if map_style_options[map_style] != st.session_state.map_style:
        st.session_state.map_style = map_style_options[map_style]
        st.rerun()
    
    st.markdown("### Layer Peta")
    col1, col2 = st.columns(2)
    with col1:
        show_overlap = st.checkbox("Tumpang Tindih", value=st.session_state.show_overlap, 
                                  key="show_overlap_check")
    with col2:
        show_displacement = st.checkbox("Pergeseran", value=st.session_state.show_displacement,
                                      key="show_displacement_check")
    
    show_animation = st.checkbox("Animasi Pergeseran", value=st.session_state.show_animation,
                                key="show_animation_check")
    
    if show_overlap != st.session_state.show_overlap:
        st.session_state.show_overlap = show_overlap
        st.rerun()
        
    if show_displacement != st.session_state.show_displacement:
        st.session_state.show_displacement = show_displacement
        st.rerun()
        
    if show_animation != st.session_state.show_animation:
        st.session_state.show_animation = show_animation
        st.rerun()

# Data referensi model AI berdasarkan sektor
ai_model_references = {
    "Konflik Lahan": "Agent-Based Modeling + Rule-Based + Fuzzy Logic",
    "Banjir (Ciliwung-Cisadane)": "LSTM + CNN + Physical-AI Hybrid + RL",
    "Gempa (Termasuk Megathrust)": "Bayesian Networks + PINNs + ABM + LSTM"
}

# Tab sidebar yang disederhanakan dengan gaya global
with st.sidebar.expander("🧠 KECERDASAN BUATAN", expanded=False):
    st.markdown('<div class="global-form">', unsafe_allow_html=True)
    # Sektor analisis
    analysis_sector = st.selectbox(
        "Sektor Analisis",
        list(ai_model_references.keys()),
        index=0
    )
    
    # Rekomendasi model AI berdasarkan sektor
    recommended_model = ai_model_references[analysis_sector]
    st.info(f"**Rekomendasi Model:** {recommended_model}")
    
    # AI configuration
    ai_model = st.selectbox(
        "Model AI",
        ["Random Forest", "XGBoost", "Neural Network", "BERT", "Ensemble", "Deep Learning", recommended_model],
        index=6  # Default to recommended model
    )
    
    accuracy_level = st.slider(
        "Target Akurasi",
        min_value=80,
        max_value=99,
        value=92
    )
    st.markdown('</div>', unsafe_allow_html=True)

with st.sidebar.expander("📊 SUMBER DATA", expanded=False):
    st.markdown('<div class="global-form">', unsafe_allow_html=True)
    # Data integration
    data_sources = st.multiselect(
        "Sumber Data",
        ["API Pemerintah", "Landsat Satellite", "Sensor IoT", "Media Sosial", "Database Lokal"],
        default=["API Pemerintah", "Landsat Satellite"]
    )
    
    # Visualization options
    viz_options = st.multiselect(
        "Tampilkan Visualisasi",
        ["Heatmap Kepadatan", "Grafik Timeline", "Chart 3D", "Perubahan Area", "Analisis Sentimen"],
        default=["Heatmap Kepadatan", "Grafik Timeline"]
    )
    st.markdown('</div>', unsafe_allow_html=True)

with st.sidebar.expander("⚙️ PENGATURAN SISTEM", expanded=False):
    st.markdown('<div class="global-form">', unsafe_allow_html=True)
    # System settings
    col1, col2 = st.columns(2)
    with col1:
        data_refresh = st.slider("Pembaruan Data (mnt)", 1, 60, 15)
    with col2:
        cache_size = st.slider("Cache (MB)", 10, 1000, 100)
    
    performance_mode = st.selectbox(
        "Mode Performa",
        ["Optimal", "Cepat", "Presisi Tinggi"]
    )
    st.markdown('</div>', unsafe_allow_html=True)

with st.sidebar.expander("🔒 KEAMANAN", expanded=False):
    st.markdown('<div class="global-form">', unsafe_allow_html=True)
    # Security settings
    encryption_level = st.selectbox(
        "Tingkat Enkripsi",
        ["Standard", "Tinggi", "Militer"]
    )
    
    auth_method = st.multiselect(
        "Metode Autentikasi",
        ["Password", "2-Faktor", "Biometric", "SSO"],
        default=["Password", "2-Faktor"]
    )
    st.markdown('</div>', unsafe_allow_html=True)

with st.sidebar.expander("💰 EKONOMI", expanded=False):
    st.markdown('<div class="global-form">', unsafe_allow_html=True)
    # Currency configuration
    exchange_rate = st.number_input(
        "Kurs USD ke IDR",
        min_value=10000.0,
        max_value=20000.0,
        value=15000.0,
        step=100.0,
        help="Nilai tukar USD ke Rupiah Indonesia saat ini"
    )
    
    show_idr = st.checkbox("Tampilkan dalam Rupiah Indonesia", value=True)
    
    # Land price prediction settings
    land_price_base = st.number_input(
        "Harga Dasar Lahan per Ha (Rp)",
        min_value=100000000,  # 100 juta
        max_value=10000000000,  # 10 milyar
        value=500000000,  # 500 juta
        step=10000000  # 10 juta
    )
    
    inflation_rate = st.slider(
        "Tingkat Inflasi Tahunan (%)",
        min_value=0.0,
        max_value=10.0,
        value=2.5,
        step=0.1
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Tombol Run Simulation
st.sidebar.markdown("---")
if st.sidebar.button("🚀 JALANKAN SIMULASI", type="primary", use_container_width=True):
    with st.spinner("Menjalankan simulasi dengan konfigurasi saat ini..."):
        time.sleep(2)
        st.sidebar.success("Simulasi berhasil dijalankan!")

# Fungsi untuk memuat data konflik
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
        'map_data': {
            'center': {'lat': 1.955793, 'lng': 100.854103},
            'zoom': 12,
            'bounds': {
                'north': 2.012072,
                'south': 1.899514,
                'east': 100.903708,
                'west': 100.804497
            },
            'boundary_points': [
                {'lat': 2.012072, 'lng': 100.804497, 'name': 'Titik 1'},
                {'lat': 2.005421, 'lng': 100.823156, 'name': 'Titik 2'},
                {'lat': 1.997832, 'lng': 100.841872, 'name': 'Titik 3'},
                {'lat': 1.987654, 'lng': 100.862345, 'name': 'Titik 4'},
                {'lat': 1.976543, 'lng': 100.876543, 'name': 'Titik 5'},
                {'lat': 1.965432, 'lng': 100.887654, 'name': 'Titik 6'},
                {'lat': 1.945678, 'lng': 100.895678, 'name': 'Titik 7'},
                {'lat': 1.923456, 'lng': 100.901234, 'name': 'Titik 8'},
                {'lat': 1.908765, 'lng': 100.903708, 'name': 'Titik 121'},
                {'lat': 1.899514, 'lng': 100.903708, 'name': 'Titik 122'}
            ],
            'disputed_areas': [
                {
                    'name': 'Blok D',
                    'coordinates': [
                        {'lat': 1.976543, 'lng': 100.876543},
                        {'lat': 1.971234, 'lng': 100.882345},
                        {'lat': 1.965432, 'lng': 100.887654},
                        {'lat': 1.958765, 'lng': 100.891234},
                        {'lat': 1.952345, 'lng': 100.893456}
                    ],
                    'area_ha': 750,
                    'status': 'high_tension'
                },
                {
                    'name': 'Blok E',
                    'coordinates': [
                        {'lat': 1.945678, 'lng': 100.895678},
                        {'lat': 1.939876, 'lng': 100.898765},
                        {'lat': 1.933456, 'lng': 100.901234},
                        {'lat': 1.923456, 'lng': 100.901234},
                        {'lat': 1.918765, 'lng': 100.902345}
                    ],
                    'area_ha': 750,
                    'status': 'medium_tension'
                }
            ],
            # Data untuk visualisasi pergeseran lahan
            'land_displacement': {
                'hpl_2005': [
                    {'lat': 1.976543, 'lng': 100.876543},
                    {'lat': 1.971234, 'lng': 100.882345},
                    {'lat': 1.965432, 'lng': 100.887654},
                    {'lat': 1.958765, 'lng': 100.891234},
                    {'lat': 1.952345, 'lng': 100.893456}
                ],
                'hgu_2005': [
                    {'lat': 1.975000, 'lng': 100.875000},
                    {'lat': 1.970000, 'lng': 100.880000},
                    {'lat': 1.964000, 'lng': 100.886000},
                    {'lat': 1.957000, 'lng': 100.890000},
                    {'lat': 1.951000, 'lng': 100.892000}
                ],
                'hgu_2011': [
                    {'lat': 1.978000, 'lng': 100.879000},
                    {'lat': 1.973000, 'lng': 100.884000},
                    {'lat': 1.967000, 'lng': 100.889000},
                    {'lat': 1.960000, 'lng': 100.893000},
                    {'lat': 1.954000, 'lng': 100.895000}
                ],
                'overlap_area': [
                    {'lat': 1.976543, 'lng': 100.876543},
                    {'lat': 1.973000, 'lng': 100.884000},
                    {'lat': 1.967000, 'lng': 100.889000},
                    {'lat': 1.960000, 'lng': 100.893000},
                    {'lat': 1.952345, 'lng': 100.893456}
                ]
            }
        },
        'legal_documents': [
            {'name': 'SK Mendagri No. SK.15/HPL/DA/81', 'year': 1981, 'type': 'HPL', 'relevance': 0.95},
            {'name': 'Sertifikat HPL Transmigrasi', 'year': 1993, 'type': 'HPL', 'relevance': 0.90},
            {'name': 'Surrat Gubernur Riau No. 525/EK/2194', 'year': 1996, 'type': 'Izin', 'relevance': 0.85},
            {'name': 'HGU No. 11/2005', 'year': 2005, 'type': 'HGU', 'relevance': 0.75},
            {'name': 'Surat Revisi PT JJP No. 008/Dir/JJP/VIII/11', 'year': 2011, 'type': 'Revisi', 'relevance': 0.65},
            {'name': 'Surat Menteri Desa No. 080/SD/M-DPDTT/V/2015', 'year': 2015, 'type': 'Pelepasan', 'relevance': 0.80},
            {'name': 'BA Peninjauan 2020', 'year': 2020, 'type': 'Mediasi', 'relevance': 0.70},
            {'name': 'Surat DPC PATRI No. 35/PATRI-RH/II/2025', 'year': 2025, 'type': 'Tuntutan', 'relevance': 0.85}
        ],
        # Data tambahan untuk visualisasi
        'economic_impact': {
            'years': [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
            'direct_loss': [15, 18, 22, 25, 30, 35, 40, 45, 50, 55, 60],
            'indirect_loss': [25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75],
            'environmental_damage': [10, 12, 15, 18, 20, 22, 25, 28, 30, 32, 35]
        },
        'population_impact': {
            'years': [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
            'affected_families': [50, 65, 80, 95, 110, 125, 140, 150, 150, 150, 150],
            'relocated_families': [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55],
            'income_reduction': [25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75]
        },
        'resolution_options': {
            'options': ['Mediasi', 'Kompensasi', 'Pembagian Lahan', 'Relokasi', 'Gugatan Hukum'],
            'cost': [5, 45, 30, 25, 15],
            'duration': [6, 12, 24, 18, 36],
            'success_rate': [70, 85, 90, 80, 60]
        }
    }
    return conflict_data

# Fungsi untuk format mata uang
def format_currency(amount, currency="IDR"):
    try:
        if currency == "IDR":
            # Format Rupiah tanpa desimal, dengan pemisah ribuan
            if amount >= 1_000_000_000_000:  # Triliun
                return f"Rp {amount/1_000_000_000_000:.2f} T"
            elif amount >= 1_000_000_000:  # Miliar
                return f"Rp {amount/1_000_000_000:.2f} M"
            elif amount >= 1_000_000:  # Juta
                return f"Rp {amount/1_000_000:.2f} Jt"
            elif amount >= 1_000:  # Ribu
                return f"Rp {amount/1_000:.2f} Rb"
            else:
                return f"Rp {amount:,.0f}".replace(",", ".")
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

# Fungsi untuk prediksi harga lahan
def predict_land_prices(years, base_price, inflation_rate):
    """Memprediksi harga lahan berdasarkan tingkat inflasi"""
    prices = []
    for year in years:
        # Hitung harga dengan inflasi tahunan
        years_from_now = year - 2023
        future_price = base_price * ((1 + inflation_rate/100) ** years_from_now)
        prices.append(future_price)
    return prices

# Fungsi untuk membuat peta interaktif dengan analisis pergeseran lahan
def create_interactive_map(conflict_data):
    """Buat peta interaktif dengan berbagai layer dan fitur"""
    st.subheader("Peta Interaktif Area Sengketa dengan Analisis Pergeseran Lahan")
    
    # Kontrol peta di sidebar
    map_style = st.session_state.map_style
    
    # Generate map data
    map_data = conflict_data['map_data']
    center = [map_data['center']['lat'], map_data['center']['lng']]
    
    # Create figure
    fig = go.Figure()
    
    # Add disputed areas dengan transparansi tinggi
    for area in map_data['disputed_areas']:
        lats = [point['lat'] for point in area['coordinates']]
        lngs = [point['lng'] for point in area['coordinates']]
        
        # Close the polygon
        lats.append(area['coordinates'][0]['lat'])
        lngs.append(area['coordinates'][0]['lng'])
        
        # Warna dengan transparansi tinggi
        color = 'rgba(231, 76, 60, 0.7)' if area['status'] == 'high_tension' else 'rgba(243, 156, 18, 0.7)'
        fill_color = 'rgba(231, 76, 60, 0.2)' if area['status'] == 'high_tension' else 'rgba(243, 156, 18, 0.2)'
        
        fig.add_trace(go.Scattermapbox(
            lat=lats,
            lon=lngs,
            mode='lines',
            fill='toself',
            name=f"{area['name']} - Area Sengketa",
            line=dict(width=3, color=color),
            fillcolor=fill_color,
            hoverinfo='text',
            text=f"{area['name']}<br>Luas: {area['area_ha']} Ha<br>Status: {'Tegangan Tinggi' if area['status'] == 'high_tension' else 'Tegangan Sedang'}"
        ))
    
    # Add land displacement visualization if enabled
    if st.session_state.show_displacement and 'land_displacement' in map_data:
        displacement_data = map_data['land_displacement']
        
        # HPL 2005
        hpl_2005_lats = [point['lat'] for point in displacement_data['hpl_2005']]
        hpl_2005_lngs = [point['lng'] for point in displacement_data['hpl_2005']]
        hpl_2005_lats.append(displacement_data['hpl_2005'][0]['lat'])
        hpl_2005_lngs.append(displacement_data['hpl_2005'][0]['lng'])
        
        fig.add_trace(go.Scattermapbox(
            lat=hpl_2005_lats,
            lon=hpl_2005_lngs,
            mode='lines',
            fill='toself',
            name='HPL 2005',
            line=dict(width=2, color='rgba(46, 204, 113, 0.8)'),
            fillcolor='rgba(46, 204, 113, 0.2)',
            hoverinfo='text',
            text='Hak Pengelolaan Lahan (HPL) 2005<br>Luas: 9.220 Ha'
        ))
        
        # HGU 2005
        hgu_2005_lats = [point['lat'] for point in displacement_data['hgu_2005']]
        hgu_2005_lngs = [point['lng'] for point in displacement_data['hgu_2005']]
        hgu_2005_lats.append(displacement_data['hgu_2005'][0]['lat'])
        hgu_2005_lngs.append(displacement_data['hgu_2005'][0]['lng'])
        
        fig.add_trace(go.Scattermapbox(
            lat=hgu_2005_lats,
            lon=hgu_2005_lngs,
            mode='lines',
            fill='toself',
            name='HGU 2005',
            line=dict(width=2, color='rgba(52, 152, 219, 0.8)'),
            fillcolor='rgba(52, 152, 219, 0.2)',
            hoverinfo='text',
            text='Hak Guna Usaha (HGU) 2005<br>Luas: 8.200 Ha'
        ))
        
        # HGU 2011
        hgu_2011_lats = [point['lat'] for point in displacement_data['hgu_2011']]
        hgu_2011_lngs = [point['lng'] for point in displacement_data['hgu_2011']]
        hgu_2011_lats.append(displacement_data['hgu_2011'][0]['lat'])
        hgu_2011_lngs.append(displacement_data['hgu_2011'][0]['lng'])
        
        fig.add_trace(go.Scattermapbox(
            lat=hgu_2011_lats,
            lon=hgu_2011_lngs,
            mode='lines',
            fill='toself',
            name='HGU 2011',
            line=dict(width=2, color='rgba(155, 89, 182, 0.8)'),
            fillcolor='rgba(155, 89, 182, 0.2)',
            hoverinfo='text',
            text='Hak Guna Usaha (HGU) 2011<br>Revisi Koordinat'
        ))
        
        # Overlap area if enabled
        if st.session_state.show_overlap:
            overlap_lats = [point['lat'] for point in displacement_data['overlap_area']]
            overlap_lngs = [point['lng'] for point in displacement_data['overlap_area']]
            overlap_lats.append(displacement_data['overlap_area'][0]['lat'])
            overlap_lngs.append(displacement_data['overlap_area'][0]['lng'])
            
            fig.add_trace(go.Scattermapbox(
                lat=overlap_lats,
                lon=overlap_lngs,
                mode='lines',
                fill='toself',
                name='Area Tumpang Tindih',
                line=dict(width=3, color='rgba(231, 76, 60, 0.9)'),
                fillcolor='rgba(231, 76, 60, 0.3)',
                hoverinfo='text',
                text='Area Tumpang Tindih<br>Luas: ±1.500 Ha<br>Konflik antara HPL dan HGU'
            ))
    
    # Add boundary points
    boundary_lats = [point['lat'] for point in map_data['boundary_points']]
    boundary_lngs = [point['lng'] for point in map_data['boundary_points']]
    
    fig.add_trace(go.Scattermapbox(
        lat=boundary_lats,
        lon=boundary_lngs,
        mode='markers+lines',
        name='Batas Area',
        line=dict(width=2, color='rgba(52, 73, 94, 0.8)'),
        marker=dict(size=8, color='rgba(52, 73, 94, 0.8)'),
        hoverinfo='text',
        text=[point['name'] for point in map_data['boundary_points']]
    ))
    
    # Add heatmap for conflict intensity
    heatmap_data = []
    for area in map_data['disputed_areas']:
        for point in area['coordinates']:
            intensity = 0.9 if area['status'] == 'high_tension' else 0.6
            heatmap_data.append({
                'lat': point['lat'],
                'lon': point['lng'],
                'intensity': intensity
            })
    
    heatmap_df = pd.DataFrame(heatmap_data)
    
    if not heatmap_df.empty:
        fig.add_trace(go.Densitymapbox(
            lat=heatmap_df.lat,
            lon=heatmap_df.lon,
            z=heatmap_df.intensity,
            radius=20,
            colorscale='Hot',
            opacity=0.7,
            name='Heatmap Konflik'
        ))
    
    # Update layout
    fig.update_layout(
        mapbox=dict(
            style=map_style,
            center=dict(lat=center[0], lon=center[1]),
            zoom=map_data['zoom']
        ),
        height=600,
        margin={"r":0,"t":0,"l":0,"b":0},
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='rgba(0, 0, 0, 0.1)',
            borderwidth=1,
            font=dict(size=14)
        )
    )
    
    # Display the map
    st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
    
    # Map tools
    st.subheader("Alat Analisis Peta")
    
    tools_col1, tools_col2, tools_col3, tools_col4 = st.columns(4)
    
    with tools_col1:
        st.button("📏 Ukur Area", use_container_width=True)
    with tools_col2:
        st.button("📍 Tambah Marka", use_container_width=True)
    with tools_col3:
        st.button("📊 Analisis Perubahan", use_container_width=True)
    with tools_col4:
        st.button("💾 Ekspor Peta", use_container_width=True)
    
    # Professional map legend
    st.markdown("""
    <div class="professional-legend">
        <h4>Legenda Peta</h4>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgba(46, 204, 113, 0.3); border-color: rgba(46, 204, 113, 0.8);"></div>
            <div class="legend-label">HPL 2005</div>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgba(52, 152, 219, 0.3); border-color: rgba(52, 152, 219, 0.8);"></div>
            <div class="legend-label">HGU 2005</div>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgba(155, 89, 182, 0.3); border-color: rgba(155, 89, 182, 0.8);"></div>
            <div class="legend-label">HGU 2011</div>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgba(231, 76, 60, 0.3); border-color: rgba(231, 76, 60, 0.9);"></div>
            <div class="legend-label">Area Tumpang Tindih</div>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgba(243, 156, 18, 0.3); border-color: rgba(243, 156, 18, 0.8);"></div>
            <div class="legend-label">Area Sengketa</div>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: rgba(52, 73, 94, 0.3); border-color: rgba(52, 73, 94, 0.8);"></div>
            <div class="legend-label">Batas Area</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Fungsi untuk membuat visualisasi analisis pergeseran lahan
def create_displacement_analysis(conflict_data):
    """Buat visualisasi analisis pergeseran lahan"""
    st.subheader("Analisis Pergeseran Lahan dan Tumpang Tindih")
    
    # Data untuk analisis
    coord_changes = conflict_data['coordinate_changes']
    df_changes = pd.DataFrame(coord_changes)
    
    # Hitung statistik pergeseran
    avg_dx = df_changes['dx'].mean()
    avg_dy = df_changes['dy'].mean()
    avg_distance = df_changes['distance'].mean()
    max_distance = df_changes['distance'].max()
    min_distance = df_changes['distance'].min()
    
    # Tampilkan statistik
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rata-rata ΔX", f"{avg_dx:.2f} m")
    col2.metric("Rata-rata ΔY", f"{avg_dy:.2f} m")
    col3.metric("Rata-rata Pergeseran", f"{avg_distance:.2f} m")
    col4.metric("Pergeseran Maksimum", f"{max_distance:.2f} m")
    
    # Grafik pergeseran koordinat
    st.markdown("### Grafik Pergeseran Koordinat Batas Lahan")
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Pergeseran Koordinat X', 'Pergeseran Koordinat Y', 
                       'Jarak Pergeseran', 'Tingkat Signifikansi'),
        specs=[[{"type": "bar"}, {"type": "bar"}], [{"type": "bar"}, {"type": "bar"}]]
    )
    
    # X changes
    fig.add_trace(
        go.Bar(x=df_changes['tugu'], y=df_changes['dx'], name='ΔX', marker_color='#3498db'),
        row=1, col=1
    )
    
    # Y changes
    fig.add_trace(
        go.Bar(x=df_changes['tugu'], y=df_changes['dy'], name='ΔY', marker_color='#e74c3c'),
        row=1, col=2
    )
    
    # Distance changes
    fig.add_trace(
        go.Bar(x=df_changes['tugu'], y=df_changes['distance'], name='Jarak', marker_color='#2ecc71'),
        row=2, col=1
    )
    
    # Significance (convert to numerical values)
    significance_map = {'low': 1, 'medium': 2, 'high': 3, 'very_high': 4}
    df_changes['significance_num'] = df_changes['significance'].map(significance_map)
    
    fig.add_trace(
        go.Bar(x=df_changes['tugu'], y=df_changes['significance_num'], name='Signifikansi', marker_color='#f39c12'),
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
    
    # Tabel detail pergeseran
    st.markdown("### Tabel Detail Pergeseran Koordinat")
    display_df = df_changes[['tugu', 'x_2005', 'y_2005', 'x_2011', 'y_2011', 'dx', 'dy', 'distance', 'keterangan']].copy()
    display_df.columns = ['Titik', 'X 2005', 'Y 2005', 'X 2011', 'Y 2011', 'ΔX (m)', 'ΔY (m)', 'Jarak (m)', 'Keterangan']
    st.dataframe(display_df, use_container_width=True)
    
    # Analisis dampak pergeseran
    st.markdown("### Analisis Dampak Pergeseran Lahan")
    
    impact_col1, impact_col2 = st.columns(2)
    
    with impact_col1:
        st.markdown("""
        <div class="analysis-card">
            <h3>Dampak terhadap Masyarakat</h3>
            <ul>
                <li>Kehilangan akses ke lahan garapan seluas ±1.500 Ha</li>
                <li>Penurunan produktivitas pertanian dan ekonomi</li>
                <li>Ketidakpastian hukum dan sosial</li>
                <li>Konflik horizontal antar masyarakat</li>
                <li>Dampak psikologis dan stres</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with impact_col2:
        st.markdown("""
        <div class="analysis-card">
            <h3>Dampak terhadap Perusahaan</h3>
            <ul>
                <li>Resiko reputasi dan citra perusahaan</li>
                <li>Potensi gugatan hukum dan denda</li>
                <li>Gangguan operasional akibat konflik</li>
                <li>Peningkatan biaya keamanan dan mediasi</li>
                <li>Ketidakpastian investasi jangka panjang</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Rekomendasi penyelesaian
    st.markdown("### Rekomendasi Penyelesaian Konflik")
    
    st.markdown("""
    <div class="analysis-card">
        <h3>Langkah-langkah Penyelesaian</h3>
        <ol>
            <li><strong>Verifikasi ulang batas-batas lahan</strong> oleh tim independen yang melibatkan semua pihak</li>
            <li><strong>Mediasi multipihak</strong> dengan fasilitator netral untuk mencapai kesepakatan win-win solution</li>
            <li><strong>Kompensasi yang adil</strong> bagi masyarakat yang terdampak berdasarkan nilai ekonomi lahan</li>
            <li><strong>Program pemberdayaan masyarakat</strong> untuk mengembangkan sumber penghidupan alternatif</li>
            <li><strong>Penguatan kelembagaan adat</strong> dan pengakuan hak-hak masyarakat dalam perencanaan tata ruang</li>
            <li><strong>Monitoring dan evaluasi</strong> berkelanjutan untuk mencegah konflik serupa di masa depan</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

# Fungsi untuk membuat animasi pergeseran lahan
def create_displacement_animation(conflict_data):
    """Buat animasi pergeseran lahan dari 2005 ke 2011"""
    st.subheader("Animasi Pergeseran Lahan")
    
    map_data = conflict_data['map_data']
    center = [map_data['center']['lat'], map_data['center']['lng']]
    displacement_data = map_data['land_displacement']
    
    # Buat frame animasi
    frames = []
    steps = 10  # Jumlah frame animasi
    
    for i in range(steps + 1):
        ratio = i / steps
        interpolated_lats = []
        interpolated_lons = []
        
        for j in range(len(displacement_data['hgu_2005'])):
            # Interpolasi antara koordinat 2005 dan 2011
            lat_2005 = displacement_data['hgu_2005'][j]['lat']
            lon_2005 = displacement_data['hgu_2005'][j]['lng']
            lat_2011 = displacement_data['hgu_2011'][j]['lat']
            lon_2011 = displacement_data['hgu_2011'][j]['lng']
            
            interp_lat = lat_2005 + (lat_2011 - lat_2005) * ratio
            interp_lon = lon_2005 + (lon_2011 - lon_2005) * ratio
            
            interpolated_lats.append(interp_lat)
            interpolated_lons.append(interp_lon)
        
        # Tutup poligon
        interpolated_lats.append(interpolated_lats[0])
        interpolated_lons.append(interpolated_lons[0])
        
        frames.append(go.Frame(data=[go.Scattermapbox(
            lat=interpolated_lats,
            lon=interpolated_lons,
            mode='lines',
            fill='toself',
            line=dict(width=2, color='rgba(155, 89, 182, 0.8)'),
            fillcolor='rgba(155, 89, 182, 0.2)',
            name='HGU Animasi'
        )], name=f"frame_{i}"))
    
    # Buat figure dengan animasi
    anim_fig = go.Figure(
        data=[go.Scattermapbox(
            lat=[point['lat'] for point in displacement_data['hgu_2005']] + [displacement_data['hgu_2005'][0]['lat']],
            lon=[point['lng'] for point in displacement_data['hgu_2005']] + [displacement_data['hgu_2005'][0]['lng']],
            mode='lines',
            fill='toself',
            line=dict(width=2, color='rgba(52, 152, 219, 0.8)'),
            fillcolor='rgba(52, 152, 219, 0.2)',
            name='HGU 2005'
        )],
        frames=frames
    )
    
    # Tambahkan HPL sebagai referensi
    hpl_lats = [point['lat'] for point in displacement_data['hpl_2005']]
    hpl_lons = [point['lng'] for point in displacement_data['hpl_2005']]
    hpl_lats.append(displacement_data['hpl_2005'][0]['lat'])
    hpl_lons.append(displacement_data['hpl_2005'][0]['lng'])
    
    anim_fig.add_trace(go.Scattermapbox(
        lat=hpl_lats,
        lon=hpl_lons,
        mode='lines',
        fill='toself',
        name='HPL 2005',
        line=dict(width=2, color='rgba(46, 204, 113, 0.8)'),
        fillcolor='rgba(46, 204, 113, 0.2)',
    ))
    
    anim_fig.update_layout(
        mapbox=dict(
            style=st.session_state.map_style,
            center=dict(lat=center[0], lon=center[1]),
            zoom=map_data['zoom']
        ),
        updatemenus=[dict(
            type="buttons",
            buttons=[dict(
                label="Play",
                method="animate",
                args=[None, {"frame": {"duration": 500, "redraw": True}, "fromcurrent": True}]
            )]
        )],
        height=500
    )
    
    st.plotly_chart(anim_fig, use_container_width=True)
    
    # Tambahkan penjelasan animasi
    st.markdown("""
    <div class="analysis-card">
        <h3>Interpretasi Animasi Pergeseran Lahan</h3>
        <p>Animasi di atas menunjukkan bagaimana batas lahan HGU PT JJP bergeser dari posisi tahun 2005 ke posisi tahun 2011.
        Pergeseran ini menyebabkan tumpang tindih dengan lahan HPL masyarakat, yang menjadi sumber konflik.</p>
        <ul>
            <li><strong>Area Hijau</strong>: HPL Masyarakat (tetap)</li>
            <li><strong>Area Biru</strong>: HGU PT JJP 2005 (posisi awal)</li>
            <li><strong>Area Ungu</strong>: HGU PT JJP 2011 (posisi akhir setelah revisi)</li>
        </ul>
        <p>Pergeseran batas ini mengakibatkan tumpang tindih lahan seluas ±1.500 Ha yang sebelumnya digarap oleh masyarakat.</p>
    </div>
    """, unsafe_allow_html=True)

# Fungsi untuk membuat visualisasi dashboard
def create_dashboard(conflict_data):
    """Buat dashboard dengan berbagai visualisasi data"""
    st.subheader("Dashboard Analisis Konflik Lahan")
    
    # Statistik utama
    stats = conflict_data['stats']
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Luas Sengketa</div>
            <div class="stat-value">{stats['luas_sengketa']} Ha</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Durasi Konflik</div>
            <div class="stat-value">{stats['durasi_konflik']} Tahun</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Keluarga Terdampak</div>
            <div class="stat-value">{stats['keluarga_terdampak']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-label">Nilai Kerugian</div>
            <div class="stat-value">{format_currency(stats['nilai_kerugian'], "IDR")}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Grafik timeline konflik
    st.markdown("### Timeline Konflik Lahan")
    timeline_df = pd.DataFrame(conflict_data['timeline'])
    
    fig_timeline = px.scatter(timeline_df, x='year', y='sources', size='sources',
                             color='impact', color_discrete_map={
                                 'high': '#e74c3c',
                                 'medium': '#f39c12', 
                                 'very_high': '#c0392b'
                             },
                             hover_name='event', hover_data={'year': True, 'sources': True, 'impact': True})
    
    fig_timeline.update_layout(
        height=400,
        xaxis_title="Tahun",
        yaxis_title="Jumlah Sumber",
        showlegend=True
    )
    
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Grafik dampak ekonomi
    st.markdown("### Dampak Ekonomi Konflik")
    economic_data = conflict_data['economic_impact']
    economic_df = pd.DataFrame(economic_data)
    
    fig_economic = go.Figure()
    fig_economic.add_trace(go.Scatter(x=economic_df['years'], y=economic_df['direct_loss'],
                                     mode='lines+markers', name='Kerugian Langsung (Miliar Rp)',
                                     line=dict(color='#e74c3c', width=3)))
    fig_economic.add_trace(go.Scatter(x=economic_df['years'], y=economic_df['indirect_loss'],
                                     mode='lines+markers', name='Kerugian Tidak Langsung (Miliar Rp)',
                                     line=dict(color='#f39c12', width=3)))
    fig_economic.add_trace(go.Scatter(x=economic_df['years'], y=economic_df['environmental_damage'],
                                     mode='lines+markers', name='Kerusakan Lingkungan (Miliar Rp)',
                                     line=dict(color='#2ecc71', width=3)))
    
    fig_economic.update_layout(
        height=400,
        xaxis_title="Tahun",
        yaxis_title="Nilai (Miliar Rupiah)",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_economic, use_container_width=True)
    
    # Grafik dampak sosial
    st.markdown("### Dampak Sosial Konflik")
    population_data = conflict_data['population_impact']
    population_df = pd.DataFrame(population_data)
    
    fig_population = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig_population.add_trace(
        go.Scatter(x=population_df['years'], y=population_df['affected_families'],
                  mode='lines+markers', name='Keluarga Terdampak',
                  line=dict(color='#3498db', width=3)),
        secondary_y=False,
    )
    
    fig_population.add_trace(
        go.Scatter(x=population_df['years'], y=population_df['relocated_families'],
                  mode='lines+markers', name='Keluarga Direlokasi',
                  line=dict(color='#9b59b6', width=3)),
        secondary_y=False,
    )
    
    fig_population.add_trace(
        go.Scatter(x=population_df['years'], y=population_df['income_reduction'],
                  mode='lines+markers', name='Penurunan Pendapatan (%)',
                  line=dict(color='#e74c3c', width=3)),
        secondary_y=True,
    )
    
    fig_population.update_layout(
        height=400,
        xaxis_title="Tahun",
        hovermode='x unified'
    )
    
    fig_population.update_yaxes(title_text="Jumlah Keluarga", secondary_y=False)
    fig_population.update_yaxes(title_text="Penurunan Pendapatan (%)", secondary_y=True)
    
    st.plotly_chart(fig_population, use_container_width=True)
    
    # Analisis opsi resolusi
    st.markdown("### Analisis Opsi Resolusi Konflik")
    resolution_data = conflict_data['resolution_options']
    resolution_df = pd.DataFrame(resolution_data)
    
    fig_resolution = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig_resolution.add_trace(
        go.Bar(x=resolution_df['options'], y=resolution_df['cost'],
               name='Biaya (Miliar Rp)', marker_color='#3498db'),
        secondary_y=False,
    )
    
    fig_resolution.add_trace(
        go.Scatter(x=resolution_df['options'], y=resolution_df['success_rate'],
                  mode='lines+markers', name='Tingkat Keberhasilan (%)',
                  line=dict(color='#2ecc71', width=3)),
        secondary_y=True,
    )
    
    fig_resolution.update_layout(
        height=400,
        xaxis_title="Opsi Resolusi",
        hovermode='x unified'
    )
    
    fig_resolution.update_yaxes(title_text="Biaya (Miliar Rp)", secondary_y=False)
    fig_resolution.update_yaxes(title_text="Tingkat Keberhasilan (%)", secondary_y=True)
    
    st.plotly_chart(fig_resolution, use_container_width=True)
    
    # Tabel opsi resolusi
    st.markdown("### Detail Opsi Resolusi")
    resolution_display_df = resolution_df[['options', 'cost', 'duration', 'success_rate']].copy()
    resolution_display_df.columns = ['Opsi Resolusi', 'Biaya (Miliar Rp)', 'Durasi (Bulan)', 'Tingkat Keberhasilan (%)']
    st.dataframe(resolution_display_df, use_container_width=True)

# Fungsi untuk membuat analisis AI
def create_ai_analysis(conflict_data):
    """Buat analisis AI dengan prediksi dan rekomendasi"""
    st.subheader("Analisis Kecerdasan Buatan")
    
    st.markdown("""
    <div class="analysis-card">
        <h3>Prediksi Model AI</h3>
        <p>Berdasarkan analisis data historis dan pola konflik lahan, model AI kami memprediksi:</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Prediksi perkembangan konflik
    st.markdown("### Prediksi Perkembangan Konflik")
    
    years = [2023, 2024, 2025, 2026, 2027]
    conflict_intensity = [75, 80, 85, 78, 70]
    resolution_probability = [20, 30, 45, 60, 75]
    
    fig_prediction = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig_prediction.add_trace(
        go.Scatter(x=years, y=conflict_intensity,
                  mode='lines+markers', name='Intensitas Konflik',
                  line=dict(color='#e74c3c', width=3)),
        secondary_y=False,
    )
    
    fig_prediction.add_trace(
        go.Scatter(x=years, y=resolution_probability,
                  mode='lines+markers', name='Probabilitas Resolusi',
                  line=dict(color='#2ecc71', width=3)),
        secondary_y=True,
    )
    
    fig_prediction.update_layout(
        height=400,
        xaxis_title="Tahun",
        hovermode='x unified'
    )
    
    fig_prediction.update_yaxes(title_text="Intensitas Konflik (%)", secondary_y=False)
    fig_prediction.update_yaxes(title_text="Probabilitas Resolusi (%)", secondary_y=True)
    
    st.plotly_chart(fig_prediction, use_container_width=True)
    
    # Rekomendasi AI
    st.markdown("### Rekomendasi Berbasis AI")
    
    recommendations = [
        {"title": "Mediasi Segera", "priority": "Tinggi", "impact": "Mengurangi ketegangan sebesar 40%"},
        {"title": "Kompensasi Bertahap", "priority": "Sedang", "impact": "Meningkatkan kepuasan masyarakat sebesar 35%"},
        {"title": "Peninjauan Ulang Batas", "priority": "Tinggi", "impact": "Mengurangi area sengketa sebesar 60%"},
        {"title": "Program Pemberdayaan", "priority": "Sedang", "impact": "Meningkatkan ekonomi alternatif sebesar 45%"}
    ]
    
    for rec in recommendations:
        priority_color = "#e74c3c" if rec["priority"] == "Tinggi" else "#f39c12"
        st.markdown(f"""
        <div class="analysis-card">
            <h3>{rec['title']} <span style="color: {priority_color}; font-size: 0.8em;">({rec['priority']})</span></h3>
            <p>{rec['impact']}</p>
        </div>
        """, unsafe_allow_html=True)

# Fungsi untuk membuat tab data
def create_data_tab(conflict_data):
    """Buat tab data dengan informasi lengkap"""
    st.subheader("Data Lengkap Konflik Lahan")
    
    # Data timeline
    st.markdown("### Timeline Konflik")
    timeline_df = pd.DataFrame(conflict_data['timeline'])
    st.dataframe(timeline_df, use_container_width=True)
    
    # Data perubahan koordinat
    st.markdown("### Data Pergeseran Koordinat")
    coord_df = pd.DataFrame(conflict_data['coordinate_changes'])
    st.dataframe(coord_df, use_container_width=True)
    
    # Data perubahan luas lahan
    st.markdown("### Data Perubahan Luas Lahan")
    area_df = pd.DataFrame(conflict_data['land_area_changes'])
    st.dataframe(area_df, use_container_width=True)
    
    # Data dokumen hukum
    st.markdown("### Dokumen Hukum Terkait")
    legal_df = pd.DataFrame(conflict_data['legal_documents'])
    st.dataframe(legal_df, use_container_width=True)

# Fungsi untuk membuat tab resolusi
def create_resolution_tab(conflict_data):
    """Buat tab resolusi dengan analisis mendalam"""
    st.subheader("Analisis Resolusi Konflik")
    
    st.markdown("""
    <div class="analysis-card">
        <h3>Pendekatan Resolusi Konflik Lahan</h3>
        <p>Berdasarkan analisis mendalam terhadap konflik lahan di Desa Pedamaran, berikut adalah pendekatan resolusi yang direkomendasikan:</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Analisis stakeholder
    st.markdown("### Analisis Stakeholder")
    parties_df = pd.DataFrame(conflict_data['parties_involved'])
    
    fig_stakeholder = px.sunburst(parties_df, path=['type', 'name'], values='resources',
                                 color='type', color_discrete_map={
                                     'company': '#e74c3c',
                                     'community': '#3498db',
                                     'government': '#2ecc71',
                                     'ngo': '#f39c12'
                                 })
    
    fig_stakeholder.update_layout(height=500)
    st.plotly_chart(fig_stakeholder, use_container_width=True)
    
    # Matriks analisis konflik
    st.markdown("### Matriks Analisis Konflik")
    
    conflict_matrix = {
        'Aspek': ['Legal', 'Sosial', 'Ekonomi', 'Lingkungan', 'Politik'],
        'Tingkat Keparahan': [8, 9, 7, 6, 5],
        'Tingkat Urgensi': [9, 8, 7, 6, 5],
        'Kompleksitas': [8, 7, 6, 5, 9]
    }
    
    matrix_df = pd.DataFrame(conflict_matrix)
    st.dataframe(matrix_df, use_container_width=True)
    
    # Rencana aksi
    st.markdown("### Rencana Aksi Resolusi")
    
    action_plan = [
        {"phase": "Fase 1 (0-6 bulan)", "actions": ["Mediasi multipihak", "Verifikasi data lapangan", "Penghentian aktivitas konflik"]},
        {"phase": "Fase 2 (6-12 bulan)", "actions": ["Penandatanganan MoU", "Penentuan kompensasi", "Program pemberdayaan masyarakat"]},
        {"phase": "Fase 3 (12-24 bulan)", "actions": ["Implementasi solusi", "Monitoring dan evaluasi", "Penyusunan regulasi pencegahan"]}
    ]
    
    for phase in action_plan:
        st.markdown(f"""
        <div class="analysis-card">
            <h3>{phase['phase']}</h3>
            <ul>
                {''.join([f'<li>{action}</li>' for action in phase['actions']])}
            </ul>
        </div>
        """, unsafe_allow_html=True)

# Inisialisasi session state
if 'conflict_data' not in st.session_state:
    st.session_state.conflict_data = load_conflict_data()

if 'ai_results' not in st.session_state:
    st.session_state.ai_results = None

# Tabs utama dengan tambahan tab untuk analisis pergeseran
main_tabs = st.tabs(["🗺️ Peta Interaktif", "📊 Dashboard", "📈 Analisis Pergeseran", "🤖 Analisis AI", "🔍 Data", "⚖️ Resolusi", "💰 Ekonomi"])

with main_tabs[0]:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.header("Peta Interaktif Konflik Lahan")
    
    # Create the interactive map
    create_interactive_map(st.session_state.conflict_data)
    
    # Additional map information
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="glass-card">
            <h3>Informasi Area Sengketa</h3>
            <p><strong>Total Area Sengketa:</strong> 1,500 Ha</p>
            <p><strong>Lokasi:</strong> Desa Pedamaran, Kecamatan Pekaitan, Kabupaten Rokan Hilir</p>
            <p><strong>Koordinat:</strong> 1.955793°N, 100.854103°E</p>
            <p><strong>Jenis Konflik:</strong> Sengketa Lahan antara Masyarakat dan PT Jatim Jaya Perkasa</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="glass-card">
            <h3>Layer Tersedia</h3>
            <ul>
                <li>Batas Administratif</li>
                <li>Area Sengketa</li>
                <li>Heatmap Konflik</li>
                <li>Pergeseran Batas</li>
                <li>Penggunaan Lahan</li>
                <li>Infrastruktur</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with main_tabs[1]:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    create_dashboard(st.session_state.conflict_data)
    st.markdown('</div>', unsafe_allow_html=True)

with main_tabs[2]:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.header("Analisis Pergeseran Lahan dan Tumpang Tindih")
    create_displacement_analysis(st.session_state.conflict_data)
    
    # Tampilkan animasi jika diaktifkan
    if st.session_state.show_animation:
        create_displacement_animation(st.session_state.conflict_data)
    st.markdown('</div>', unsafe_allow_html=True)

with main_tabs[3]:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    create_ai_analysis(st.session_state.conflict_data)
    st.markdown('</div>', unsafe_allow_html=True)

with main_tabs[4]:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    create_data_tab(st.session_state.conflict_data)
    st.markdown('</div>', unsafe_allow_html=True)

with main_tabs[5]:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    create_resolution_tab(st.session_state.conflict_data)
    st.markdown('</div>', unsafe_allow_html=True)

with main_tabs[6]:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.header("Analisis Ekonomi Konflik Lahan")
    
    # Analisis dampak ekonomi
    economic_data = st.session_state.conflict_data['economic_impact']
    economic_df = pd.DataFrame(economic_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Biaya Kumulatif Konflik")
        total_direct = sum(economic_df['direct_loss'])
        total_indirect = sum(economic_df['indirect_loss'])
        total_environmental = sum(economic_df['environmental_damage'])
        
        fig_costs = go.Figure(data=[go.Pie(
            labels=['Kerugian Langsung', 'Kerugian Tidak Langsung', 'Kerusakan Lingkungan'],
            values=[total_direct, total_indirect, total_environmental],
            hole=0.4,
            marker_colors=['#e74c3c', '#f39c12', '#2ecc71']
        )])
        
        fig_costs.update_layout(height=400)
        st.plotly_chart(fig_costs, use_container_width=True)
    
    with col2:
        st.markdown("### Prediksi Biaya Masa Depan")
        
        # Prediksi biaya berdasarkan inflasi
        years = [2025, 2026, 2027, 2028, 2029]
        inflation_rate = 2.5  # %
        
        future_direct = [economic_df['direct_loss'].iloc[-1] * (1 + inflation_rate/100) ** i for i in range(5)]
        future_indirect = [economic_df['indirect_loss'].iloc[-1] * (1 + inflation_rate/100) ** i for i in range(5)]
        
        fig_future = go.Figure()
        fig_future.add_trace(go.Scatter(x=years, y=future_direct, mode='lines+markers',
                                       name='Kerugian Langsung', line=dict(color='#e74c3c', width=3)))
        fig_future.add_trace(go.Scatter(x=years, y=future_indirect, mode='lines+markers',
                                       name='Kerugian Tidak Langsung', line=dict(color='#f39c12', width=3)))
        
        fig_future.update_layout(
            height=400,
            xaxis_title="Tahun",
            yaxis_title="Nilai (Miliar Rupiah)"
        )
        
        st.plotly_chart(fig_future, use_container_width=True)
    
    # Analisis cost-benefit resolusi
    st.markdown("### Analisis Cost-Benefit Resolusi")
    
    resolution_data = st.session_state.conflict_data['resolution_options']
    resolution_df = pd.DataFrame(resolution_data)
    
    fig_roi = go.Figure()
    fig_roi.add_trace(go.Bar(x=resolution_df['options'], y=resolution_df['cost'],
                            name='Biaya (Miliar Rp)', marker_color='#3498db'))
    fig_roi.add_trace(go.Scatter(x=resolution_df['options'], y=resolution_df['success_rate'],
                                mode='lines+markers', name='Tingkat Keberhasilan (%)',
                                line=dict(color='#2ecc71', width=3)))
    
    fig_roi.update_layout(
        height=400,
        xaxis_title="Opsi Resolusi",
        yaxis_title="Nilai",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_roi, use_container_width=True)
    
    # Rekomendasi ekonomi
    st.markdown("### Rekomendasi Ekonomi")
    
    st.markdown("""
    <div class="analysis-card">
        <h3>Strategi Pengoptimalan Sumber Daya</h3>
        <ol>
            <li><strong>Alokasi dana kompensasi bertahap</strong> untuk mengurangi beban keuangan sekaligus membangun kepercayaan</li>
            <li><strong>Investasi dalam program pemberdayaan masyarakat</strong> untuk menciptakan sumber pendapatan alternatif</li>
            <li><strong>Pengembangan skema bagi hasil</strong> antara perusahaan dan masyarakat untuk solusi win-win</li>
            <li><strong>Utilisasi dana CSR perusahaan</strong> untuk program pembangunan berkelanjutan di area konflik</li>
            <li><strong>Kerjasama dengan lembaga keuangan</strong> untuk pembiayaan resolusi konflik yang berkelanjutan</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Watermark dengan style profesional yang diperbarui
st.markdown(
    """
    <div class="watermark">
        <div>Powered by Agung Basuki</div>
        <div>Didukung oleh LSM Bismi</div>
    </div>
    """,
    unsafe_allow_html=True
)

# Tutup container untuk konten utama
st.markdown('</div>', unsafe_allow_html=True)

# Footer yang diperbarui
st.markdown("---")
st.markdown(
    """
    <div class="footer">
        <p>© 2025 Simulator Konflik Lahan Rohil | Didukung oleh AI & Analitik Geospasial</p>
        <p>Disclaimer: Ini adalah alat simulasi untuk tujuan analitis saja</p>
    </div>
    """,
    unsafe_allow_html=True
)