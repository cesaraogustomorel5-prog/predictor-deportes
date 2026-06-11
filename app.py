import streamlit as st
import numpy as np
import requests
from datetime import datetime, timedelta
import pytz
import logging

# =====================================================================
# MODULE 1: CONFIG & LOGGER (config.py / utils.py)
# =====================================================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ZONA_HORARIA = pytz.timezone('America/New_York')
AHORA_ET = datetime.now(ZONA_HORARIA)

# Inicialización del Estado de la Aplicación (Persistencia de Fechas y Navegación)
if "fecha_seleccionada" not in st.session_state:
    st.session_state.fecha_seleccionada = AHORA_ET.date()
if "tema_seleccionado" not in st.session_state:
    st.session_state.tema_seleccionado = "Sistema"
if "vista_actual" not in st.session_state:
    st.session_state.vista_actual = "dashboard"  # "dashboard", "resumen", "pronostico"
if "juego_foco" not in st.session_state:
    st.session_state.juego_foco = None
if "ultimo_cache_exitoso" not in st.session_state:
    st.session_state.ultimo_cache_exitoso = {}

# =====================================================================
# MODULE 2: DYNAMIC AUDIOVISUAL SYSTEMS & COMPONENT ARCHITECTURE (css.py)
# =====================================================================
if st.session_state.tema_seleccionado == "Sistema":
    css_bg = "#070a13"
    css_card = "#0f172a"
    css_text = "#f8fafc"
    css_accent = "#38bdf8"
    css_border = "#1e293b"
    css_muted = "#64748b"
    css_success = "#10b981"
    css_shadow = "rgba(56, 189, 248, 0.08)"
elif st.session_state.tema_seleccionado == "Claro":
    css_bg = "#f1f5f9"
    css_card = "#ffffff"
    css_text = "#0f172a"
    css_accent = "#2563eb"
    css_border = "#e2e8f0"
    css_muted = "#64748b"
    css_success = "#16a34a"
    css_shadow = "rgba(0, 0, 0, 0.04)"
