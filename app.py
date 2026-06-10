import streamlit as st
import numpy as np
from datetime import datetime
import pytz

st.set_page_config(page_title="Statline Predictor Pro", layout="wide")

st.title("🧠 Statline Predictor Pro - SHARP SYSTEM")
st.write("Calendario automatizado en tiempo real. Los partidos en desarrollo se eliminan automáticamente.")

# --- 1. CONFIGURACIÓN DEL RELOJ EN VIVO (Zona Horaria) ---
# Usamos la zona horaria estándar para sincronizar con los juegos (puedes cambiarla a tu país)
zona_horaria = pytz.timezone('America/New_York')
hora_actual = datetime.now(zona_horaria)

st.sidebar.markdown(f"🕒 **Hora del Servidor (ET):** {hora_actual.strftime('%I:%M %p')}")

# --- 2. BASE DE DATOS DINÁMICA CON HORARIOS DE JUEGOS ---
# El formato de hora es militar (24h) para que el código pueda comparar matemáticamente
calendario_completo = {
    "Los Angeles Dodgers vs Pittsburgh Pirates": {"hora_inicio": "19:05", "datos_key": "LAD_PIT"},
    "New York Yankees vs Boston Red Sox": {"hora_inicio": "19:10", "datos_key": "NYY_BOS"},
    "Houston Astros vs New York Mets": {"hora_inicio": "20:10", "datos_key": "HOU_NYM"},
    "Atlanta Braves vs Philadelphia Phillies": {"hora_inicio": "22:00", "datos_key": "ATL_PHI"}
}

# --- 3. FILTRO AUTOMÁTICO DE PARTIDOS EN VIVO ---
partidos_disponibles = []

for partido, info in calendario_completo.items():
    # Convertimos la hora de inicio del partido a un objeto de tiempo para comparar
    hora_juego = datetime.strptime(info["hora_inicio"], "%H:%M").time()
    
    # Si la hora actual es MENOR que la hora del juego, el partido NO ha empezado. Lo dejamos.
    if hora_actual.time() < hora_juego:
        partidos_disponibles.append(partido)

# Añadimos la opción mágica para que puedas editar o escribir el partido que tú quieras
partidos_disponibles.append("➕ ANALIZAR OTRO PARTIDO (ENTRADA MANUAL)")

# --- 4. INTERFAZ VISUAL DESPLEGABLE ---
partido_seleccionado = st.selectbox("🎯 Selecciona un partido disponible para hoy:", partidos_disponibles)

# Si el usuario elige la opción manual, se activan los campos de texto para escribir
if partido_seleccionado == "➕ ANALIZAR OTRO PARTIDO (ENTRADA MANUAL)":
    st.markdown("### 📝 Configura tu Partido Personalizado")
    col_v, col_l = st.columns(2)
    with col_v: equipo_vis = st.text_input("Equipo Visitante:", "New York Yankees")
    with col_l: equipo_loc = st.text_input("Equipo Local:", "Boston Red Sox")
    nombre_clave = f"{equipo_vis} vs {equipo_loc}"
else:
    nombre_clave = partido_seleccionado

# --- 5. DICCIONARIO MAESTRO DE ESTADÍSTICAS AUTOMÁTICAS ---
# Cuando el usuario escribe o selecciona un equipo, el sistema "arrastra" estos perfiles estadísticos profesionales
perfiles_estadisticos = {
    "Dodgers": {"wrc": 122, "era_ab": 2.10, "whip_ab": 0.88, "xera": 2.45, "fip": 2.30, "bp_era": 3.45, "bp_fatiga": "BAJA", "lesionados": ["Mookie Betts"]},
    "Pirates": {"wrc": 92, "era_ab": 4.80, "whip_ab": 1.42, "xera": 4.65, "fip": 4.80, "bp_era": 4.10, "bp_fatiga": "ALTA", "lesionados": ["David Bednar"]},
    "Yankees": {"wrc": 125, "era_ab": 2.85, "whip_ab": 1.02, "xera": 2.90, "fip": 3.10, "bp_era": 3.15, "bp_fatiga": "BAJA", "lesionados": []},
    "Red Sox": {"wrc": 104, "era_ab": 4.15, "whip_ab": 1.30, "xera": 4.10, "fip": 3.95, "bp_era": 3.90, "bp_fatiga": "MODERADA", "lesionados": []},
    "Astros": {"wrc": 110, "era_ab": 3.40, "whip_ab": 1.22, "xera": 3.50, "fip": 3.65, "bp_era": 3.80, "bp_fatiga": "MODERADA", "lesionados": ["Kyle Tucker"]},
    "Mets": {"wrc": 108, "era_ab": 3.10, "whip_ab": 1.15, "xera": 3.25, "fip": 3.40, "bp_era": 3.60, "bp_fatiga": "BAJA", "lesionados": ["Francisco Lindor"]},
    "Braves": {"wrc": 112, "era_ab": 2.75, "whip_ab": 1.01, "xera": 2.65, "fip": 2.80, "bp_era": 3.30, "bp_fatiga": "BAJA", "lesionados": ["Ronald Acuña Jr."]},
    "Phillies": {"wrc": 115, "era_ab": 2.60, "whip_ab": 0.98, "xera": 2.50, "fip": 2.70, "bp_era": 3.20, "bp_fatiga": "BAJA", "lesionados": ["Trea Turner"]}
}

