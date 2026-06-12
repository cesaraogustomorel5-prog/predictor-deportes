import streamlit as st
import numpy as np
import requests
from datetime import datetime
import pytz
import hashlib
import time

# =====================================================================
# MODULO 0: MOTOR DE TRADUCCIÓN (I18N)
# =====================================================================
TRADUCCIONES = {
    "ES": {
        "title": "SISTEMA AVANZADO DE PREDICCIÓN CUANTITATIVA",
        "back": "⚾ VOLVER AL CALENDARIO",
        "filter": "Filtro Temporal",
        "total": "📅 Total",
        "live": "🔴 En curso",
        "final": "🏁 Final",
        "missing": "⏳ Faltantes",
        "suspended": "❌ Suspend.",
        "mode_dark": "Modo Oscuro",
        "mode_light": "Modo Claro"
    },
    "EN": {
        "title": "ADVANCED QUANTITATIVE PREDICTION SYSTEM",
        "back": "⚾ BACK TO CALENDAR",
        "filter": "Time Filter",
        "total": "📅 Total",
        "live": "🔴 Live",
        "final": "🏁 Final",
        "missing": "⏳ Upcoming",
        "suspended": "❌ Susp.",
        "mode_dark": "Dark Mode",
        "mode_light": "Light Mode"
    }
}

def _T(key):
    lang = st.session_state.get("lang", "ES")
    return TRADUCCIONES[lang].get(key, key)

# =====================================================================
# MODULO 1: ESTADO E INICIALIZACIÓN
# =====================================================================
if "lang" not in st.session_state: st.session_state.lang = "ES"
if "fecha_seleccionada" not in st.session_state: st.session_state.fecha_seleccionada = datetime.now().date()
if "vista_actual" not in st.session_state: st.session_state.vista_actual = "dashboard"

with st.sidebar:
    st.markdown("### ⚙️")
    st.selectbox("🌍 Language / Idioma", ["ES", "EN"], key="lang")
    st.toggle(_T("mode_light") if st.session_state.get("tema_is_dark") else _T("mode_dark"), key="tema_is_dark", value=True)

# ... [MANTEN TU CÓDIGO DE CSS, MAPEO_ORGANIZACIONES, Y FUNCIONES API AQUÍ] ...
# (He omitido las funciones de lógica repetida para optimizar el espacio, 
# asegúrate de mantener tus funciones originales de API y Motor Predictivo)

# =====================================================================
# RENDER: VISTA CALENDARIO CENTRAL (CON TRADUCCIÓN APLICADA)
# =====================================================================
if st.session_state.vista_actual == "dashboard":
    st.markdown(f"### 📅 {_T('total').replace('📅 ','')}")
    fecha_dt = st.date_input(_T("filter"), st.session_state.fecha_seleccionada, label_visibility="collapsed")
    
    # Renderizado Compacto con Traducciones dinámicas
    cols = st.columns(5)
    data_metrics = [
        (_T("total"), 10), # Reemplaza con tus variables reales
        (_T("live"), 2),
        (_T("final"), 5),
        (_T("missing"), 3),
        (_T("suspended"), 0)
    ]
    
    for i, (label, val) in enumerate(data_metrics):
        with cols[i]:
            st.markdown(f"""
                <div class='mini-metric-container'>
                    <div class='mini-metric-label'>{label}</div>
                    <div class='mini-metric-value'>{val}</div>
                </div>
            """, unsafe_allow_html=True)

    # El resto de tu lógica de renderizado debe usar _T("clave") 
    # para cualquier etiqueta o botón que necesites traducir.
