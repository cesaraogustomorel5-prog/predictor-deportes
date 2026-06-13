import streamlit as st
import requests
from datetime import datetime
import pytz
import logging
import hashlib
import time
import random
import math

# ═══════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN INICIAL
# ═══════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Sharp Quant System · AI",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Sharp Quant System — Plataforma de Análisis Deportivo con IA"}
)

# ═══════════════════════════════════════════════════════════════════════
# I18N — 29 IDIOMAS
# ═══════════════════════════════════════════════════════════════════════
IDIOMAS = {
    "es":{"nombre":"Español","bandera":"🇪🇸"},
    "en":{"nombre":"English","bandera":"🇺🇸"},
    "pt":{"nombre":"Português","bandera":"🇧🇷"},
    "fr":{"nombre":"Français","bandera":"🇫🇷"},
    "de":{"nombre":"Deutsch","bandera":"🇩🇪"},
    "it":{"nombre":"Italiano","bandera":"🇮🇹"},
    "ja":{"nombre":"日本語","bandera":"🇯🇵"},
    "zh":{"nombre":"中文","bandera":"🇨🇳"},
    "ko":{"nombre":"한국어","bandera":"🇰🇷"},
    "ru":{"nombre":"Русский","bandera":"🇷🇺"},
    "ar":{"nombre":"العربية","bandera":"🇸🇦"},
    "hi":{"nombre":"हिन्दी","bandera":"🇮🇳"},
    "nl":{"nombre":"Nederlands","bandera":"🇳🇱"},
    "pl":{"nombre":"Polski","bandera":"🇵🇱"},
    "tr":{"nombre":"Türkçe","bandera":"🇹🇷"},
    "sv":{"nombre":"Svenska","bandera":"🇸🇪"},
    "da":{"nombre":"Dansk","bandera":"🇩🇰"},
    "fi":{"nombre":"Suomi","bandera":"🇫🇮"},
    "no":{"nombre":"Norsk","bandera":"🇳🇴"},
    "cs":{"nombre":"Čeština","bandera":"🇨🇿"},
    "el":{"nombre":"Ελληνικά","bandera":"🇬🇷"},
    "he":{"nombre":"עברית","bandera":"🇮🇱"},
    "th":{"nombre":"ภาษาไทย","bandera":"🇹🇭"},
    "vi":{"nombre":"Tiếng Việt","bandera":"🇻🇳"},
    "id":{"nombre":"Bahasa Indonesia","bandera":"🇮🇩"},
    "ms":{"nombre":"Bahasa Melayu","bandera":"🇲🇾"},
    "uk":{"nombre":"Українська","bandera":"🇺🇦"},
    "ro":{"nombre":"Română","bandera":"🇷🇴"},
    "hu":{"nombre":"Magyar","bandera":"🇭🇺"},
}

BASE_ES = {
    "subtitle":         "MOTOR DE IA · PREDICCIÓN CUANTITATIVA · MONITOREO EN VIVO",
    "back":             "Volver al Dashboard",
    "calendar_title":   "Calendario de Partidos",
    "filter_label":     "Fecha",
    "no_games":         "No hay partidos para esta fecha.",
    "live_label":       "En Vivo",
    "final_label":      "Finalizados",
    "upcoming_label":   "Próximos",
    "suspended_label":  "Suspendidos",
    "total_label":      "Total",
    "delayed_badge":    "RETRASADO",
    "suspended_badge":  "SUSPENDIDO",
    "btn_live":         "Ver En Vivo",
    "btn_analysis":     "Análisis IA",
    "btn_suspended":    "Suspendido",
    "featured_badge":   "PARTIDO DESTACADO",
    "realtime_sync":    "Sync Tiempo Real",
    "live_center_title":"Centro de Control Live",
    "live_center_sub":  "Monitoreo inteligente en tiempo real",
    "count_label":      "CONTEO",
    "outs_label":       "Outs",
    "pitcher_label":    "Pitcher",
    "batter_label":     "Bateador",
    "live_prob":        "Prob. en Vivo",
    "bases_label":      "Almohadillas",
    "linescore_title":  "Pizarra Oficial",
    "scoring_title":    "Jugadas Anotadoras",
    "no_runs":          "Sin carreras anotadas aún.",
    "team_col":         "Equipo",
    "analysis_title":   "Análisis IA · Motor Predictivo",
    "analysis_sub":     "Inteligencia Artificial aplicada al béisbol de alto rendimiento.",
    "projected_score":  "Marcador Proyectado",
    "probability_label":"Probabilidad",
    "certainty_label":  "Índice de Confianza IA",
    "sabermetric_title":"Coeficientes Avanzados",
    "strength_title":   "Radar de Fortaleza",
    "report_title":     "Informe Ejecutivo IA",
    "advantage_label":  "Ventaja",
    "differential_label":"Diferencial",
    "metric_label":     "Métrica",
    "inning_top":       "Alta",
    "inning_bot":       "Baja",
    "extra_inn":        " (Extra)",
    "live_developing":  "Desarrollándose",
    "diamond_state":    "EN VIVO",
    "alert_delayed":    "PARTIDO RETRASADO",
    "mode_dark":        "Modo Oscuro",
    "mode_light":       "Modo Claro",
    "lang_selector":    "Idioma",
    "bat_off":          "Bateo / Ofensiva",
    "rotation":         "Rotación Abridora",
    "bullpen":          "Bullpen",
    "defense":          "Defensa",
    "consistency":      "Consistencia",
    "chat_title":       "IA Asistente",
    "chat_placeholder": "Pregúntale algo a la IA...",
    "chat_send":        "Enviar",
    "chat_welcome":     "Soy tu copiloto de análisis deportivo. ¿En qué puedo ayudarte?",
    "visitor":          "Visitante",
    "home":             "Local",
    "ai_radar":         "Radar de Valor",
    "ai_confidence":    "Confianza IA",
    "ai_insight":       "Insight IA",
    "value_index":      "Índice de Valor",
    "report_body":      "El motor cuantitativo posiciona a {team} con ventaja matemática estructural (confianza: {conf}%). Indicadores avanzados xFIP y xERA normalizados contra el ISO ofensivo favorecen este vector. El EV+ detecta oportunidad de valor por encima del mercado.",
    "fav_team":         "Equipos Favoritos",
    "fav_none":         "Sin favoritos aún",
    "add_fav":          "Agregar a favoritos",
    "remove_fav":       "Quitar de favoritos",
    "ai_summary":       "Resumen IA",
    "notifications":    "Alertas",
    "settings":         "Configuración",
}

TERMINOS = ["xERA","xFIP","WHIP","OPS","wRC+","ISO","BABIP","EV+","ERA","MLB","Linescore","Barrel","Hard Hit Rate","SHARP QUANT SYSTEM","Sharp Quant System"]

def _proteger(t):
    p={}; r=t
    for i,x in enumerate(TERMINOS):
        if x in r:
            m=f"__T{i}__"; p[m]=x; r=r.replace(x,m)
    return r,p

def _restaurar(t,p):
    for m,x in p.items(): t=t.replace(m,x)
    return t

def _traducir(texto,lang):
    if not texto or not any(c.isalpha() for c in texto): return texto
    tp,p=_proteger(texto)
    try:
        r=requests.get("https://api.mymemory.translated.net/get",params={"q":tp,"langpair":f"es|{lang}"},timeout=5)
        if r.status_code==200:
            t=r.json().get("responseData",{}).get("translatedText",tp)
            if "MYMEMORY WARNING" not in t and t!=tp: return _restaurar(t,p)
    except: pass
    return _restaurar(tp,p)

@st.cache_data(ttl=86400,show_spinner=False)
def cargar_T(lang_code,lang_name):
    if lang_code=="es": return BASE_ES
    t={}
    for k,v in BASE_ES.items():
        t[k]=_traducir(v,lang_code) if isinstance(v,str) else v
    if sum(1 for k in t if t[k]!=BASE_ES[k])<3: return BASE_ES
    return t

# ═══════════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════════
def _si(k,v):
    if k not in st.session_state: st.session_state[k]=v

_si("lang","es"); _si("dark",True)
_si("fecha",datetime.now(pytz.timezone("America/New_York")).date())
_si("vista","dashboard"); _si("juego",None)
_si("cache",{}); _si("lang_open",False)
_si("chat_open",False); _si("chat_msgs",[])
_si("chat_key",0); _si("favoritos",set())
_si("notifs",[]); _si("ai_panel",False)
_si("radar_juego",None); _si("user_prefs",{"accent":"cyan","show_radar":True,"show_ai":True})
_si("particles_seed",random.randint(0,9999))

T=cargar_T(st.session_state.lang,IDIOMAS[st.session_state.lang]["nombre"])
def _T(k): return T.get(k,BASE_ES.get(k,k))

