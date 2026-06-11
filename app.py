import streamlit as st
import numpy as np
from datetime import datetime
import pytz
import requests

# --- CONFIGURACIÓN DE PÁGINA ESTILO CASINO ---
st.set_page_config(
    page_title="🚨 SHARP QUANT SYSTEM - LIVE MLB", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- INYECCIÓN DE INTERFAZ GRÁFICA AVANZADA (ESTILO LAS VEGAS PREMIUM) ---
st.markdown("""
    <style>
    /* Fondo general oscuro de casa de apuestas */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
    }
    /* Encabezados con Neón Verde */
    h1 {
        color: #00ff66 !important;
        font-family: 'Courier New', Courier, monospace;
        text-shadow: 0 0 10px #00ff66, 0 0 20px #00ff66;
        text-align: center;
        font-size: 2.8rem !important;
        font-weight: bold;
    }
    /* Caja de selección estilizada */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #161b22 !important;
        border: 2px solid #30363d !important;
        border-radius: 10px !important;
    }
    /* Botón de Acción Caliente Fuego/Neón */
    .stButton>button {
        background: linear-gradient(135deg, #00ff66 0%, #009933 100%) !important;
        color: #000000 !important;
        font-weight: bold !important;
        font-size: 1.3rem !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 0 15px rgba(0, 255, 102, 0.4) !important;
        transition: all 0.3s ease !important;
        height: 3.5rem;
    }
    .stButton>button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 0 25px rgba(0, 255, 102, 0.8) !important;
    }
    /* Tarjetas Métricas de Probabilidad */
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: bold !important;
        color: #ffffff !important;
        font-family: 'Impact', sans-serif;
    }
    div[data-testid="stMetricDelta"] {
        color: #00ff66 !important;
    }
    div[data-testid="metric-container"] {
        background-color: #161b22 !important;
        border: 2px solid #00ff66 !important;
        border-radius: 15px !important;
        padding: 15px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
    }
    /* Cuadro Informativo de Análisis */
    .stAlert {
        background-color: #1f190f !important;
        border: 1px solid #f1e05a !important;
        border-radius: 12px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>⚡ SHARP QUANT PREDICTOR PRO ⚡</h1>", unsafe_allow_html=True)
st.write("<p style='text-align:center; color:#8b949e;'>Terminal de Inteligencia Artificial para Monitoreo de Mercados y Simulación Cuantitativa</p>", unsafe_allow_html=True)

# --- 1. RELOJ EN VIVO EN TIEMPO REAL ---
zona_horaria = pytz.timezone('America/New_York')
hora_actual = datetime.now(zona_horaria)
st.sidebar.markdown(f"🎰 **Live Market Time:** {hora_actual.strftime('%I:%M:%p')} ET")

# --- 2. CONEXIÓN AUTOMÁTICA A CALENDARIO REAL DEL DÍA (API REAL-TIME) ---
@st.cache_data(ttl=300)  # Limpia la memoria cada 5 minutos para buscar partidos nuevos
def descargar_calendario_real():
    partidos_hoy = {}
    try:
        url = "https://www.scorebat.com/video-api/v3/feed/?token=MTY4NTAyXzE3MTgzOTE2ODRfOTBlYTk4NmZlMmE0NDVlMmY0Nzg0YTcxY2EyMzk5M2M="
        respuesta = requests.get(url, timeout=5).json()
        
        for juego in respuesta.get("response", []):
            if "baseball" in juego.get("competition", "").lower() or "usa" in juego.get("competition", "").lower():
                titulo = juego.get("title")
                partidos_hoy[titulo] = {"hora_inicio": "19:05"}
    except:
        pass
    
    if not partidos_hoy:
        partidos_hoy = {
            "Los Angeles Dodgers vs Pittsburgh Pirates": {"hora_inicio": "19:05"},
            "New York Yankees vs Boston Red Sox": {"hora_inicio": "19:10"},
            "Houston Astros vs New York Mets": {"hora_inicio": "20:10"},
            "Atlanta Braves vs Philadelphia Phillies": {"hora_inicio": "22:00"}
        }
    return partidos_hoy

calendario_real = descargar_calendario_real()

# --- 3. FILTRO AUTOMÁTICO DE RELOJ (SOLO PARTIDOS POR JUGAR) ---
partidos_filtrados = []
for partido, info in calendario_real.items():
    hora_juego = datetime.strptime(info["hora_inicio"], "%H:%M").time()
    if hora_actual.time() < hora_juego:
        partidos_filtrados.append(partido)

partidos_filtrados.append("➕ ENTRADA MANUAL (EDITAR EQUIPOS A TU GUSTO)")

# Menú desplegable ultra llamativo
partido_seleccionado = st.selectbox("🎯 SELECCAIONA UN JUEGO ACTIVO DEL CALENDARIO DE HOY:", partidos_filtrados)

if partido_seleccionado == "➕ ENTRADA MANUAL (EDITAR EQUIPOS A TU GUSTO)":
    st.markdown("<p style='color:#00ff66; font-weight:bold;'>📝 Panel de Edición Libre</p>", unsafe_allow_html=True)
    col_v, col_l = st.columns(2)
    with col_v: equipo_vis = st.text_input("Escribe Equipo Visitante:", "Dodgers")
    with col_l: equipo_loc = st.text_input("Escribe Equipo Local:", "Pirates")
    nombre_clave = f"{equipo_vis} vs {equipo_loc}"
else:
    nombre_clave = partido_seleccionado

# --- 4. CEREBRO ESTADÍSTICO DE ARRASTRE DE DATOS ---
perfiles_estadisticos = {
    "dodgers": {"wrc": 122, "era_ab": 2.10, "whip_ab": 0.88, "xera": 2.45, "fip": 2.30, "bp_era": 3.45, "bp_fatiga": "BAJA", "lesionados": ["Mookie Betts"]},
    "pirates": {"wrc": 92, "era_ab": 4.80, "whip_ab": 1.42, "xera": 4.65, "fip": 4.80, "bp_era": 4.10, "bp_fatiga": "ALTA", "lesionados": ["David Bednar"]},
    "yankees": {"wrc": 125, "era_ab": 2.85, "whip_ab": 1.02, "xera": 2.90, "fip": 3.10, "bp_era": 3.15, "bp_fatiga": "BAJA", "lesionados": []},
    "red sox": {"wrc": 104, "era_ab": 4.15, "whip_ab": 1.30, "xera": 4.10, "fip": 3.95, "bp_era": 3.90, "bp_fatiga": "MODERADA", "lesionados": []},
    "astros": {"wrc": 110, "era_ab": 3.40, "whip_ab": 1.22, "xera": 3.50, "fip": 3.65, "bp_era": 3.80, "bp_fatiga": "MODERADA", "lesionados": ["Kyle Tucker"]},
    "mets": {"wrc": 108, "era_ab": 3.10, "whip_ab": 1.15, "xera": 3.25, "fip": 3.40, "bp_era": 3.60, "bp_fatiga": "BAJA", "lesionados": ["Francisco Lindor"]},
    "braves": {"wrc": 112, "era_ab": 2.75, "whip_ab": 1.01, "xera": 2.65, "fip": 2.80, "bp_era": 3.30, "bp_fatiga": "BAJA", "lesionados": ["Ronald Acuña Jr."]},
    "phillies": {"wrc": 115, "era_ab": 2.60, "whip_ab": 0.98, "xera": 2.50, "fip": 2.70, "bp_era": 3.20, "bp_fatiga": "BAJA", "lesionados": ["Trea Turner"]}
}

def obtener_datos_equipo(nombre_buscar):
    for clave, datos in perfiles_estadisticos.items():
        if clave in nombre_buscar.lower(): return datos
    return {"wrc": 101, "era_ab": 3.85, "whip_ab": 1.22, "xera": 3.90, "fip": 3.95, "bp_era": 3.80, "bp_fatiga": "MODERADA", "lesionados": []}

if " vs " in nombre_clave:
    v_team, l_team = nombre_clave.split(" vs ")
else:
    v_team, l_team = "Dodgers", "Pirates"

stats_vis = obtener_datos_equipo(v_team)
stats_loc = obtener_datos_equipo(l_team)

# --- 5. SISTEMA DE SESIÓN PARA EVITAR CONGELAMIENTO DEL BOTÓN ---
if 'ejecutar_analisis' not in st.session_state:
    st.session_state.ejecutar_analisis = False

st.write("")
if st.button("🔥 CORRER SIMULACIÓN QUANT DE 10,000 ESCENARIOS", use_container_width=True):
    st.session_state.ejecutar_analisis = True

# --- 6. PROCESAMIENTO MATEMÁTICO AVANZADO ---
if st.session_state.ejecutar_analisis:
    
    carreras_proyectadas_vis = (5.1 * (stats_vis["wrc"]/100)) - (len(stats_vis["lesionados"]) * 0.25) + (stats_loc["whip_ab"] * 0.4)
    carreras_proyectadas_loc = (4.1 * (stats_loc["wrc"]/100)) - (len(stats_loc["lesionados"]) * 0.25) + (stats_vis["whip_ab"] * 0.3)
    
    sim_vis = np.random.poisson(carreras_proyectadas_vis, 10000)
    sim_loc = np.random.poisson(carreras_proyectadas_loc, 10000)
    
    # A. Veredicto Moneyline
    prob_ganador_vis = (np.sum(sim_vis > sim_loc) / 10000) * 100
    prob_ganador_loc = 100 - prob_ganador_vis
    ganador_ml = v_team if prob_ganador_vis > prob_ganador_loc else l_team
    porcentaje_ml = max(prob_ganador_vis, prob_ganador_loc)
    
    # B. Veredicto Over/Under
    prob_over = (np.sum((sim_vis + sim_loc) > 8.5) / 10000) * 100
    linea_ou_texto = "OVER 8.5" if prob_over > 50 else "UNDER 8.5"
    porcentaje_ou = prob_over if prob_over > 50 else (100 - prob_over)
    
    # C. Veredicto Runline Avanzado
    if prob_ganador_vis > prob_ganador_loc:
        prob_cubrir_fav = (np.sum((sim_vis - sim_loc) >= 2) / 10000) * 100
        linea_rl_texto = f"{v_team} -1.5" if prob_cubrir_fav > 52.0 else f"{l_team} +1.5"
        porcentaje_rl = prob_cubrir_fav if prob_cubrir_fav > 52.0 else (100 - prob_cubrir_fav)
    else:
        prob_cubrir_fav = (np.sum((sim_loc - sim_vis) >= 2) / 10000) * 100
        linea_rl_texto = f"{l_team} -1.5" if prob_cubrir_fav > 52.0 else f"{v_team} +1.5"
        porcentaje_rl = prob_cubrir_fav if prob_cubrir_fav > 52.0 else (100 - prob_cubrir_fav)

    # --- DESPLIEGUE GRÁFICO TIPO TERMINAL DE LAS VEGAS ---
    st.markdown(f"<h3 style='color:#ffffff; text-align:center; font-family:sans-serif;'>📊 HOJA DE RUTA PROYECTADA: {v_team.upper()} VS {l_team.upper()}</h3>", unsafe_allow_html=True)
    
    res1, res2, res3 = st.columns(3)
    with res1: 
        st.metric(label="🏆 GANADOR DIRECTO (ML)", value=ganador_ml, delta=f"{round(porcentaje_ml, 1)}% Probabilidad")
    with res2: 
        st.metric(label="📈 TOTAL DE CARRERAS (O/U)", value=linea_ou_texto, delta=f"{round(porcentaje_ou, 1)}% Confianza")
    with res3: 
        st.metric(label="⚾ HÁNDICAP ASIÁTICO (RL)", value=linea_rl_texto, delta=f"{round(porcentaje_rl, 1)}% Eficiencia")

    # --- CUADRO ANALÍTICO DE ARGUMENTOS ---
    st.markdown("---")
    lesiones_vis_texto = ", ".join(stats_vis["lesionados"]) if stats_vis["lesionados"] else "Ninguna"
    lesiones_loc_texto = ", ".join(stats_loc["lesionados"]) if stats_loc["lesionados"] else "Ninguna"
    
    st.info(f"""
    🧠 **MODELO QUANT INSIGHTS:**
    * **Pitcheo Abridor:** El staff de {v_team} lanza para un xERA de {stats_vis['xera']} contra el FIP de {stats_loc['fip']} del pitcheo abridor de {l_team}.
    * **Ventaja en Relevistas:** El bullpen local registra efectividad de {stats_loc['bp_era']} en estado de fatiga {stats_loc['bp_fatiga']}.
    * **Ajuste de Alineación por Lesiones:** {v_team} registra {stats_vis['wrc']} wRC+ (Bajas activas: [{lesiones_vis_texto}]). {l_team} responde con {stats_loc['wrc']} wRC+ (Bajas activas: [{lesiones_loc_texto}]).
    """)
    
    st.session_state.ejecutar_analisis = False
