import streamlit as st
import numpy as np
import requests
from datetime import datetime
import pytz

# --- 1. CONFIGURACIÓN DE LA APP PREMIUM ---
st.set_page_config(
    page_title="SHARP QUANT SYSTEM - MLB PRO", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Adaptable a Temas Claro/Oscuro Absoluto con Estilo MLB ESPN
st.markdown("""
    <style>
    /* Soporte de Temas Dinámicos (Claro/Oscuro Completo) */
    :root {
        --bg-app: rgba(var(--st-background-color-rgb), 1);
        --bg-card: rgba(var(--st-secondary-background-color-rgb), 1);
        --text-main: rgba(var(--st-text-color-rgb), 1);
    }
    
    .stApp { 
        background-color: var(--bg-app); 
        color: var(--text-main); 
    }
    
    /* Cintillo de Identidad MLB */
    .mlb-bar {
        height: 6px;
        background: linear-gradient(90deg, #041E42 0%, #041E42 50%, #BF0D3E 50%, #BF0D3E 100%);
        border-radius: 4px;
        margin-bottom: 15px;
    }
    
    h1 {
        color: #BF0D3E !important;
        font-family: 'Arial Black', sans-serif;
        text-align: center;
        font-size: 2.5rem !important;
        font-weight: bold;
        margin-bottom: 2px;
    }
    [data-theme="dark"] h1 {
        color: #00ff66 !important;
        text-shadow: 0 0 10px rgba(0, 255, 102, 0.3);
    }
    
    .subtitle { text-align: center; color: #8b949e; margin-bottom: 25px; font-weight: 500; }
    
    /* Tarjetas Estilo ESPN Scoreboard */
    .game-card {
        background-color: var(--bg-card);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    .team-container { display: flex; align-items: center; justify-content: space-between; margin: 6px 0; }
    .team-identity { display: flex; align-items: center; gap: 12px; }
    .team-logo { width: 26px; height: 26px; object-fit: contain; }
    .team-name { color: var(--text-main); font-size: 1.15rem; font-weight: bold; }
    .team-score { font-size: 1.3rem; font-weight: 900; font-family: 'Impact', sans-serif; padding-right: 10px; }
    
    .game-header { display: flex; justify-content: flex-end; padding-bottom: 4px; margin-bottom: 6px; font-size: 0.82rem; font-family: monospace; }
    .status-badge { padding: 2px 8px; border-radius: 4px; font-weight: bold; color: #ffffff !important; }
    .badge-live { background-color: #BF0D3E; text-shadow: 0 0 5px rgba(255,255,255,0.4); }
    .badge-final { background-color: #555555; }
    .badge-preview { background-color: #041E42; }
    
    /* Pizarra ESPN Boxscore */
    .espn-table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        font-family: Arial, sans-serif;
        background-color: var(--bg-card);
        color: var(--text-main);
        border-radius: 8px;
        overflow: hidden;
    }
    .espn-table th { background-color: rgba(4, 30, 66, 0.9); color: white; padding: 10px; text-align: center; font-size: 0.9rem; }
    .espn-table td { padding: 10px; border-bottom: 1px solid rgba(128, 128, 128, 0.15); text-align: center; font-weight: bold; }
    .espn-table .team-cell { text-align: left; padding-left: 15px; display: flex; align-items: center; gap: 10px; }
    
    /* Ajustes Métricas */
    div[data-testid="metric-container"] { background-color: var(--bg-card) !important; border: 1px solid rgba(128, 128, 128, 0.2) !important; border-radius: 10px !important; }
    </style>
""", unsafe_allow_html=True)

# Cintillo decorativo superior de la MLB
st.markdown("<div class='mlb-bar'></div>", unsafe_allow_html=True)
st.markdown("<h1>⚾ SHARP QUANT SYSTEM PRO 🔥</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Consola de Sabermetría Predictiva e Historial de la Grandes Ligas (MLB)</p>", unsafe_allow_html=True)

# --- 2. DICCIONARIO TRADUCTOR DE LA MLB CON IDS CORREGIDOS PARA LOGOS ---
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
                    "id_juego": juego["gamePk"],
                    "vis_completo": nombre_vis_completo, "vis_name": vis_org, "vis_logo": vis_logo, "vis_score": score_vis,
                    "loc_completo": nombre_loc_completo, "loc_name": loc_org, "loc_logo": loc_logo, "loc_score": score_loc,
                    "status": abstract_status, "detalle": detailed_status, "inning_status": inning_texto,
                    "hora_texto": dt_et.strftime('%I:%M %p ET')
                })
    except:
        pass
    return lista_juegos