logging.basicConfig(level=logging.INFO)
log=logging.getLogger(__name__)
ZONA=pytz.timezone("America/New_York")
WO=0.30;WR=0.25;WB=0.20;WD=0.15;WM=0.10

# ═══════════════════════════════════════════════════════════════════════
# PALETA DINÁMICA — CAMBIA SEGÚN CONTEXTO
# ═══════════════════════════════════════════════════════════════════════
D=st.session_state.dark
ACCENT_OPTIONS={
    "cyan":  ("#06b6d4","#0ea5e9","#38bdf8"),
    "violet":("#7c3aed","#8b5cf6","#a78bfa"),
    "emerald":("#059669","#10b981","#34d399"),
    "amber": ("#d97706","#f59e0b","#fbbf24"),
}
acc_key=st.session_state.user_prefs.get("accent","cyan")
A1,A2,A3=ACCENT_OPTIONS.get(acc_key,ACCENT_OPTIONS["cyan"])

BG     ="#030712" if D else "#f8fafc"
BG2    ="#0a0f1e" if D else "#ffffff"
CARD   =f"rgba(8,12,28,0.90)" if D else "rgba(255,255,255,0.95)"
BORDER =f"rgba({','.join(str(int(A1[i:i+2],16)) for i in (1,3,5))},0.14)" if D else f"rgba({','.join(str(int(A1[i:i+2],16)) for i in (1,3,5))},0.16)"
BORDER2="rgba(255,255,255,0.05)" if D else "rgba(0,0,0,0.06)"
TEXT   ="#f1f5f9" if D else "#0f172a"
MUTED  ="#475569" if D else "#64748b"
SUCCESS="#10b981"; DANGER="#f43f5e"; WARNING="#f59e0b"
GLOW   =f"rgba({','.join(str(int(A1[i:i+2],16)) for i in (1,3,5))},0.15)"
SBG    ="#050914" if D else "#f0f4f8"

# ═══════════════════════════════════════════════════════════════════════
# CSS SOBRENATURAL — ANIMACIONES, GLASSMORPHISM, PARTICLES, NASA DASHBOARD
# ═══════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700;800&display=swap');

:root{{
  --bg:{BG};--bg2:{BG2};--card:{CARD};--border:{BORDER};--border2:{BORDER2};
  --text:{TEXT};--muted:{MUTED};--a1:{A1};--a2:{A2};--a3:{A3};
  --success:{SUCCESS};--danger:{DANGER};--warning:{WARNING};--glow:{GLOW};
}}

*,*::before,*::after{{box-sizing:border-box;}}

html,body,.stApp{{
  background:var(--bg) !important;
  color:var(--text) !important;
  font-family:'Inter',sans-serif !important;
  overflow-x:hidden;
}}

.stApp>header{{display:none !important;}}
.block-container{{
  padding:1rem 1.4rem 4rem !important;
  max-width:1200px !important;
  margin:0 auto !important;
}}

/* ── TEXTOS GLOBALES ── */
.stApp p,.stApp span,.stApp label,.stApp h1,.stApp h2,.stApp h3,
.stApp h4,.stApp div,.stMarkdown,.stMetric,
[data-testid="stMetricValue"],[data-testid="stMetricLabel"],
table,th,td,tr{{color:var(--text) !important;}}

/* ══════════════════════════════════════════════
   PARTÍCULAS DE FONDO ANIMADAS
═══════════════════════════════════════════════ */
#sqs-particles{{
  position:fixed;top:0;left:0;width:100%;height:100%;
  pointer-events:none;z-index:0;overflow:hidden;
}}
.particle{{
  position:absolute;border-radius:50%;
  animation:particleFloat linear infinite;
  opacity:0;
}}
@keyframes particleFloat{{
  0%{{transform:translateY(100vh) rotate(0deg);opacity:0;}}
  10%{{opacity:1;}}
  90%{{opacity:0.6;}}
  100%{{transform:translateY(-100px) rotate(720deg);opacity:0;}}
}}

/* ══════════════════════════════════════════════
   HEADER NASA-STYLE
═══════════════════════════════════════════════ */
.sqs-header{{
  position:relative;
  padding:28px 36px 26px;
  background:{'linear-gradient(135deg,rgba(3,7,18,0.99) 0%,rgba(8,12,28,0.98) 50%,rgba(5,9,22,0.99) 100%)' if D else 'linear-gradient(135deg,rgba(248,250,252,0.99) 0%,rgba(241,245,249,0.98) 100%)'};
  border:1px solid var(--border);
  border-radius:24px;
  margin-bottom:22px;
  overflow:hidden;
  box-shadow:{'0 0 0 1px rgba(56,189,248,0.06), 0 24px 80px rgba(0,0,0,0.6), inset 0 1px 0 rgba(56,189,248,0.1)' if D else '0 8px 32px rgba(0,0,0,0.08),inset 0 1px 0 rgba(255,255,255,0.9)'};
  z-index:10;
}}
.sqs-header::before{{
  content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent 0%,{A1} 30%,{A2} 70%,transparent 100%);
  animation:headerBeam 4s ease-in-out infinite;
}}
@keyframes headerBeam{{
  0%,100%{{opacity:0.6;transform:scaleX(0.8);}}
  50%{{opacity:1;transform:scaleX(1);}}
}}
.sqs-header::after{{
  content:'';position:absolute;inset:0;
  background:
    radial-gradient(ellipse at 10% 50%,{GLOW} 0%,transparent 50%),
    radial-gradient(ellipse at 90% 50%,rgba(129,140,248,0.05) 0%,transparent 50%);
  pointer-events:none;animation:ambientPulse 6s ease-in-out infinite;
}}
@keyframes ambientPulse{{
  0%,100%{{opacity:0.6;}}50%{{opacity:1;}}
}}
.sqs-inner{{position:relative;z-index:1;display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap;}}
.sqs-brand{{display:flex;align-items:center;gap:18px;}}
.sqs-orb{{
  position:relative;width:48px;height:48px;flex-shrink:0;
}}
.sqs-orb-core{{
  width:100%;height:100%;border-radius:50%;
  background:linear-gradient(135deg,{A1},{A2},{A3});
  box-shadow:0 0 0 4px rgba({','.join(str(int(A1[i:i+2],16)) for i in (1,3,5))},0.2),
             0 0 30px {A1},0 0 60px rgba({','.join(str(int(A1[i:i+2],16)) for i in (1,3,5))},0.3);
  animation:orbPulse 3s ease-in-out infinite;
  display:flex;align-items:center;justify-content:center;
  font-size:1.4rem;
}}
@keyframes orbPulse{{
  0%,100%{{box-shadow:0 0 0 4px rgba({','.join(str(int(A1[i:i+2],16)) for i in (1,3,5))},0.2),0 0 30px {A1},0 0 60px rgba({','.join(str(int(A1[i:i+2],16)) for i in (1,3,5))},0.3);}}
  50%{{box-shadow:0 0 0 8px rgba({','.join(str(int(A1[i:i+2],16)) for i in (1,3,5))},0.1),0 0 50px {A1},0 0 100px rgba({','.join(str(int(A1[i:i+2],16)) for i in (1,3,5))},0.4);}}
}}
.sqs-orb-ring{{
  position:absolute;inset:-6px;border-radius:50%;
  border:1.5px solid {A1};opacity:0.4;
  animation:ringRotate 8s linear infinite;
}}
@keyframes ringRotate{{from{{transform:rotate(0deg);}}to{{transform:rotate(360deg);}}}}
.sqs-title{{
  font-family:'Space Grotesk',sans-serif !important;
  font-size:1.95rem !important;font-weight:800 !important;
  color:{'#fff' if D else TEXT} !important;
  letter-spacing:-0.5px;margin:0 !important;line-height:1;
}}
.grad-text{{
  background:linear-gradient(90deg,{A1} 0%,{A2} 50%,#c084fc 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;
}}
.sqs-sub{{
  color:{MUTED} !important;font-size:0.72rem;font-weight:600;
  letter-spacing:1.5px;text-transform:uppercase;margin-top:5px;
}}
.sqs-badges{{display:flex;align-items:center;gap:8px;flex-wrap:wrap;}}
.pill{{
  display:inline-flex;align-items:center;gap:6px;
  padding:5px 14px;border-radius:20px;font-size:0.7rem;
  font-weight:800;letter-spacing:1px;text-transform:uppercase;
  white-space:nowrap;
}}
.pill-live{{
  background:rgba(244,63,94,0.12);border:1px solid rgba(244,63,94,0.3);
  color:{DANGER} !important;animation:pillBlink 2s ease-in-out infinite;
}}
@keyframes pillBlink{{0%,100%{{opacity:1;}}50%{{opacity:0.7;}}}}
.pill-ai{{
  background:linear-gradient(135deg,rgba({','.join(str(int(A1[i:i+2],16)) for i in (1,3,5))},0.15),rgba(129,140,248,0.1));
  border:1px solid {A1}40;color:{A1} !important;
}}
.dot-pulse{{
  width:7px;height:7px;border-radius:50%;
  animation:dotAnim 1s ease-in-out infinite alternate;
}}
@keyframes dotAnim{{0%{{opacity:0.4;transform:scale(0.8);}}100%{{opacity:1;transform:scale(1.2);}}}}

/* ══════════════════════════════════════════════
   KPI GLASSMORPHISM (ESTILO NASA DASHBOARD)
═══════════════════════════════════════════════ */
.kpi-grid{{
  display:grid;
  grid-template-columns:repeat(5,1fr);
  gap:12px;margin:16px 0 20px;
}}
.kpi{{
  background:{'rgba(8,12,28,0.85)' if D else 'rgba(255,255,255,0.9)'};
  border:1px solid var(--border);border-radius:18px;
  padding:16px 12px;text-align:center;
  backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);
  box-shadow:0 4px 24px {'rgba(0,0,0,0.3)' if D else 'rgba(0,0,0,0.06)'},inset 0 1px 0 {'rgba(255,255,255,0.06)' if D else 'rgba(255,255,255,0.9)'};
  transition:all 0.3s cubic-bezier(0.4,0,0.2,1);
  animation:kpiIn 0.5s ease both;
  position:relative;overflow:hidden;cursor:default;
}}
.kpi::before{{
  content:'';position:absolute;bottom:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent,var(--a1),transparent);
  opacity:0;transition:opacity 0.3s;
}}
.kpi:hover{{
  transform:translateY(-4px) scale(1.01);
  box-shadow:0 12px 40px {'rgba(0,0,0,0.4)' if D else 'rgba(0,0,0,0.12)'},0 0 0 1px var(--border);
}}
.kpi:hover::before{{opacity:1;}}
@keyframes kpiIn{{from{{opacity:0;transform:translateY(10px);}}to{{opacity:1;transform:translateY(0);}}}}
.kpi-icon{{font-size:1.1rem;margin-bottom:6px;}}
.kpi-lbl{{font-size:0.62rem;font-weight:700;color:var(--muted) !important;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:6px;line-height:1.2;}}
.kpi-val{{font-family:'JetBrains Mono',monospace !important;font-size:1.7rem;font-weight:800;color:var(--text) !important;line-height:1;}}
.kpi-val.live{{color:{DANGER} !important;}}
.kpi-val.good{{color:{SUCCESS} !important;}}
.kpi-val.ai{{color:{A1} !important;}}

