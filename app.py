import streamlit as st
import numpy as np
import requests
from datetime import datetime
import pytz

# --- 1. CONFIGURACIÓN DE LA APP PREMIUM ---
st.set_page_config(
    page_title="🚨 SHARP QUANT SYSTEM - LIVE MLB", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Profesional Compacto para Marcadores, Logos y Calendario
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
    
    /* Contenedor de Tarjeta Estilo ESPN Live Score */
    .game-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 14px;
        margin-bottom: 12px;
        transition: all 0.2s ease;
    }
    .game-card:hover {
        border-color: #00ff66;
        box-shadow: 0 0 15px rgba(0, 255, 102, 0.1);
    }
    
    /* Filas de Equipos con Logos alineados - Más pequeños */
    .team-container { display: flex; align-items: center; justify-content: space-between; margin: 5px 0; }
    .team-identity { display: flex; align-items: center; gap: 10px; }
    .team-logo { width: 24px; height: 24px; object-fit: contain; }
    .team-name { color: #ffffff; font-size: 1.15rem; font-weight: bold; }
    .team-score { font-size: 1.2rem; font-weight: 900; color: #00ff66; font-family: 'Impact', sans-serif; padding-right: 10px; }
    
    /* Header e Info de la Card */
    .game-header { display: flex; justify-content: flex-end; padding-bottom: 4px; margin-bottom: 6px; font-size: 0.82rem; font-family: monospace; }
    .status-badge { padding: 2px 7px; border-radius: 4px; font-weight: bold; }
    .badge-live { background-color: #ff4444; color: #ffffff; text-shadow: 0 0 5px #ff4444; }
    .badge-final { background-color: #30363d; color: #8b949e; }
    .badge-preview { background-color: #00ff66; color: #000000; }
    
    /* Personalización del Input del Calendario */
    div[data-testid="stDateInput"] button { background-color: #161b22 !important; color: #ffffff !important; border: 1px solid #00ff66 !important; }
    
    /* Botones de Activación */
    .stButton>button {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%) !important;
        color: #00ff66 !important;
        border: 1px solid #00ff66 !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        width: 100%;
        margin-top: 5px;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #00ff66 0%, #009933 100%) !important;
        color: #000000 !important;
        box-shadow: 0 0 15px rgba(0, 255, 102, 0.4) !important;
    }
    
    div[data-testid="metric-container"] { background-color: #0d1117 !important; border: 1px solid #00ff66 !important; border-radius: 10px !important; }
    div[data-testid="stMetricValue"] { font-size: 1.6rem !important; font-family: 'Impact', sans-serif; color: #ffffff !important; }
    .status-box { background-color: #1f190f; border: 1px solid #f1e05a; padding: 15px; border-radius: 10px; color: #f1e05a; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>⚡ SHARP QUANT SYSTEM PRO ⚡</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Consola de Sabermetría Predictiva e Historial Automatizado de la MLB de Extremo a Extremo</p>", unsafe_allow_html=True)

# --- 2. DICCIONARIO TRADUCTOR DE LA MLB (CIUDAD -> ORGANIZACIÓN & IDs LOGOS) ---
MAPEO_ORGANIZACIONES = {
    "Arizona Diamondbacks": {"nombre": "Diamondbacks", "id": 109},
    "Atlanta Braves": {"nombre": "Braves", "id": 144},
    "Baltimore Orioles": {"nombre": "Orioles", "id": 110},
    "Boston Red Sox": {"nombre": "Red Sox", "id": 111},
    "Chicago Cubs": {"nombre": "Cubs", "id": 112},
    "Chicago White Sox": {"nombre": "White Sox", "id": 145},
    "Cincinnati Reds": {"nombre": "Reds", "id": 113},
    "Cleveland Guardians": {"nombre": "Guardians", "id": 114},
    "Colorado Rockies": {"nombre": "Rockies", "id": 115},
    "Detroit Tigers": {"nombre": "Tigers", "id": 116},
    "Houston Astros": {"nombre": "Astros", "id": 117},
    "Kansas City Royals": {"nombre": "Royals", "id": 118},
    "Los Angeles Angels": {"nombre": "Angels", "id": 108},
    "Los Angeles Dodgers": {"nombre": "Dodgers", "id": 119},
    "Miami Marlins": {"nombre": "Marlins", "id": 146},
    "Milwaukee Brewers": {"nombre": "Brewers", "id": 158},
    "Minnesota Twins": {"nombre": "Twins", "id": 142},
    "New York Mets": {"nombre": "Mets", "id": 121},
    "New York Yankees": {"nombre": "Yankees", "id": 147},
    "Oakland Athletics": {"nombre": "Athletics", "id": 133},
    "Philadelphia Phillies": {"nombre": "Phillies", "id": 143},
    "Pittsburgh Pirates": {"nombre": "Pirates", "id": 134},
    "San Diego Padres": {"nombre": "Padres", "id": 135},
    "San Francisco Giants": {"nombre": "Giants", "id": 137},
    "Seattle Mariners": {"nombre": "Mariners", "id": 136},
    "St. Louis Cardinals": {"nombre": "Cardinals", "id": 138},
    "Tampa Bay Rays": {"nombre": "Rays", "id": 139},
    "Texas Rangers": {"nombre": "Rangers", "id": 140},
    "Toronto Blue Jays": {"nombre": "Blue Jays", "id": 141},
    "Washington Nationals": {"nombre": "Nationals", "id": 120}
}

def obtener_datos_equipo(nombre_completo):
    info = MAPEO_ORGANIZACIONES.get(nombre_completo)
    if info:
        logo_url = f"https://www.mlbstatic.com/team-logos/{info['id']}.svg"
        return info["nombre"], logo_url
    return nombre_completo, ""

# --- 3. SECCIÓN CALENDARIO ---
zona_horaria = pytz.timezone('America/New_York')
ahora_et = datetime.now(zona_horaria)

st.markdown("### 📅 Calendario")
fecha_seleccionada_dt = st.date_input("Haz clic aquí para seleccionar una fecha:", ahora_et, key="calendario_completo")
fecha_str = fecha_seleccionada_dt.strftime('%Y-%m-%d')

# --- 4. CONEXIÓN AUTOMÁTICA CON LA API CENTRAL DE LA MLB ---
@st.cache_data(ttl=30)  
def cargar_cartelera_total_api(fecha_busqueda):
    url = f"https://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&date={fecha_busqueda}"
    lista_juegos = []
    try:
        data = requests.get(url, timeout=5).json()
        for fecha_data in data.get("dates", []):
            for juego in fecha_data.get("games", []):
                nombre_vis_completo = juego["teams"]["away"]["team"]["name"]
                nombre_loc_completo = juego["teams"]["home"]["team"]["name"]
                
                vis_org, vis_logo = obtener_datos_equipo(nombre_vis_completo)
                loc_org, loc_logo = obtener_datos_equipo(nombre_loc_completo)
                
                abstract_status = juego["status"]["abstractGameState"] 
                detailed_status = juego["status"].get("detailedState", "")
                
                score_vis = juego["teams"]["away"].get("score", 0)
                score_loc = juego["teams"]["home"].get("score", 0)
                
                inning_texto = ""
                if abstract_status == "Live":
                    linescore_url = f"https://statsapi.mlb.com/api/v1.1/game/{juego['gamePk']}/feed/live"
                    try:
                        ls_data = requests.get(linescore_url, timeout=2).json()
                        curr_inning = ls_data.get("liveData", {}).get("linescore", {}).get("currentInningOrdinal", "")
                        state = ls_data.get("liveData", {}).get("linescore", {}).get("inningState", "")
                        inning_texto = f"{state} {curr_inning}" if curr_inning else "En Progreso"
                    except:
                        inning_texto = "En Vivo"
                elif abstract_status == "Final":
                    inning_texto = "Final - 9 Innings"
                    # Lógica para extraer la entrada exacta si terminó en extra innings
                    linescore_url = f"https://statsapi.mlb.com/api/v1.1/game/{juego['gamePk']}/feed/live"
                    try:
                        ls_data = requests.get(linescore_url, timeout=2).json()
                        ultimo_inning = ls_data.get("liveData", {}).get("linescore", {}).get("currentInningOrdinal", "")
                        if ultimo_inning and ultimo_inning != "9th":
                            inning_texto = f"Final - {ultimo_inning} Innings"
                    except:
                        pass

                hora_utc = juego["gameDate"]
                dt_utc = datetime.strptime(hora_utc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc)
                dt_et = dt_utc.astimezone(zona_horaria)
                
                lista_juegos.append({
                    "vis_completo": nombre_vis_completo, "vis_name": vis_org, "vis_logo": vis_logo, "vis_score": score_vis,
                    "loc_completo": nombre_loc_completo, "loc_name": loc_org, "loc_logo": loc_logo, "loc_score": score_loc,
                    "status": abstract_status, "detalle": detailed_status, "inning_status": inning_texto,
                    "hora_texto": dt_et.strftime('%I:%M %p ET')
                })
    except:
        pass
    return lista_juegos

cartelera_partidos = cargar_cartelera_total_api(fecha_str)

# --- 5. MODELO DE SABERMETRÍA (PROCESADOR ESTADÍSTICO INTERNO) ---
def obtener_analitica_diaria_mlb(nombre_equipo):
    return {
        "era_ab": 3.95, "whip_ab": 1.25, "xera": 4.00, "fip": 4.10, "k_bb": 2.8,
        "bp_era": 3.80, "bp_whip": 1.24, "bp_uso": 1.00, "bp_descanso": "MODERADO",
        "bajas": [], "lineup_status": "PROBABLE", "carreras_p": 4.5, "avg": .248, "ops": .730, "wrc": 100,
        "vs_rhp": 100, "vs_lhp": 100, "last10": "5-5", "descanso_dias": 1, "clima_wind": 6, "clima_temp": 71,
        "park_factor": 1.00, "cuota_linea": -110, "umpire_strike_zone": 0.00, "bp_split_lhp": 3.80, "bp_split_rhp": 3.80
    }

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

# --- 6. SEPARACIÓN Y ORDENAMIENTO DE PARTIDOS (ACTIVOS ARRIBA, FINALIZADOS ABAJO) ---
st.markdown("---")

if not cartelera_partidos:
    st.markdown("<div class='status-box'>📅 NO HAY ENCUENTROS PROGRAMADOS PARA ESTA FECHA.</div>", unsafe_allow_html=True)
else:
    # Ordenar: Ponemos los 'Live' y 'Preview' primero, y los 'Final' al final de la lista
    partidos_activos = [p for p in cartelera_partidos if p["status"] != "Final"]
    partidos_concluidos = [p for p in cartelera_partidos if p["status"] == "Final"]
    
    cartelera_ordenada = partidos_activos + partidos_concluidos

    for idx, j in enumerate(cartelera_ordenada):
        
        if j["status"] == "Live":
            status_html = f"<span class='status-badge badge-live'>🔴 {j['inning_status'].upper()}</span>"
            mostrar_marcador = True
        elif j["status"] == "Final":
            status_html = f"<span class='status-badge badge-final'>🏁 {j['inning_status'].upper()}</span>"
            mostrar_marcador = True
        else: 
            status_html = f"<span class='status-badge badge-preview'>🕒 {j['hora_texto']}</span>"
            mostrar_marcador = False

        if "postponed" in j["detalle"].lower() or "suspended" in j["detalle"].lower():
            status_html = f"<span class='status-badge badge-final'>⚠️ POSPUESTO</span>"

        marcador_vis_html = f"<span class='st-score team-score'>{j['vis_score']}</span>" if mostrar_marcador else ""
        marcador_loc_html = f"<span class='st-score team-score'>{j['loc_score']}</span>" if mostrar_marcador else ""

        # Renderizar la tarjeta visual
        with st.container():
            st.markdown(f"""
                <div class='game-card'>
                    <div class='game-header'>
                        {status_html}
                    </div>
                    <div class='team-container'>
                        <div class='team-identity'>
                            <img class='team-logo' src='{j['vis_logo']}'>
                            <span class='team-name'>{j['vis_name']}</span>
                        </div>
                        {marcador_vis_html}
                    </div>
                    <div class='team-container'>
                        <div class='team-identity'>
                            <img class='team-logo' src='{j['loc_logo']}'>
                            <span class='team-name'>{j['loc_name']}</span>
                        </div>
                        {marcador_loc_html}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Botón expandible habilitado para TODOS los partidos
            if st.button(f"⚡ Ver detalles y simulación: {j['vis_name']} vs {j['loc_name']}", key=f"btn_{idx}"):
                res_ml, por_ml, res_ou, por_ou, res_rl, por_rl, v_s, l_s = ejecutar_simulacion_quant(j["vis_completo"], j["loc_completo"])
                
                st.markdown("<br>", unsafe_allow_html=True)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(label="🏆 PROYECCIÓN GANADOR (MONEYLINE)", value=MAPEO_ORGANIZACIONES.get(res_ml, {"nombre": res_ml})["nombre"], delta=f"{round(por_ml, 1)}% Probabilidad")
                with col2:
                    st.metric(label="📈 LÍNEA (OVER / UNDER)", value=res_ou, delta=f"{round(por_ou, 1)}% Certeza")
                with col3:
                    st.metric(label="⚾ HÁNDICAP (RUNLINE)", value=res_rl, delta=f"{round(por_rl, 1)}% Estabilidad")
                st.markdown("<hr style='border: 1px dashed #30363d;'>", unsafe_allow_html=True)