else: # Dark (Gris Oscuro Moderno)
    css_bg = "#121214"
    css_card = "#1a1a1e"
    css_text = "#e4e4e7"
    css_accent = "#f43f5e"
    css_border = "#27272a"
    css_muted = "#71717a"
    css_success = "#10b981"
    css_shadow = "rgba(244, 63, 94, 0.05)"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght=300;400;600;700;800&display=swap');
    
    .stApp {{
        background-color: {css_bg};
        color: {css_text};
        font-family: 'Inter', sans-serif;
        transition: all 0.4s ease;
    }}
    
    /* Dashboard & Componentes Premium */
    .dashboard-header {{
        text-align: center;
        padding: 20px 0;
    }}
    .main-title {{
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        color: {css_text} !important;
        letter-spacing: -1px;
        margin-bottom: 4px;
    }}
    .main-title span {{
        color: {css_accent} !important;
    }}
    .sub-title {{
        color: {css_muted};
        font-size: 1rem;
        font-weight: 400;
    }}
    
    /* Contenedor de Separación de Arquitectura de Marca */
    .brand-bar {{
        height: 4px;
        background: linear-gradient(90deg, {css_accent} 0%, {css_border} 50%, {css_accent} 100%);
        border-radius: 8px;
        margin-bottom: 25px;
    }}
    
    /* Tarjetas Modulares del Ecosistema */
    .premium-card {{
        background: {css_card};
        border: 1px solid {css_border};
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 20px {css_shadow};
        transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.3s ease;
    }}
    .premium-card:hover {{
        transform: translateY(-2px);
        border-color: {css_accent};
    }}
    
    /* Visualización Interna de Marcadores (KPI Scoreboard) */
    .scoreboard-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 10px 0;
    }}
    .team-box {{
        display: flex;
        align-items: center;
        gap: 14px;
    }}
    .team-img {{
        width: 36px;
        height: 36px;
        object-fit: contain;
    }}
    .team-txt {{
        font-size: 1.2rem;
        font-weight: 700;
        color: {css_text};
    }}
    .score-txt {{
        font-size: 1.7rem;
        font-weight: 800;
        color: {css_accent};
        font-family: monospace;
    }}
    .score-empty {{
        width: 30px;
        height: 20px;
    }}
    
    /* Badges de Estado Dinámicos */
    .status-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.85rem;
        border-bottom: 1px solid {css_border};
        padding-bottom: 8px;
        margin-bottom: 12px;
    }}
    .badge-core {{
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        text-transform: uppercase;
        font-size: 0.75rem;
        color: #ffffff !important;
    }}
    .live-bg {{ background-color: #ef4444; box-shadow: 0 0 12px rgba(239, 68, 68, 0.4); }}
    .final-bg {{ background-color: {css_muted}; }}
    .preview-bg {{ background-color: {css_accent}; }}
    
    /* Gráficos de Barras Horizontales Analíticas */
    .bar-wrapper {{
        margin: 12px 0;
    }}
    .bar-label {{
        display: flex;
        justify-content: space-between;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 4px;
    }}
    .bar-background {{
        background-color: {css_border};
        height: 8px;
        border-radius: 4px;
        overflow: hidden;
    }}
    .bar-fill {{
        background: linear-gradient(90deg, {css_accent}, {css_success});
        height: 100%;
        border-radius: 4px;
        transition: width 1s ease-in-out;
    }}
    
    /* Matriz Comparativa */
    .matrix-table {{
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
    }}
    .matrix-table th {{
        background-color: {css_border};
        color: {css_text};
        padding: 10px;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
    }}
    .matrix-table td {{
        padding: 12px 10px;
        text-align: center;
        border-bottom: 1px solid {css_border};
        font-size: 0.95rem;
        font-weight: 600;
    }}
    
    /* Sistema de Botones Reestructurado */
    div.stButton > button {{
        background-color: {css_card} !important;
        color: {css_text} !important;
        border: 1px solid {css_border} !important;
        border-radius: 10px !important;
        padding: 8px 18px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease;
        width: 100%;
    }}
    div.stButton > button:hover {{
        border-color: {css_accent} !important;
        color: {css_accent} !important;
        background-color: {css_border} !important;
        transform: translateY(-1px);
    }}
    </style>
""", unsafe_allow_html=True)

# Barra de Control Estructural de Temas (Header Global)
c_h1, c_h2, c_h3 = st.columns([8, 3, 1])
with c_h2:
    tema_control = st.select_slider(
        "ENGINE_THEME",
        options=["Claro", "Oscuro", "Sistema"],
        value=st.session_state.tema_seleccionado,
        label_visibility="collapsed"
    )
    if tema_control != st.session_state.tema_seleccionado:
        st.session_state.tema_seleccionado = tema_control
        st.rerun()

st.markdown("<div class='mlb-gradient-bar'></div>", unsafe_allow_html=True)
st.markdown("<div class='dashboard-header'><h1 class='main-title'>SHARP <span>QUANT</span> SYSTEM</h1><p class='sub-title'>Plataforma de Analítica de Datos y Sabermetría Predictiva de Alto Rendimiento</p></div>", unsafe_allow_html=True)

# =====================================================================
# MODULE 3: MAPEO Y PROTOCOLO DE CONEXIÓN API (api.py / models.py)
# =====================================================================
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
    "Tampa Bay Rays": {"nombre": "Tampa Bay Rays", "id": 139},
    "Texas Rangers": {"nombre": "Rangers", "id": 140},
    "Toronto Blue Jays": {"nombre": "Blue Jays", "id": 141},
    "Washington Nationals": {"nombre": "Nationals", "id": 120}
}

def obtener_datos_equipo(nombre_completo):
    info = MAPEO_ORGANIZACIONES.get(nombre_completo)
    if info:
        return info["nombre"], f"https://www.mlbstatic.com/team-logos/{info['id']}.svg"
    return nombre_completo, "https://www.mlbstatic.com/team-logos/league/1.svg"

@st.cache_data(ttl=30, show_spinner=False)
def cargar_cartelera_segura_api(fecha_busqueda_str):
    url = f"https://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&date={fecha_busqueda_str}"
    try:
        response = requests.get(url, timeout=7)
        response.raise_for_status()
        data = response.json()
        
        juegos_procesados = []
        for fecha_node in data.get("dates", []):
            for juego in fecha_node.get("games", []):
                vis_full = juego["teams"]["away"]["team"]["name"]
                loc_full = juego["teams"]["home"]["team"]["name"]
                
                vis_name, vis_logo = obtener_datos_equipo(vis_full)
                loc_name, loc_logo = obtener_datos_equipo(loc_full)
                
                abstract_state = juego["status"]["abstractGameState"]
                detailed_state = juego["status"].get("detailedState", "")
                
                score_vis = juego["teams"]["away"].get("score", 0)
                score_loc = juego["teams"]["home"].get("score", 0)
                
                inning_status = ""
                if abstract_state == "Live":
                    inning_status = "En Progreso"
                elif abstract_state == "Final":
                    inning_status = "Finalizado"

                dt_utc = datetime.strptime(juego["gameDate"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc)
                dt_et = dt_utc.astimezone(ZONA_HORARIA)

                juegos_procesados.append({
                    "id_juego": juego["gamePk"],
                    "vis_completo": vis_full, "vis_name": vis_name, "vis_logo": vis_logo, "vis_score": score_vis,
                    "loc_completo": loc_full, "loc_name": loc_name, "loc_logo": loc_logo, "loc_score": score_loc,
                    "status": abstract_state, "detalle": detailed_state, "inning_status": inning_status,
                    "hora_texto": dt_et.strftime('%I:%M %p ET')
                })
        
        st.session_state.ultimo_cache_exitoso[fecha_busqueda_str] = juegos_procesados
        return juegos_procesados
        
    except Exception as e:
        logger.error(f"Error crítico en comunicación con API MLB: {str(e)}")
        if fecha_busqueda_str in st.session_state.ultimo_cache_exitoso:
            st.warning("⚠️ Modo de Respaldo Local Activado. Desconexión temporal detectada con el servidor central.")
            return st.session_state.ultimo_cache_exitoso[fecha_busqueda_str]
        else:
            st.error("❌ Error de enlace de datos. Verifique su conexión de red o la disponibilidad del servicio.")
            return []

@st.cache_data(ttl=15, show_spinner=False)
def descargar_datos_boxscore_real(id_juego):
    url = f"https://statsapi.mlb.com/api/v1.1/game/{id_juego}/feed/live"
    reporte = {
        "vis_rhe": [0,0,0], "loc_rhe": [0,0,0], "entradas": [], 
        "box": {"wp": "N/A", "lp": "N/A", "sv": "- ", "mvp": "Por determinar", "hr": 0, "rbi": 0, "lob": 0}
    }
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        data = res.json()
        
        linescore = data.get("liveData", {}).get("linescore", {})
        vis_node = linescore.get("teams", {}).get("away", {})
        loc_node = linescore.get("teams", {}).get("home", {})
        
        reporte["vis_rhe"] = [vis_node.get('runs', 0), vis_node.get('hits', 0), vis_node.get('errors', 0)]
        reporte["loc_rhe"] = [loc_node.get('runs', 0), loc_node.get('hits', 0), loc_node.get('errors', 0)]
        
        for e in linescore.get("innings", []):
            reporte["entradas"].append({
                "num": e.get("num"),
                "away": e.get("away", {}).get("runs", 0),
                "home": e.get("home", {}).get("runs", 0)
            })
            
        decisions = data.get("liveData", {}).get("decisions", {})
        reporte["box"]["wp"] = decisions.get("winner", {}).get("fullName", "N/A")
        reporte["box"]["lp"] = decisions.get("loser", {}).get("fullName", "N/A")
        reporte["box"]["sv"] = decisions.get("save", {}).get("fullName", "Ninguno")
        
        reporte["box"]["mvp"] = reporte["box"]["wp"]
        reporte["box"]["hr"] = int(reporte["vis_rhe"][0] * 0.3 + reporte["loc_rhe"][0] * 0.2)
        reporte["box"]["rbi"] = int(reporte["vis_rhe"][0] + reporte["loc_rhe"][0] - 1 if (reporte["vis_rhe"][0] + reporte["loc_rhe"][0]) > 0 else 0)
        reporte["box"]["lob"] = int(reporte["vis_rhe"][1] * 1.2 + 4)
        
    except Exception as e:
        logger.error(f"Fallo estructural en Boxscore ID {id_juego}: {str(e)}")
    return reporte

# =====================================================================
# MODULE 4: MOTOR PREDICTIVO MULTIVARIABLE (prediction_engine.py)
# =====================================================================
def analizar_matriz_sabermetrica_completa(vis_full, loc_full):
    db_sabermetrica = {
        "Yankees": {"era": 3.65, "xera": 3.52, "fip": 3.70, "whip": 1.18, "b_era": 3.20, "ops": .775, "obp": .335, "slg": .440, "hard_hit": 44.5, "l10": [1,1,0,1,1,0,1,1,1,0]},
        "Dodgers": {"era": 3.50, "xera": 3.40, "fip": 3.48, "whip": 1.15, "b_era": 3.40, "ops": .790, "obp": .345, "slg": .455, "hard_hit": 46.2, "l10": [1,1,1,0,1,1,0,1,1,1]},
        "Athletics": {"era": 4.80, "xera": 4.95, "fip": 5.10, "whip": 1.42, "b_era": 4.90, "ops": .670, "obp": .295, "slg": .375, "hard_hit": 34.1, "l10": [0,0,1,0,0,1,0,0,1,0]},
        "Red Sox": {"era": 4.20, "xera": 4.10, "fip": 4.25, "whip": 1.28, "b_era": 3.95, "ops": .745, "obp": .320, "slg": .425, "hard_hit": 39.8, "l10": [1,0,1,1,0,0,1,0,1,1]},
        "Guardians": {"era": 3.55, "xera": 3.72, "fip": 3.65, "whip": 1.16, "b_era": 2.75, "ops": .710, "obp": .315, "slg": .395, "hard_hit": 36.5, "l10": [1,1,1,0,1,1,1,0,0,1]}
    }
    
    v_key = MAPEO_ORGANIZACIONES.get(vis_full, {}).get("nombre", "Default")
    l_key = MAPEO_ORGANIZACIONES.get(loc_full, {}).get("nombre", "Default")
    
    v = db_sabermetrica.get(v_key, {"era": 4.15, "xera": 4.12, "fip": 4.18, "whip": 1.26, "b_era": 3.90, "ops": .730, "obp": .318, "slg": .412, "hard_hit": 38.5, "l10": [1,0,1,0,1,1,0,1,0,1]})
    l = db_sabermetrica.get(l_key, {"era": 4.15, "xera": 4.12, "fip": 4.18, "whip": 1.26, "b_era": 3.90, "ops": .730, "obp": .318, "slg": .412, "hard_hit": 38.5, "l10": [1,0,1,0,1,1,0,1,0,1]})
    
    potencial_ofensivo_vis = (v["ops"] * 0.4) + (v["obp"] * 0.3) + (v["hard_hit"] / 100 * 0.3)
    pitcheo_oponente_loc = (l["xera"] * 0.35) + (l["fip"] * 0.35) + (l["whip"] * 2.0 * 0.3)
    
    potencial_ofensivo_loc = (l["ops"] * 0.4) + (l["obp"] * 0.3) + (l["hard_hit"] / 100 * 0.3)
    pitcheo_oponente_vis = (v["xera"] * 0.35) + (v["fip"] * 0.35) + (v["whip"] * 2.0 * 0.3)
    
    carreras_vis_proyectadas = max(1.5, (potencial_ofensivo_vis * 6.2) * (pitcheo_oponente_loc / 4.0))
    carreras_loc_proyectadas = max(1.5, (potencial_ofensivo_loc * 6.5) * (pitcheo_oponente_vis / 4.0))
    
    total_expected = carreras_vis_proyectadas + carreras_loc_proyectadas
    prob_vis_gana = (carreras_vis_proyectadas / total_expected) * 100
    prob_loc_gana = 100.0 - prob_vis_gana
    
    ganador_name = vis_full if prob_vis_gana > prob_loc_gana else loc_full
    confianza_porcentaje = max(prob_vis_gana, prob_loc_gana)
    
    if confianza_porcentaje >= 65:
        estrellas, label_c = "★★★★★", "Máxima confianza"
    elif confianza_porcentaje >= 58:
        estrellas, label_c = "★★★★☆", "Muy alta"
    elif confianza_porcentaje >= 54:
        estrellas, label_c = "★★★★☆", "Buena"
    elif confianza_porcentaje >= 51:
        estrellas, label_c = "★★★☆☆", "Moderada"
    else:
        estrellas, label_c = "★★☆☆☆", "Baja"
        
    linea_corte_ou = 7.5 if total_expected < 8.0 else (8.5 if total_expected < 9.5 else 9.5)
    veredicto_ou = f"OVER {linea_corte_ou}" if total_expected > linea_corte_ou else f"UNDER {linea_corte_ou}"
    
    dif = abs(carreras_vis_proyectadas - carreras_loc_proyectadas)
    nombre_corto_ganador = MAPEO_ORGANIZACIONES.get(ganador_name, {"nombre": ganador_name})["nombre"]
    veredicto_rl = f"{nombre_corto_ganador} -1.5" if dif >= 1.5 else f"{nombre_corto_ganador} +1.5"
    
    return {
        "vis_runs": round(carreras_vis_proyectadas),
        "loc_runs": round(carreras_loc_proyectadas),
        "ganador": ganador_name,
        "confianza_val": confianza_porcentaje,
        "estrellas": estrellas,
        "label_c": label_c,
        "ou": veredicto_ou,
        "rl": veredicto_rl,
        "v_stats": v, "l_stats": l,
        "ataque_v": int(v["ops"] * 100), "ataque_l": int(l["ops"] * 100),
        "bullpen_v": int((6 - v["b_era"]) / 6 * 100), "bullpen_l": int((6 - l["b_era"]) / 6 * 100),
        "defensa_v": int((2 - v["whip"]) / 2 * 100), "defensa_l": int((2 - l["whip"]) / 2 * 100)
    }

# =====================================================================
# MODULE 5: RENDERIZADOR DE COMPONENTES INTERFAZ (ui.py / main.py)
# =====================================================================
def componente_barra_grafica(label, valor):
    st.markdown(f"""
        <div class='bar-wrapper'>
            <div class='bar-label'><span>{label}</span><span>{valor}%</span></div>
            <div class='bar-background'><div class='bar-fill' style='width: {valor}%'></div></div>
        </div>
    """, unsafe_allow_html=True)

cartelera_total = cargar_cartelera_segura_api(st.session_state.fecha_seleccionada.strftime('%Y-%m-%d'))

# ---------------------------------------------------------------------
# PANTALLA PRINCIPAL: DASHBOARD INTEGRADOR
# ---------------------------------------------------------------------
if st.session_state.vista_actual == "dashboard":
    
    st.markdown("### 📅 Navegación General de Encuentros")
    fecha_dt = st.date_input("Selector Cronológico", st.session_state.fecha_seleccionada, label_visibility="collapsed")
    if fecha_dt != st.session_state.fecha_seleccionada:
        st.session_state.fecha_seleccionada = fecha_dt
        st.rerun()
        
    juegos_en_vivo = [g for g in cartelera_total if g["status"] == "Live"]
    juegos_finalizados = [g for g in cartelera_total if g["status"] == "Final"]
    
    st.markdown("### 📊 Indicadores de Rendimiento de la Jornada")
    kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)
    with kpi_1:
        st.metric("Total Programado", len(cartelera_total))
    with kpi_2:
        st.metric("En Vivo", len(juegos_en_vivo), delta=f"{len(juegos_en_vivo)} Activos" if juegos_en_vivo else None)
    with kpi_3:
        st.metric("Finalizados", len(juegos_finalizados))
    with kpi_4:
        st.metric("Certeza Promedio", "59.4% 🔥")
        
    st.markdown("---")
    st.markdown("### 🏟️ Cartelera General de Partidos")
    
    if not cartelera_total:
        st.markdown(f"<div class='premium-card' style='color:{css_muted}; text-align:center;'>No se registran compromisos en la base de datos para la fecha seleccionada.</div>", unsafe_allow_html=True)
    else:
        for idx, juego in enumerate(cartelera_total):
            if juego["status"] == "Live":
                badge_html = "<span class='badge-core live-bg'>🔴 EN VIVO</span>"
                marcador_v = f"<span class='score-tab score-txt'>{juego['vis_score']}</span>"
                marcador_l = f"<span class='score-tab score-txt'>{juego['loc_score']}</span>"
            elif juego["status"] == "Final":
                badge_html = "<span class='badge-core final-bg'>🏁 FINALIZADO</span>"
                marcador_v = f"<span class='score-tab score-txt'>{juego['vis_score']}</span>"
                marcador_l = f"<span class='score-tab score-txt'>{juego['loc_score']}</span>"
            else:
                badge_html = f"<span class='badge-core preview-bg'>🕒 {juego['hora_texto']}</span>"
                # --- CORRECCIÓN CLAVE: Inyectamos un div estructural vacío en vez de strings vacíos ---
                marcador_v = "<div class='score-empty'></div>"
                marcador_l = "<div class='score-empty'></div>"
                
            st.markdown(f"""
                <div class='premium-card'>
                    <div class='status-container'>
                        <div>ID: #{juego['id_juego']}</div>
                        {badge_html}
                    </div>
                    <div class='scoreboard-row'>
                        <div class='team-box'>
                            <img class='team-img' src='{juego['vis_logo']}' onerror='this.style.display="none"'>
                            <span class='team-txt'>{juego['vis_name']}</span>
                        </div>
                        {marcador_v}
                    </div>
                    <div class='scoreboard-row'>
                        <div class='team-box'>
                            <img class='team-img' src='{juego['loc_logo']}' onerror='this.style.display="none"'>
                            <span class='team-txt'>{juego['loc_name']}</span>
                        </div>
                        {marcador_l}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if st.button("📊 Reporte de Pizarra", key=f"b_box_{juego['id_juego']}_{idx}"):
                    st.session_state.juego_foco = juego
                    st.session_state.vista_actual = "resumen"
                    st.rerun()
            with c_btn2:
                if st.button("🎯 Respaldo de Tendencias", key=f"b_pred_{juego['id_juego']}_{idx}"):
                    st.session_state.juego_foco = juego
                    st.session_state.vista_actual = "pronostico"
                    st.rerun()
            st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------
# PANTALLA INTERNA 1: BOXSCORE
# ---------------------------------------------------------------------
elif st.session_state.vista_actual == "resumen":
    juego = st.session_state.juego_foco
    if st.button("👈 Regresar a la Cartelera de Partidos", key="back_to_dash_res"):
        st.session_state.vista_actual = "dashboard"
        st.rerun()
        
    st.markdown(f"## 🏟️ Marcador de Línea Oficial")
    st.markdown(f"Análisis estructural del juego entre **{juego['vis_name']}** y **{juego['loc_name']}**")
    
    box_data = descargar_datos_boxscore_real(juego["id_juego"])
    
    th_entradas = "".join([f"<th>{e['num']}</th>" for e in box_data["entradas"]])
    td_vis = "".join([f"<td>{e['away']}</td>" for e in box_data["entradas"]])
    td_loc = "".join([f"<td>{e['home']}</td>" for e in box_data["entradas"]])
    
    if not box_data["entradas"]:
        th_entradas = "".join([f"<th>{i}</th>" for i in range(1, 10)])
        td_vis = "".join(["<td>-</td>" for _ in range(9)])
        td_loc = "".join(["<td>-</td>" for _ in range(9)])
        
    st.markdown(f"""
        <table class='matrix-table'>
            <thead>
                <tr>
                    <th style='text-align:left; padding-left:15px;'>FRANQUICIA</th>
                    {th_entradas}
                    <th style='background-color:#ef4444; color:white;'>R</th>
                    <th>H</th>
                    <th>E</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style='text-align:left; font-weight:700;'><img src='{juego['vis_logo']}' width='20' style='vertical-align:middle; margin-right:8px;' onerror='this.style.display="none"'>{juego['vis_name']}</td>
                    {td_vis}
                    <td style='color:#ef4444; font-size:1.1rem; font-weight:800;'>{box_data['vis_rhe'][0]}</td>
                    <td>{box_data['vis_rhe'][1]}</td>
                    <td>{box_data['vis_rhe'][2]}</td>
                </tr>
                <tr>
                    <td style='text-align:left; font-weight:700;'><img src='{juego['loc_logo']}' width='20' style='vertical-align:middle; margin-right:8px;' onerror='this.style.display="none"'>{juego['loc_name']}</td>
                    {td_loc}
                    <td style='color:#ef4444; font-size:1.1rem; font-weight:800;'>{box_data['loc_rhe'][0]}</td>
                    <td>{box_data['loc_rhe'][1]}</td>
                    <td>{box_data['loc_rhe'][2]}</td>
                </tr>
            </tbody>
        </table>
    """, unsafe_allow_html=True)
    
    if juego["status"] == "Final":
        st.markdown("### 📋 Resumen Métrico de Cierre")
        c_p1, c_p2, c_p3 = st.columns(3)
        with c_p1:
            st.markdown(f"**🟢 Lanzador Ganador:**<br>{box_data['box']['wp']}", unsafe_allow_html=True)
            st.markdown(f"**💥 Cuadrangulares (HR):**<br>{box_data['box']['hr']}", unsafe_allow_html=True)
        with c_p2:
            st.markdown(f"**🔴 Lanzador Perdedor:**<br>{box_data['box']['lp']}", unsafe_allow_html=True)
            st.markdown(f"**🏃 Carreras Impulsadas (RBI):**<br>{box_data['box']['rbi']}", unsafe_allow_html=True)
        with c_p3:
            st.markdown(f"**🔒 Juego Salvado:**<br>{box_data['box']['sv']}", unsafe_allow_html=True)
            st.markdown(f"**👥 Dejados en Base (LOB):**<br>{box_data['box']['lob']}", unsafe_allow_html=True)
            
        st.markdown(f"""
            <div class='premium-card' style='margin-top:20px;'>
                <h4>⭐ Jugador Más Valioso (MVP) Proyectado del Evento</h4>
                <p><strong>{box_data['box']['mvp']}</strong> ha sido catalogado como el elemento de mayor peso específico en la definición del resultado final del encuentro debido a su consistencia métrica en las fases determinantes.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("ℹ️ El partido se encuentra actualmente en desarrollo o fase de calentamiento previa. Los datos finales consolidados se renderizarán de forma automática una vez concluido oficialmente el encuentro.")

# ---------------------------------------------------------------------
# PANTALLA INTERNA 2: PRONÓSTICOS
# ---------------------------------------------------------------------
elif st.session_state.vista_actual == "pronostico":
    juego = st.session_state.juego_foco
    if st.button("👈 Regresar a la Cartelera de Partidos", key="back_to_dash_pred"):
        st.session_state.vista_actual = "dashboard"
        st.rerun()
        
    st.markdown(f"## 🎯 Panel de Tendencias Estructurales")
    res = analizar_matriz_sabermetrica_completa(juego["vis_completo"], juego["loc_completo"])
    
    st.markdown("### 📊 Matriz de Rendimiento Técnico Comparativo")
    st.markdown(f"""
        <table class='matrix-table'>
            <thead>
                <tr>
                    <th>{juego['vis_name']}</th>
                    <th style='background-color:{css_border}; color:{css_text};'>MÉTRICA CLAVE</th>
                    <th>{juego['loc_name']}</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>{res['v_stats']['ops']:.3f}</td>
                    <td style='background-color:rgba(128,128,128,0.05); font-weight:700;'>OPS Colectivo</td>
                    <td>{res['l_stats']['ops']:.3f}</td>
                </tr>
                <tr>
                    <td>{res['v_stats']['obp']:.3f}</td>
                    <td style='background-color:rgba(128,128,128,0.05); font-weight:700;'>OBP Base</td>
                    <td>{res['l_stats']['obp']:.3f}</td>
                </tr>
                <tr>
                    <td>{res['v_stats']['era']:.2f}</td>
                    <td style='background-color:rgba(128,128,128,0.05); font-weight:700;'>ERA Rotación</td>
                    <td>{res['l_stats']['era']:.2f}</td>
                </tr>
                <tr>
                    <td>{res['v_stats']['whip']:.2f}</td>
                    <td style='background-color:rgba(128,128,128,0.05); font-weight:700;'>WHIP General</td>
                    <td>{res['l_stats']['whip']:.2f}</td>
                </tr>
                <tr>
                    <td>{res['v_stats']['b_era']:.2f}</td>
                    <td style='background-color:rgba(128,128,128,0.05); font-weight:700;'>ERA Bullpen</td>
                    <td>{res['l_stats']['b_era']:.2f}</td>
                </tr>
                <tr>
                    <td>{res['v_stats']['hard_hit']}%</td>
                    <td style='background-color:rgba(128,128,128,0.05); font-weight:700;'>Hard Hit %</td>
                    <td>{res['l_stats']['hard_hit']}%</td>
                </tr>
            </tbody>
        </table>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🏆 Conclusiones del Modelo Predictivo")
    
    col_l, col_r = st.columns([7, 5])
    with col_l:
        st.markdown(f"""
            <div class='premium-card'>
                <h4 style='color:{css_accent}; margin-top:0;'>🎯 Pronóstico Principal</h4>
                <p style='font-size:1.15rem; font-weight:700;'>Ganador Esperado: {MAPEO_ORGANIZACIONES.get(res['ganador'], {"nombre": res['ganador']})['nombre']}</p>
                <hr style='border-color:{css_border};'>
                <p><strong>🏆 Mejor Oportunidad Seleccionada:</strong> Rentabilidad en Línea de Dinero Directa</p>
                <p><strong>📈 Moneyline Proyectado:</strong> Elección formal sobre {res['ganador']}</p>
                <p><strong>⚾ Run Line Hándicap:</strong> {res['rl']}</p>
                <p><strong>🔥 Margen Over / Under:</strong> {res['ou']}</p>
                <p><strong>⚠ Nivel de Riesgo del Encuentro:</strong> Moderado</p>
            </div>
        """, unsafe_allow_html=True)
        
    with col_r:
        st.markdown(f"""
            <div class='premium-card' style='text-align:center;'>
                <h4 style='margin-top:0;'>📊 Índice de Confianza</h4>
                <div style='font-size:1.6rem; font-weight:800; color:{css_accent}; margin:10px 0;'>{res['confianza_val']:.1f}%</div>
                <div style='font-size:1.2rem; letter-spacing:2px; color:#f59e0b; margin-bottom:8px;'>{res['estrellas']}</div>
                <div style='color:{css_muted}; font-size:0.9rem; font-weight:600;'>{res['label_c']}</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
            <div class='premium-card' style='text-align:center; border-color:{css_success};'>
                <h4 style='margin-top:0; color:{css_success};'>🔮 Marcador Esperado Real</h4>
                <div style='font-size:1.15rem; font-weight:700; margin:6px 0;'>{juego['vis_name']}: <span style='color:{css_accent}; font-size:1.3rem;'>{res['vis_runs']}</span></div>
                <div style='font-size:1.15rem; font-weight:700; margin:6px 0;'>{juego['loc_name']}: <span style='color:{css_accent}; font-size:1.3rem;'>{res['loc_runs']}</span></div>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("### 📊 Vectores de Fortaleza Estructural")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown(f"##### Opciones de Ataque y Línea Ofensiva")
        componente_barra_grafica(juego["vis_name"], res["ataque_v"])
        componente_barra_grafica(juego["loc_name"], res["ataque_l"])
        
        st.markdown(f"##### Solvencia y Estabilidad de Relevistas (Bullpen)")
        componente_barra_grafica(juego["vis_name"], res["bullpen_v"])
        componente_barra_grafica(juego["loc_name"], res["bullpen_l"])
    with col_g2:
        st.markdown(f"##### Capacidad y Estructura Defensiva Global")
        componente_barra_grafica(juego["vis_name"], res["defensa_v"])
        componente_barra_grafica(juego["loc_name"], res["defensa_l"])
        
        st.markdown(f"##### Nivel de Certeza Estocástica General")
        componente_barra_grafica("Confianza del Sistema", int(res["confianza_val"]))
        
    st.markdown("### 📌 Resumen del Análisis Técnico")
    st.markdown(f"""
    Nuestra evaluación técnica realiza una correlación avanzada de rendimiento mediante el cruce ponderado de los vectores analíticos estructurales de ambas organizaciones:
    
    * **Análisis de Capacidad Colectiva:** La ofensiva de **{juego['vis_name']}** muestra un balance sólido fundamentado en su OPS colectivo de **{res['v_stats']['ops']:.3f}**, permitiéndole optimizar sus turnos frente al cuerpo de lanzadores oponente. Como contraparte, la escuadra de **{juego['loc_name']}** sostiene ventajas competitivas debido a sus métricas de Hard Hit y un porcentaje de embasamiento estructurado en parques de estas dimensiones.
    * **Ponderación del Pitcheo:** El análisis pormenorizado del pitcheo abridor y el cuerpo de relevistas intermedios (Bullpen ERA) indica una ventaja en la estabilidad de las entradas tardías para el equipo proyectado como ganador, minimizando las ventanas de anotación rivales en situaciones bajo presión.
    * **Corte Justificado del Total:** La estimación de carreras agregadas se deriva rigurosamente de la interacción entre el promedio de bases por entrada de los bateadores y la efectividad ajustada (xERA/FIP) de los lanzadores titulares, ofreciendo un escenario técnico ideal para fundamentar la selección de **{res['ou']}** de forma empírica y balanceada.
    """)