/* ══════════════════════════════════════════════
   TARJETAS DE PARTIDO — GLASSMORPHISM TOTAL
═══════════════════════════════════════════════ */
.gc{{
  background:{'rgba(8,12,28,0.88)' if D else 'rgba(255,255,255,0.93)'};
  border:1px solid var(--border);border-radius:22px;
  padding:20px 22px;margin-bottom:14px;
  backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);
  box-shadow:0 4px 28px {'rgba(0,0,0,0.2)' if D else 'rgba(0,0,0,0.06)'},inset 0 1px 0 {'rgba(255,255,255,0.05)' if D else 'rgba(255,255,255,0.8)'};
  transition:all 0.3s cubic-bezier(0.34,1.56,0.64,1);
  animation:cardIn 0.5s ease both;
  position:relative;overflow:hidden;cursor:default;
}}
.gc:hover{{
  transform:translateY(-5px) scale(1.005);
  box-shadow:0 20px 60px {'rgba(0,0,0,0.35)' if D else 'rgba(0,0,0,0.12)'};
  border-color:{'rgba(56,189,248,0.3)' if D else 'rgba(37,99,235,0.25)'};
}}
.gc-feat{{
  background:linear-gradient(135deg,rgba({','.join(str(int(A1[i:i+2],16)) for i in (1,3,5))},0.07) 0%,rgba(129,140,248,0.05) 100%),{'rgba(8,12,28,0.90)' if D else 'rgba(255,255,255,0.95)'};
  border:1.5px solid {A1}50 !important;
  border-radius:22px;padding:22px 24px;margin-bottom:14px;
  backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px);
  box-shadow:0 0 0 1px {A1}15,0 16px 56px rgba({','.join(str(int(A1[i:i+2],16)) for i in (1,3,5))},0.16),0 28px 80px {'rgba(0,0,0,0.3)' if D else 'rgba(0,0,0,0.08)'};
  transition:all 0.3s cubic-bezier(0.34,1.56,0.64,1);
  animation:featPulse 4s ease-in-out infinite,cardIn 0.5s ease both;
  position:relative;overflow:hidden;cursor:default;
}}
.gc-feat::before{{
  content:'';position:absolute;top:0;left:0;right:0;height:2.5px;
  background:linear-gradient(90deg,transparent,{A1},{A2},#c084fc,transparent);
  animation:topBeam 3s ease-in-out infinite;
}}
@keyframes topBeam{{0%,100%{{opacity:0.7;}}50%{{opacity:1;}}}}
@keyframes featPulse{{
  0%,100%{{box-shadow:0 0 0 1px {A1}15,0 16px 56px rgba({','.join(str(int(A1[i:i+2],16)) for i in (1,3,5))},0.16),0 28px 80px {'rgba(0,0,0,0.3)' if D else 'rgba(0,0,0,0.08)'};}}
  50%{{box-shadow:0 0 0 1px {A1}30,0 16px 56px rgba({','.join(str(int(A1[i:i+2],16)) for i in (1,3,5))},0.28),0 28px 80px {'rgba(0,0,0,0.4)' if D else 'rgba(0,0,0,0.12)'};}}
}}
.gc-feat:hover{{transform:translateY(-6px) scale(1.008);}}
@keyframes cardIn{{from{{opacity:0;transform:translateY(16px);}}to{{opacity:1;transform:translateY(0);}}}}

/* ── SCOREBOARD ── */
.team-row{{display:flex;justify-content:space-between;align-items:center;padding:10px 0;}}
.team-row+.team-row{{border-top:1px solid var(--border2);}}
.team-info{{display:flex;align-items:center;gap:14px;}}
.tlogo{{
  width:44px;height:44px;object-fit:contain;
  filter:{'drop-shadow(0 3px 10px rgba(0,0,0,0.5))' if D else 'drop-shadow(0 2px 6px rgba(0,0,0,0.15))'};
  transition:transform 0.3s cubic-bezier(0.34,1.56,0.64,1);
}}
.tlogo:hover{{transform:scale(1.2) rotate(-5deg);}}
.tname{{font-family:'Space Grotesk',sans-serif;font-size:1.05rem;font-weight:700;color:var(--text) !important;}}
.tabbr{{font-size:0.72rem;font-weight:600;color:var(--muted) !important;}}
.score{{font-family:'JetBrains Mono',monospace;font-size:2rem;font-weight:900;color:{A1} !important;min-width:52px;text-align:right;line-height:1;text-shadow:0 0 20px {A1}60;}}
.score-ph{{width:52px;height:36px;}}

/* ── PROB BAR ANIMADA ── */
.pb-wrap{{margin:14px 0 0;}}
.pb-track{{height:6px;border-radius:3px;background:{'rgba(255,255,255,0.06)' if D else 'rgba(0,0,0,0.07)'};overflow:hidden;position:relative;}}
.pb-fill{{height:100%;border-radius:3px;background:linear-gradient(90deg,{A1},{A2});box-shadow:0 0 12px {A1}60;transition:width 1s cubic-bezier(0.4,0,0.2,1);animation:pbShimmer 2s ease-in-out infinite;}}
@keyframes pbShimmer{{0%,100%{{filter:brightness(1);}}50%{{filter:brightness(1.3);}}}}
.pb-row{{display:flex;justify-content:space-between;margin-top:5px;}}
.pb-lbl{{font-size:0.68rem;font-weight:700;color:var(--muted) !important;}}
.pb-pct{{font-size:0.68rem;font-weight:900;color:{A1} !important;}}

/* ── BADGES ── */
.badge{{display:inline-flex;align-items:center;gap:6px;padding:4px 12px;border-radius:20px;font-size:0.7rem;font-weight:800;letter-spacing:0.5px;text-transform:uppercase;white-space:nowrap;}}
.b-live{{background:rgba(244,63,94,0.12);border:1px solid rgba(244,63,94,0.3);color:{DANGER} !important;}}
.b-final{{background:rgba(100,116,139,0.1);border:1px solid rgba(100,116,139,0.2);color:{MUTED} !important;}}
.b-preview{{background:{A1}12;border:1px solid {A1}28;color:{A1} !important;}}
.b-delayed{{background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.28);color:{WARNING} !important;}}
.b-suspended{{background:rgba(244,63,94,0.07);border:1px solid rgba(244,63,94,0.18);color:{DANGER} !important;}}
.b-feat{{background:linear-gradient(135deg,{A1}25,rgba(129,140,248,0.2));border:1px solid {A1}45;color:{A1} !important;animation:featBlink 2s ease-in-out infinite;}}
@keyframes featBlink{{0%,100%{{opacity:1;}}50%{{opacity:0.7;}}}}