def obtener_detalles_reales_partido(id_juego):
    url = f"https://statsapi.mlb.com/api/v1.1/game/{id_juego}/feed/live"
    reporte = {"vis_rhe": [0,0,0], "loc_rhe": [0,0,0], "entradas": [], "destacados": ""}
    try:
        res = requests.get(url, timeout=3).json()
        linescore = res.get("liveData", {}).get("linescore", {})
        
        # Data RHE
        vis_t = linescore.get("teams", {}).get("away", {})
        loc_t = linescore.get("teams", {}).get("home", {})
        reporte["vis_rhe"] = [vis_t.get('runs', 0), vis_t.get('hits', 0), vis_t.get('errors', 0)]
        reporte["loc_rhe"] = [loc_t.get('runs', 0), loc_t.get('hits', 0), loc_t.get('errors', 0)]
        
        # Desglose de entradas
        for e in linescore.get("innings", []):
            reporte["entradas"].append({
                "num": e.get("num"),
                "away": e.get("away", {}).get("runs", 0),
                "home": e.get("home", {}).get("runs", 0)
            })
            
        info_juego = res.get("gameData", {})
        probables = info_juego.get("probablePitchers", {})
        p_vis = probables.get("away", {}).get("fullName", "Por anunciar")
        p_loc = probables.get("home", {}).get("fullName", "Por anunciar")
        reporte["destacados"] = f"Pitcher Abridor: {p_vis} (VIS) vs {p_loc} (LOC)"
    except:
        pass
    return reporte

cartelera_partidos = cargar_cartelera_total_api(fecha_str)

# --- 5. MODELO DE SABERMETRÍA ---
def obtener_analitica_diaria_mlb(nombre_equipo):
    return {"carreras_p": 4.5, "wrc": 100, "whip_ab": 1.25, "k_bb": 2.8, "bp_era": 3.80, "bp_uso": 1.00, "umpire_strike_zone": 0.00, "park_factor": 1.00, "avg": .248, "ops": .730}

def ejecutar_simulacion_quant(vis, loc):
    v_stats = obtener_analitica_diaria_mlb(vis)
    l_stats = obtener_analitica_diaria_mlb(loc)
    runs_vis = (v_stats["carreras_p"] * (v_stats["wrc"] / 100)) + (l_stats["whip_ab"] * 0.35) - (l_stats["k_bb"] * 0.05)
    runs_loc = (l_stats["carreras_p"] * (l_stats["wrc"] / 100)) + (v_stats["whip_ab"] * 0.30) - (v_stats["k_bb"] * 0.05)
    sim_vis = np.random.poisson(runs_vis, 10000)
    sim_loc = np.random.poisson(runs_loc, 10000)
    prob_v = (np.sum(sim_vis > sim_loc) / 10000) * 100
    prob_l = 100 - prob_v
    ganador_ml = vis if prob_v > prob_l else loc
    veredicto_ou = "OVER 8.5" if (np.sum((sim_vis + sim_loc) > 8.5) / 10000) * 100 > 50 else "UNDER 8.5"
    veredicto_rl = f"{vis} -1.5" if prob_v > prob_l else f"{loc} -1.5"
    return ganador_ml, max(prob_v, prob_l), veredicto_ou, 55.0, veredicto_rl, 53.0, v_stats, l_stats

# --- 6. GESTIÓN DE NAVEGACIÓN TIPO ESPN (PANTALLA COMPLETA INTERNA) ---
if "partido_seleccionado" not in st.session_state:
    st.session_state.partido_seleccionado = None

st.markdown("---")