# --- 6. PROCESADOR DE DATOS DE ENTRADA ---
# Si el usuario escribe un equipo que no está en la lista, el sistema le asigna valores promedio de la liga automáticamente
def obtener_datos_equipo(nombre_buscar):
    for clave, datos in perfiles_estadisticos.items():
        if clave.lower() in nombre_buscar.lower():
            return datos
    # Perfil por defecto (Promedio de la MLB si el equipo es nuevo o editado libremente)
    return {"wrc": 100, "era_ab": 3.90, "whip_ab": 1.20, "xera": 3.95, "fip": 4.00, "bp_era": 3.85, "bp_fatiga": "MODERADA", "lesionados": []}

# Separamos los nombres para buscar sus estadísticas
if " vs " in nombre_clave:
    v_team, l_team = nombre_clave.split(" vs ")
else:
    v_team, l_team = "Dodgers", "Pirates"

stats_vis = obtener_datos_equipo(v_team)
stats_loc = obtener_datos_equipo(l_team)

# --- 7. BOTÓN DE PROCESAMIENTO MATEMÁTICO ---
if st.button("🔥 EJECUTAR ANÁLISIS PROFESIONAL", use_container_width=True):
    
    # Fórmulas Sabermétricas Avanzadas aplicando las variables arrastradas
    carreras_proyectadas_vis = (5.0 * (stats_vis["wrc"]/100)) - (len(stats_vis["lesionados"]) * 0.25) + (stats_loc["whip_ab"] * 0.4)
    carreras_proyectadas_loc = (4.2 * (stats_loc["wrc"]/100)) - (len(stats_loc["lesionados"]) * 0.25) + (stats_vis["whip_ab"] * 0.3)
    
    # Simulador de Montecarlo (10,000 juegos en un milisegundo)
    sim_vis = np.random.poisson(carreras_proyectadas_vis, 10000)
    sim_loc = np.random.poisson(carreras_proyectadas_loc, 10000)
    
    prob_ganador_vis = (np.sum(sim_vis > sim_loc) / 10000) * 100
    prob_ganador_loc = 100 - prob_ganador_vis
    prob_over = (np.sum((sim_vis + sim_loc) > 8.5) / 10000) * 100
    
    ganador_proyectado = v_team if prob_ganador_vis > prob_ganador_loc else l_team
    porcentaje_ganador = max(prob_ganador_vis, prob_ganador_loc)
    linea_totales_texto = "OVER 8.5" if prob_over > 50 else "UNDER 8.5"
    porcentaje_totales = prob_over if prob_over > 50 else (100 - prob_over)

    # Despliegue de Resultados Dinámicos
    st.markdown(f"## 📊 Análisis Cuantitativo Final: {v_team} vs {l_team}")
    res1, res2 = st.columns(2)
    with res1: st.metric("🏆 GANADOR PROYECTADO", ganador_proyectado, f"{round(porcentaje_ganador, 1)}% Probabilidad")
    with res2: st.metric("📈 TOTAL (Over/Under)", linea_totales_texto, f"{round(porcentaje_totales, 1)}% Probabilidad")

    # --- 8. REPORTE EXPLICATIVO AUTOMÁTICO ---
    st.markdown("---")
    st.markdown("### 📋 Justificación Técnico-Analítica")
    
    lesiones_vis_texto = ", ".join(stats_vis["lesionados"]) if stats_vis["lesionados"] else "Ninguna baja"
    lesiones_loc_texto = ", ".join(stats_loc["lesionados"]) if stats_loc["lesionados"] else "Ninguna baja"
    
    st.info(f"""
    * **Duelo de Abridores:** El pitcheo de {v_team} presenta un xERA de {stats_vis['xera']} y un WHIP de {stats_vis['whip_ab']} frente al abridor de {l_team} que registra un FIP de {stats_loc['fip']} y un WHIP de {stats_loc['whip_ab']}.
    * **Situación del Bullpen:** El relevo intermedio de {l_team} maneja un ERA colectivo de {stats_loc['bp_era']} con una fatiga calificada como {stats_loc['bp_fatiga']}.
    * **Fuerza Ofensiva Arrastrada:** El lineup activo de {v_team} posee un poder base de {stats_vis['wrc']} wRC+, descontando la baja por lesión de: [{lesiones_vis_texto}]. El lineup de {l_team} genera {stats_loc['wrc']} wRC+, resintiendo a: [{lesiones_loc_texto}].
    """)