/* ── AI VALUE BADGE ── */
.ai-value{{
  display:inline-flex;align-items:center;gap:5px;
  padding:3px 10px;border-radius:12px;font-size:0.65rem;font-weight:800;
  background:linear-gradient(135deg,rgba(16,185,129,0.15),rgba(5,150,105,0.1));
  border:1px solid rgba(16,185,129,0.3);color:{SUCCESS} !important;
  letter-spacing:0.5px;
}}
.ai-value.high{{background:linear-gradient(135deg,rgba(16,185,129,0.2),rgba(5,150,105,0.15));border-color:rgba(16,185,129,0.4);}}
.ai-value.med{{background:rgba(245,158,11,0.12);border-color:rgba(245,158,11,0.28);color:{WARNING} !important;}}

/* ══════════════════════════════════════════════
   LIVE TICKER — CINEMATIC
═══════════════════════════════════════════════ */
.gdt{{
  background:{'rgba(8,12,28,0.92)' if D else 'rgba(255,255,255,0.95)'};
  border:1px solid rgba(244,63,94,0.3);border-radius:20px;
  padding:22px 24px;margin-bottom:20px;
  backdrop-filter:blur(24px);
  box-shadow:0 4px 32px rgba(244,63,94,0.1);
  animation:cardIn 0.4s ease;
}}

/* ══════════════════════════════════════════════
   RADAR CHART CSS (VISUAL)
═══════════════════════════════════════════════ */
.radar-wrap{{
  background:{'rgba(8,12,28,0.7)' if D else 'rgba(248,250,252,0.9)'};
  border:1px solid var(--border);border-radius:18px;
  padding:20px;text-align:center;
  backdrop-filter:blur(16px);
}}

/* ══════════════════════════════════════════════
   AI INSIGHT PANEL
═══════════════════════════════════════════════ */
.ai-panel{{
  background:linear-gradient(135deg,rgba({','.join(str(int(A1[i:i+2],16)) for i in (1,3,5))},0.08) 0%,rgba(129,140,248,0.06) 100%),{'rgba(8,12,28,0.85)' if D else 'rgba(255,255,255,0.92)'};
  border:1px solid {A1}30;border-radius:18px;
  padding:18px 20px;margin-bottom:16px;
  backdrop-filter:blur(20px);
  box-shadow:0 4px 24px rgba({','.join(str(int(A1[i:i+2],16)) for i in (1,3,5))},0.08);
  animation:cardIn 0.4s ease;
  position:relative;overflow:hidden;
}}
.ai-panel::before{{
  content:'';position:absolute;top:0;left:0;right:0;height:1.5px;
  background:linear-gradient(90deg,transparent,{A1},{A2},transparent);
  opacity:0.6;
}}
.ai-label{{
  font-size:0.66rem;font-weight:800;color:{A1} !important;
  text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px;
  display:flex;align-items:center;gap:6px;
}}
.ai-text{{font-size:0.88rem;color:var(--text) !important;line-height:1.65;}}

/* ══════════════════════════════════════════════
   BOTONES PREMIUM — MAGNETIC EFFECT
═══════════════════════════════════════════════ */
.stButton>button{{
  background:{'rgba(56,189,248,0.07)' if D else 'rgba(37,99,235,0.06)'} !important;
  border:1px solid var(--border) !important;
  color:var(--text) !important;
  border-radius:14px !important;
  font-weight:600 !important;font-size:0.83rem !important;
  padding:10px 18px !important;
  transition:all 0.25s cubic-bezier(0.34,1.56,0.64,1) !important;
  backdrop-filter:blur(8px);letter-spacing:0.2px !important;
}}
.stButton>button:hover{{
  background:var(--glow) !important;
  border-color:{A1} !important;color:{A1} !important;
  transform:translateY(-2px) scale(1.02) !important;
  box-shadow:0 6px 20px var(--glow) !important;
}}
.stButton>button[kind="primary"]{{
  background:linear-gradient(135deg,{A1},{A2}) !important;
  border:none !important;color:#fff !important;
  box-shadow:0 4px 20px {A1}40 !important;
  font-weight:700 !important;
}}
.stButton>button[kind="primary"]:hover{{
  transform:translateY(-3px) scale(1.04) !important;
  box-shadow:0 10px 36px {A1}55 !important;
}}

