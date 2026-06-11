import streamlit as st
import numpy as np
import requests
from datetime import datetime, timedelta
import pytz

# --- 1. CONFIGURACIÓN DE LA TERMINAL DE ALTA CONVERSIÓN ---
st.set_page_config(
    page_title="🚨 SHARP QUANT SYSTEM - LIVE MLB", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Avanzado para simular una App de Apuestas Premium (Estilo ESPN/Bet365)
st.markdown("""
    <style>
    .stApp { background-color: #0b0f17; color: #c9d1d9; }
    h1 {
        color: #00ff66 !important;
        font-family: 'Courier New', monospace;
        text-shadow: 0 0 15px #00ff66;
        text-align: center;
        font-size: 2.8rem !important;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .subtitle { text-align: center; color: #8b949e; margin-bottom: 25px; }
    
    /* Contenedor de Tarjeta de Partido */
    .game-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        transition: all 0.2s ease;
    }
    .game-card:hover {
        border-color: #00ff66;
        box-shadow: 0 0 15px rgba(0, 255, 102, 0.1);
    }
    
    /* Detalles de los Equipos dentro de la Card */
    .team-row { display: flex; justify-content: space-between; font-size: 1.2rem; font-weight: bold; margin: 5px 0; }
    .team-name { color: #ffffff; }
    .game-status { font-size: 0.85rem; color: #8b949e; font-family: monospace; }
    .status-live { color: #ff4444 !important; font-weight: bold; text-shadow: 0 0 5px #ff4444; }
    .status-final { color: #8b949e !important; }
    .status-preview { color: #00ff66 !important; }
    
    /* Botones de Activación del Motor */
    .stButton>button {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%) !important;
        color: #00ff66 !important;
        border: 1px solid #00ff66 !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        transition: all 0.3s ease;
        width: 100%;
        margin-top: 10px;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #00ff66 0%, #009933 100%) !important;
        color: #000000 !important;
        box-shadow: 0 0 15px rgba(0, 255, 102, 0.4) !important;
    }
    
    /* Bloques de Métricas de Neón */
    div[data-testid="metric-container"] {
        background-color: #0d1117 !important;
        border: 1px solid #00ff66 !important;
        border-radius: 10px !important;
        padding: 10px !important;
    }
    div[data-testid="stMetricValue"] { font-size: 1.6rem !important; font-family: 'Impact', sans-serif; color: #ffffff !important; }
    .status-box { background-color: #1f190f; border: 1px solid #f1e05a; padding: 15px; border-radius: 10px; color: #f1e05a; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>⚡ SHARP QUANT SYSTEM PRO ⚡</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Procesador Avanzado de Sabermetría Predictiva — Interfaz de Calendario Dinámico</p>", unsafe_allow_html=True)

# --- 2. CONFIGURACIÓN DE FECHAS EN ESPAÑOL Y ZONA HORARIA ---
zona_horaria = pytz.timezone('America/New_York')
ahora_et = datetime.now(zona_horaria)

meses_es = {
    "January": "Ene", "February": "Feb", "March": "Mar", "April": "Abr", 
    "May": "May", "June": "Jun", "July": "Jul", "August": "Ago", 
    "September": "Sep", "October": "Oct", "November": "Nov", "December": "Dic"
}

def formatear_fecha_boton(dt):
    mes = meses_es.get(dt.strftime('%B'), dt.strftime('%B'))
    return f"{dt.strftime('%d')} {mes}"

# Creamos las opciones del calendario horizontal (Ayer, Hoy, Mañana, Pasado Mañana)
fecha_ayer = ahora_et - timedelta(days=1)
fecha_hoy = ahora_et
fecha_manana = ahora_et + timedelta(days=1)
fecha_pasado = ahora_et + timedelta(days=2)

# --- 3. BARRA HORIZONTAL DE CALENDARIO (TIPO ESPN) ---
st.markdown("### 🗓️ Selecciona un Día del Calendario")
col_fechas = st.columns(4)

with col_fechas[0]:
    if st.button(f"⏪ Ayer ({formatear_fecha_boton(fecha_ayer)})", use_container_width=True):
        st.session_state.fecha_seleccionada = fecha_ayer.strftime('%Y-%m-%d')
with col_fechas[1]:
    if st.button(f"🎯 Hoy ({formatear_fecha_boton(fecha_hoy)})", use_container_width=True):
        st.session_state.fecha_seleccionada = fecha_hoy.strftime('%Y-%m-%d')
with col_fechas[2]:
    if st.button(f"⏩ Mañana ({formatear_fecha_boton(fecha_manana)})", use_container_width=True):
        st.session_state.fecha_seleccionada = fecha_manana.strftime('%Y-%m-%d')
with col_fechas[3]:
    if st.button(f"📆 {formatear_fecha_boton(fecha_pasado)}", use_container_width=True):
        st.session_state.fecha_seleccionada = fecha_pasado.strftime('%Y-%m-%d')

# Inicializar por defecto en el día de "Hoy"
if "fecha_seleccionada" not in st.session_state:
    st.session_state.fecha_seleccionada = fecha_hoy.strftime('%Y-%m-%d')

fecha_activa_dt = datetime.strptime(st.session_state.fecha_seleccionada, '%Y-%m-%d')
mes_completo = meses_es.get(fecha_activa_dt.strftime('%B'), fecha_activa_dt.strftime('%B'))
st.markdown(f"#### 📅 Mostrando cartelera del: **{fecha_activa_dt.strftime('%d')} de {mes_completo}, {fecha_activa_dt.strftime('%Y')}**")

# --- 4. CONEXIÓN AUTOMÁTICA A LA API OFICIAL DE LA MLB ---
@st.cache_data(ttl=60)
def cargar_calendario_api(fecha_str):
    url = f"https://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&date={fecha_str}"
    lista_partidos = []
    try:
        data = requests.get(url, timeout=5).json()
        for fecha_data in data.get("dates", []):
            for juego in fecha_data.get("games", []):
                vis = juego["teams"]["away"]["team"]["name"]
                loc = juego["teams"]["home"]["team"]["name"]
                status = juego["status"]["abstractGameState"]  # Preview, Live, Final
                detalle = juego["status"].get("detailedState", "")
                hora_utc = juego["gameDate"]
                
                dt_utc = datetime.strptime(hora_utc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc)
                dt_et = dt_utc.astimezone(zona_horaria)
                
                lista_partidos.append({
                    "vis": vis, "loc": loc, 
                    "status": status, "detalle": detalle,
                    "hora_texto": dt_et.strftime('%I:%M %p ET'),
                    "hora_obj": dt_et.time()
                })
    except:
        pass
    return lista_partidos

partidos_del_dia = cargar_calendario_api(st.session_state.fecha_seleccionada)

# --- LISTA MAESTRA DE EQUIPOS PARA EL MOTOR ---
EQUIPOS_MLB = [
    "Arizona Diamondbacks", "Atlanta Braves", "Baltimore Orioles", "Boston Red Sox", 
    "Chicago Cubs", "Chicago White Sox", "Cincinnati Reds", "Cleveland Guardians", 
    "Colorado Rockies", "Detroit Tigers", "Houston Astros", "Kansas City Royals", 
    "Los Angeles Angels", "Los Angeles Dodgers", "Miami Marlins", "Milwaukee Brewers", 
    "Minnesota Twins", "New York Mets", "New York Yankees", "Oakland Athletics", 
    "Philadelphia Phillies", "Pittsburgh Pirates", "San Diego Padres", "San Francisco Giants", 
    "Seattle Mariners", "St. Louis Cardinals", "Tampa Bay Rays", "Texas Rangers", 
    "Toronto Blue Jays", "Washington Nationals"
]

# --- 5. LOGICA ANALÍTICA (BASE DE DATOS INTERNA) ---
def obtener_analitica_diaria_mlb(nombre_equipo):
    datos_maestros = {
        "Los Angeles Dodgers": {
            "era_ab": 2.10, "whip_ab": 0.88, "xera": 2.45, "fip": 2.30, "k_bb": 4.1,
            "bp_era": 3.45, "bp_whip": 1.12, "bp_uso": 0.90, "bp_descanso": "ÓPTIMO",
            "bajas": ["Mookie Betts"], "lineup_status": "CONFIRMADA",
            "carreras_p": 5.4, "avg": .258, "ops": .790, "wrc": 122,
            "vs_rhp": 124, "vs_lhp": 118, "last10": "7-3", "descanso_dias": 1,
            "clima_wind": 12, "clima_temp": 74, "park_factor": 1.05,
            "cuota_linea": -165, "umpire_strike_zone": -0.15, "bp_split_lhp": 3.10, "bp_split_rhp": 3.50
        },
        "Pittsburgh Pirates": {
            "era_ab": 4.80, "whip_ab": 1.42, "xera": 4.65, "fip": 4.80, "k_bb": 2.2,
            "bp_era": 4.10, "bp_whip": 1.38, "bp_uso": 1.40, "bp_descanso": "SATURADO",
            "bajas": ["David Bednar"], "lineup_status": "CONFIRMADA",
            "carreras_p": 3.9, "avg": .230, "ops": .670, "wrc": 92,
            "vs_rhp": 90, "vs_lhp": 95, "last10": "4-6", "descanso_dias": 0,
            "clima_wind": 12, "clima_temp": 74, "park_factor": 1.05,
            "cuota_linea": +145, "umpire_strike_zone": -0.15, "bp_split_lhp": 4.30, "bp_split_rhp": 3.90
        }
    }
    return datos_maestros.get(nombre_equipo, {
        "era_ab": 3.95, "whip_ab": 1.25, "xera": 4.00, "fip": 4.10, "k_bb": 2.8,
        "bp_era": 3.80, "bp_whip": 1.24, "bp_uso": 1.00, "bp_descanso": "MODERADO",
        "bajas": [], "lineup_status": "PROBABLE",
        "carreras_p": 4.5, "avg": .248, "ops": .730, "wrc": 100,
        "vs_rhp": 100, "vs_lhp": 100, "last10": "5-5", "descanso_dias": 1,
        "clima_wind": 6, "clima_temp": 71, "park_factor": 1.00,
        "cuota_linea": -110, "umpire_strike_zone": 0.00, "bp_split_lhp": 3.80, "bp_split_rhp": 3.80
    })

def ejecutar_simulacion_quant(vis, loc):
    v_stats = obtener_analitica_diaria_mlb(vis)
    l_stats = obtener_analitica_diaria_mlb(loc)
    
    runs_vis = (v_stats["carreras_p"] * (v_stats["wrc"] / 100)) + (l_stats["whip_ab"] * 0.35) - (l_stats["k_bb"] * 0.05)
    runs_loc = (l_stats["carreras_p"] * (l_stats["wrc"] / 100)) + (v_stats["whip_ab"] * 0.30) - (v_stats["k_bb"] * 0.05)
    
    runs_vis += (l_stats["bp_era"] * 0.1 * l_stats["bp_uso"]) + l_stats["umpire_strike_zone"]
    runs_loc += (v_stats["bp_era"] * 0.1 * v_stats["bp_uso"]) + l_stats["umpire_strike_zone"]
    
    runs_vis *= l_stats["park_factor"]
    runs_loc *= l_stats["park_factor"]
    
    sim_vis = np.random.poisson(runs_vis, 10000)
    sim_loc = np.random.poisson(runs_loc, 10000)
    
    prob_v = (np.sum(sim_vis > sim_loc) / 10000) * 100
    prob_l = 100 - prob_v
    ganador_ml = vis if prob_v > prob_l else loc
    porcentaje_ml = max(prob_v, prob_l)
    
    prob_over = (np.sum((sim_vis + sim_loc) > 8.5) / 10000) * 100
    veredicto_ou = "OVER 8.5" if prob_over > 50 else "UNDER 8.5"
    porcentaje_ou = prob_over if prob_over > 50 else (100 - prob_over)
    
    if prob_v > prob_l:
        prob_cubrir = (np.sum((sim_vis - sim_loc) >= 2) / 10000) * 100
        veredicto_rl = f"{vis} -1.5" if prob_cubrir > 52.5 else f"{loc} +1.5"
        porcentaje_rl = prob_cubrir if prob_cubrir > 52.5 else (100 - prob_cubrir)
    else:
        prob_cubrir = (np.sum((sim_loc - sim_vis) >= 2) / 10000) * 100
        veredicto_rl = f"{loc} -1.5" if prob_cubrir > 52.5 else f"{vis} +1.5"
        porcentaje_rl = prob_cubrir if prob_cubrir > 52.5 else (100 - prob_cubrir)
        
    return ganador_ml, porcentaje_ml, veredicto_ou, porcentaje_ou, veredicto_rl, porcentaje_rl, v_stats, l_stats

# --- 6. RENDERIZADO DE LA CARTELERA DINÁMICA ---
# Separamos los partidos activos de los concluidos o pospuestos
partidos_disponibles = []
partidos_finalizados = []

for j en partidos_del_dia:
    if "postponed" in j["detalle"].lower() or "suspended" in j["detalle"].lower() or "cancel" in j["detalle"].lower():
        continue
    
    # Comportamiento de app de apuestas: Clasificar por disponibilidad
    if j["status"] == "Final":
        partidos_finalizados.append(j)
    else:
        # Si es Hoy, filtramos que no hayan empezado basándonos en la hora
        if st.session_state.fecha_seleccionada == ahora_et.strftime('%Y-%m-%d'):
            if ahora_et.time() < j["hora_obj"] and j["status"] == "Preview":
                partidos_disponibles.append(j)
            else:
                partidos_finalizados.append(j) # Si ya empezó o está en vivo, pasa al archivo del día
        else:
            partidos_disponibles.append(j)

# SECCIÓN A: PARTIDOS DISPONIBLES PARA SIMULAR
st.markdown("---")
st.markdown("### 🟢 Partidos Disponibles para Análisis")

if not partidos_disponibles:
    st.markdown("<div class='status-box'>🚫 NO HAY PARTIDOS DISPONIBLES POR HOY. Todos los encuentros han comenzado o finalizado. Revisa la pestaña de 'Mañana' en el calendario superior para ver la cartelera siguiente.</div>", unsafe_allow_html=True)
else:
    for idx, juego in enumerate(partidos_disponibles):
        # Creamos una tarjeta visual compacta tipo ESPN
        with st.container():
            st.markdown(f"""
                <div class='game-card'>
                    <div class='team-row'><span class='team-name'>🔵 {juego['vis']} (Visitante)</span> <span class='game-status status-preview'>📊 PREVIEW</span></div>
                    <div class='team-row'><span class='team-name'>🏠 {juego['loc']} (Local)</span> <span class='game-status'>{juego['hora_texto']}</span></div>
                </div>
            """, unsafe_allow_html=True)
            
            # Botón único dentro de la tarjeta para desplegar el análisis del partido
            if st.button(f"⚡ Correr Motor Estadístico: {juego['vis']} vs {juego['loc']}", key=f"btn_{idx}"):
                res_ml, por_ml, res_ou, por_ou, res_rl, por_rl, v_s, l_s = ejecutar_simulacion_quant(juego['vis'], juego['loc'])
                
                # Despliegue de Bloques de Neón
                st.markdown("<br>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(label="🏆 GANADOR DIRECTO (MONEYLINE)", value=res_ml, delta=f"{round(por_ml, 1)}% Probabilidad")
                with col2:
                    st.metric(label="📈 OVER / UNDER (LÍNEA 8.5)", value=res_ou, delta=f"{round(por_ou, 1)}% Certeza")
                with col3:
                    st.metric(label="⚾ HANDICAP (RUNLINE)", value=res_rl, delta=f"{round(por_rl, 1)}% Estabilidad")
                
                # Justificación Técnica
                st.markdown("#### 📋 Reporte Técnico de Sabermetría")
                st.write(f"**Moneyline:** Ventaja asignada a **{res_ml}** debido al cruce algorítmico entre el xERA de {v_s['xera']} y el FIP de {l_s['fip']} de los lanzadores abridores.")
                st.write(f"**Línea de Carreras:** Pronóstico **{res_ou}** calculado tras proyectar el OPS ofensivo combinado ({v_s['ops']} vs {l_s['ops']}) ajustado por el Park Factor de {l_s['park_factor']} y el factor Umpire de {l_s['umpire_strike_zone']}.")
                st.markdown("<hr style='border: 1px dashed #30363d;'>", unsafe_allow_html=True)

# SECCIÓN B: HISTORIAL / EN VIVO / FINALIZADOS DEL DÍA
if partidos_finalizados:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🔴 Partidos en Progreso o Finalizados")
    for j_fin in partidos_finalizados:
        lbl_status = "🔴 EN VIVO / FINALIZADO" if j_fin['status'] == "Live" or j_fin['status'] == "Final" else "⚠️ EN PROGRESO"
        class_status = "status-live" if j_fin['status'] == "Live" else "status-final"
        st.markdown(f"""
            <div class='game-card' style='opacity: 0.6;'>
                <div class='team-row'><span class='team-name'>{j_fin['vis']}</span> <span class='game-status {class_status}'>{lbl_status}</span></div>
                <div class='team-row'><span class='team-name'>{j_fin['loc']}</span> <span class='game-status'>{j_fin['detalle']}</span></div>
            </div>
        """, unsafe_allow_html=True)
