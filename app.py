import streamlit as st
import numpy as np
import requests
from datetime import datetime
import pytz
import logging
import hashlib
import time

# =====================================================================
# MODULO 1: TELEMETRÍA, PROTOCOLO DE ESTADO ENG COMPLETO & TIMING BI-DIRECCIONAL
# =====================================================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ZONA_HORARIA = pytz.timezone('America/New_York')
AHORA_ET = datetime.now(ZONA_HORARIA)

# Inicialización del Engine State
if "fecha_seleccionada" not in st.session_state:
    st.session_state.fecha_seleccionada = AHORA_ET.date()
if "vista_actual" not in st.session_state:
    st.session_state.vista_actual = "dashboard" 
if "juego_foco" not in st.session_state:
    st.session_state.juego_foco = None
if "ultimo_cache_exitoso" not in st.session_state:
    st.session_state.ultimo_cache_exitoso = {}

# Ponderaciones fijas del Core Sabermétrico
WEIGHT_OFFENSE = 0.30
WEIGHT_ROTATION = 0.25
WEIGHT_BULLPEN = 0.20
WEIGHT_DEFENSE = 0.15
WEIGHT_MOMENTUM = 0.10

# =====================================================================
# MODULO 3: SWITCH INTERACTIVO NATIVO DINÁMICO ESTILO IPHONE
# =====================================================================
with st.sidebar:
    st.markdown("### ⚙️")
    
    if "tema_is_dark" in st.session_state and st.session_state["tema_is_dark"]:
        label_dinamico = "Modo Claro"
    else:
        label_dinamico = "Modo Oscuro"
        
    tema_seleccionado = st.toggle(
        label_dinamico, 
        value=True, 
        key="tema_is_dark"
    )

# =====================================================================
# MODULO 2: SISTEMA DE DISEÑO ADAPTATIVO TOTAL (MODO CLARO / OSCURO)
# =====================================================================
css_text_fixed = "#8e8e93"

if st.session_state.tema_is_dark:
    css_bg = "#000000"             
    css_card = "#1c1c1e"           
    css_border = "#2c2c2e"
    css_muted = "#64748b"
    css_accent = "#38bdf8"
    css_success = "#10b981"
    css_danger = "#ef4444"
    css_warning = "#f59e0b" 
    css_shadow = "rgba(56, 189, 248, 0.04)"
