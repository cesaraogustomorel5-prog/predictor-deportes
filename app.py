import streamlit as st
import numpy as np
from datetime import datetime
import pytz

st.set_page_config(page_title="Statline Predictor Pro", layout="wide")

st.title("🧠 Statline Predictor Pro - SHARP SYSTEM")
st.write("Consola Cuantitativa Definitiva: 30 Equipos MLB, Moneyline, Over/Under y Runline.")

# --- 1. CONFIGURACIÓN DEL RELOJ EN VIVO ---
zona_horaria = pytz.timezone('America/New_York')
hora_actual = datetime.now(zona_horaria)
st.sidebar.markdown(f"🕒 **Hora del Servidor (ET):** {hora_actual.strftime('%I:%M %p')}")

# --- 2. BASE DE DATOS DINÁMICA DE JUEGOS DEL CALENDARIO ---
calendario_completo = {
    "Los Angeles Dodgers vs Pittsburgh Pirates": {"hora_inicio": "19:05"},
    "New York Yankees vs Boston Red Sox": {"hora_inicio": "19:10"},
    "Houston Astros vs New York Mets": {"hora_inicio": "20:10"},
    "Atlanta Braves vs Philadelphia Phillies": {"hora_inicio": "22:00"}
}

# Filtro de partidos automáticos por hora
partidos_disponibles = []
for partido, info in calendario_completo.items():
    hora_juego = datetime.strptime(info["hora_inicio"], "%H:%M").time()
    if hora_actual.time() < hora_juego:
        partidos_disponibles.append(partido)

partidos_disponibles.append("➕ ANALIZAR OTRO PARTIDO (ENTRADA MANUAL)")
partido_seleccionado = st.selectbox("🎯 Partidos del Calendario Activo:", partidos_disponibles)

# --- 3. MENÚ DE LOS 30 EQUIPOS OFICIALES DE LA MLB ---
lista_30_equipos = [
    "Arizona Diamondbacks", "Atlanta Braves", "Baltimore Orioles", "Boston Red Sox", 
    "Chicago Cubs", "Chicago White Sox", "Cincinnati Reds", "Cleveland Guardians", 
    "Colorado Rockies", "Detroit Tigers", "Houston Astros", "Kansas City Royals", 
    "Los Angeles Angels", "Los Angeles Dodgers", "Miami Marlins", "Milwaukee Brewers", 
    "Minnesota Twins", "New York Mets", "New York Yankees", "Oakland Athletics", 
    "Philadelphia Phillies", "Pittsburgh Pirates", "San Diego Padres", "San Francisco Giants", 
    "Seattle Mariners", "St. Louis Cardinals", "Tampa Bay Rays", "Texas Rangers", 
    "Toronto Blue Jays", "Washington Nationals"
]

# Si elige entrada manual, se activan los selectores con los 30 equipos
if partido_seleccionado == "➕ ANALIZAR OTRO PARTIDO (ENTRADA MANUAL)":
    st.markdown("### 📝 Panel de Edición Libre (Selección de Equipos)")
    col_v, col_l = st.columns(2)
    with col_v: equipo_vis = st.selectbox("Selecciona Equipo Visitante:", lista_30_equipos, index=13) # Default Dodgers
    with col_l: equipo_loc = st.selectbox("Selecciona Equipo Local:", lista_30_equipos, index=21) # Default Pirates
    nombre_clave = f"{equipo_vis} vs {equipo_loc}"
else:
    nombre_clave = partido_seleccionado

