
import streamlit as st
import numpy as np

st.set_page_config(page_title="Statline Predictor AI", layout="wide")

st.title("⚾ Statline Predictor AI")
st.write("Calculadora de Probabilidades Avanzada para Béisbol")

# Formulario adaptable
col1, col2 = st.columns(2)

with col1:
    st.subheader("Líneas de las Casas de Apuestas")
    linea_total = st.number_input("Línea Over/Under del partido:", value=8.5, step=0.5)
    linea_runline = st.number_input("Runline del Favorito (Ej: -1.5):", value=-1.5, step=0.5)

with col2:
    st.subheader("Datos Proyectados del Partido")
    eq_local = st.text_input("Equipo Local:", value="Yankees")
    carreras_local = st.number_input(f"Carreras estimadas para {eq_local}:", value=4.5, step=0.1)
    
    st.markdown("---")
    
    eq_vis = st.text_input("Equipo Visitante:", value="Red Sox")
    carreras_vis = st.number_input(f"Carreras estimadas para {eq_vis}:", value=4.0, step=0.1)

if st.button("🔥 GENERAR PRONÓSTICO", use_container_width=True):
    sim_loc = np.random.poisson(carreras_local, 10000)
    sim_vis = np.random.poisson(carreras_vis, 10000)
    
    ganas_loc = np.sum(sim_loc > sim_vis) / 10000
    ganas_vis = np.sum(sim_vis > sim_loc) / 10000
    total_decidido = ganas_loc + ganas_vis
    prob_ganador_loc = (ganas_loc / total_decidido) * 100
    prob_ganador_vis = (ganas_vis / total_decidido) * 100
    
    totales_simulados = sim_loc + sim_vis
    prob_over = np.sum(totales_simulados > linea_total) / 10000 * 100
    prob_under = np.sum(totales_simulados < linea_total) / 10000 * 100
    
    diferencia = sim_loc - sim_vis
    if linea_runline < 0:
        prob_cubrir_favorito = np.sum(diferencia > abs(linea_runline)) / 10000 * 100
        label_runline = f"{eq_local} {linea_runline}"
        label_dog = f"{eq_vis} +{abs(linea_runline)}"
    else:
        prob_cubrir_favorito = np.sum(sim_vis - sim_loc > linea_runline) / 10000 * 100
        label_runline = f"{eq_vis} -{linea_runline}"
        label_dog = f"{eq_local} +{linea_runline}"
    prob_cubrir_dog = 100 - prob_cubrir_favorito

    st.markdown("### 📊 Resultados del Análisis")
    res1, res2, res3 = st.columns(3)
    
    with res1:
        st.metric(label="🏆 GANADOR (Moneyline)", value=eq_local if prob_ganador_loc > prob_ganador_vis else eq_vis)
        st.write(f"{eq_local}: **{round(prob_ganador_loc, 1)}%**")
        st.write(f"{eq_vis}: **{round(prob_ganador_vis, 1)}%**")
        
    with res2:
        pred_ou = "OVER" if prob_over > prob_under else "UNDER"
        st.metric(label="📈 TOTAL (Over/Under)", value=f"{pred_ou} ({linea_total})")
        st.write(f"OVER: **{round(prob_over, 1)}%**")
        st.write(f"UNDER: **{round(prob_under, 1)}%**")
        
    with res3:
        pred_rl = label_runline if prob_cubrir_favorito > prob_cubrir_dog else label_dog
        st.metric(label="⚾ RUNLINE (Hándicap)", value=pred_rl)
        st.write(f"{label_runline}: **{round(prob_cubrir_favorito, 1)}%**")
        st.write(f"{label_dog}: **{round(prob_cubrir_dog, 1)}%**")