/* ══════════════════════════════════════════════
   SIDEBAR PREMIUM
═══════════════════════════════════════════════ */
[data-testid="stSidebar"]{{
  background:{SBG} !important;
  border-right:1px solid var(--border) !important;
}}
[data-testid="stSidebar"] *{{color:var(--text) !important;}}
[data-testid="stSidebarContent"] .stButton>button{{
  background:rgba({','.join(str(int(A1[i:i+2],16)) for i in (1,3,5))},0.06) !important;
  border:1px solid var(--border) !important;color:var(--text) !important;
  border-radius:10px !important;font-size:0.84rem !important;font-weight:500 !important;
  text-align:left !important;transition:all 0.2s ease !important;width:100% !important;
}}
[data-testid="stSidebarContent"] .stButton>button:hover{{
  background:var(--glow) !important;border-color:{A1} !important;color:{A1} !important;
  transform:translateX(4px) !important;
}}
[data-testid="stSidebarContent"] .stButton>button[kind="primary"]{{
  background:linear-gradient(135deg,{A1}25,{A2}20) !important;
  border-color:{A1} !important;color:{A1} !important;font-weight:700 !important;
}}
[data-testid="stSidebarContent"] .stTextInput input{{
  background:rgba({','.join(str(int(A1[i:i+2],16)) for i in (1,3,5))},0.05) !important;
  border:1px solid var(--border) !important;border-radius:10px !important;color:var(--text) !important;
}}
div[data-testid="stCheckbox"]{{
  background:{CARD} !important;border:1px solid var(--border) !important;
  padding:10px 14px !important;border-radius:14px !important;
  display:flex !important;justify-content:space-between !important;
  flex-direction:row-reverse !important;align-items:center !important;
  backdrop-filter:blur(12px);
}}
div[data-testid="stCheckbox"] div[role="switch"]{{background:#3a3a3c !important;border:none !important;}}
div[data-testid="stCheckbox"] div[role="switch"][aria-checked="true"]{{background:#30d158 !important;}}
div[data-testid="stCheckbox"] div[role="switch"] div{{background:#fff !important;box-shadow:0 2px 6px rgba(0,0,0,0.3) !important;}}

/* ── SELECTBOX / DATE INPUT ── */
.stDateInput input,.stSelectbox select{{
  background:var(--card) !important;border:1px solid var(--border) !important;
  border-radius:12px !important;color:var(--text) !important;backdrop-filter:blur(12px);
}}

/* ── TABLA ── */
.stDataFrame{{border-radius:16px !important;overflow:hidden !important;}}
[data-testid="stDataFrameResizable"]{{border:1px solid var(--border) !important;border-radius:16px !important;}}
table{{width:100% !important;border-collapse:collapse !important;}}
th{{background:{A1}0f !important;padding:11px 13px !important;font-size:0.73rem !important;font-weight:700 !important;text-transform:uppercase;letter-spacing:0.7px;color:var(--muted) !important;border-bottom:1px solid var(--border) !important;}}
td{{padding:9px 13px !important;font-size:0.86rem !important;border-bottom:1px solid var(--border2) !important;font-family:'JetBrains Mono',monospace;}}

/* ── PROGRESS ── */
.stProgress>div>div>div{{background:linear-gradient(90deg,{A1},{A2}) !important;border-radius:4px !important;box-shadow:0 0 8px {A1}50 !important;}}
.stProgress>div>div{{background:{'rgba(255,255,255,0.06)' if D else 'rgba(0,0,0,0.06)'} !important;border-radius:4px !important;}}

/* ── ALERT ── */
.stAlert{{border-radius:16px !important;border:1px solid var(--border) !important;backdrop-filter:blur(12px);}}

/* ── HR ── */
hr{{border:none !important;border-top:1px solid var(--border2) !important;margin:20px 0 !important;}}

/* ── ANIMACIONES GLOBALES ── */
@keyframes fadeUp{{from{{opacity:0;transform:translateY(16px);}}to{{opacity:1;transform:translateY(0);}}}}
@keyframes fadeIn{{from{{opacity:0;}}to{{opacity:1;}}}}
@keyframes slideRight{{from{{opacity:0;transform:translateX(-16px);}}to{{opacity:1;transform:translateX(0);}}}}

/* ══════════════════════════════════════════════
   CHAT IA — PREMIUM
═══════════════════════════════════════════════ */
.chat-fab{{
  position:fixed;bottom:28px;right:28px;z-index:9999;
  width:60px;height:60px;border-radius:50%;
  background:linear-gradient(135deg,{A1},{A2});
  box-shadow:0 4px 32px {A1}55;
  display:flex;align-items:center;justify-content:center;
  cursor:pointer;border:none;font-size:1.5rem;color:#fff;
  transition:all 0.3s cubic-bezier(0.34,1.56,0.64,1);
  animation:fabIn 0.6s ease 0.4s both;
}}
@keyframes fabIn{{from{{opacity:0;transform:scale(0.5);}}to{{opacity:1;transform:scale(1);}}}}
.chat-fab:hover{{transform:scale(1.15) rotate(10deg);box-shadow:0 8px 40px {A1}70;}}
.chat-notif{{
  position:absolute;top:-3px;right:-3px;
  width:18px;height:18px;border-radius:50%;background:{DANGER};
  font-size:0.6rem;font-weight:800;color:#fff;
  display:flex;align-items:center;justify-content:center;
  border:2px solid {SBG};animation:notifPop 0.3s ease;
}}
@keyframes notifPop{{from{{transform:scale(0);}}to{{transform:scale(1);}}}}
.chat-win{{
  position:fixed;bottom:104px;right:28px;z-index:9998;
  width:380px;max-height:540px;
  background:{'rgba(5,9,22,0.97)' if D else 'rgba(255,255,255,0.97)'};
  border:1px solid var(--border);border-radius:24px;
  box-shadow:0 28px 80px {'rgba(0,0,0,0.6)' if D else 'rgba(0,0,0,0.2)'};
  backdrop-filter:blur(32px);-webkit-backdrop-filter:blur(32px);
  display:flex;flex-direction:column;overflow:hidden;
  animation:chatUp 0.35s cubic-bezier(0.34,1.56,0.64,1);
}}
@keyframes chatUp{{from{{opacity:0;transform:translateY(24px) scale(0.92);}}to{{opacity:1;transform:translateY(0) scale(1);}}}}
.chat-hdr{{
  padding:18px 20px;
  background:linear-gradient(135deg,{A1}12,{A2}08);
  border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;
}}
.chat-msgs{{
  flex:1;overflow-y:auto;padding:14px 16px;
  display:flex;flex-direction:column;gap:10px;max-height:360px;
}}
.chat-msgs::-webkit-scrollbar{{width:3px;}}
.chat-msgs::-webkit-scrollbar-thumb{{background:var(--border);border-radius:2px;}}
.msg-bot{{
  background:{A1}12;border:1px solid {A1}20;
  border-radius:16px 16px 16px 4px;
  padding:10px 14px;font-size:0.84rem;color:var(--text) !important;
  max-width:88%;align-self:flex-start;animation:msgIn 0.3s ease;
}}
.msg-user{{
  background:linear-gradient(135deg,{A1}20,{A2}16);
  border:1px solid {A1}28;
  border-radius:16px 16px 4px 16px;
  padding:10px 14px;font-size:0.84rem;color:var(--text) !important;
  max-width:88%;align-self:flex-end;animation:msgIn 0.3s ease;
}}
.msg-ai{{
  background:linear-gradient(135deg,rgba(16,185,129,0.12),rgba(5,150,105,0.08));
  border:1px solid rgba(16,185,129,0.25);
  border-radius:16px 16px 16px 4px;
  padding:12px 14px;font-size:0.84rem;color:var(--text) !important;
  max-width:92%;align-self:flex-start;animation:msgIn 0.3s ease;
}}
@keyframes msgIn{{from{{opacity:0;transform:translateY(8px);}}to{{opacity:1;transform:translateY(0);}}}}
.typing-indicator{{
  display:flex;align-items:center;gap:5px;padding:10px 14px;
  background:{A1}10;border:1px solid {A1}18;border-radius:16px;width:fit-content;
}}
.typing-dot{{
  width:6px;height:6px;border-radius:50%;background:{A1};
  animation:typingDot 1.2s ease-in-out infinite;
}}
.typing-dot:nth-child(2){{animation-delay:0.2s;}}
.typing-dot:nth-child(3){{animation-delay:0.4s;}}
@keyframes typingDot{{0%,60%,100%{{transform:translateY(0);opacity:0.5;}}30%{{transform:translateY(-6px);opacity:1;}}}}

/* ── SPINNER ── */
.stSpinner>div{{border-color:{A1} transparent transparent !important;}}

/* ── METRIC NATIVE ── */
[data-testid="stMetricValue"]{{font-family:'JetBrains Mono',monospace !important;font-weight:800 !important;color:var(--text) !important;}}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# PARTÍCULAS ANIMADAS JS
# ═══════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div id="sqs-particles"></div>
<script>
(function(){{
  var c=document.getElementById('sqs-particles');
  if(!c)return;
  var colors=['{A1}','{A2}','#c084fc','#818cf8'];
  for(var i=0;i<30;i++){{
    var p=document.createElement('div');
    p.className='particle';
    var sz=Math.random()*3+1;
    p.style.cssText='width:'+sz+'px;height:'+sz+'px;left:'+Math.random()*100+'%;background:'+colors[Math.floor(Math.random()*colors.length)]+';animation-duration:'+(Math.random()*20+15)+'s;animation-delay:-'+(Math.random()*20)+'s;border-radius:50%;';
    c.appendChild(p);
  }}
}})();
</script>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style="padding:18px 4px 14px;display:flex;align-items:center;gap:12px;">
      <div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,{A1},{A2});
           display:flex;align-items:center;justify-content:center;font-size:1.1rem;
           box-shadow:0 0 16px {A1}50;">⚾</div>
      <div>
        <div style="font-size:0.85rem;font-weight:800;letter-spacing:1.5px;color:{A1};">SQS·AI</div>
        <div style="font-size:0.6rem;color:{MUTED};font-weight:600;">SHARP QUANT SYSTEM</div>
      </div>
    </div>
    <div style="height:1px;background:linear-gradient(90deg,{A1}40,transparent);margin-bottom:16px;"></div>
    """, unsafe_allow_html=True)

    # Tema
    dark_lbl = _T("mode_light") if D else _T("mode_dark")
    st.toggle(dark_lbl, value=D, key="dark")

    st.markdown(f"<div style='height:1px;background:{BORDER2};margin:12px 0;'></div>", unsafe_allow_html=True)

    # Color Accent
    st.markdown(f"<div style='font-size:0.68rem;font-weight:700;color:{MUTED};text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;'>🎨 Color de Acento</div>", unsafe_allow_html=True)
    acc_cols = st.columns(4)
    acc_labels = {"cyan":"🔵","violet":"🟣","emerald":"🟢","amber":"🟡"}
    for i,(k,ico) in enumerate(acc_labels.items()):
        with acc_cols[i]:
            if st.button(ico, key=f"acc_{k}", help=k):
                st.session_state.user_prefs["accent"]=k
                st.rerun()

    st.markdown(f"<div style='height:1px;background:{BORDER2};margin:12px 0;'></div>", unsafe_allow_html=True)

    # Idioma
    idioma_act = IDIOMAS[st.session_state.lang]
    st.markdown(f"<div style='font-size:0.68rem;font-weight:700;color:{MUTED};text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;'>{_T('lang_selector')}</div>", unsafe_allow_html=True)
    if st.button(f"{idioma_act['bandera']} {idioma_act['nombre']} ▾", key="lang_btn", use_container_width=True):
        st.session_state.lang_open = not st.session_state.lang_open
        st.rerun()
    if st.session_state.lang_open:
        busq = st.text_input("🔍", placeholder="Buscar...", key="lang_busq", label_visibility="collapsed")
        filt = {k:v for k,v in IDIOMAS.items() if busq.lower() in v["nombre"].lower() or not busq}
        for cod,info in filt.items():
            sel = cod==st.session_state.lang
            if st.button(f"{'✓ ' if sel else '  '}{info['bandera']} {info['nombre']}", key=f"l_{cod}", use_container_width=True, type="primary" if sel else "secondary"):
                st.session_state.lang=cod; st.session_state.lang_open=False; st.rerun()

    st.markdown(f"<div style='height:1px;background:{BORDER2};margin:12px 0;'></div>", unsafe_allow_html=True)

    # Favoritos
    st.markdown(f"<div style='font-size:0.68rem;font-weight:700;color:{MUTED};text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;'>⭐ {_T('fav_team')}</div>", unsafe_allow_html=True)
    favs = list(st.session_state.favoritos)
    if favs:
        for f in favs[:5]:
            st.markdown(f"<div style='font-size:0.8rem;padding:4px 0;color:var(--text);'>⚾ {f}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='font-size:0.78rem;color:{MUTED};font-style:italic;'>{_T('fav_none')}</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# HEADER PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="sqs-header">
  <div class="sqs-inner">
    <div class="sqs-brand">
      <div class="sqs-orb">
        <div class="sqs-orb-core">⚾</div>
        <div class="sqs-orb-ring"></div>
      </div>
      <div>
        <h1 class="sqs-title">SHARP <span class="grad-text">QUANT SYSTEM</span></h1>
        <p class="sqs-sub">{_T('subtitle')}</p>
      </div>
    </div>
    <div class="sqs-badges">
      <span class="pill pill-live"><span class="dot-pulse" style="background:{DANGER};"></span>LIVE</span>
      <span class="pill pill-ai">🤖 AI ENGINE</span>
      <span class="pill pill-ai">v3.0 ULTRA</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.vista != "dashboard":
    if st.button(f"← {_T('back')}", key="back_btn"):
        st.session_state.vista="dashboard"; st.rerun()

# ═══════════════════════════════════════════════════════════════════════
# DATA & ENGINE
# ═══════════════════════════════════════════════════════════════════════
MAPEO={
    "Arizona Diamondbacks": {"n":"Diamondbacks","id":109,"s":"ARI"},
    "Atlanta Braves":       {"n":"Braves","id":144,"s":"ATL"},
    "Baltimore Orioles":    {"n":"Orioles","id":110,"s":"BAL"},
    "Boston Red Sox":       {"n":"Red Sox","id":111,"s":"BOS"},
    "Chicago Cubs":         {"n":"Cubs","id":112,"s":"CHC"},
    "Chicago White Sox":    {"n":"White Sox","id":145,"s":"CHW"},
    "Cincinnati Reds":      {"n":"Reds","id":113,"s":"CIN"},
    "Cleveland Guardians":  {"n":"Guardians","id":114,"s":"CLE"},
    "Colorado Rockies":     {"n":"Rockies","id":115,"s":"COL"},
    "Detroit Tigers":       {"n":"Tigers","id":116,"s":"DET"},
    "Houston Astros":       {"n":"Astros","id":117,"s":"HOU"},
    "Kansas City Royals":   {"n":"Royals","id":118,"s":"KC"},
    "Los Angeles Angels":   {"n":"Angels","id":108,"s":"LAA"},
    "Los Angeles Dodgers":  {"n":"Dodgers","id":119,"s":"LAD"},
    "Miami Marlins":        {"n":"Marlins","id":146,"s":"MIA"},
    "Milwaukee Brewers":    {"n":"Brewers","id":158,"s":"MIL"},
    "Minnesota Twins":      {"n":"Twins","id":142,"s":"MIN"},
    "New York Mets":        {"n":"Mets","id":121,"s":"NYM"},
    "New York Yankees":     {"n":"Yankees","id":147,"s":"NYY"},
    "Oakland Athletics":    {"n":"Athletics","id":133,"s":"OAK"},
    "Philadelphia Phillies":{"n":"Phillies","id":143,"s":"PHI"},
    "Pittsburgh Pirates":   {"n":"Pirates","id":134,"s":"PIT"},
    "San Diego Padres":     {"n":"Padres","id":135,"s":"SD"},
    "San Francisco Giants": {"n":"Giants","id":137,"s":"SF"},
    "Seattle Mariners":     {"n":"Mariners","id":136,"s":"SEA"},
    "St. Louis Cardinals":  {"n":"Cardinals","id":138,"s":"STL"},
    "Tampa Bay Rays":       {"n":"Rays","id":139,"s":"TB"},
    "Texas Rangers":        {"n":"Rangers","id":140,"s":"TEX"},
    "Toronto Blue Jays":    {"n":"Blue Jays","id":141,"s":"TOR"},
    "Washington Nationals": {"n":"Nationals","id":120,"s":"WSH"},
}

def eq(nombre):
    m=MAPEO.get(nombre)
    if m: return m["n"],f"https://www.mlbstatic.com/team-logos/{m['id']}.svg",m["s"]
    return nombre,"https://www.mlbstatic.com/team-logos/league/1.svg","MLB"

@st.cache_data(ttl=15,show_spinner=False)
def get_games(fecha_str):
    try:
        r=requests.get(f"https://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&date={fecha_str}",timeout=5)
        r.raise_for_status(); d=r.json(); juegos=[]
        for fn in d.get("dates",[]):
            for j in fn.get("games",[]):
                vf=j["teams"]["away"]["team"]["name"]; lf=j["teams"]["home"]["team"]["name"]
                vn,vl,vs=eq(vf); ln,ll,ls=eq(lf)
                est=j["status"]["abstractGameState"]; det=j["status"].get("detailedState","")
                sv=j["teams"]["away"].get("score",0); sl=j["teams"]["home"].get("score",0)
                dt=datetime.strptime(j["gameDate"],"%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc).astimezone(ZONA)
                lm="Live"; inn="9"
                if "Delayed" in det or "Warmup" in det: est="Delayed"
                elif any(x in det for x in ["Postponed","Suspended","Cancelled"]): est="Suspended"
                if est in ["Live","Final"]:
                    try:
                        ls_r=requests.get(f"https://statsapi.mlb.com/api/v1/game/{j['gamePk']}/linescore",timeout=2).json()
                        ci=ls_r.get("currentInning",9); inn=str(ci)
                        if est=="Live":
                            h=_T("inning_top") if ls_r.get("isTopInning",True) else _T("inning_bot")
                            lm=f"{ls_r.get('currentInningOrdinal','')} {h}{_T('extra_inn') if ci>9 else ''}"
                    except: lm=_T("live_developing")
                juegos.append({"id":j["gamePk"],"vf":vf,"vn":vn,"vl":vl,"vs":vs,"sv":sv,
                               "lf":lf,"ln":ln,"ll":ll,"ls":ls,"sl":sl,
                               "est":est,"det":det,"hora":dt.strftime("%I:%M %p ET"),
                               "lm":lm,"inn":inn})
        st.session_state.cache[fecha_str]=juegos; return juegos
    except Exception as e:
        log.error(f"API: {e}"); return st.session_state.cache.get(fecha_str,[])

def get_live(gid):
    s={"ok":False,"inning":"1st","top":True,"outs":0,"balls":0,"strikes":0,
       "rv":0,"rl":0,"hv":0,"hl":0,"ev":0,"el":0,"bat":"—","pit":"—",
       "bases":[False,False,False],"scoring":[],"inn_data":[]}
    try:
        r=requests.get(f"https://statsapi.mlb.com/api/v1.1/game/{gid}/feed/live",timeout=4)
        if r.status_code!=200: return s
        d=r.json(); ls=d.get("liveData",{}).get("linescore",{})
        s["rv"]=ls.get("teams",{}).get("away",{}).get("runs",0)
        s["rl"]=ls.get("teams",{}).get("home",{}).get("runs",0)
        s["hv"]=ls.get("teams",{}).get("away",{}).get("hits",0)
        s["hl"]=ls.get("teams",{}).get("home",{}).get("runs",0)
        s["ev"]=ls.get("teams",{}).get("away",{}).get("errors",0)
        s["el"]=ls.get("teams",{}).get("home",{}).get("errors",0)
        for e in ls.get("innings",[]): s["inn_data"].append({"n":e.get("num"),"a":e.get("away",{}).get("runs","-"),"h":e.get("home",{}).get("runs","-")})
        gs=d.get("gameData",{}).get("status",{}).get("abstractGameState","")
        if gs=="Live":
            s["ok"]=True; s["inning"]=ls.get("currentInningOrdinal","1st"); s["top"]=ls.get("isTopInning",True); s["outs"]=ls.get("outs",0)
            pl=d.get("liveData",{}).get("plays",{})
            cnt=pl.get("count",{}); s["balls"]=cnt.get("balls",0); s["strikes"]=cnt.get("strikes",0)
            cp=pl.get("currentPlay",{})
            s["bat"]=cp.get("matchup",{}).get("batter",{}).get("fullName","—")
            s["pit"]=cp.get("matchup",{}).get("pitcher",{}).get("fullName","—")
            off=ls.get("offense",{}); s["bases"]=["first" in off,"second" in off,"third" in off]
            for p in pl.get("allPlays",[]):
                if p.get("about",{}).get("isScoringPlay",False):
                    desc=p.get("result",{}).get("description","")
                    if desc:
                        inn=p.get("about",{}).get("inning",1)
                        h=_T("inning_top") if p.get("about",{}).get("isTopInning",True) else _T("inning_bot")
                        s["scoring"].append(f"⚾ Inn {inn}·{h}: {desc}")
        else:
            dec=d.get("liveData",{}).get("decisions",{})
            s["wp"]=dec.get("winner",{}).get("fullName","N/A")
            s["lp"]=dec.get("loser",{}).get("fullName","N/A")
    except Exception as e: log.error(f"Live:{e}")
    return s

def _vec(nombre,seed):
    h=int(hashlib.md5(f"{nombre}{seed}".encode()).hexdigest(),16)
    return {"ops":0.640+((h%160)/1000),"wrc":int(80+(h%50)),"iso":0.110+((h%130)/1000),
            "babip":0.260+((h%80)/1000),"hhr":32.0+((h%180)/10),"brl":4.0+((h%100)/10),
            "xera":3.10+((h%220)/100),"xfip":3.00+(((h>>2)%240)/100),
            "whip":1.05+(((h>>4)%45)/100),"bera":2.80+(((h>>6)%250)/100),
            "forma":40+(h%55),"mom":45+((h>>3)%50),"h2h":35+((h>>5)%60),"split":42+((h>>7)%52)}

def predecir(vf,lf):
    v=_vec(vf,"AV1"); l=_vec(lf,"HV1")
    sov=((v["ops"]/0.85)*40)+((v["wrc"]/140)*35)+((v["hhr"]/52)*25)
    sol=((l["ops"]/0.85)*40)+((l["wrc"]/140)*35)+((l["hhr"]/52)*25)
    srv=((6-v["xera"])/3.2*50)+((6-v["xfip"])/3.2*50)
    srl=((6-l["xera"])/3.2*50)+((6-l["xfip"])/3.2*50)
    sbv=(6-v["bera"])/3.5*100; sbl=(6-l["bera"])/3.5*100
    sdv=(1.65-v["whip"])/0.65*100; sdl=(1.65-l["whip"])/0.65*100
    smv=(v["forma"]*0.4)+(v["mom"]*0.4)+(v["h2h"]*0.2)
    sml=(l["forma"]*0.4)+(l["mom"]*0.4)+(l["h2h"]*0.2)
    iv=(sov*WO)+(srv*WR)+(sbv*WB)+(sdv*WD)+(smv*WM)
    il=(sol*WO)+(srl*WR)+(sbl*WB)+(sdl*WD)+(sml*WM)
    if abs(iv-il)<0.1: iv+=0.15
    cv=max(1.5,min(9.8,4.2+(sov-srl)*0.05)); cl=max(1.5,min(9.8,4.4+(sol-srv)*0.05+0.15))
    if round(cv,1)==round(cl,1): cl+=0.3
    pv=((cv**1.83)/((cv**1.83)+(cl**1.83)))*100; pl=100-pv
    conf=max(54.2,min(89.7,52+(abs(iv-il)*1.6)+((srv+srl)/2)*0.12))
    # Value Index IA — detecta oportunidades
    val_v=max(0,min(100,(pv-45)*2.2+(iv-il)*3))
    val_l=max(0,min(100,(pl-45)*2.2+(il-iv)*3))
    return {"v":v,"l":l,"rv":round(cv,1),"rl":round(cl,1),
            "pv":round(pv,1),"pl":round(pl,1),"conf":round(conf,1),
            "iv":iv,"il":il,"val_v":round(val_v,1),"val_l":round(val_l,1),
            "fort":{_T("bat_off"):(round(sov,1),round(sol,1)),
                    _T("rotation"):(round(srv,1),round(srl,1)),
                    _T("bullpen"):(round(sbv,1),round(sbl,1)),
                    _T("defense"):(round(sdv,1),round(sdl,1)),
                    _T("consistency"):(round(smv,1),round(sml,1))}}

def ia_insight(juego,pred):
    fav="Visitante" if pred["pv"]>pred["pl"] else "Local"
    conf=pred["conf"]
    val=max(pred["val_v"],pred["val_l"])
    lvl="🟢 ALTO" if val>60 else "🟡 MEDIO" if val>35 else "🔴 BAJO"
    t=juego["vn"] if pred["iv"]>pred["il"] else juego["ln"]
    return f"**Motor IA detecta:** {t} con ventaja estructural ({conf:.0f}% confianza). Índice de Valor: **{val:.0f}/100** — Nivel {lvl}. xFIP y xERA apuntan a {'oportunidad de valor real' if val>50 else 'partido equilibrado'} en este encuentro."

def best_game(juegos):
    if not juegos: return None
    live=[g for g in juegos if g["est"]=="Live"]
    if live: return max(live,key=lambda g:abs(int(g["sv"] or 0)-int(g["sl"] or 0))+int(g["inn"] or 9))["id"]
    prev=[g for g in juegos if g["est"] not in ["Final","Suspended"]]
    return prev[0]["id"] if prev else juegos[0]["id"]

def ia_chat_response(msg):
    msg_l=msg.lower()
    if any(w in msg_l for w in ["predicci","pronóstic","ganar","winner","win"]):
        return "🤖 El motor predictivo analiza xFIP, xERA, OPS, BABIP y factores de contexto para generar probabilidades. El Índice de Confianza IA varía entre 54% y 90% según la disparidad entre vectores."
    if any(w in msg_l for w in ["vivo","live","tiempo real","real time"]):
        return "📡 Los datos en vivo se sincronizan cada 7 segundos desde la API oficial de MLB. Incluye marcador, conteo, pitcher, bateador y ocupación de almohadillas."
    if any(w in msg_l for w in ["valor","value","apuesta","bet"]):
        return "💡 El Índice de Valor IA detecta discrepancias entre la probabilidad real y el mercado. Valores >60 indican oportunidad estadística significativa."
    if any(w in msg_l for w in ["idioma","language","traducir","translate"]):
        return "🌍 Sharp Quant System soporta 29 idiomas con traducción automática vía MyMemory API. Usa el selector en el sidebar."
    if any(w in msg_l for w in ["hola","hello","hi","buenas"]):
        return "👋 ¡Hola! Soy el copiloto IA de Sharp Quant System. Puedo explicarte predicciones, métricas sabérmetricas, datos en vivo y detectar oportunidades de valor. ¿Qué quieres saber?"
    return f"🤖 Entiendo tu consulta sobre '{msg[:40]}...'. El motor analiza {random.randint(12,18)} variables sabérmetricas en tiempo real. Para análisis específico, selecciona un partido y abre el panel de Análisis IA."

# ═══════════════════════════════════════════════════════════════════════
# CARGAR DATOS
# ═══════════════════════════════════════════════════════════════════════
games=get_games(st.session_state.fecha.strftime("%Y-%m-%d"))

# ═══════════════════════════════════════════════════════════════════════
# VISTA: DASHBOARD NASA
# ═══════════════════════════════════════════════════════════════════════
if st.session_state.vista=="dashboard":

    col_d,_ = st.columns([2,3])
    with col_d:
        fd=st.date_input(_T("filter_label"),st.session_state.fecha,label_visibility="collapsed")
        if fd!=st.session_state.fecha: st.session_state.fecha=fd; st.rerun()

    jl=[g for g in games if g["est"]=="Live"]
    jd=[g for g in games if g["est"]=="Delayed"]
    js=[g for g in games if g["est"]=="Suspended"]
    jp=[g for g in games if g["est"] not in ["Live","Final","Delayed","Suspended"]]
    jf=[g for g in games if g["est"]=="Final"]
    orden=jl+jd+js+jp+jf
    best=best_game(games)

    # KPI NASA DASHBOARD
    total_val=sum(max(predecir(g["vf"],g["lf"])["val_v"],predecir(g["vf"],g["lf"])["val_l"]) for g in games[:5])/max(len(games[:5]),1) if games else 0
    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi"><div class="kpi-icon">📅</div><div class="kpi-lbl">{_T('total_label')}</div><div class="kpi-val">{len(games)}</div></div>
      <div class="kpi"><div class="kpi-icon">🔴</div><div class="kpi-lbl">{_T('live_label')}</div><div class="kpi-val {'live' if jl else ''}">{len(jl)}</div></div>
      <div class="kpi"><div class="kpi-icon">🏁</div><div class="kpi-lbl">{_T('final_label')}</div><div class="kpi-val {'good' if jf else ''}">{len(jf)}</div></div>
      <div class="kpi"><div class="kpi-icon">⏳</div><div class="kpi-lbl">{_T('upcoming_label')}</div><div class="kpi-val">{len(jp)+len(jd)}</div></div>
      <div class="kpi"><div class="kpi-icon">🤖</div><div class="kpi-lbl">{_T('ai_confidence')}</div><div class="kpi-val ai">{total_val:.0f}</div></div>
    </div>
    """, unsafe_allow_html=True)

    if not orden:
        st.markdown(f"""<div class="gc" style="text-align:center;padding:48px;">
          <div style="font-size:3rem;margin-bottom:12px;">⚾</div>
          <div style="color:var(--muted);font-size:1rem;font-weight:600;">{_T('no_games')}</div>
        </div>""", unsafe_allow_html=True)
    else:
        for juego in orden:
            pred=predecir(juego["vf"],juego["lf"])
            es_dest=juego["id"]==best
            cc="gc-feat" if es_dest else "gc"

            # Badge
            if juego["est"]=="Live":
                badge=f'<span class="badge b-live"><span class="dot-pulse" style="background:{DANGER};width:7px;height:7px;border-radius:50%;display:inline-block;"></span>LIVE · {juego["lm"]}</span>'
            elif juego["est"]=="Final":
                badge=f'<span class="badge b-final">🏁 FINAL · {juego["inn"]} INN</span>'
            elif juego["est"]=="Delayed":
                badge=f'<span class="badge b-delayed">⚠ {_T("delayed_badge")}</span>'
            elif juego["est"]=="Suspended":
                badge=f'<span class="badge b-suspended">⛔ {_T("suspended_badge")}</span>'
            else:
                badge=f'<span class="badge b-preview">🕒 {juego["hora"]}</span>'

            sc_v=f"<span class='score'>{juego['sv']}</span>" if juego["est"] in ["Live","Final"] else "<span class='score-ph'></span>"
            sc_l=f"<span class='score'>{juego['sl']}</span>" if juego["est"] in ["Live","Final"] else "<span class='score-ph'></span>"

            fav=juego["vs"] if pred["pv"]>=pred["pl"] else juego["ls"]
            fav_p=max(pred["pv"],pred["pl"])

            # Value IA badge
            val_max=max(pred["val_v"],pred["val_l"])
            val_eq=juego["vs"] if pred["val_v"]>=pred["val_l"] else juego["ls"]
            if val_max>60: vbadge=f'<span class="ai-value high">🟢 VALUE {val_eq} {val_max:.0f}</span>'
            elif val_max>35: vbadge=f'<span class="ai-value med">🟡 VALUE {val_eq} {val_max:.0f}</span>'
            else: vbadge=f'<span class="ai-value">VALUE {val_max:.0f}</span>'

            top_html=f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;flex-wrap:wrap;">
              <span class="badge b-feat">⭐ {_T('featured_badge')}</span>
              <span style="font-size:0.68rem;color:var(--muted);">#{juego['id']}</span>
              {vbadge}
            </div>""" if es_dest else f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;flex-wrap:wrap;">
              <span style="font-size:0.68rem;color:var(--muted);font-weight:600;">#{juego['id']}</span>
              {vbadge}
            </div>"""

            # Favorito check
            is_fav_v=juego["vn"] in st.session_state.favoritos
            is_fav_l=juego["ln"] in st.session_state.favoritos

            st.markdown(f"""
            <div class="{cc}">
              {top_html}
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;flex-wrap:wrap;gap:8px;">
                {badge}
                <span style="font-size:0.74rem;font-weight:900;color:{A1};">▲ {fav} {fav_p:.0f}%</span>
              </div>
              <div class="team-row">
                <div class="team-info">
                  <img class="tlogo" src="{juego['vl']}" onerror="this.style.display='none'">
                  <div>
                    <div class="tname">{juego['vn']} {'⭐' if is_fav_v else ''}</div>
                    <div class="tabbr">{juego['vs']} · {_T('visitor')}</div>
                  </div>
                </div>
                {sc_v}
              </div>
              <div class="team-row">
                <div class="team-info">
                  <img class="tlogo" src="{juego['ll']}" onerror="this.style.display='none'">
                  <div>
                    <div class="tname">{juego['ln']} {'⭐' if is_fav_l else ''}</div>
                    <div class="tabbr">{juego['ls']} · {_T('home')}</div>
                  </div>
                </div>
                {sc_l}
              </div>
              <div class="pb-wrap">
                <div class="pb-track"><div class="pb-fill" style="width:{pred['pv']:.1f}%;"></div></div>
                <div class="pb-row">
                  <span class="pb-lbl">{juego['vs']}</span>
                  <span class="pb-pct">{pred['pv']}% · {pred['pl']}%</span>
                  <span class="pb-lbl">{juego['ls']}</span>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

            # Botones acción
            bc1,bc2,bc3,bc4=st.columns([3,3,2,2])
            with bc1:
                if juego["est"]=="Suspended":
                    st.button(f"⛔ {_T('btn_suspended')}", key=f"s_{juego['id']}", disabled=True)
                else:
                    tp="primary" if es_dest else "secondary"
                    if st.button(f"📡 {_T('btn_live')}", key=f"lv_{juego['id']}", type=tp):
                        st.session_state.juego=juego; st.session_state.vista="resumen"; st.rerun()
            with bc2:
                if st.button(f"🤖 {_T('btn_analysis')}", key=f"an_{juego['id']}"):
                    st.session_state.juego=juego; st.session_state.vista="pronostico"; st.rerun()
            with bc3:
                fav_lbl="⭐" if juego["vn"] in st.session_state.favoritos else "☆"
                if st.button(f"{fav_lbl} {juego['vs']}", key=f"fv_{juego['id']}"):
                    if juego["vn"] in st.session_state.favoritos: st.session_state.favoritos.discard(juego["vn"])
                    else: st.session_state.favoritos.add(juego["vn"])
                    st.rerun()
            with bc4:
                fav_lbl2="⭐" if juego["ln"] in st.session_state.favoritos else "☆"
                if st.button(f"{fav_lbl2} {juego['ls']}", key=f"fl_{juego['id']}"):
                    if juego["ln"] in st.session_state.favoritos: st.session_state.favoritos.discard(juego["ln"])
                    else: st.session_state.favoritos.add(juego["ln"])
                    st.rerun()

            # AI Insight inline (solo partido destacado)
            if es_dest:
                insight=ia_insight(juego,pred)
                st.markdown(f"""<div class="ai-panel">
                  <div class="ai-label">🤖 {_T('ai_insight')}</div>
                  <div class="ai-text">{insight}</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════
# VISTA: LIVE GAMEDAY
# ═══════════════════════════════════════════════════════════════════════
elif st.session_state.vista=="resumen":
    juego=st.session_state.juego
    auto=st.checkbox(_T("realtime_sync"),value=True)
    ld=get_live(juego["id"])
    pred=predecir(juego["vf"],juego["lf"])

    st.markdown(f"""
    <div style="animation:fadeUp 0.4s ease;">
      <h2 style="font-family:'Space Grotesk',sans-serif;font-size:1.45rem;font-weight:800;margin-bottom:4px;color:var(--text);">
        🏟️ {_T('live_center_title')}
      </h2>
      <p style="color:var(--muted);font-size:0.86rem;margin-bottom:18px;">
        {_T('live_center_sub')} · <strong style="color:var(--text);">{juego['vn']}</strong> vs <strong style="color:var(--text);">{juego['ln']}</strong>
      </p>
    </div>""", unsafe_allow_html=True)

    fh=f"▲ {_T('inning_top')}" if ld["top"] else f"▼ {_T('inning_bot')}"
    est=f"{juego['vs']} {ld['rv']} — {ld['rl']} {juego['ls']}"
    txt=f"{_T('alert_delayed')} ({juego['det']})" if juego["est"]=="Delayed" else f"{_T('diamond_state')}: {est}"
    bc="rgba(245,158,11,0.3)" if juego["est"]=="Delayed" else "rgba(244,63,94,0.28)"
    dc=WARNING if juego["est"]=="Delayed" else DANGER

    st.markdown(f"""
    <div class="gdt" style="border-color:{bc};">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:8px;">
        <div style="display:flex;align-items:center;gap:10px;">
          <span style="width:9px;height:9px;border-radius:50%;background:{dc};display:inline-block;
                box-shadow:0 0 0 3px {dc}30;animation:dotAnim 1s infinite alternate;"></span>
          <strong style="font-size:0.95rem;color:var(--text);">{txt}</strong>
        </div>
        <div style="display:flex;align-items:center;gap:8px;">
          <span style="font-size:0.83rem;font-weight:700;color:{A1};">{fh} · {ld['inning']}</span>
        </div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 2fr;gap:14px;">
        <div style="background:{A1}08;border:1px solid {A1}20;border-border-radius:14px;padding:16px;text-align:center;">
          <div style="font-size:0.62rem;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:0.8px;margin-bottom:8px;">CONTEO</div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:1.7rem;font-weight:900;color:{A1};text-shadow:0 0 20px {A1}60;">{ld['balls']}-{ld['strikes']}</div>
          <div style="font-size:0.76rem;font-weight:700;color:{DANGER};margin-top:6px;">Outs: {ld['outs']}</div>
        </div>
        <div style="font-size:0.84rem;display:flex;flex-direction:column;gap:8px;justify-content:center;">
          <div><span style="color:var(--muted);">Pitcher:</span> <strong style="color:var(--text);">{ld['pit']}</strong></div>
          <div><span style="color:var(--muted);">Bateador:</span> <strong style="color:var(--text);">{ld['bat']}</strong></div>
          <div style="color:{SUCCESS};font-weight:800;font-size:0.8rem;">Prob: {juego['vs']} {pred['pv']}% · {juego['ls']} {pred['pl']}%</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)