# --- 4. DICCIONARIO MAESTRO CON LAS ESTADÍSTICAS AVANZADAS (30 EQUIPOS) ---
# Contiene wRC+, xERA, FIP, WHIP del abridor, efectividad del bullpen, fatiga y lesionados.
perfiles_estadisticos = {
    "dodgers": {"wrc": 122, "era_ab": 3.20, "whip_ab": 0.88, "xera": 2.45, "fip": 2.30, "bp_era": 3.45, "bp_fatiga": "BAJA", "lesionados": ["Mookie Betts", "Max Muncy"]},
    "pirates": {"wrc": 92, "era_ab": 3.95, "whip_ab": 1.42, "xera": 4.65, "fip": 4.80, "bp_era": 4.10, "bp_fatiga": "ALTA", "lesionados": ["David Bednar"]},
    "yankees": {"wrc": 125, "era_ab": 2.85, "whip_ab": 1.02, "xera": 2.90, "fip": 3.10, "bp_era": 3.15, "bp_fatiga": "BAJA", "lesionados": ["Giancarlo Stanton"]},
    "red sox": {"wrc": 104, "era_ab": 4.15, "whip_ab": 1.30, "xera": 4.10, "fip": 3.95, "bp_era": 3.90, "bp_fatiga": "MODERADA", "lesionados": []},
    "astros": {"wrc": 110, "era_ab": 3.40, "whip_ab": 1.22, "xera": 3.50, "fip": 3.65, "bp_era": 3.80, "bp_fatiga": "MODERADA", "lesionados": ["Kyle Tucker"]},
    "mets": {"wrc": 108, "era_ab": 3.10, "whip_ab": 1.15, "xera": 3.25, "fip": 3.40, "bp_era": 3.60, "bp_fatiga": "BAJA", "lesionados": ["Francisco Lindor"]},
    "braves": {"wrc": 112, "era_ab": 2.75, "whip_ab": 1.01, "xera": 2.65, "fip": 2.80, "bp_era": 3.30, "bp_fatiga": "BAJA", "lesionados": ["Ronald Acuña Jr."]},
    "phillies": {"wrc": 115, "era_ab": 2.60, "whip_ab": 0.98, "xera": 2.50, "fip": 2.70, "bp_era": 3.20, "bp_fatiga": "BAJA", "lesionados": ["Trea Turner"]},
    "blue jays": {"wrc": 101, "era_ab": 3.85, "whip_ab": 1.21, "xera": 3.90, "fip": 3.80, "bp_era": 3.95, "bp_fatiga": "MODERADA", "lesionados": []},
    "orioles": {"wrc": 116, "era_ab": 3.15, "whip_ab": 1.08, "xera": 3.20, "fip": 3.35, "bp_era": 3.50, "bp_fatiga": "BAJA", "lesionados": []},
    "rays": {"wrc": 103, "era_ab": 3.65, "whip_ab": 1.14, "xera": 3.55, "fip": 3.60, "bp_era": 3.40, "bp_fatiga": "BAJA", "lesionados": []},
    "guardians": {"wrc": 105, "era_ab": 3.70, "whip_ab": 1.18, "xera": 3.65, "fip": 3.75, "bp_era": 2.80, "bp_fatiga": "BAJA", "lesionados": []},
    "twins": {"wrc": 109, "era_ab": 3.60, "whip_ab": 1.16, "xera": 3.45, "fip": 3.50, "bp_era": 3.75, "bp_fatiga": "MODERADA", "lesionados": []},
    "royals": {"wrc": 102, "era_ab": 3.55, "whip_ab": 1.15, "xera": 3.60, "fip": 3.65, "bp_era": 3.90, "bp_fatiga": "MODERADA", "lesionados": []},
    "tigers": {"wrc": 96, "era_ab": 3.80, "whip_ab": 1.20, "xera": 3.50, "fip": 3.40, "bp_era": 3.85, "bp_fatiga": "MODERADA", "lesionados": []},
    "white sox": {"wrc": 82, "era_ab": 4.95, "whip_ab": 1.48, "xera": 4.80, "fip": 4.90, "bp_era": 4.70, "bp_fatiga": "ALTA", "lesionados": []},
    "mariners": {"wrc": 99, "era_ab": 3.10, "whip_ab": 1.03, "xera": 3.15, "fip": 3.25, "bp_era": 3.45, "bp_fatiga": "BAJA", "lesionados": []},
    "rangers": {"wrc": 106, "era_ab": 3.90, "whip_ab": 1.24, "xera": 3.85, "fip": 3.90, "bp_era": 3.80, "bp_fatiga": "MODERADA", "lesionados": []},
    "angels": {"wrc": 95, "era_ab": 4.50, "whip_ab": 1.36, "xera": 4.40, "fip": 4.45, "bp_era": 4.30, "bp_fatiga": "ALTA", "lesionados": ["Mike Trout"]},
    "athletics": {"wrc": 91, "era_ab": 4.60, "whip_ab": 1.38, "xera": 4.50, "fip": 4.55, "bp_era": 4.25, "bp_fatiga": "MODERADA", "lesionados": []},
    "marlins": {"wrc": 88, "era_ab": 4.45, "whip_ab": 1.35, "xera": 4.40, "fip": 4.50, "bp_era": 4.20, "bp_fatiga": "ALTA", "lesionados": []},
    "nationals": {"wrc": 93, "era_ab": 4.30, "whip_ab": 1.32, "xera": 4.35, "fip": 4.25, "bp_era": 4.15, "bp_fatiga": "MODERADA", "lesionados": []},
    "cubs": {"wrc": 103, "era_ab": 3.75, "whip_ab": 1.22, "xera": 3.70, "fip": 3.80, "bp_era": 3.80, "bp_fatiga": "MODERADA", "lesionados": []},
    "cardinals": {"wrc": 98, "era_ab": 4.00, "whip_ab": 1.26, "xera": 4.10, "fip": 4.05, "bp_era": 3.70, "bp_fatiga": "BAJA", "lesionados": []},
    "brewers": {"wrc": 105, "era_ab": 3.65, "whip_ab": 1.20, "xera": 3.80, "fip": 3.85, "bp_era": 3.25, "bp_fatiga": "BAJA", "lesionados": []},
    "reds": {"wrc": 97, "era_ab": 4.10, "whip_ab": 1.25, "xera": 3.90, "fip": 3.95, "bp_era": 3.85, "bp_fatiga": "MODERADA", "lesionados": []},
    "padres": {"wrc": 111, "era_ab": 3.50, "whip_ab": 1.15, "xera": 3.40, "fip": 3.45, "bp_era": 3.65, "bp_fatiga": "BAJA", "lesionados": ["Fernando Tatis Jr."]},
    "giants": {"wrc": 102, "era_ab": 3.90, "whip_ab": 1.23, "xera": 3.75, "fip": 3.70, "bp_era": 3.90, "bp_fatiga": "MODERADA", "lesionados": []},
    "diamondbacks": {"wrc": 108, "era_ab": 3.95, "whip_ab": 1.24, "xera": 3.85, "fip": 3.90, "bp_era": 3.75, "bp_fatiga": "BAJA", "lesionados": []},
    "rockies": {"wrc": 86, "era_ab": 5.20, "whip_ab": 1.52, "xera": 5.05, "fip": 5.15, "bp_era": 5.10, "bp_fatiga": "ALTA", "lesionados": []}
}