# MODO DETALLE DE ENCUENTRO (PANTALLA INDEPENDIENTE TIPO ESPN)
if st.session_state.partido_seleccionado is not None:
    partido = st.session_state.partido_seleccionado
    
    # BOTÓN DE SALIDA DESTACADO
    if st.button("⬅️ Volver a la Cartelera Completa", key="btn_salir_espn"):
        st.session_state.partido_seleccionado = None
        st.rerun()
        
    st.markdown(f"## 🏟️ Centro de Partido ESPN Style")
    
    info_real = obtener_detalles_reales_partido(partido["id_juego"])
    
    # Construcción de la Tabla Boxscore de Entradas
    th_entradas = "".join([f"<th>{e['num']}</th>" for e in info_real["entradas"]])
    td_vis_entradas = "".join([f"<td>{e['away']}</td>" for e in info_real["entradas"]])
    td_loc_entradas = "".join([f"<td>{e['home']}</td>" for e in info_real["entradas"]])
    
    # Si no ha empezado el partido, rellenar boxscore estándar de 9 entradas vacías
    if not info_real["entradas"]:
        th_entradas = "".join([f"<th>{i}</th>" for i in range(1, 10)])
        td_vis_entradas = "".join(["<td>-</td>" for _ in range(9)])
        td_loc_entradas = "".join(["<td>-</td>" for _ in range(9)])

    html_boxscore = f"""
    <table class='espn-table'>
        <thead>
            <tr>
                <th style='text-align:left; padding-left:15px;'>EQUIPO</th>
                {th_entradas}
                <th style='background-color:#BF0D3E;'>R</th>
                <th style='background-color:#333;'>H</th>
                <th style='background-color:#333;'>E</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td class='team-cell'><img src='{partido["vis_logo"]}' width='20'>{partido["vis_name"]}</td>
                {td_vis_entradas}
                <td style='color:#BF0D3E; font-size:1.1rem;'>{info_real["vis_rhe"][0]}</td>
                <td>{info_real["vis_rhe"][1]}</td>
                <td>{info_real["vis_rhe"][2]}</td>
            </tr>
            <tr>
                <td class='team-cell'><img src='{partido["loc_logo"]}' width='20'>{partido["loc_name"]}</td>
                {td_loc_entradas}
                <td style='color:#BF0D3E; font-size:1.1rem;'>{info_real["loc_rhe"][0]}</td>
                <td>{info_real["loc_rhe"][1]}</td>
                <td>{info_real["loc_rhe"][2]}</td>
            </tr>
        </tbody>
    </table>
    """
    st.markdown(html_boxscore, unsafe_allow_html=True)
    st.caption(f"ℹ️ {info_real['destacados']} | Estado actual: {partido['detalle']}")
    
    # Bloque estadístico predictivo dentro del panel de entrada
    st.markdown("### 🤖 Simulación Quant System (Sabermetría)")
    res_ml, por_ml, res_ou, por_ou, res_rl, por_rl, v_s, l_s = ejecutar_simulacion_quant(partido["vis_completo"], partido["loc_completo"])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="🏆 GANADOR PROYECTADO", value=MAPEO_ORGANIZACIONES.get(res_ml, {"nombre": res_ml})["nombre"], delta=f"{round(por_ml, 1)}% Certeza")
    with col2:
        st.metric(label="📈 OVER / UNDER", value=res_ou, delta="Línea 8.5 runs")
    with col3:
        st.metric(label="⚾ RUNLINE HÁNDICAP", value=res_rl, delta="Estabilidad del Margen")

# MODO LISTA COMPLETA (CARTELERA)
else:
    if not cartelera_partidos:
        st.markdown("<div class='status-box'>📅 NO HAY ENCUENTROS PROGRAMADOS PARA ESTA FECHA.</div>", unsafe_allow_html=True)
    else:
        partidos_activos = [p for p in cartelera_partidos if p["status"] != "Final"]
        partidos_concluidos = [p for p in cartelera_partidos if p["status"] == "Final"]
        cartelera_ordenada = partidos_activos + partidos_concluidos

        for idx, j in enumerate(cartelera_ordenada):
            if j["status"] == "Live":
                status_html = f"<span class='status-badge badge-live'>🔴 {j['inning_status'].upper()}</span>"
                marcador_vis = f"<span class='team-score'>{j['vis_score']}</span>"
                marcador_loc = f"<span class='team-score'>{j['loc_score']}</span>"
            elif j["status"] == "Final":
                status_html = f"<span class='status-badge badge-final'>🏁 {j['inning_status'].upper()}</span>"
                marcador_vis = f"<span class='team-score'>{j['vis_score']}</span>"
                marcador_loc = f"<span class='team-score'>{j['loc_score']}</span>"
            else: 
                status_html = f"<span class='status-badge badge-preview'>🕒 {j['hora_texto']}</span>"
                marcador_vis = ""
                marcador_loc = ""

            html_tarjeta = (
                f"<div class='game-card'>"
                    f"<div class='game-header'>{status_html}</div>"
                    f"<div class='team-container'>"
                        f"<div class='team-identity'>"
                            f"<img class='team-logo' src='{j['vis_logo']}'>"
                            f"<span class='team-name'>{j['vis_name']}</span>"
                        f"</div>"
                        f"{marcador_vis}"
                    f"</div>"
                    f"<div class='team-container'>"
                        f"<div class='team-identity'>"
                            f"<img class='team-logo' src='{j['loc_logo']}'>"
                            f"<span class='team-name'>{j['loc_name']}</span>"
                        f"</div>"
                        f"{marcador_loc}"
                    f"</div>"
                f"</div>"
            )
            st.markdown(html_tarjeta, unsafe_allow_html=True)
            
            # Botón estilizado para INTRUSIÓN total al reporte ESPN
            if st.button(f"📊 Entrar a los detalles de ESPN: {j['vis_name']} vs {j['loc_name']}", key=f"btn_go_{idx}"):
                st.session_state.partido_seleccionado = j
                st.rerun()
            
            st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)
