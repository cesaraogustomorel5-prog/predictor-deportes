import streamlit as st
import numpy as np
import datetime

st.set_page_config(page_title="Statline Predictor Pro", layout="wide")

# --- ENCABEZADO Y FECHA ---
st.title("🧠 Statline Predictor Pro - SHARP SYSTEM")
fecha_hoy = datetime.date.today().strftime("%d de %B de %Y")
st.write(f"📅 **Fecha de Análisis:** {fecha_hoy}")
st.write("Sistema Híbrido: Selección automatizada o edición manual avanzada.")

# --- 1. BASE DE DATOS DE PARTIDOS PRE-CARGADOS ---
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
    "🔧 MODO MANUAL (Ingresar datos propios)": {
        "local": "Equipo Local", "visitante": "Equipo Visitante",
        "abridor_loc": "Pitcher Local", "era_ab_loc": 4.00, "whip_ab_loc": 1.20, "xera_loc": 4.00, "fip_loc": 4.00,
        "abridor_vis": "Pitcher Visitante", "era_ab_vis": 4.00, "whip_ab_vis": 1.20, "xera_vis": 4.00, "fip_vis": 4.00,
        "bullpen_era_loc": 4.00, "bullpen_fatiga_loc": "BAJA",
        "bullpen_era_vis": 4.00, "bullpen_fatiga_vis": "BAJA",
        "lesionados_vis": [], "lesionados_loc": [],
        "wrc_lineup_vis": 100, "wrc_lineup_loc": 100,
        "umpire_tendencia": "Neutral (Zona estándar)",
        "park_factor": 1.00, "temperatura": "25°C", "viento": "0 mph", "linea_ou": 8.5,
        "apuestas_publico_fav": "50% Dividido", "cuota_apertura": -110, "cuota_actual": -110, "rlm_detectado": False
    }
}

# --- 2. SELECCIÓN DEL PARTIDO ---
opciones = list(base_datos_mlb.keys())
seleccion = st.selectbox("🎯 Selecciona un partido del día o activa el Modo Manual:", opciones)

# Cargamos los datos por defecto según la selección
datos_defecto = base_datos_mlb[seleccion]

st.markdown("---")
st.subheader("🛠️ Panel de Edición de Variables (Edita lo que quieras aquí abajo)")

# --- 3. FORMULARIO INTERACTIVO (PERMITE EDICIÓN MANUAL SIEMPRE) ---
# Usamos columnas para que se vea ordenado en el celular
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🏠 EQUIPO LOCAL")
    eq_local = st.text_input("Nombre del Equipo Local:", datos_defecto["local"])
    p_local = st.text_input("Pitcher Abridor Local:", datos_defecto["abridor_loc"])
    era_loc = st.number_input("ERA Abridor Local:", value=datos_defecto["era_ab_loc"], format="%.2f")
    whip_loc = st.number_input("WHIP Abridor Local:", value=datos_defecto["whip_ab_loc"], format="%.2f")
    fip_loc = st.number_input("FIP Abridor Local:", value=datos_defecto["fip_loc"], format="%.2f")
    bp_era_loc = st.number_input("Bullpen ERA Local:", value=datos_defecto["bullpen_era_loc"], format="%.2f")
    bp_fatiga_loc = st.selectbox("Fatiga Bullpen Local:", ["BAJA", "MODERADA", "ALTA"], index=["BAJA", "MODERADA", "ALTA"].index(datos_defecto["bullpen_fatiga_loc"]))
    wrc_loc = st.number_input("Fuerza Bateo Local (wRC+):", value=datos_defecto["wrc_lineup_loc"])

with col2:
    st.markdown("### 🚀 EQUIPO VISITANTE")
    eq_vis = st.text_input("Nombre del Equipo Visitante:", datos_defecto["visitante"])
    p_vis = st.text_input("Pitcher Abridor Visitante:", datos_defecto["abridor_vis"])
    era_vis = st.number_input("ERA Abridor Visitante:", value=datos_defecto["era_ab_vis"], format="%.2f")
    whip_vis = st.number_input("WHIP Abridor Visitante:", value=datos_defecto["whip_ab_vis"], format="%.2f")
    fip_vis = st.number_input("FIP Abridor Visitante:", value=datos_defecto["fip_vis"], format="%.2f")
    bp_era_vis = st.number_input("Bullpen ERA Visitante:", value=datos_defecto["bullpen_era_vis"], format="%.2f")
    bp_fatiga_vis = st.selectbox("Fatiga Bullpen Visitante:", ["BAJA", "MODERADA", "ALTA"], index=["BAJA", "MODERADA", "ALTA"].index(datos_defecto["bullpen_fatiga_vis"]))
    wrc_vis = st.number_input("Fuerza Bateo Visitante (wRC+):", value=datos_defecto["wrc_lineup_vis"])

st.markdown("### 🏟️ Entorno, Líneas y Cuotas del Casino")
col3, col4 = st.columns(2)
with col3:
    linea_ou = st.number_input("Línea de Over/Under del Casino:", value=datos_defecto["linea_ou"], step=0.5)
    park_f = st.number_input("Factor de Estadio (Park Factor):", value=datos_defecto["park_factor"], format="%.2f")
    umpire = st.text_input("Tendencia del Umpire:", datos_defecto["umpire_tendencia"])
with col4:
    pub_fav = st.text_input("Apuestas del Público:", datos_defecto["apuestas_publico_fav"])
    c_apertura = st.number_input("Cuota Apertura:", value=datos_defecto["cuota_apertura"])
    c_actual = st.number_input("Cuota Actual:", value=datos_defecto["cuota_actual"])
    rlm_check = st.checkbox("¿Activar Alerta de Movimiento Inverso (RLM)?", value=datos_defecto["rlm_detectado"])

# --- 4. EJECUCIÓN DEL PROCESAMIENTO ---
st.markdown("---")
if st.button("🔥 EJECUTAR ANÁLISIS PROFESIONAL CON ESTOS DATOS", use_container_width=True):
    
    # El motor matemático procesa estrictamente lo que esté escrito en los cuadros de texto editables
    carreras_proyectadas_vis = (5.0 * (wrc_vis/100)) + (whip_loc * 0.4)
    carreras_proyectadas_loc = (4.2 * (wrc_loc/100)) + (whip_vis * 0.3)
    
    # Multiplicador por estadio
    carreras_proyectadas_vis *= park_f
    carreras_proyectadas_loc *= park_f
    
    # Simulación de Montecarlo (10,000 juegos usando los datos del formulario)
    sim_vis = np.random.poisson(carreras_proyectadas_vis, 10000)
    sim_loc = np.random.poisson(carreras_proyectadas_loc, 10000)
    
    prob_ganador_vis = (np.sum(sim_vis > sim_loc) / 10000) * 100
    prob_ganador_loc = 100 - prob_ganador_vis
    prob_over = (np.sum((sim_vis + sim_loc) > linea_ou) / 10000) * 100
    
    ganador_proyectado = eq_vis if prob_ganador_vis > prob_ganador_loc else eq_local
    porcentaje_ganador = max(prob_ganador_vis, prob_gan