# Filtro extractor por coincidencia de texto
def obtener_datos_equipo(nombre_completo):
    for clave, datos in perfiles_estadisticos.items():
        if clave in nombre_completo.lower():
            return datos
    return {"wrc": 100, "era_ab": 4.00, "whip_ab": 1.25, "xera": 4.00, "fip": 4.00, "bp_era": 3.90, "bp_fatiga": "MODERADA", "lesionados": []}

# Separar nombres para el análisis
if " vs " in nombre_clave:
    v_team, l_team = nombre_clave.split(" vs ")
else:
    v_team, l_team = "Los Angeles Dodgers", "Pittsburgh Pirates"

stats_vis = obtener_datos_equipo(v_team)
stats_loc = obtener_datos_equipo(l_team)

# --- 5. CONFIGURACIÓN INDEPENDIENTE DEL ENTORNO ---
# Variables de ajuste por estadio y condiciones ambientales del partido seleccionado
config_entorno = {
    "linea_ou": 8.5, "park_factor": 1.03, "temperatura": "27°C", "viento": "10 mph hacia afuera",
    "umpire_tendencia": "Over (Zona estrecha, +0.3 carreras)",
    "apuestas_publico": "76% al Favorito", "cuota_apertura": -170, "cuota_actual": -150, "rlm_detectado": True
}

# --- 6. EJECUCIÓN DEL MOTOR QUANT PROFESIONAL ---
if st.button("🔥 EJECUTAR ANÁLISIS PROFESIONAL", use_container_width=True):
    
    # Ecuación Sabermétrica Base (wRC+ del Lineup, WHIP/xERA del rival y penalización por Lesionados)
    carreras_vis = (5.0 * (stats_vis["wrc"]/100)) - (len(stats_vis["lesionados"]) * 0.25) + (stats_loc["whip_ab"] * 0.4)
    carreras_loc = (4.1 * (stats_loc["wrc"]/100)) - (len(stats_loc["lesionados"]) * 0.25) + (stats_vis["whip_ab"] * 0.3)
    
    # Multiplicador por Entorno (Clima y Parque)
    carreras_vis *= config_entorno["park_factor"]
    carreras_loc *= config_entorno["park_factor"]
    
    # 🎲 Simulación de Montecarlo (10,000 iteraciones instantáneas)
    sim_vis = np.random.poisson(carreras_vis, 10000)
    sim_loc = np.random.poisson(carreras_loc, 10000)
    
    # 🏆 1. CÁLCULO DE PROBABILIDAD DEL MONEYLINE
    prob_ganador_vis = (np.sum(sim_vis > sim_loc) / 10000) * 100
    prob_ganador_loc = 100 - prob_ganador_vis
    ganador_ml = v_team if prob_ganador_vis > prob_ganador_loc else l_team
    porcentaje_ml = max(prob_ganador_vis, prob_ganador_loc)
    
    # 📈 2. CÁLCULO DE PROBABILIDAD DEL OVER/UNDER
    prob_over = (np.sum((sim_vis + sim_loc) > config_entorno["linea_ou"]) / 10000) * 100
    linea_ou_texto = f"OVER {config_entorno['linea_ou']}" if prob_over > 50 else f"UNDER {config_entorno['linea_ou']}"
    porcentaje_ou = prob_over if prob_over > 50 else (100 - prob_over)
    
    # ⚾ 3. CÁLCULO DE PROBABILIDAD DEL RUNLINE (HÁNDICAP -1.5 / +1.5)
    if prob_ganador_vis > prob_ganador_loc:
        fav_n, dog_n = v_team, l_team
        prob_cubrir_fav = (np.sum((sim_vis - sim_loc) >= 2) / 10000) * 10
