import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import geopandas as gpd
from shapely.geometry import Point, Polygon
import json
from datetime import datetime, timedelta
import time
import requests
from io import BytesIO
import base64
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap, MarkerCluster, MiniMap, Fullscreen, Draw, MeasureControl, TimestampedGeoJson
import leafmap.foliumap as leafmap
import pydeck as pdk
import altair as alt
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import torch
import torch.nn as nn
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import networkx as nx
from pyvis.network import Network
import speech_recognition as sr
from PIL import Image
import cv2
import io
import hashlib
import threading
import asyncio
import websockets
import functools
from concurrent.futures import ThreadPoolExecutor
import joblib
import xgboost as xgb
from google.cloud import bigquery
import boto3
from azure.core.exceptions import AzureError
import warnings
warnings.filterwarnings('ignore')

# Import modul dari src
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from data_ingestion import load_config, read_shapefile
    from data_processing import clean_geospatial_data
    from visualization import create_interactive_map, create_static_map
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.info("Running in standalone mode without src modules")

# Konfigurasi halaman
st.set_page_config(
    page_title="AI-Powered Land Conflict Simulator - Rokan Hilir",
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
    --neon-effect: 0 0 5px #fff, 0 0 10px #fff, 0 0 15px #0073e6, 0 0 20px #0073e6;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

body {
    background: linear-gradient(135deg, var(--dark) 0%, #2c3e50 100%);
    color: var(--light);
    line-height: 1.6;
    overflow-x: hidden;
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
    animation: headerGlow 3s infinite alternate;
}

@keyframes headerGlow {
    0% { box-shadow: 0 0 20px rgba(102, 126, 234, 0.5); }
    100% { box-shadow: 0 0 30px rgba(118, 75, 162, 0.8); }
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

.stat-box::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: 0.5s;
}

.stat-box:hover::before {
    left: 100%;
}

.stat-value {
    font-size: 1.8rem;
    font-weight: bold;
    color: white;
    margin: 10px 0;
    text-shadow: var(--neon-effect);
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
    box-shadow: 0 0 10px var(--secondary);
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
    -webkit-animation: AnimationName 10s ease infinite;
    -moz-animation: AnimationName 10s ease infinite;
    animation: AnimationName 10s ease infinite;
    padding: 5px 10px;
    border-radius: 5px;
}

@-webkit-keyframes AnimationName {
    0% { background-position: 0% 50% }
    50% { background-position: 100% 50% }
    100% { background-position: 0% 50% }
}
@-moz-keyframes AnimationName {
    0% { background-position: 0% 50% }
    50% { background-position: 100% 50% }
    100% { background-position: 0% 50% }
}
@keyframes AnimationName {
    0% { background-position: 0% 50% }
    50% { background-position: 100% 50% }
    100% { background-position: 0% 50% }
}

/* 3D effect for cards */
.card-3d {
    transform-style: preserve-3d;
    perspective: 1000px;
}

.card-3d-inner {
    transition: transform 0.6s;
    transform-style: preserve-3d;
}

.card-3d:hover .card-3d-inner {
    transform: rotateY(10deg) rotateX(5deg);
}

/* Cyberpunk theme elements */
.cyberpunk {
    border: 1px solid #0ff;
    box-shadow: 0 0 10px #0ff, inset 0 0 20px rgba(0, 255, 255, 0.1);
    position: relative;
    overflow: hidden;
}

.cyberpunk::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(45deg, transparent, rgba(0, 255, 255, 0.1), transparent);
    transform: rotate(45deg);
    animation: cyberpunkGlow 3s linear infinite;
}

@keyframes cyberpunkGlow {
    0% { transform: rotate(45deg) translate(-50%, -50%); }
    100% { transform: rotate(45deg) translate(50%, 50%); }
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
        <h1>🌍 AI-Powered Land Conflict Simulator</h1>
        <p>Advanced Geospatial Analytics for Rokan Hilir Land Dispute Resolution</p>
    </div>
    ''', 
    unsafe_allow_html=True
)

# Container untuk konten utama
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Sidebar dengan fitur canggih
st.sidebar.markdown('<div class="animated-gradient">CONFIGURATION PANEL</div>', unsafe_allow_html=True)

# Tabs di sidebar
sidebar_tabs = st.sidebar.tabs(["⚙️ Core Settings", "🧠 AI Modules", "🌐 Cloud Services", "📡 Real-time Data", "🔒 Security"])

with sidebar_tabs[0]:
    st.subheader("Global Configuration")
    
    # Mode operasi
    app_mode = st.selectbox(
        "Application Mode",
        ["Standard Analysis", "Advanced Simulation", "Predictive Modeling", "Crisis Management"]
    )
    