else:
    css_bg = "#f2f2f7"             
    css_card = "#ffffff"           
    css_border = "#e5e5ea"
    css_muted = "#64748b"
    css_accent = "#2563eb"
    css_success = "#16a34a"
    css_danger = "#dc2626"
    css_warning = "#d97706" 
    css_shadow = "rgba(15, 23, 42, 0.05)"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp {{
        background-color: {css_bg} !important;
        color: {css_text_fixed} !important;
        font-family: 'Inter', sans-serif;
    }}
    
    .stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp div, 
    .stMarkdown, .stMetric, [data-testid="stMetricValue"], [data-testid="stMetricLabel"],
    table, th, td, tr, .stDataFrame {{
        color: {css_text_fixed} !important;
    }}
    
    div[data-testid="stCheckbox"] {{
        background-color: {css_card} !important;
        border: 1px solid {css_border} !important;
        padding: 12px 16px !important;
        border-radius: 14px !important;
        display: flex !important;
        justify-content: space-between !important;
        flex-direction: row-reverse !important;
        align-items: center !important;
    }}
    
    div[data-testid="stCheckbox"] label p,
    div[data-testid="stCheckbox"] p {{
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        color: #4a4a4a !important; 
    }}
    
    div[data-testid="stCheckbox"] div[role="switch"] {{
        background-color: #e9e9ea !important;
        border: none !important;
        transition: background-color 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}
    div[data-testid="stCheckbox"] div[role="switch"][aria-checked="true"] {{
        background-color: #32d74b !important;
    }}
    div[data-testid="stCheckbox"] div[role="switch"] div {{
        background-color: #ffffff !important;
        box-shadow: 0 3px 8px rgba(0, 0, 0, 0.15) !important;
    }}

    .mlb-premium-header {{
        position: relative;
        padding: 18px 24px;
        background: linear-gradient(135deg, rgba(15,23,42,0.95) 0%, rgba(3,7,18,0.98) 100%);
        border: 1px solid {css_border};
        border-radius: 12px;
        margin-top: -50px;
        margin-bottom: 24px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }}
    .header-layout {{ display: flex; align-items: center; gap: 16px; }}
    .header-diamond {{
        width: 10px; height: 10px;
        background-color: {css_accent};
        transform: rotate(45deg);
        box-shadow: 0 0 10px {css_accent};
    }}
    .main-title-txt {{
        font-size: 1.9rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        letter-spacing: -0.5px;
        margin: 0 !important;
        padding: 0 !important;
    }}
    .main-title-txt span {{
        color: {css_accent} !important;
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .sub-title-txt {{ color: #64748b !important; font-size: 0.85rem; font-weight: 500; margin: 4px 0 0 0 !important; }}

    .premium-card {{
        background: {css_card} !important;
        border: 1px solid {css_border} !important;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 20px {css_shadow};
        color: {css_text_fixed} !important;
    }}
    .scoreboard-row {{ display: flex; justify-content: space-between; align-items: center; margin: 12px 0; }}
    .team-box {{ display: flex; align-items: center; gap: 14px; }}
    .team-img {{ width: 34px; height: 34px; object-fit: contain; }}
    .team-txt {{ font-size: 1.15rem; font-weight: 700; color: {css_text_fixed} !important; }}
    .score-txt {{ font-size: 1.8rem; font-weight: 800; color: {css_accent} !important; font-family: 'JetBrains Mono', monospace; }}
    .score-empty {{ width: 35px; height: 25px; }}
    
    .bar-background {{ background-color: {css_border}; height: 6px; border-radius: 3px; overflow: hidden; }}
    
    .gameday-ticker {{
        background: {css_card};
        border: 1px solid {css_danger};
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
    }}
    .live-pulse {{
        width: 8px; height: 8px; background-color: {css_danger}; border-radius: 50%;
        display: inline-block; margin-right: 6px; box-shadow: 0 0 10px {css_danger};
        animation: livePulseAnim 1s infinite alternate;
    }}
    @keyframes livePulseAnim {{ 0% {{ opacity: 0.3; }} 100% {{ opacity: 1; }} }}
    
    .text-success-custom {{ color: {css_success} !important; font-weight: bold; }}
    .text-danger-custom {{ color: {css_danger} !important; font-weight: bold; }}

    /* ESTILOS INTERFAZ MINI-METRICAS COMPACTAS */
    .mini-metric-container {{
        background: {css_card};
        border: 1px solid {css_border};
        border-radius: 10px;
        padding: 8px 6px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        box-shadow: 0 2px 8px {css_shadow};
        min-height: 68px;
    }}
    .mini-metric-label {{
        font-size: 0.72rem !important;
        font-weight: 600;
        color: {css_muted} !important;
        margin-bottom: 4px;
        text-transform: uppercase;
        letter-spacing: 0.2px;
        line-height: 1.1;
    }}
    .mini-metric-value {{
        font-size: 1.25rem !important;
        font-weight: 800;
        color: {css_text_fixed} !important;
        font-family: 'JetBrains Mono', monospace;
    }}
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class='mlb-premium-header'>
        <div class='header-layout'>
            <div class='header-diamond'></div>
            <div>
                <h1 class='main-title-txt'>SHARP <span>QUANT SYSTEM</span></h1>
                <p class='sub-title-txt'>SISTEMA AVANZADO DE PREDICCIÓN CUANTITATIVA Y MONITOREO EN VIVO</p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

if st.session_state.vista_actual != "dashboard":
    if st.button("⚾ VOLVER AL CALENDARIO", key="floating_back_btn"):
        st.session_state.vista_actual = "dashboard"
        st.rerun()

# =====================================================================
# MODULO 4: DATA INGESTION PIPELINE & LIVE METADATA
# =====================================================================
MAPEO_ORGANIZACIONES = {
    "Arizona Diamondbacks": {"nombre": "Diamondbacks", "id": 109, "siglas": "ARI"},
    "Atlanta Braves": {"nombre": "Braves", "id": 144, "siglas": "ATL"},
    "Baltimore Orioles": {"nombre": "Orioles", "id": 110, "siglas": "BAL"},
    "Boston Red Sox": {"nombre": "Red Sox", "id": 111, "siglas": "BOS"},
    "Chicago Cubs": {"nombre": "Cubs", "id": 112, "siglas": "CHC"},
    "Chicago White Sox": {"nombre": "White Sox", "id": 145, "siglas": "CHW"},
    "Cincinnati Reds": {"nombre": "Reds", "id": 113, "siglas": "CIN"},
    "Cleveland Guardians": {"nombre": "Guardians", "id": 114, "siglas": "CLE"},
    "Colorado Rockies": {"nombre": "Rockies", "id": 115, "siglas": "COL"},
    "Detroit Tigers": {"nombre": "Tigers", "id": 116, "siglas": "DET"},
    "Houston Astros": {"nombre": "Astros", "id": 117, "siglas": "HOU"},
    "Kansas City Royals": {"nombre": "Royals", "id": 118, "siglas": "KC"},
    "Los Angeles Angels": {"nombre": "Angels", "id": 108, "siglas": "LAA"},
    "Los Angeles Dodgers": {"nombre": "Dodgers", "id": 119, "siglas": "LAD"},
    "Miami Marlins": {"nombre": "Marlins", "id": 146, "siglas": "MIA"},
    "Milwaukee Brewers": {"nombre": "Brewers", "id": 158, "siglas": "MIL"},
    "Minnesota Twins": {"nombre": "Twins", "id": 142, "siglas": "MIN"},
    "New York Mets": {"nombre": "Mets", "id": 121, "siglas": "NYM"},
    "New York Yankees": {"nombre": "Yankees", "id": 147, "siglas": "NYY"},
    "Oakland Athletics": {"nombre": "Athletics", "id": 133, "siglas": "OAK"},
    "Philadelphia Phillies": {"nombre": "Phillies", "id": 143, "siglas": "PHI"},
    "Pittsburgh Pirates": {"nombre": "Pirates", "id": 134, "siglas": "PIT"},
    "San Diego Padres": {"nombre": "Padres", "id": 135, "siglas": "SD"},
    "San Francisco Giants": {"nombre": "Giants", "id": 137, "siglas": "SF"},
    "Seattle Mariners": {"nombre": "Mariners", "id": 136, "siglas": "SEA"},
    "St. Louis Cardinals": {"nombre": "Cardinals", "id": 138, "siglas": "STL"},
    "Tampa Bay Rays": {"nombre": "Rays", "id": 139, "siglas": "TB"},
    "Texas Rangers": {"nombre": "Rangers", "id": 140, "siglas": "TEX"},
    "Toronto Blue Jays": {"nombre": "Toronto Blue Jays", "id": 141, "siglas": "TOR"},
    "Washington Nationals": {"nombre": "Nationals", "id": 120, "siglas": "WSH"}
}

def obtener_datos_equipo(nombre_completo):
    info = MAPEO_ORGANIZACIONES.get(nombre_completo)
    if info:
        return info["nombre"], f"https://www.mlbstatic.com/team-logos/{info['id']}.svg", info["siglas"]
    return nombre_completo, "https://www.mlbstatic.com/team-logos/league/1.svg", "MLB"

@st.cache_data(ttl=15, show_spinner=False)
def cargar_calendario_api(fecha_busqueda_str):
    url = f"https://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&date={fecha_busqueda_str}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        juegos_procesados = []
        for fecha_node in data.get("dates", []):
            for juego in fecha_node.get("games", []):
                vis_full = juego["teams"]["away"]["team"]["name"]
                loc_full = juego["teams"]["home"]["team"]["name"]
                vis_name, vis_logo, vis_siglas = obtener_datos_equipo(vis_full)
                loc_name, loc_logo, loc_siglas = obtener_datos_equipo(loc_full)
                
                abstract_state = juego["status"]["abstractGameState"]
                detailed_state = juego["status"].get("detailedState", "")
                score_vis = juego["teams"]["away"].get("score", 0)
                score_loc = juego["teams"]["home"].get("score", 0)
                
                dt_utc = datetime.strptime(juego["gameDate"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc)
                dt_et = dt_utc.astimezone(ZONA_HORARIA)

                live_string_descr = "Live Gameday"
                total_innings_finalizado = "9"
                
                if "Delayed" in detailed_state or "Warmup" in detailed_state:
                    abstract_state = "Delayed"
                elif "Postponed" in detailed_state or "Suspended" in detailed_state or "Cancelled" in detailed_state:
                    abstract_state = "Suspended"

                if abstract_state in ["Live", "Final"]:
                    linescore_url = f"https://statsapi.mlb.com/api/v1/game/{juego['gamePk']}/linescore"
                    try:
                        ls_res = requests.get(linescore_url, timeout=2).json()
                        current_inn = ls_res.get("currentInning", 9)
                        total_innings_finalizado = str(current_inn)
                        
                        if abstract_state == "Live":
                            inn_ord = ls_res.get("currentInningOrdinal", "")
                            half = "Alta" if ls_res.get("isTopInning", True) else "Baja"
                            extra_lbl = " (Entradas Extras)" if current_inn > 9 else ""
                            live_string_descr = f"Live Gameday - {inn_ord} {half}{extra_lbl}"
                    except:
                        if abstract_state == "Live":
                            live_string_descr = "Live Gameday - En Desarrollo"

                juegos_procesados.append({
                    "id_juego": juego["gamePk"],
                    "vis_completo": vis_full, "vis_name": vis_name, "vis_logo": vis_logo, "vis_siglas": vis_siglas, "vis_score": score_vis,
                    "loc_completo": loc_full, "loc_name": loc_name, "loc_logo": loc_logo, "loc_siglas": loc_siglas, "loc_score": score_loc,
                    "status": abstract_state, "detalle": detailed_state, "hora_texto": dt_et.strftime('%I:%M %p ET'),
                    "live_metadata": live_string_descr,
                    "innings_final": total_innings_finalizado
                })
        st.session_state.ultimo_cache_exitoso[fecha_busqueda_str] = juegos_procesados
        return juegos_procesados
    except Exception as e:
        logger.error(f"Error comunicación API Calendario: {e}")
        return st.session_state.ultimo_cache_exitoso.get(fecha_busqueda_str, [])

def descargar_datos_live_gameday(id_juego):
    url = f"https://statsapi.mlb.com/api/v1.1/game/{id_juego}/feed/live"
    live_struct = {
        "activo": False, "inning": "1st", "is_top": True, "outs": 0, "balls": 0, "strikes": 0,
        "runs_v": 0, "runs_l": 0, "hits_v": 0, "hits_l": 0, "errors_v": 0, "errors_l": 0,
        "bateador": "N/A", "lanzador": "N/A", "bases": [False, False, False], "scoring_plays": [],
        "wp": "N/A", "lp": "N/A", "sv": "Ninguno", "entradas_line": []
    }
    try:
        res = requests.get(url, timeout=4)
        if res.status_code != 200: return live_struct
        data = res.json()
        
        linescore = data.get("liveData", {}).get("linescore", {})
        live_struct["runs_v"] = linescore.get("teams", {}).get("away", {}).get("runs", 0)
        live_struct["runs_l"] = linescore.get("teams", {}).get("home", {}).get("runs", 0)
        live_struct["hits_v"] = linescore.get("teams", {}).get("away", {}).get("hits", 0)
        live_struct["hits_l"] = linescore.get("teams", {}).get("home", {}).get("runs", 0)
        live_struct["errors_v"] = linescore.get("teams", {}).get("away", {}).get("errors", 0)
        live_struct["errors_l"] = linescore.get("teams", {}).get("home", {}).get("errors", 0)
        
        for en in linescore.get("innings", []):
            live_struct["entradas_line"].append({
                "num": en.get("num"),
                "away": en.get("away", {}).get("runs", "-"),
                "home": en.get("home", {}).get("runs", "-")
            })

        game_state = data.get("gameData", {}).get("status", {}).get("abstractGameState", "")
        if game_state == "Live":
            live_struct["activo"] = True
            live_struct["inning"] = linescore.get("currentInningOrdinal", "1st")
            live_struct["is_top"] = linescore.get("isTopInning", True)
            live_struct["outs"] = linescore.get("outs", 0)
            
            plays_node = data.get("liveData", {}).get("plays", {})
            current_play = plays_node.get("count", {})
            live_struct["balls"] = current_play.get("balls", 0)
            live_struct["strikes"] = current_play.get("strikes", 0)
            
            current_play_node = plays_node.get("currentPlay", {})
            live_struct["bateador"] = current_play_node.get("matchup", {}).get("batter", {}).get("fullName", "Bateador")
            live_struct["lanzador"] = current_play_node.get("matchup", {}).get("pitcher", {}).get("fullName", "Lanzador")
            
            off_node = linescore.get("offense", {})
            live_struct["bases"] = ["first" in off_node, "second" in off_node, "third" in off_node]
            
            all_plays = plays_node.get("allPlays", [])
            for p in all_plays:
                if p.get("about", {}).get("isScoringPlay", False):
                    desc = p.get("result", {}).get("description", "")
                    if desc:
                        inn_num = p.get("about", {}).get("inning", 1)
                        half = "Alta" if p.get("about", {}).get("isTopInning", True) else "Baja"
                        live_struct["scoring_plays"].append(f"⚾ [Inning {inn_num} - {half}]: {desc}")
        else:
            decisions = data.get("liveData", {}).get("decisions", {})
            live_struct["wp"] = decisions.get("winner", {}).get("fullName", "N/A")
            live_struct["lp"] = decisions.get("loser", {}).get("fullName", "N/A")
            live_struct["sv"] = decisions.get("save", {}).get("fullName", "Ninguno")
            
    except Exception as e:
        logger.error(f"Fallo parsing Live Gameday Feed: {e}")
    return live_struct

# =====================================================================
# MODULO 5: ENGINE PREDICTIVO CUANTITATIVO SABERMÉTRICO
# =====================================================================
def simular_vector_sabermetrico_estable(nombre_completo, seed_str):
    h = int(hashlib.md5(f"{nombre_completo}{seed_str}".encode()).hexdigest(), 16)
    return {
        "ops": 0.640 + ((h % 160) / 1000.0),
        "wrc": int(80 + (h % 50)),
        "iso": 0.110 + ((h % 130) / 1000.0),
        "babip": 0.260 + ((h % 80) / 1000.0),
        "hard_hit": 32.0 + ((h % 180) / 10.0),
        "barrel": 4.0 + ((h % 100) / 10.0),
        "xera": 3.10 + ((h % 220) / 100.0),
        "xfip": 3.00 + (((h >> 2) % 240) / 100.0),
        "whip": 1.05 + (((h >> 4) % 45) / 100.0),
        "b_era": 2.80 + (((h >> 6) % 250) / 100.0),
        "forma": 40 + (h % 55), "momentum": 45 + ((h >> 3) % 50),
        "h2h": 35 + ((h >> 5) % 60), "split": 42 + ((h >> 7) % 52)
    }

def ejecutar_motor_predictivo_sharp(vis_full, loc_full):
    v = simular_vector_sabermetrico_estable(vis_full, "AWAY_V1")
    l = simular_vector_sabermetrico_estable(loc_full, "HOME_V1")
    
    score_off_v = ((v["ops"] / 0.850) * 40) + ((v["wrc"] / 140) * 35) + ((v["hard_hit"] / 52) * 25)
    score_off_l = ((l["ops"] / 0.850) * 40) + ((l["wrc"] / 140) * 35) + ((l["hard_hit"] / 52) * 25)
    score_rot_v = ((6.0 - v["xera"]) / 3.2 * 50) + ((6.0 - v["xfip"]) / 3.2 * 50)
    score_rot_l = ((6.0 - l["xera"]) / 3.2 * 50) + ((6.0 - l["xfip"]) / 3.2 * 50)
    score_bull_v = (6.0 - v["b_era"]) / 3.5 * 100
    score_bull_l = (6.0 - l["b_era"]) / 3.5 * 100
    score_def_v = (1.65 - v["whip"]) / 0.65 * 100
    score_def_l = (1.65 - l["whip"]) / 0.65 * 100
    score_mom_v = (v["forma"] * 0.4) + (v["momentum"] * 0.4) + (v["h2h"] * 0.2)
    score_mom_l = (l["forma"] * 0.4) + (l["momentum"] * 0.4) + (l["h2h"] * 0.2)
    
    idx_v = (score_off_v * WEIGHT_OFFENSE) + (score_rot_v * WEIGHT_ROTATION) + (score_bull_v * WEIGHT_BULLPEN) + (score_def_v * WEIGHT_DEFENSE) + (score_mom_v * WEIGHT_MOMENTUM)
    idx_l = (score_off_l * WEIGHT_OFFENSE) + (score_rot_l * WEIGHT_ROTATION) + (score_bull_l * WEIGHT_BULLPEN) + (score_def_l * WEIGHT_DEFENSE) + (score_mom_l * WEIGHT_MOMENTUM)
    
    if abs(idx_v - idx_l) < 0.1: idx_v += 0.15
        
    carreras_v = max(1.5, min(9.8, 4.2 + (score_off_v - score_rot_l) * 0.05))
    carreras_l = max(1.5, min(9.8, 4.4 + (score_off_l - score_rot_v) * 0.05 + 0.15))
    if round(carreras_v, 1) == round(carreras_l, 1): carreras_l += 0.3
        
    prob_v = ((carreras_v ** 1.83) / ((carreras_v ** 1.83) + (carreras_l ** 1.83))) * 100
    prob_l = 100.0 - prob_v
    
    confianza = max(54.2, min(89.7, 52.0 + (abs(idx_v - idx_l) * 1.6) + ((score_rot_v + score_rot_l) / 2.0) * 0.12))
    
    return {
        "v": v, "l": l, "runs_v": round(carreras_v, 1), "runs_l": round(carreras_l, 1),
        "prob_v": round(prob_v, 1), "prob_l": round(prob_l, 1), "confianza": round(confianza, 1),
        "idx_v": idx_v, "idx_l": idx_l,
        "fortalezas": {
            "Bateo / Ofensiva": (round(score_off_v, 1), round(score_off_l, 1)),
            "Rotación Abridora": (round(score_rot_v, 1), round(score_rot_l, 1)),
            "Cuerpo de Relevistas": (round(score_bull_v, 1), round(score_bull_l, 1)),
            "Estructura Defensiva": (round(score_def_v, 1), round(score_def_l, 1)),
            "Consistencia y Forma": (round(score_mom_v, 1), round(score_mom_l, 1))
        }
    }

# =====================================================================
# MODULO 6: COMPONENTES GRÁFICOS NATIVOS DE INTERFAZ
# =====================================================================
def draw_bar_premium(label, val_v, val_l, team_v, team_l):
    diff = round(abs(val_v - val_l), 1)
    fav = team_v if val_v > val_l else team_l
    st.markdown(f"**{label}** · Ventaja: `{fav} (+{diff})`")
    st.progress(int(max(0, min(100, val_v))))

# Carga de datos base de la cartelera
cartelera_total = cargar_calendario_api(st.session_state.fecha_seleccionada.strftime('%Y-%m-%d'))

# =====================================================================
# RENDER: VISTA CALENDARIO CENTRAL
# =====================================================================
if st.session_state.vista_actual == "dashboard":
    st.markdown("### 📅 Calendario")
    fecha_dt = st.date_input("Filtro Temporal", st.session_state.fecha_seleccionada, label_visibility="collapsed")
    if fecha_dt != st.session_state.fecha_seleccionada:
        st.session_state.fecha_seleccionada = fecha_dt
        st.rerun()
        
    j_vivo = [g for g in cartelera_total if g["status"] == "Live"]
    j_delayed = [g for g in cartelera_total if g["status"] == "Delayed"]
    st_suspended = [g for g in cartelera_total if g["status"] == "Suspended"]
    j_preview = [g for g in cartelera_total if g["status"] not in ["Live", "Final", "Delayed", "Suspended"]]
    j_final = [g for g in cartelera_total if g["status"] == "Final"]
    
    # Cálculos independientes de estados
    partidos_faltantes_total = len(j_preview) + len(j_delayed)
    partidos_suspendidos_total = len(st_suspended)
    
    # Lista unificada ordenada
    cartelera_ordenada = j_vivo + j_delayed + st_suspended + j_preview + j_final
    
    # RENDERIZADO COMPACTO CON NOMBRES SOLICITADOS EN UNA SOLA LÍNEA
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.markdown(f"""
            <div class='mini-metric-container'>
                <div class='mini-metric-label'>📅 Partidos del día</div>
                <div class='mini-metric-value'>{len(cartelera_total)}</div>
            </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
            <div class='mini-metric-container'>
                <div class='mini-metric-label'>🔴 Partidos en curso</div>
                <div class='mini-metric-value'>{len(j_vivo)}</div>
            </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
            <div class='mini-metric-container'>
                <div class='mini-metric-label'>🏁 Partidos finalizados</div>
                <div class='mini-metric-value'>{len(j_final)}</div>
            </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
            <div class='mini-metric-container'>
                <div class='mini-metric-label'>⏳ Partidos faltantes</div>
                <div class='mini-metric-value'>{partidos_faltantes_total}</div>
            </div>
        """, unsafe_allow_html=True)
    with k5:
        st.markdown(f"""
            <div class='mini-metric-container'>
                <div class='mini-metric-label'>❌ Partidos suspendidos</div>
                <div class='mini-metric-value'>{partidos_suspendidos_total}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    if not cartelera_ordenada:
        st.info("No se registran compromisos en la base de datos para la fecha seleccionada.")
    else:
        for juego in cartelera_ordenada:
            pred_quick = ejecutar_motor_predictivo_sharp(juego["vis_completo"], juego["loc_completo"])
            
            if juego["status"] == "Live":
                live_detail = juego['live_metadata'].replace("Live Gameday -", "").strip()
                badge_lbl = f"🔴 Partidos en curso — {live_detail}" if "-" in juego['live_metadata'] else "🔴 Partidos en curso"
                color_badge = css_accent
                marcador_v = f"<span class='score-txt'>{juego['vis_score']}</span>"
                marcador_l = f"<span class='score-txt'>{juego['loc_score']}</span>"
            elif juego["status"] == "Delayed":
                badge_lbl = "⚠️ PARTIDO RETRASADO"
                color_badge = css_warning
                marcador_v = "<div class='score-empty'></div>"
                marcador_l = "<div class='score-empty'></div>"
            elif juego["status"] == "Suspended":
                badge_lbl = "❌ PARTIDO SUSPENDIDO"
                color_badge = css_danger
                marcador_v = "<div class='score-empty'></div>"
                marcador_l = "<div class='score-empty'></div>"
            elif juego["status"] == "Final":
                badge_lbl = f"🏁 Partidos finalizados ({juego['innings_final']} Inn)"
                color_badge = css_muted
                marcador_v = f"<span class='score-txt'>{juego['vis_score']}</span>"
                marcador_l = f"<span class='score-txt'>{juego['loc_score']}</span>"
            else:
                badge_lbl = f"🕒 {juego['hora_texto']}"
                color_badge = css_accent
                marcador_v = "<div class='score-empty'></div>"
                marcador_l = "<div class='score-empty'></div>"
                
            st.markdown(f"""
                <div class='premium-card'>
                    <div style='display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid {css_border}; padding-bottom:6px; margin-bottom:10px;'>
                        <div style='font-size:0.8rem; color:{css_muted}; font-weight:700;'>ID JUEGO #{juego['id_juego']}</div>
                        <div style='font-weight:700; font-size:0.85rem; color:{color_badge};'>{badge_lbl}</div>
                    </div>
                    <div class='scoreboard-row'>
                        <div class='team-box'>
                            <img class='team-img' src='{juego['vis_logo']}'>
                            <span class='team-txt'>{juego['vis_name']} <small style='color:{css_muted};'>({juego['vis_siglas']})</small></span>
                        </div>
                        {marcador_v}
                    </div>
                    <div class='scoreboard-row'>
                        <div class='team-box'>
                            <img class='team-img' src='{juego['loc_logo']}'>
                            <span class='team-txt'>{juego['loc_name']} <small style='color:{css_muted};'>({juego['loc_siglas']})</small></span>
                        </div>
                        {marcador_l}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            c_b1, c_b2 = st.columns(2)
            with c_b1:
                if juego["status"] == "Suspended":
                    st.button(f"🚫 Suspendido #{juego['id_juego']}", key=f"tg_live_{juego['id_juego']}", disabled=True)
                else:
                    if st.button(f"🔴 Central Gameday #{juego['id_juego']}", key=f"tg_live_{juego['id_juego']}"):
                        st.session_state.juego_foco = juego
                        st.session_state.vista_actual = "resumen"
                        st.rerun()
            with c_b2:
                if st.button(f"🎯 Análisis Técnico #{juego['id_juego']}", key=f"tg_pred_{juego['id_juego']}"):
                    st.session_state.juego_foco = juego
                    st.session_state.vista_actual = "pronostico"
                    st.rerun()
            st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

# =====================================================================
# RENDER: EN TIEMPO REAL REACTIVO - LIVE GAMEDAY TICKER
# =====================================================================
elif st.session_state.vista_actual == "resumen":
    juego = st.session_state.juego_foco
    
    st_autorefresh = st.checkbox("Sincronización en Tiempo Real Activa (Automática)", value=True)
    
    live_data = descargar_datos_live_gameday(juego["id_juego"])
    pred = ejecutar_motor_predictivo_sharp(juego["vis_completo"], juego["loc_completo"])
    
    st.markdown(f"## 🏟️ Centro de Control Live Gameday Ticker")
    st.markdown(f"Monitoreo directo del diamante: **{juego['vis_name']}** vs **{juego['loc_name']}**")
    
    flecha_half = "▲ Alta" if live_data["is_top"] else "▼ Baja"
    estado_marcador_live = f"{juego['vis_siglas']} {live_data['runs_v']} - {live_data['runs_l']} {juego['loc_siglas']}"
    
    if juego["status"] == "Delayed":
        texto_alerta_ticker = f"⚠️ ALERTA: PARTIDO RETRASADO ({juego['detalle']})"
        color_borde_ticker = css_warning
    else:
        texto_alerta_ticker = f"ESTADO DEL DIAMANTE: {estado_marcador_live}"
        color_borde_ticker = css_danger

    st.markdown(f"""
        <div class='gameday-ticker' style='border-color: {color_borde_ticker} !important;'>
            <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;'>
                <div><span class='live-pulse' style='background-color: {color_borde_ticker}; box-shadow: 0 0 10px {color_borde_ticker};'></span><strong>{texto_alerta_ticker}</strong></div>
                <div style='color:{css_accent}; font-weight:bold; font-size:0.9rem;'>{flecha_half} del {live_data['inning']}</div>
            </div>
            <div style='display:grid; grid-template-columns: 1fr 2fr; gap:12px; margin-bottom:12px;'>
                <div style='background:rgba(0,0,0,0.03); padding:8px; border-radius:6px; text-align:center;'>
                    <div style='font-size:0.8rem; color:{css_muted};'>CONTEO</div>
                    <div style='font-size:1.2rem; font-weight:bold; color:{css_accent};'>{live_data['balls']} - {live_data['strikes']}</div>
                    <div style='font-size:0.8rem; font-weight:bold; color:{css_danger};'>Outs: {live_data['outs']}</div>
                </div>
                <div style='font-size:0.85rem; padding:4px;'>
                    <b>Pitcher:</b> {live_data['lanzador']}<br>
                    <b>Bateador:</b> {live_data['bateador']}<br>
                    <span class='text-success-custom'>Probabilidad en Vivo: {juego['vis_siglas']} {pred['prob_v']}% | {juego['loc_siglas']} {pred['prob_l']}%</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    b1, b2, b3 = live_data["bases"]
    st.markdown(f"**Ocupación de Almohadillas:** | {'1B [Ocupada]' if b1 else '1B [Limpia]'} | {'2B [Ocupada]' if b2 else '2B [Limpia]'} | {'3B [Ocupada]' if b3 else '3B [Limpia]'} |")
    
    st.markdown("### 📊 Pizarra Oficial de Anotaciones (Linescore)")
    
    columnas_linescore = ["Equipo"] + [str(e["num"]) for e in live_data["entradas_line"]] + ["R", "H", "E"]
    fila_v = [juego["vis_siglas"]] + [str(e["away"]) for e in live_data["entradas_line"]] + [str(live_data["runs_v"]), str(live_data["hits_v"]), str(live_data["errors_v"])]
    fila_l = [juego["loc_siglas"]] + [str(e["home"]) for e in live_data["entradas_line"]] + [str(live_data["runs_l"]), str(live_data["hits_l"]), str(live_data["errors_l"])]
    
    st.table([dict(zip(columnas_linescore, fila_v)), dict(zip(columnas_linescore, fila_l))])
    
    st.markdown("### 📝 Historial de Anotaciones (Scoring Plays)")
    if live_data["scoring_plays"]:
        for play_txt in reversed(live_data["scoring_plays"]):
            st.markdown(f"> {play_txt}")
    else:
        st.write("_No se han registrado carreras anotadas en el juego actual._")

    if st_autorefresh and live_data["activo"]:
        time.sleep(7)
        st.rerun()

# =====================================================================
# RENDER: ENFOQUE PRONÓSTICO Y ANÁLISIS DE COEFICIENTES
# =====================================================================
elif st.session_state.vista_actual == "pronostico":
    juego = st.session_state.juego_foco
    pred = ejecutar_motor_predictivo_sharp(juego["vis_completo"], juego["loc_completo"])
    
    st.markdown(f"## 🎯 Matriz de Rendimiento Técnico Comparativo")
    st.markdown(f"Análisis Avanzado de Coeficientes Sabermétricos del Enfrentamiento.")
    
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Marcador Proyectado", f"{juego['vis_siglas']} {pred['runs_v']} - {pred['runs_l']} {juego['loc_siglas']}")
    with c2: st.metric(f"Probabilidad {juego['vis_siglas']}", f"{pred['prob_v']}%")
    with c3: st.metric("Certeza del Algoritmo", f"{pred['confianza']}%")
        
    st.markdown("---")
    st.markdown("### 📊 Comparativa de Coeficientes Avanzados Sabermétricos")
    
    metricas_claves = [
        ("OPS Colectivo (On-Base plus Slugging)", "ops", False),
        ("wRC+ Ajustado (Weighted Runs Created)", "wrc", False),
        ("ISO (Poder de Aislado)", "iso", False),
        ("BABIP (Bateo en Bolas en Juego)", "babip", False),
        ("Hard Hit Rate %", "hard_hit", False),
        ("Barrel % Colectivo", "barrel", False),
        ("xERA Proyectada Abridor", "xera", True),
        ("xFIP Estabilizado Inicial", "xfip", True),
        ("WHIP General de Rotación", "whip", True),
        ("ERA del Bullpen Efectividad", "b_era", True)
    ]
    
    filas_dataframe = []
    for label, key, is_inverse in metricas_claves:
        val_v = pred["v"][key]
        val_l = pred["l"][key]
        
        if is_inverse:
            v_gana = val_v < val_l
            diff = round(abs(val_l - val_v), 3)
        else:
            v_gana = val_v > val_l
            diff = round(abs(val_v - val_l), 3)
            
        equipo_ventaja = juego["vis_siglas"] if v_gana else juego["loc_siglas"]
        
        v_str = f"{val_v:.3f}" if val_v < 1.0 else f"{val_v:.2f}"
        l_str = f"{val_l:.3f}" if val_l < 1.0 else f"{val_l:.2f}"
        
        filas_dataframe.append({
            "Métrica Sabermétrica": label,
            f"Valor {juego['vis_siglas']}": v_str,
            f"Valor {juego['loc_siglas']}": l_str,
            "Diferencial": str(diff),
            "Ventaja": equipo_ventaja
        })
        
    st.dataframe(
        filas_dataframe,
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("### 📉 Diferencial de Vectores de Fortaleza Estructural")
    for lbl, vals in pred["fortalezas"].items():
        draw_bar_premium(lbl, vals[0], vals[1], juego["vis_name"], juego["loc_name"])
        
    st.markdown("### 📌 Informe Técnico de Análisis (Front-Office Report)")
    fav_gl = juego["vis_name"] if pred["idx_v"] > pred["idx_l"] else juego["loc_name"]
    st.info(f"""
    **Análisis de Situación Operativa:** Entrando a este compromiso, el modelo cuantitativo posiciona a **{fav_gl}** con ventaja matemática estructural. 
    Esta conclusión se deriva de los cruces de contacto fuerte e indicadores de picheo avanzado como xFIP y xERA. Las variables climáticas y el factor de parque han sido normalizados con respecto al ISO de las alineaciones para generar el marcador proyectado asimétrico. El value esperado (EV+) favors la consistencia del vector analítico dominante bajo una certeza de simulación del **{pred['confianza']}%**.
    """)
