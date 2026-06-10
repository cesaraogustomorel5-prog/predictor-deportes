import streamlit as st
import numpy as np

st.set_page_config(page_title="Statline Predictor Pro", layout="wide")

st.title("🧠 Statline Predictor Pro - SHARP SYSTEM")
st.write("Análisis estadístico automatizado y dinámico para Grandes Ligas.")

# --- 1. BASE DE DATOS COMPLETA DE PARTIDOS DEL DÍA ---
# El robot real alimentará esta lista automáticamente cada mañana con los juegos del calendario
opciones_partidos = [
    "Los Angeles Dodgers vs Pittsburgh Pirates",
    "New York Yankees vs Boston Red Sox",
    "Houston Astros vs New York Mets",
    "Atlanta Braves vs Philadelphia Phillies"
]

partido_seleccionado = st.selectbox("🎯 Selecciona el partido que deseas analizar hoy:", opciones_partidos)

# --- 2. DICCIONARIO DE DATOS POR PARTIDO (El robot cambia estos números diario)
base_datos_mlb = {
    "Los Angeles Dodgers vs Pittsburgh Pirates": {
        "local": "Pirates", "visitante": "Dodgers",
        "abridor_loc": "Mitch Keller", "era_ab_loc": 4.80, "whip_ab_loc": 1.42, "xera_loc": 4.65, "fip_loc": 4.80,
        "abridor_vis": "Tyler Glasnow", "era_ab_vis": 2.10, "whip_ab_vis": 0.88, "xera_vis": 2.45, "fip_vis": 2.30,
        "bullpen_era_loc": 4.10, "bullpen_fatiga_loc": "ALTA",
        "bullpen_era_vis": 3.45, "bullpen_fatiga_vis": "BAJA",
        "lesionados_vis": ["Mookie Betts", "Max Muncy"], "lesionados_loc": ["David Bednar"],
        "wrc_lineup_vis": 118, "wrc_lineup_loc": 92,
        "umpire_tendencia": "Over (Zona estrecha, +0.3 carreras)",
        "park_factor": 1.05, "temperatura": "29°C", "viento": "12 mph hacia afuera", "linea_ou": 8.5,
        "apuestas_publico_fav": "82% con Dodgers", "cuota_apertura": -180, "cuota_actual": -155, "rlm_detectado": True
    },
    "New York Yankees vs Boston Red Sox": {
        "local": "Red Sox", "visitante": "Yankees",
        "abridor_loc": "Brayan Bello", "era_ab_loc": 4.15, "whip_ab_loc": 1.30, "xera_loc": 4.10, "fip_loc": 3.95,
        "abridor_vis": "Gerrit Cole", "era_ab_vis": 2.85, "whip_ab_vis": 1.02, "xera_vis": 2.90, "fip_vis": 3.10,
        "bullpen_era_loc": 3.90, "bullpen_fatiga_loc": "MODERADA",
        "bullpen_era_vis": 3.15, "bullpen_fatiga_vis": "BAJA",
        "lesionados_vis": ["Giancarlo Stanton"], "lesionados_loc": [],
        "wrc_lineup_vis": 125, "wrc_lineup_loc": 104,
        "umpire_tendencia": "Under (Zona amplia, -0.2 carreras)",
        "park_factor": 1.02, "temperatura": "22°C", "viento": "5 mph cruzado", "linea_ou": 9.0,
        "apuestas_publico_fav": "75% con Yankees", "cuota_apertura": -150, "cuota_actual": -170, "rlm_detectado": False
    },
    "Houston Astros vs New York Mets": {
        "local": "Mets", "visitante": "Astros",
        "abridor_loc": "Kodai Senga", "era_ab_loc": 3.10, "whip_ab_loc": 1.15, "xera_loc": 3.25, "fip_loc": 3.40,
        "abridor_vis": "Framber Valdez", "era_ab_vis": 3.40, "whip_ab_vis": 1.22, "xera_vis": 3.50, "fip_vis": 3.65,
        "bullpen_era_loc": 3.60, "bullpen_fatiga_loc": "BAJA",
        "bullpen_era_vis": 3.80, "bullpen_fatiga_vis": "MODERADA",
        "lesionados_vis": ["Kyle Tucker"], "lesionados_loc": ["Francisco Lindor"],
        "wrc_lineup_vis": 110, "wrc_lineup_loc": 108,
        "umpire_tendencia": "Neutral (Zona estándar)",
        "park_factor": 0.96, "temperatura": "24°C", "viento": "8 mph hacia adentro", "linea_ou": 7.5,
        "apuestas_publico_fav": "50% Dividido", "cuota_apertura": -110, "cuota_actual": -110, "rlm_detectado": False
    },
    "Atlanta Braves vs Philadelphia Phillies": {
        "local": "Phillies", "visitante": "Braves",
        "abridor_loc": "Zack Wheeler", "era_ab_loc": 2.60, "whip_ab_loc": 0.98, "xera_loc": 2.50, "fip_loc": 2.70,
        "abridor_vis": "Chris Sale", "era_ab_vis": 2.75, "whip_ab_vis": 1.01, "xera_vis": 2.65, "fip_vis": 2.80,
        "bullpen_era_loc": 3.20, "bullpen_fatiga_loc": "BAJA",
        "bullpen_era_vis": 3.30, "bullpen_fatiga_vis": "BAJA",
        "lesionados_vis": ["Ronald Acuña Jr."], "lesionados_loc": ["Trea Turner"],
        "wrc_lineup_vis": 112, "wrc_lineup_loc": 115,
        "umpire_tendencia": "Under (Zona estricta para pitchers, -0.4 carreras)",
        "park_factor": 1.00, "temperatura": "26°C", "viento": "3 mph calma", "linea_ou": 7.0,
        "apuestas_publico_fav": "68% con Phillies", "cuota_apertura": -130, "cuota_actual": -115, "rlm_detectado": True
    }
}

# Extraemos los datos específicos del partido seleccionado por el usuario
datos_juego = base_datos_mlb[partido_seleccionado]

# --- 3. BOTÓN DE PROCESAMIENTO ---
if st.button("🔥 EJECUTAR ANÁLISIS PROFESIONAL", use_container_width=True):
    
    # El motor matemático dinámico lee las variables específicas del juego elegido
    carreras_proyectadas_vis = (5.0 * (datos_juego["wrc_lineup_vis"]/100)) - (len(datos_juego["lesionados_vis"]) * 0.25) + (datos_juego["whip_ab_loc"] * 0.4)
    carreras_proyectadas_loc = (4.2 * (datos_juego["wrc_lineup_loc"]/100)) - (len(datos_juego["lesionados_loc"]) * 0.25) + (datos_juego["whip_ab_vis"] * 0.3)
    
    # Ajuste multiplicador por estadio
    carreras_proyectadas_vis *= datos_juego["park_factor"]
    carreras_proyectadas_loc *= datos_juego["park_factor"]
    
    # Simulación Matemática de Montecarlo (10,000 iteraciones en vivo)
    sim_vis = np.random.poisson(carreras_proyectadas_vis, 10000)
    sim_loc = np.random.poisson(carreras_proyectadas_loc, 10000)
    
    # Cálculos probabilísticos basados en la simulación
    prob_ganador_vis = (np.sum(sim_vis > sim_loc) / 10000) * 10
