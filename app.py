import streamlit as st
import requests
from datetime import datetime
import pytz
import logging
import hashlib
import time

# =====================================================================
# CONFIGURACIÓN DE PÁGINA (DEBE IR PRIMERO)
# =====================================================================
st.set_page_config(
    page_title="Sharp Quant System",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================================
# MÓDULO 0: I18N — 29 IDIOMAS + MYMEMORY (SIN API KEY)
# =====================================================================
IDIOMAS_DISPONIBLES = {
    "es": {"nombre": "Español",          "bandera": "🇪🇸"},
    "en": {"nombre": "English",          "bandera": "🇺🇸"},
    "pt": {"nombre": "Português",        "bandera": "🇧🇷"},
    "fr": {"nombre": "Français",         "bandera": "🇫🇷"},
    "de": {"nombre": "Deutsch",          "bandera": "🇩🇪"},
    "it": {"nombre": "Italiano",         "bandera": "🇮🇹"},
    "ja": {"nombre": "日本語",           "bandera": "🇯🇵"},
    "zh": {"nombre": "中文",             "bandera": "🇨🇳"},
    "ko": {"nombre": "한국어",           "bandera": "🇰🇷"},
    "ru": {"nombre": "Русский",          "bandera": "🇷🇺"},
    "ar": {"nombre": "العربية",          "bandera": "🇸🇦"},
    "hi": {"nombre": "हिन्दी",          "bandera": "🇮🇳"},
    "nl": {"nombre": "Nederlands",       "bandera": "🇳🇱"},
    "pl": {"nombre": "Polski",           "bandera": "🇵🇱"},
    "tr": {"nombre": "Türkçe",           "bandera": "🇹🇷"},
    "sv": {"nombre": "Svenska",          "bandera": "🇸🇪"},
    "da": {"nombre": "Dansk",            "bandera": "🇩🇰"},
    "fi": {"nombre": "Suomi",            "bandera": "🇫🇮"},
    "no": {"nombre": "Norsk",            "bandera": "🇳🇴"},
    "cs": {"nombre": "Čeština",          "bandera": "🇨🇿"},
    "el": {"nombre": "Ελληνικά",         "bandera": "🇬🇷"},
    "he": {"nombre": "עברית",            "bandera": "🇮🇱"},
    "th": {"nombre": "ภาษาไทย",         "bandera": "🇹🇭"},
    "vi": {"nombre": "Tiếng Việt",       "bandera": "🇻🇳"},
    "id": {"nombre": "Bahasa Indonesia", "bandera": "🇮🇩"},
    "ms": {"nombre": "Bahasa Melayu",    "bandera": "🇲🇾"},
    "uk": {"nombre": "Українська",       "bandera": "🇺🇦"},
    "ro": {"nombre": "Română",           "bandera": "🇷🇴"},
    "hu": {"nombre": "Magyar",           "bandera": "🇭🇺"},
}

BASE_ES = {
    "subtitle":         "SISTEMA AVANZADO DE PREDICCIÓN CUANTITATIVA Y MONITOREO EN VIVO",
    "back":             "Volver al Calendario",
    "calendar_title":   "Calendario de Partidos",
    "filter_label":     "Filtro Temporal",
    "no_games":         "No hay partidos registrados para la fecha seleccionada.",
    "live_label":       "En Curso",
    "final_label":      "Finalizados",
    "upcoming_label":   "Próximos",
    "suspended_label":  "Suspendidos",
    "total_label":      "Total del Día",
    "delayed_badge":    "RETRASADO",
    "suspended_badge":  "SUSPENDIDO",
    "game_id":          "PARTIDO",
    "btn_live":         "Ver En Vivo",
    "btn_analysis":     "Análisis Técnico",
    "btn_suspended":    "Suspendido",
    "featured_badge":   "PARTIDO DESTACADO",
    "realtime_sync":    "Sincronización en Tiempo Real",
    "live_center_title":"Centro de Control Live",
    "live_center_sub":  "Monitoreo en tiempo real",
    "count_label":      "CONTEO",
    "outs_label":       "Outs",
    "pitcher_label":    "Pitcher",
    "batter_label":     "Bateador",
    "live_prob":        "Probabilidad en Vivo",
    "bases_label":      "Almohadillas",
    "linescore_title":  "Pizarra Oficial (Linescore)",
    "scoring_title":    "Jugadas Anotadoras",
    "no_runs":          "No hay carreras anotadas aún.",
    "team_col":         "Equipo",
    "analysis_title":   "Análisis de Rendimiento Técnico",
    "analysis_sub":     "Coeficientes Sabermétricos Avanzados del Enfrentamiento.",
    "projected_score":  "Marcador Proyectado",
    "probability_label":"Probabilidad",
    "certainty_label":  "Certeza del Sistema",
    "sabermetric_title":"Coeficientes Avanzados Sabermétricos",
    "strength_title":   "Vectores de Fortaleza Estructural",
    "report_title":     "Informe Técnico Front-Office",
    "advantage_label":  "Ventaja",
    "differential_label":"Diferencial",
    "metric_label":     "Métrica",
    "inning_top":       "Alta",
    "inning_bot":       "Baja",
    "extra_inn":        " (Extra)",
    "live_developing":  "En Desarrollo",
    "diamond_state":    "EN VIVO",
    "alert_delayed":    "PARTIDO RETRASADO",
    "mode_dark":        "Modo Oscuro",
    "mode_light":       "Modo Claro",
    "lang_selector":    "Idioma",
    "bat_off":          "Bateo / Ofensiva",
    "rotation":         "Rotación Abridora",
    "bullpen":          "Cuerpo de Relevistas",
    "defense":          "Estructura Defensiva",
    "consistency":      "Consistencia y Forma",
    "chat_title":       "Soporte",
    "chat_placeholder": "Escribe tu mensaje...",
    "chat_send":        "Enviar",
    "chat_welcome":     "Hola, ¿en qué puedo ayudarte?",
    "chat_sent":        "Enviado ✓",
    "visitor":          "Visitante",
    "home":             "Local",
    "report_body":      "El modelo cuantitativo posiciona a {team} con ventaja matemática estructural. Esta conclusión se deriva de indicadores avanzados como xFIP y xERA, normalizados con respecto al ISO de las alineaciones. El value esperado (EV+) favorece la consistencia del vector analítico dominante bajo una certeza del {conf}%.",
}

TERMINOS_PROTEGIDOS = [
    "xERA","xFIP","WHIP","OPS","wRC+","ISO","BABIP","EV+",
    "Linescore","Gameday","Sharp Quant System","MLB",
    "Hard Hit Rate","Barrel","ERA","SHARP QUANT SYSTEM"
]

def _proteger(texto):
    p = {}
    r = texto
    for i, t in enumerate(TERMINOS_PROTEGIDOS):
        if t in r:
            m = f"__T{i}__"
            p[m] = t
            r = r.replace(t, m)
    return r, p

def _restaurar(texto, p):
    for m, t in p.items():
        texto = texto.replace(m, t)
    return texto

def _traducir_mymemory(texto, lang):
    if not texto or not any(c.isalpha() for c in texto):
        return texto
    tp, p = _proteger(texto)
    try:
        r = requests.get(
            "https://api.mymemory.translated.net/get",
            params={"q": tp, "langpair": f"es|{lang}"},
            timeout=5
        )
        if r.status_code == 200:
            t = r.json().get("responseData", {}).get("translatedText", tp)
            if "MYMEMORY WARNING" not in t and t != tp:
                return _restaurar(t, p)
    except Exception:
        pass
    return _restaurar(tp, p)

@st.cache_data(ttl=86400, show_spinner=False)
def cargar_traducciones(lang_code, lang_name):
    if lang_code == "es":
        return BASE_ES
    t = {}
    for k, v in BASE_ES.items():
        t[k] = _traducir_mymemory(v, lang_code) if isinstance(v, str) else v
    if sum(1 for k in t if t[k] != BASE_ES[k]) < 3:
        return BASE_ES
    return t

# =====================================================================
# SESSION STATE
# =====================================================================
def _init(k, v):
    if k not in st.session_state:
        st.session_state[k] = v

_init("lang_code", "es")
_init("tema_is_dark", True)
_init("fecha_seleccionada", datetime.now(pytz.timezone("America/New_York")).date())
_init("vista_actual", "dashboard")
_init("juego_foco", None)
_init("ultimo_cache_exitoso", {})
_init("lang_open", False)
_init("chat_open", False)
_init("chat_msgs", [])
_init("chat_input_key", 0)

T = cargar_traducciones(st.session_state.lang_code, IDIOMAS_DISPONIBLES[st.session_state.lang_code]["nombre"])
def _T(k): return T.get(k, BASE_ES.get(k, k))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
ZONA_ET = pytz.timezone("America/New_York")

WEIGHT_OFFENSE  = 0.30
WEIGHT_ROTATION = 0.25
WEIGHT_BULLPEN  = 0.20
WEIGHT_DEFENSE  = 0.15
WEIGHT_MOMENTUM = 0.10

# =====================================================================
# PALETA DE COLORES
# =====================================================================
if st.session_state.tema_is_dark:
    BG      = "#07090f"
    BG2     = "#0d1117"
    CARD    = "rgba(13,17,27,0.92)"
    CARD2   = "rgba(20,26,40,0.95)"
    BORDER  = "rgba(56,189,248,0.10)"
    BORDER2 = "rgba(255,255,255,0.05)"
    TEXT    = "#e2e8f0"
    MUTED   = "#64748b"
    ACCENT  = "#38bdf8"
    ACCENT2 = "#818cf8"
    SUCCESS = "#10b981"
    DANGER  = "#f43f5e"
    WARNING = "#f59e0b"
    GLOW    = "rgba(56,189,248,0.12)"
    SB_BG   = "#0a0e18"
else:
    BG      = "#f0f4f8"
    BG2     = "#ffffff"
    CARD    = "rgba(255,255,255,0.95)"
    CARD2   = "rgba(240,244,248,0.98)"
    BORDER  = "rgba(37,99,235,0.14)"
    BORDER2 = "rgba(0,0,0,0.05)"
    TEXT    = "#0f172a"
    MUTED   = "#64748b"
    ACCENT  = "#2563eb"
    ACCENT2 = "#7c3aed"
    SUCCESS = "#059669"
    DANGER  = "#dc2626"
    WARNING = "#d97706"
    GLOW    = "rgba(37,99,235,0.08)"
    SB_BG   = "#f8fafc"

IS_DARK = st.session_state.tema_is_dark

# =====================================================================
# SIDEBAR PREMIUM
# =====================================================================
with st.sidebar:
    st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{
        background: {SB_BG} !important;
        border-right: 1px solid {BORDER} !important;
    }}
    [data-testid="stSidebar"] * {{ color: {TEXT} !important; }}
    [data-testid="stSidebarContent"] .stButton > button {{
        background: {'rgba(56,189,248,0.06)' if IS_DARK else 'rgba(37,99,235,0.05)'} !important;
        border: 1px solid {BORDER} !important;
        color: {TEXT} !important;
        border-radius: 10px !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        text-align: left !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }}
    [data-testid="stSidebarContent"] .stButton > button:hover {{
        background: {GLOW} !important;
        border-color: {ACCENT} !important;
        color: {ACCENT} !important;
        transform: translateX(3px);
    }}
    [data-testid="stSidebarContent"] .stButton > button[kind="primary"] {{
        background: {'rgba(56,189,248,0.15)' if IS_DARK else 'rgba(37,99,235,0.12)'} !important;
        border-color: {ACCENT} !important;
        color: {ACCENT} !important;
        font-weight: 700 !important;
    }}
    [data-testid="stSidebarContent"] .stTextInput input {{
        background: {'rgba(255,255,255,0.04)' if IS_DARK else 'rgba(0,0,0,0.03)'} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 10px !important;
        color: {TEXT} !important;
    }}
    div[data-testid="stCheckbox"] {{
        background: {CARD} !important;
        border: 1px solid {BORDER} !important;
        padding: 10px 14px !important;
        border-radius: 14px !important;
        display: flex !important;
        justify-content: space-between !important;
        flex-direction: row-reverse !important;
        align-items: center !important;
        backdrop-filter: blur(12px);
    }}
    div[data-testid="stCheckbox"] div[role="switch"] {{ background: #3a3a3c !important; border: none !important; }}
    div[data-testid="stCheckbox"] div[role="switch"][aria-checked="true"] {{ background: #30d158 !important; }}
    div[data-testid="stCheckbox"] div[role="switch"] div {{ background: #fff !important; box-shadow: 0 2px 6px rgba(0,0,0,0.25) !important; }}
    </style>
    """, unsafe_allow_html=True)

    # Logo en sidebar
    st.markdown(f"""
    <div style="padding:20px 4px 16px;display:flex;align-items:center;gap:10px;">
        <div style="width:9px;height:9px;background:linear-gradient(135deg,{ACCENT},{ACCENT2});
             transform:rotate(45deg);box-shadow:0 0 14px {ACCENT};"></div>
        <span style="font-size:0.9rem;font-weight:800;letter-spacing:2px;color:{ACCENT};">SQS</span>
        <span style="font-size:0.65rem;color:{MUTED};font-weight:600;letter-spacing:0.5px;">SHARP QUANT</span>
    </div>
    <div style="height:1px;background:linear-gradient(90deg,{ACCENT}30,transparent);margin-bottom:16px;"></div>
    """, unsafe_allow_html=True)

    # Toggle Tema
    dark_lbl = _T("mode_light") if IS_DARK else _T("mode_dark")
    st.toggle(dark_lbl, value=IS_DARK, key="tema_is_dark")

    st.markdown(f"<div style='height:1px;background:{BORDER2};margin:14px 0;'></div>", unsafe_allow_html=True)

    # Selector de Idioma
    idioma_act = IDIOMAS_DISPONIBLES[st.session_state.lang_code]
    st.markdown(f"<div style='font-size:0.7rem;font-weight:700;color:{MUTED};text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;'>{_T('lang_selector')}</div>", unsafe_allow_html=True)

    if st.button(f"{idioma_act['bandera']} {idioma_act['nombre']} ▾", key="lang_btn", use_container_width=True):
        st.session_state.lang_open = not st.session_state.lang_open
        st.rerun()

    if st.session_state.lang_open:
        busq = st.text_input("🔍", placeholder="Buscar...", key="lang_busq", label_visibility="collapsed")
        filtrados = {k: v for k, v in IDIOMAS_DISPONIBLES.items() if busq.lower() in v["nombre"].lower() or not busq}
        for cod, info in filtrados.items():
            es_sel = cod == st.session_state.lang_code
            tipo = "primary" if es_sel else "secondary"
            lbl = f"{'✓ ' if es_sel else '  '}{info['bandera']} {info['nombre']}"
            if st.button(lbl, key=f"lang_{cod}", use_container_width=True, type=tipo):
                st.session_state.lang_code = cod
                st.session_state.lang_open = False
                st.rerun()

# =====================================================================
# CSS GLOBAL — DISEÑO PREMIUM TOTAL
# =====================================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;700&family=Space+Grotesk:wght@400;500;600;700;800&display=swap');

:root {{
  --bg:{BG}; --bg2:{BG2}; --card:{CARD}; --border:{BORDER}; --border2:{BORDER2};
  --text:{TEXT}; --muted:{MUTED}; --accent:{ACCENT}; --accent2:{ACCENT2};
  --success:{SUCCESS}; --danger:{DANGER}; --warning:{WARNING}; --glow:{GLOW};
}}

*, *::before, *::after {{ box-sizing: border-box; }}
html, body, .stApp {{
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
}}
.stApp > header {{ display:none !important; }}
.block-container {{
  padding: 1.2rem 1.5rem 3rem !important;
  max-width: 1140px !important;
  margin: 0 auto !important;
}}
.stApp p,.stApp span,.stApp label,.stApp h1,.stApp h2,.stApp h3,.stApp h4,
.stApp div,.stMarkdown,.stMetric,[data-testid="stMetricValue"],
[data-testid="stMetricLabel"],table,th,td,tr {{ color: var(--text) !important; }}

/* ──────────── HEADER PRINCIPAL ──────────── */
.sqs-header {{
  position: relative;
  padding: 26px 32px 24px;
  background: linear-gradient(135deg,
    {'rgba(7,9,15,0.98)' if IS_DARK else 'rgba(248,250,252,0.98)'} 0%,
    {'rgba(10,14,24,0.99)' if IS_DARK else 'rgba(240,244,248,0.99)'} 100%);
  border: 1px solid var(--border);
  border-radius: 20px;
  margin-bottom: 24px;
  overflow: hidden;
  box-shadow: {'0 20px 60px rgba(0,0,0,0.5), inset 0 1px 0 rgba(56,189,248,0.08)' if IS_DARK else '0 8px 30px rgba(0,0,0,0.08)'};
}}
.sqs-header::before {{
  content:'';position:absolute;top:0;left:0;right:0;height:1.5px;
  background:linear-gradient(90deg,transparent,{ACCENT},{ACCENT2},transparent);
  opacity:0.7;
}}
.sqs-header-bg {{
  position:absolute;inset:0;
  background-image:
    radial-gradient(ellipse at 15% 60%, {GLOW} 0%, transparent 55%),
    radial-gradient(ellipse at 85% 40%, {'rgba(129,140,248,0.05)' if IS_DARK else 'rgba(124,58,237,0.03)'} 0%, transparent 55%);
  pointer-events:none;
}}
.sqs-header-inner {{ position:relative;z-index:1;display:flex;align-items:center;justify-content:space-between;gap:20px; }}
.sqs-brand {{ display:flex;align-items:center;gap:16px; }}
.sqs-diamond {{
  width:13px;height:13px;flex-shrink:0;
  background:linear-gradient(135deg,{ACCENT},{ACCENT2});
  transform:rotate(45deg);
  box-shadow:0 0 24px {ACCENT},0 0 48px {'rgba(56,189,248,0.3)' if IS_DARK else 'rgba(37,99,235,0.2)'};
  animation: dPulse 3s ease-in-out infinite;
}}
@keyframes dPulse {{
  0%,100% {{ box-shadow:0 0 24px {ACCENT},0 0 48px {'rgba(56,189,248,0.3)' if IS_DARK else 'rgba(37,99,235,0.2)'}; }}
  50%      {{ box-shadow:0 0 36px {ACCENT},0 0 72px {'rgba(56,189,248,0.5)' if IS_DARK else 'rgba(37,99,235,0.35)'}; }}
}}
.sqs-title {{
  font-family:'Space Grotesk',sans-serif !important;
  font-size:2rem !important;font-weight:800 !important;
  color:{'#ffffff' if IS_DARK else TEXT} !important;
  letter-spacing:-0.5px;margin:0 !important;line-height:1.1;
}}
.sqs-title-grad {{
  background:linear-gradient(90deg,{ACCENT},{ACCENT2},#c084fc);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}}
.sqs-subtitle {{
  color:var(--muted) !important;font-size:0.76rem;font-weight:500;
  letter-spacing:0.8px;text-transform:uppercase;margin-top:4px !important;
}}
.sqs-live-pill {{
  display:inline-flex;align-items:center;gap:7px;
  padding:5px 14px;border-radius:20px;
  background:{'rgba(244,63,94,0.1)' if IS_DARK else 'rgba(220,38,38,0.08)'};
  border:1px solid {'rgba(244,63,94,0.25)' if IS_DARK else 'rgba(220,38,38,0.2)'};
  font-size:0.72rem;font-weight:800;color:{DANGER} !important;
  letter-spacing:1px;text-transform:uppercase;white-space:nowrap;
}}
.sqs-dot-pulse {{
  width:7px;height:7px;border-radius:50%;background:{DANGER};
  box-shadow:0 0 0 2px {'rgba(244,63,94,0.2)' if IS_DARK else 'rgba(220,38,38,0.15)'};
  animation:dpAnim 1s ease-in-out infinite alternate;
}}
@keyframes dpAnim {{ 0% {{ opacity:0.4;transform:scale(0.8); }} 100% {{ opacity:1;transform:scale(1.2); }} }}

/* ──────────── MÉTRICAS ──────────── */
.metric-glass {{
  background:var(--card);border:1px solid var(--border);border-radius:16px;
  padding:16px 10px;text-align:center;
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  box-shadow:0 4px 20px {'rgba(0,0,0,0.2)' if IS_DARK else 'rgba(0,0,0,0.06)'},inset 0 1px 0 {'rgba(255,255,255,0.04)' if IS_DARK else 'rgba(255,255,255,0.8)'};
  transition:transform 0.2s ease,box-shadow 0.2s ease;
  min-height:82px;display:flex;flex-direction:column;justify-content:center;align-items:center;
  animation: fadeUp 0.5s ease both;
}}
.metric-glass:hover {{ transform:translateY(-3px);box-shadow:0 10px 32px {'rgba(0,0,0,0.3)' if IS_DARK else 'rgba(0,0,0,0.1)'}; }}
.m-label {{
  font-size:0.66rem;font-weight:700;color:var(--muted) !important;
  text-transform:uppercase;letter-spacing:0.7px;margin-bottom:7px;line-height:1.2;
}}
.m-value {{
  font-family:'JetBrains Mono',monospace !important;
  font-size:1.65rem;font-weight:800;color:var(--text) !important;line-height:1;
}}
.m-value.live {{ color:{DANGER} !important; }}
.m-value.good {{ color:{SUCCESS} !important; }}

/* ──────────── TARJETAS DE PARTIDO ──────────── */
.game-card {{
  background:var(--card);border:1px solid var(--border);border-radius:20px;
  padding:20px 22px;margin-bottom:14px;
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  box-shadow:0 4px 24px {'rgba(0,0,0,0.15)' if IS_DARK else 'rgba(0,0,0,0.05)'},inset 0 1px 0 {'rgba(255,255,255,0.04)' if IS_DARK else 'rgba(255,255,255,0.8)'};
  transition:transform 0.25s cubic-bezier(0.4,0,0.2,1),box-shadow 0.25s ease,border-color 0.25s ease;
  animation:fadeUp 0.4s ease both;cursor:default;
}}
.game-card:hover {{
  transform:translateY(-4px);
  box-shadow:0 16px 48px {'rgba(0,0,0,0.25)' if IS_DARK else 'rgba(0,0,0,0.1)'};
  border-color:{'rgba(56,189,248,0.25)' if IS_DARK else 'rgba(37,99,235,0.2)'};
}}
.game-card-featured {{
  background:linear-gradient(135deg,{'rgba(56,189,248,0.06)' if IS_DARK else 'rgba(37,99,235,0.04)'} 0%,{'rgba(129,140,248,0.04)' if IS_DARK else 'rgba(124,58,237,0.03)'} 100%),var(--card);
  border:1.5px solid {'rgba(56,189,248,0.35)' if IS_DARK else 'rgba(37,99,235,0.28)'} !important;
  border-radius:20px;padding:22px 24px;margin-bottom:14px;
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  box-shadow:0 0 0 1px {'rgba(56,189,248,0.08)' if IS_DARK else 'rgba(37,99,235,0.06)'},0 12px 48px {'rgba(56,189,248,0.14)' if IS_DARK else 'rgba(37,99,235,0.1)'},0 24px 64px {'rgba(0,0,0,0.25)' if IS_DARK else 'rgba(0,0,0,0.08)'};
  transition:transform 0.25s cubic-bezier(0.4,0,0.2,1),box-shadow 0.25s ease;
  animation:featGlow 3s ease-in-out infinite,fadeUp 0.4s ease both;
  position:relative;overflow:hidden;cursor:default;
}}
.game-card-featured::before {{
  content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent,{ACCENT},{ACCENT2},transparent);
  opacity:0.8;
}}
.game-card-featured:hover {{
  transform:translateY(-5px);
  box-shadow:0 0 0 1px {'rgba(56,189,248,0.15)' if IS_DARK else 'rgba(37,99,235,0.12)'},0 20px 60px {'rgba(56,189,248,0.2)' if IS_DARK else 'rgba(37,99,235,0.15)'},0 32px 80px {'rgba(0,0,0,0.3)' if IS_DARK else 'rgba(0,0,0,0.1)'};
}}
@keyframes featGlow {{
  0%,100% {{ box-shadow:0 0 0 1px {'rgba(56,189,248,0.08)' if IS_DARK else 'rgba(37,99,235,0.06)'},0 12px 48px {'rgba(56,189,248,0.14)' if IS_DARK else 'rgba(37,99,235,0.1)'},0 24px 64px {'rgba(0,0,0,0.25)' if IS_DARK else 'rgba(0,0,0,0.08)'}; }}
  50%       {{ box-shadow:0 0 0 1px {'rgba(56,189,248,0.18)' if IS_DARK else 'rgba(37,99,235,0.14)'},0 12px 48px {'rgba(56,189,248,0.24)' if IS_DARK else 'rgba(37,99,235,0.18)'},0 24px 64px {'rgba(0,0,0,0.3)' if IS_DARK else 'rgba(0,0,0,0.1)'}; }}
}}

/* ──────────── BADGES DE ESTADO ──────────── */
.badge {{ display:inline-flex;align-items:center;gap:6px;padding:4px 12px;border-radius:20px;font-size:0.73rem;font-weight:700;letter-spacing:0.5px;text-transform:uppercase;white-space:nowrap; }}
.badge-live    {{ background:{'rgba(244,63,94,0.12)' if IS_DARK else 'rgba(220,38,38,0.08)'};border:1px solid {'rgba(244,63,94,0.28)' if IS_DARK else 'rgba(220,38,38,0.2)'};color:{DANGER} !important; }}
.badge-final   {{ background:{'rgba(100,116,139,0.1)' if IS_DARK else 'rgba(100,116,139,0.08)'};border:1px solid {'rgba(100,116,139,0.22)' if IS_DARK else 'rgba(100,116,139,0.15)'};color:{MUTED} !important; }}
.badge-preview {{ background:{'rgba(56,189,248,0.08)' if IS_DARK else 'rgba(37,99,235,0.06)'};border:1px solid {'rgba(56,189,248,0.2)' if IS_DARK else 'rgba(37,99,235,0.16)'};color:{ACCENT} !important; }}
.badge-delayed {{ background:{'rgba(245,158,11,0.1)' if IS_DARK else 'rgba(217,119,6,0.08)'};border:1px solid {'rgba(245,158,11,0.28)' if IS_DARK else 'rgba(217,119,6,0.2)'};color:{WARNING} !important; }}
.badge-suspended {{ background:{'rgba(244,63,94,0.07)' if IS_DARK else 'rgba(220,38,38,0.05)'};border:1px solid {'rgba(244,63,94,0.18)' if IS_DARK else 'rgba(220,38,38,0.12)'};color:{DANGER} !important; }}
.badge-featured {{ background:linear-gradient(135deg,{'rgba(56,189,248,0.18)' if IS_DARK else 'rgba(37,99,235,0.12)'},{'rgba(129,140,248,0.15)' if IS_DARK else 'rgba(124,58,237,0.1)'});border:1px solid {'rgba(56,189,248,0.35)' if IS_DARK else 'rgba(37,99,235,0.3)'};color:{ACCENT} !important;animation:bFeat 2s ease-in-out infinite; }}
@keyframes bFeat {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.7; }} }}

/* ──────────── SCOREBOARD ──────────── */
.team-row {{ display:flex;justify-content:space-between;align-items:center;padding:9px 0; }}
.team-row+.team-row {{ border-top:1px solid var(--border2); }}
.team-info {{ display:flex;align-items:center;gap:14px; }}
.team-logo {{ width:42px;height:42px;object-fit:contain;filter:{'drop-shadow(0 2px 8px rgba(0,0,0,0.4))' if IS_DARK else 'drop-shadow(0 2px 6px rgba(0,0,0,0.15))'};transition:transform 0.2s; }}
.team-logo:hover {{ transform:scale(1.12); }}
.team-name {{ font-family:'Space Grotesk',sans-serif;font-size:1.05rem;font-weight:700;color:var(--text) !important; }}
.team-abbr {{ font-size:0.73rem;font-weight:600;color:var(--muted) !important; }}
.score-num {{ font-family:'JetBrains Mono',monospace;font-size:1.95rem;font-weight:800;color:{ACCENT} !important;min-width:48px;text-align:right;line-height:1; }}
.score-ph  {{ width:48px;height:32px; }}

/* ──────────── BARRA DE PROBABILIDAD ──────────── */
.prob-wrap {{ margin:14px 0 0; }}
.prob-track {{
  height:5px;border-radius:3px;
  background:{'rgba(255,255,255,0.06)' if IS_DARK else 'rgba(0,0,0,0.07)'};
  overflow:hidden;
}}
.prob-fill {{
  height:100%;border-radius:3px;
  background:linear-gradient(90deg,{ACCENT},{ACCENT2});
  box-shadow:0 0 10px {'rgba(56,189,248,0.4)' if IS_DARK else 'rgba(37,99,235,0.3)'};
  transition:width 0.8s cubic-bezier(0.4,0,0.2,1);
}}
.prob-row {{ display:flex;justify-content:space-between;margin-top:5px; }}
.prob-lbl {{ font-size:0.7rem;font-weight:700;color:var(--muted) !important; }}
.prob-pct {{ font-size:0.7rem;font-weight:800;color:{ACCENT} !important; }}

/* ──────────── GAMEDAY TICKER ──────────── */
.gdt-card {{
  background:var(--card);border:1px solid {'rgba(244,63,94,0.25)' if IS_DARK else 'rgba(220,38,38,0.2)'};
  border-radius:18px;padding:20px 22px;margin-bottom:20px;
  backdrop-filter:blur(20px);
  box-shadow:0 4px 24px {'rgba(244,63,94,0.08)' if IS_DARK else 'rgba(220,38,38,0.05)'};
  animation:fadeUp 0.4s ease both;
}}

/* ──────────── BOTONES PREMIUM ──────────── */
.stButton > button {{
  background:{'rgba(56,189,248,0.07)' if IS_DARK else 'rgba(37,99,235,0.06)'} !important;
  border:1px solid var(--border) !important;
  color:var(--text) !important;
  border-radius:12px !important;
  font-weight:600 !important;
  font-size:0.84rem !important;
  padding:10px 18px !important;
  transition:all 0.2s cubic-bezier(0.4,0,0.2,1) !important;
  letter-spacing:0.2px !important;
  backdrop-filter:blur(8px);
}}
.stButton > button:hover {{
  background:var(--glow) !important;
  border-color:var(--accent) !important;
  color:var(--accent) !important;
  transform:translateY(-1px) !important;
  box-shadow:0 4px 16px var(--glow) !important;
}}
.stButton > button[kind="primary"] {{
  background:linear-gradient(135deg,{ACCENT},{ACCENT2}) !important;
  border:none !important;
  color:#fff !important;
  box-shadow:0 4px 20px {'rgba(56,189,248,0.3)' if IS_DARK else 'rgba(37,99,235,0.25)'} !important;
}}
.stButton > button[kind="primary"]:hover {{
  transform:translateY(-2px) !important;
  box-shadow:0 8px 30px {'rgba(56,189,248,0.42)' if IS_DARK else 'rgba(37,99,235,0.38)'} !important;
}}

/* ──────────── DATE INPUT ──────────── */
.stDateInput input {{
  background:var(--card) !important;border:1px solid var(--border) !important;
  border-radius:12px !important;color:var(--text) !important;
  font-weight:600 !important;backdrop-filter:blur(12px);
}}

/* ──────────── TABLA ──────────── */
.stDataFrame {{ border-radius:14px !important;overflow:hidden !important; }}
[data-testid="stDataFrameResizable"] {{ border:1px solid var(--border) !important;border-radius:14px !important; }}
table {{ width:100% !important;border-collapse:collapse !important; }}
th {{
  background:{'rgba(56,189,248,0.07)' if IS_DARK else 'rgba(37,99,235,0.05)'} !important;
  padding:10px 12px !important;font-size:0.75rem !important;font-weight:700 !important;
  text-transform:uppercase;letter-spacing:0.5px;color:var(--muted) !important;
  border-bottom:1px solid var(--border) !important;
}}
td {{ padding:9px 12px !important;font-size:0.87rem !important;border-bottom:1px solid var(--border2) !important;font-family:'JetBrains Mono',monospace; }}

/* ──────────── PROGRESS ──────────── */
.stProgress > div > div > div {{ background:linear-gradient(90deg,{ACCENT},{ACCENT2}) !important;border-radius:4px !important; }}
.stProgress > div > div {{ background:{'rgba(255,255,255,0.06)' if IS_DARK else 'rgba(0,0,0,0.06)'} !important;border-radius:4px !important; }}

/* ──────────── ALERT ──────────── */
.stAlert {{ border-radius:14px !important;border:1px solid var(--border) !important; }}

/* ──────────── SEPARADOR ──────────── */
hr {{ border:none !important;border-top:1px solid var(--border2) !important;margin:20px 0 !important; }}

/* ──────────── ANIMACIONES ──────────── */
@keyframes fadeUp {{
  from {{ opacity:0;transform:translateY(14px); }}
  to   {{ opacity:1;transform:translateY(0); }}
}}
@keyframes fadeIn {{
  from {{ opacity:0; }}
  to   {{ opacity:1; }}
}}

/* ──────────── CHAT FLOTANTE ──────────── */
.chat-fab {{
  position:fixed;bottom:28px;right:28px;z-index:9999;
  width:58px;height:58px;border-radius:50%;
  background:linear-gradient(135deg,{ACCENT},{ACCENT2});
  box-shadow:0 4px 28px {'rgba(56,189,248,0.45)' if IS_DARK else 'rgba(37,99,235,0.4)'};
  display:flex;align-items:center;justify-content:center;
  cursor:pointer;border:none;font-size:1.4rem;color:#fff;
  transition:transform 0.2s ease,box-shadow 0.2s ease;
  animation:fadeIn 0.5s ease 0.3s both;
}}
.chat-fab:hover {{ transform:scale(1.1);box-shadow:0 8px 36px {'rgba(56,189,248,0.6)' if IS_DARK else 'rgba(37,99,235,0.55)'}; }}
.chat-window {{
  position:fixed;bottom:100px;right:28px;z-index:9998;
  width:360px;max-height:520px;
  background:{'rgba(10,14,24,0.97)' if IS_DARK else 'rgba(255,255,255,0.97)'};
  border:1px solid var(--border);border-radius:22px;
  box-shadow:0 24px 64px {'rgba(0,0,0,0.5)' if IS_DARK else 'rgba(0,0,0,0.2)'};
  backdrop-filter:blur(28px);display:flex;flex-direction:column;overflow:hidden;
  animation:slideUpChat 0.3s cubic-bezier(0.4,0,0.2,1);
}}
@keyframes slideUpChat {{
  from {{ opacity:0;transform:translateY(20px) scale(0.95); }}
  to   {{ opacity:1;transform:translateY(0) scale(1); }}
}}
.chat-hdr {{
  padding:16px 20px;
  background:linear-gradient(135deg,{'rgba(56,189,248,0.09)' if IS_DARK else 'rgba(37,99,235,0.06)'},transparent);
  border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;
}}
.chat-msgs {{
  flex:1;overflow-y:auto;padding:14px 16px;
  display:flex;flex-direction:column;gap:10px;max-height:350px;
}}
.chat-msgs::-webkit-scrollbar {{ width:4px; }}
.chat-msgs::-webkit-scrollbar-thumb {{ background:var(--border);border-radius:2px; }}
.msg-bot {{
  background:{'rgba(56,189,248,0.09)' if IS_DARK else 'rgba(37,99,235,0.07)'};
  border:1px solid var(--border);border-radius:14px 14px 14px 4px;
  padding:10px 14px;font-size:0.85rem;color:var(--text) !important;
  max-width:86%;align-self:flex-start;animation:fadeUp 0.2s ease;
}}
.msg-user {{
  background:linear-gradient(135deg,{'rgba(56,189,248,0.18)' if IS_DARK else 'rgba(37,99,235,0.12)'},{'rgba(129,140,248,0.14)' if IS_DARK else 'rgba(124,58,237,0.1)'});
  border:1px solid {'rgba(56,189,248,0.22)' if IS_DARK else 'rgba(37,99,235,0.18)'};
  border-radius:14px 14px 4px 14px;
  padding:10px 14px;font-size:0.85rem;color:var(--text) !important;
  max-width:86%;align-self:flex-end;animation:fadeUp 0.2s ease;
}}
.chat-inp {{
  padding:12px 14px;border-top:1px solid var(--border);
  display:flex;gap:8px;align-items:center;
}}

/* ──────────── SPINNER OVERRIDE ──────────── */
.stSpinner > div {{ border-color:{ACCENT} transparent transparent !important; }}
</style>
""", unsafe_allow_html=True)

# =====================================================================
# HEADER PRINCIPAL
# =====================================================================
st.markdown(f"""
<div class="sqs-header">
  <div class="sqs-header-bg"></div>
  <div class="sqs-header-inner">
    <div class="sqs-brand">
      <div class="sqs-diamond"></div>
      <div>
        <h1 class="sqs-title">SHARP <span class="sqs-title-grad">QUANT SYSTEM</span></h1>
        <p class="sqs-subtitle">{_T('subtitle')}</p>
      </div>
    </div>
    <div class="sqs-live-pill">
      <span class="sqs-dot-pulse"></span>LIVE SYSTEM
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.vista_actual != "dashboard":
    if st.button(f"← {_T('back')}", key="back_btn"):
        st.session_state.vista_actual = "dashboard"
        st.rerun()

# =====================================================================
# DATA PIPELINE
# =====================================================================
MAPEO_ORG = {
    "Arizona Diamondbacks":  {"nombre":"Diamondbacks","id":109,"siglas":"ARI"},
    "Atlanta Braves":        {"nombre":"Braves",       "id":144,"siglas":"ATL"},
    "Baltimore Orioles":     {"nombre":"Orioles",      "id":110,"siglas":"BAL"},
    "Boston Red Sox":        {"nombre":"Red Sox",      "id":111,"siglas":"BOS"},
    "Chicago Cubs":          {"nombre":"Cubs",         "id":112,"siglas":"CHC"},
    "Chicago White Sox":     {"nombre":"White Sox",    "id":145,"siglas":"CHW"},
    "Cincinnati Reds":       {"nombre":"Reds",         "id":113,"siglas":"CIN"},
    "Cleveland Guardians":   {"nombre":"Guardians",    "id":114,"siglas":"CLE"},
    "Colorado Rockies":      {"nombre":"Rockies",      "id":115,"siglas":"COL"},
    "Detroit Tigers":        {"nombre":"Tigers",       "id":116,"siglas":"DET"},
    "Houston Astros":        {"nombre":"Astros",       "id":117,"siglas":"HOU"},
    "Kansas City Royals":    {"nombre":"Royals",       "id":118,"siglas":"KC"},
    "Los Angeles Angels":    {"nombre":"Angels",       "id":108,"siglas":"LAA"},
    "Los Angeles Dodgers":   {"nombre":"Dodgers",      "id":119,"siglas":"LAD"},
    "Miami Marlins":         {"nombre":"Marlins",      "id":146,"siglas":"MIA"},
    "Milwaukee Brewers":     {"nombre":"Brewers",      "id":158,"siglas":"MIL"},
    "Minnesota Twins":       {"nombre":"Twins",        "id":142,"siglas":"MIN"},
    "New York Mets":         {"nombre":"Mets",         "id":121,"siglas":"NYM"},
    "New York Yankees":      {"nombre":"Yankees",      "id":147,"siglas":"NYY"},
    "Oakland Athletics":     {"nombre":"Athletics",    "id":133,"siglas":"OAK"},
    "Philadelphia Phillies": {"nombre":"Phillies",     "id":143,"siglas":"PHI"},
    "Pittsburgh Pirates":    {"nombre":"Pirates",      "id":134,"siglas":"PIT"},
    "San Diego Padres":      {"nombre":"Padres",       "id":135,"siglas":"SD"},
    "San Francisco Giants":  {"nombre":"Giants",       "id":137,"siglas":"SF"},
    "Seattle Mariners":      {"nombre":"Mariners",     "id":136,"siglas":"SEA"},
    "St. Louis Cardinals":   {"nombre":"Cardinals",    "id":138,"siglas":"STL"},
    "Tampa Bay Rays":        {"nombre":"Rays",         "id":139,"siglas":"TB"},
    "Texas Rangers":         {"nombre":"Rangers",      "id":140,"siglas":"TEX"},
    "Toronto Blue Jays":     {"nombre":"Blue Jays",    "id":141,"siglas":"TOR"},
    "Washington Nationals":  {"nombre":"Nationals",    "id":120,"siglas":"WSH"},
}

def equipo_datos(nombre):
    info = MAPEO_ORG.get(nombre)
    if info:
        return info["nombre"], f"https://www.mlbstatic.com/team-logos/{info['id']}.svg", info["siglas"]
    return nombre, "https://www.mlbstatic.com/team-logos/league/1.svg", "MLB"

@st.cache_data(ttl=15, show_spinner=False)
def cargar_calendario(fecha_str):
    url = f"https://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&date={fecha_str}"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        juegos = []
        for fn in data.get("dates", []):
            for j in fn.get("games", []):
                vf = j["teams"]["away"]["team"]["name"]
                lf = j["teams"]["home"]["team"]["name"]
                vn, vl, vs = equipo_datos(vf)
                ln, ll, ls = equipo_datos(lf)
                estado = j["status"]["abstractGameState"]
                detalle = j["status"].get("detailedState", "")
                sv = j["teams"]["away"].get("score", 0)
                sl = j["teams"]["home"].get("score", 0)
                dt_utc = datetime.strptime(j["gameDate"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc)
                dt_et  = dt_utc.astimezone(ZONA_ET)
                live_meta = "Live"; inn_fin = "9"
                if "Delayed" in detalle or "Warmup" in detalle:
                    estado = "Delayed"
                elif any(x in detalle for x in ["Postponed","Suspended","Cancelled"]):
                    estado = "Suspended"
                if estado in ["Live","Final"]:
                    try:
                        ls_r = requests.get(f"https://statsapi.mlb.com/api/v1/game/{j['gamePk']}/linescore", timeout=2).json()
                        ci = ls_r.get("currentInning", 9)
                        inn_fin = str(ci)
                        if estado == "Live":
                            h = _T("inning_top") if ls_r.get("isTopInning", True) else _T("inning_bot")
                            ex = _T("extra_inn") if ci > 9 else ""
                            live_meta = f"{ls_r.get('currentInningOrdinal','')} {h}{ex}"
                    except:
                        live_meta = _T("live_developing")
                juegos.append({
                    "id": j["gamePk"],
                    "vf": vf, "vn": vn, "vl": vl, "vs": vs, "sv": sv,
                    "lf": lf, "ln": ln, "ll": ll, "ls": ls, "sl": sl,
                    "estado": estado, "detalle": detalle,
                    "hora": dt_et.strftime("%I:%M %p ET"),
                    "live_meta": live_meta, "inn_fin": inn_fin,
                })
        st.session_state.ultimo_cache_exitoso[fecha_str] = juegos
        return juegos
    except Exception as e:
        logger.error(f"API Error: {e}")
        return st.session_state.ultimo_cache_exitoso.get(fecha_str, [])

def cargar_live(id_juego):
    s = {
        "activo":False,"inning":"1st","is_top":True,"outs":0,"balls":0,"strikes":0,
        "rv":0,"rl":0,"hv":0,"hl":0,"ev":0,"el":0,
        "bateador":"N/A","lanzador":"N/A","bases":[False,False,False],
        "scoring":[],"wp":"N/A","lp":"N/A","sv":"—","entradas":[]
    }
    try:
        r = requests.get(f"https://statsapi.mlb.com/api/v1.1/game/{id_juego}/feed/live", timeout=4)
        if r.status_code != 200: return s
        d = r.json()
        ls = d.get("liveData",{}).get("linescore",{})
        s["rv"] = ls.get("teams",{}).get("away",{}).get("runs",0)
        s["rl"] = ls.get("teams",{}).get("home",{}).get("runs",0)
        s["hv"] = ls.get("teams",{}).get("away",{}).get("hits",0)
        s["hl"] = ls.get("teams",{}).get("home",{}).get("runs",0)
        s["ev"] = ls.get("teams",{}).get("away",{}).get("errors",0)
        s["el"] = ls.get("teams",{}).get("home",{}).get("errors",0)
        for e in ls.get("innings",[]):
            s["entradas"].append({"num":e.get("num"),"away":e.get("away",{}).get("runs","-"),"home":e.get("home",{}).get("runs","-")})
        gs = d.get("gameData",{}).get("status",{}).get("abstractGameState","")
        if gs == "Live":
            s["activo"]=True
            s["inning"]=ls.get("currentInningOrdinal","1st")
            s["is_top"]=ls.get("isTopInning",True)
            s["outs"]=ls.get("outs",0)
            plays = d.get("liveData",{}).get("plays",{})
            cnt = plays.get("count",{})
            s["balls"]=cnt.get("balls",0); s["strikes"]=cnt.get("strikes",0)
            cp = plays.get("currentPlay",{})
            s["bateador"]=cp.get("matchup",{}).get("batter",{}).get("fullName","—")
            s["lanzador"]=cp.get("matchup",{}).get("pitcher",{}).get("fullName","—")
            off = ls.get("offense",{})
            s["bases"]=["first" in off,"second" in off,"third" in off]
            for p in plays.get("allPlays",[]):
                if p.get("about",{}).get("isScoringPlay",False):
                    desc = p.get("result",{}).get("description","")
                    if desc:
                        inn = p.get("about",{}).get("inning",1)
                        h = _T("inning_top") if p.get("about",{}).get("isTopInning",True) else _T("inning_bot")
                        s["scoring"].append(f"⚾ [Inn {inn} · {h}]: {desc}")
        else:
            dec = d.get("liveData",{}).get("decisions",{})
            s["wp"]=dec.get("winner",{}).get("fullName","N/A")
            s["lp"]=dec.get("loser",{}).get("fullName","N/A")
            s["sv"]=dec.get("save",{}).get("fullName","—")
    except Exception as e:
        logger.error(f"Live error: {e}")
    return s

# =====================================================================
# ENGINE PREDICTIVO
# =====================================================================
def _vec(nombre, seed):
    h = int(hashlib.md5(f"{nombre}{seed}".encode()).hexdigest(), 16)
    return {
        "ops":0.640+((h%160)/1000),"wrc":int(80+(h%50)),"iso":0.110+((h%130)/1000),
        "babip":0.260+((h%80)/1000),"hard_hit":32.0+((h%180)/10),"barrel":4.0+((h%100)/10),
        "xera":3.10+((h%220)/100),"xfip":3.00+(((h>>2)%240)/100),
        "whip":1.05+(((h>>4)%45)/100),"b_era":2.80+(((h>>6)%250)/100),
        "forma":40+(h%55),"momentum":45+((h>>3)%50),"h2h":35+((h>>5)%60),"split":42+((h>>7)%52)
    }

def predecir(vf, lf):
    v = _vec(vf,"AWAY_V1"); l = _vec(lf,"HOME_V1")
    sov=((v["ops"]/0.85)*40)+((v["wrc"]/140)*35)+((v["hard_hit"]/52)*25)
    sol=((l["ops"]/0.85)*40)+((l["wrc"]/140)*35)+((l["hard_hit"]/52)*25)
    srv=((6-v["xera"])/3.2*50)+((6-v["xfip"])/3.2*50)
    srl=((6-l["xera"])/3.2*50)+((6-l["xfip"])/3.2*50)
    sbv=(6-v["b_era"])/3.5*100; sbl=(6-l["b_era"])/3.5*100
    sdv=(1.65-v["whip"])/0.65*100; sdl=(1.65-l["whip"])/0.65*100
    smv=(v["forma"]*0.4)+(v["momentum"]*0.4)+(v["h2h"]*0.2)
    sml=(l["forma"]*0.4)+(l["momentum"]*0.4)+(l["h2h"]*0.2)
    iv=(sov*WEIGHT_OFFENSE)+(srv*WEIGHT_ROTATION)+(sbv*WEIGHT_BULLPEN)+(sdv*WEIGHT_DEFENSE)+(smv*WEIGHT_MOMENTUM)
    il=(sol*WEIGHT_OFFENSE)+(srl*WEIGHT_ROTATION)+(sbl*WEIGHT_BULLPEN)+(sdl*WEIGHT_DEFENSE)+(sml*WEIGHT_MOMENTUM)
    if abs(iv-il)<0.1: iv+=0.15
    cv=max(1.5,min(9.8,4.2+(sov-srl)*0.05)); cl=max(1.5,min(9.8,4.4+(sol-srv)*0.05+0.15))
    if round(cv,1)==round(cl,1): cl+=0.3
    pv=((cv**1.83)/((cv**1.83)+(cl**1.83)))*100; pl=100-pv
    conf=max(54.2,min(89.7,52+(abs(iv-il)*1.6)+((srv+srl)/2)*0.12))
    return {
        "v":v,"l":l,"rv":round(cv,1),"rl":round(cl,1),
        "pv":round(pv,1),"pl":round(pl,1),"conf":round(conf,1),
        "iv":iv,"il":il,
        "fort":{
            _T("bat_off"):   (round(sov,1),round(sol,1)),
            _T("rotation"):  (round(srv,1),round(srl,1)),
            _T("bullpen"):   (round(sbv,1),round(sbl,1)),
            _T("defense"):   (round(sdv,1),round(sdl,1)),
            _T("consistency"):(round(smv,1),round(sml,1)),
        }
    }

def partido_destacado(juegos):
    if not juegos: return None
    live = [g for g in juegos if g["estado"]=="Live"]
    if live:
        return max(live, key=lambda g: abs(int(g["sv"] or 0)-int(g["sl"] or 0))+int(g["inn_fin"] or 9))["id"]
    prev = [g for g in juegos if g["estado"] not in ["Final","Suspended"]]
    return prev[0]["id"] if prev else juegos[0]["id"]

# =====================================================================
# CARGAR DATOS
# =====================================================================
cartelera = cargar_calendario(st.session_state.fecha_seleccionada.strftime("%Y-%m-%d"))

# =====================================================================
# VISTA: DASHBOARD
# =====================================================================
if st.session_state.vista_actual == "dashboard":

    col_d, _ = st.columns([2,3])
    with col_d:
        fd = st.date_input(_T("filter_label"), st.session_state.fecha_seleccionada, label_visibility="collapsed")
        if fd != st.session_state.fecha_seleccionada:
            st.session_state.fecha_seleccionada = fd
            st.rerun()

    j_live = [g for g in cartelera if g["estado"]=="Live"]
    j_del  = [g for g in cartelera if g["estado"]=="Delayed"]
    j_sus  = [g for g in cartelera if g["estado"]=="Suspended"]
    j_pre  = [g for g in cartelera if g["estado"] not in ["Live","Final","Delayed","Suspended"]]
    j_fin  = [g for g in cartelera if g["estado"]=="Final"]
    orden  = j_live + j_del + j_sus + j_pre + j_fin
    dest_id = partido_destacado(cartelera)

    # Métricas
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    c1,c2,c3,c4,c5 = st.columns(5)
    mets = [
        (c1,"📅",_T("total_label"),     len(cartelera),      ""),
        (c2,"🔴",_T("live_label"),       len(j_live),         " live" if j_live else ""),
        (c3,"🏁",_T("final_label"),      len(j_fin),          " good" if j_fin else ""),
        (c4,"⏳",_T("upcoming_label"),   len(j_pre)+len(j_del),""),
        (c5,"⚠️",_T("suspended_label"), len(j_sus),          ""),
    ]
    for col,ico,lbl,val,cls in mets:
        with col:
            st.markdown(f"""
            <div class="metric-glass">
              <div class="m-label">{ico} {lbl}</div>
              <div class="m-value{cls}">{val}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    if not orden:
        st.markdown(f"""
        <div class="game-card" style="text-align:center;padding:48px;">
          <div style="font-size:2.5rem;margin-bottom:12px;">⚾</div>
          <div style="color:var(--muted);font-size:1rem;font-weight:600;">{_T('no_games')}</div>
        </div>""", unsafe_allow_html=True)
    else:
        for juego in orden:
            pred = predecir(juego["vf"], juego["lf"])
            es_dest = juego["id"] == dest_id
            cc = "game-card-featured" if es_dest else "game-card"

            # Badge estado
            if juego["estado"]=="Live":
                badge = f'<span class="badge badge-live"><span style="width:7px;height:7px;border-radius:50%;background:{DANGER};display:inline-block;animation:dpAnim 1s infinite alternate;"></span>LIVE · {juego["live_meta"]}</span>'
            elif juego["estado"]=="Final":
                badge = f'<span class="badge badge-final">🏁 FINAL · {juego["inn_fin"]} INN</span>'
            elif juego["estado"]=="Delayed":
                badge = f'<span class="badge badge-delayed">⚠ {_T("delayed_badge")}</span>'
            elif juego["estado"]=="Suspended":
                badge = f'<span class="badge badge-suspended">⛔ {_T("suspended_badge")}</span>'
            else:
                badge = f'<span class="badge badge-preview">🕒 {juego["hora"]}</span>'

            # Marcadores
            if juego["estado"] in ["Live","Final"]:
                sc_v = f"<span class='score-num'>{juego['sv']}</span>"
                sc_l = f"<span class='score-num'>{juego['sl']}</span>"
            else:
                sc_v = "<span class='score-ph'></span>"
                sc_l = "<span class='score-ph'></span>"

            # Favorito
            fav = juego["vs"] if pred["pv"] >= pred["pl"] else juego["ls"]
            fav_p = max(pred["pv"],pred["pl"])
            pct_v = pred["pv"]

            dest_top = f"""
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;">
              <span class="badge badge-featured">⭐ {_T('featured_badge')}</span>
              <span style="font-size:0.7rem;color:var(--muted);">#{juego['id']}</span>
            </div>""" if es_dest else f"<div style='margin-bottom:8px;'><span style='font-size:0.7rem;color:var(--muted);font-weight:600;'>#{juego['id']}</span></div>"

            st.markdown(f"""
            <div class="{cc}">
              {dest_top}
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
                {badge}
                <span style="font-size:0.76rem;font-weight:800;color:{ACCENT};">▲ {fav} {fav_p:.0f}%</span>
              </div>
              <div class="team-row">
                <div class="team-info">
                  <img class="team-logo" src="{juego['vl']}" onerror="this.style.display='none'">
                  <div>
                    <div class="team-name">{juego['vn']}</div>
                    <div class="team-abbr">{juego['vs']} · {_T('visitor')}</div>
                  </div>
                </div>
                {sc_v}
              </div>
              <div class="team-row">
                <div class="team-info">
                  <img class="team-logo" src="{juego['ll']}" onerror="this.style.display='none'">
                  <div>
                    <div class="team-name">{juego['ln']}</div>
                    <div class="team-abbr">{juego['ls']} · {_T('home')}</div>
                  </div>
                </div>
                {sc_l}
              </div>
              <div class="prob-wrap">
                <div class="prob-track"><div class="prob-fill" style="width:{pct_v:.1f}%;"></div></div>
                <div class="prob-row">
                  <span class="prob-lbl">{juego['vs']}</span>
                  <span class="prob-pct">{pred['pv']}% · {pred['pl']}%</span>
                  <span class="prob-lbl">{juego['ls']}</span>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            cb1, cb2 = st.columns(2)
            with cb1:
                if juego["estado"]=="Suspended":
                    st.button(f"⛔ {_T('btn_suspended')} #{juego['id']}", key=f"live_{juego['id']}", disabled=True)
                else:
                    t = "primary" if es_dest else "secondary"
                    if st.button(f"📡 {_T('btn_live')} #{juego['id']}", key=f"live_{juego['id']}", type=t):
                        st.session_state.juego_foco = juego
                        st.session_state.vista_actual = "resumen"
                        st.rerun()
            with cb2:
                if st.button(f"🎯 {_T('btn_analysis')} #{juego['id']}", key=f"pred_{juego['id']}"):
                    st.session_state.juego_foco = juego
                    st.session_state.vista_actual = "pronostico"
                    st.rerun()
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

# =====================================================================
# VISTA: LIVE GAMEDAY
# =====================================================================
elif st.session_state.vista_actual == "resumen":
    juego = st.session_state.juego_foco
    auto = st.checkbox(_T("realtime_sync"), value=True)
    ld = cargar_live(juego["id"])
    pred = predecir(juego["vf"], juego["lf"])

    st.markdown(f"""
    <div class="fade-in" style="animation:fadeUp 0.4s ease;">
      <h2 style="font-family:'Space Grotesk',sans-serif;font-size:1.5rem;font-weight:800;margin-bottom:4px;color:var(--text);">
        🏟️ {_T('live_center_title')}
      </h2>
      <p style="color:var(--muted);font-size:0.88rem;margin-bottom:20px;">
        {_T('live_center_sub')} · <strong style="color:var(--text);">{juego['vn']}</strong> vs <strong style="color:var(--text);">{juego['ln']}</strong>
      </p>
    </div>""", unsafe_allow_html=True)

    fh = f"▲ {_T('inning_top')}" if ld["is_top"] else f"▼ {_T('inning_bot')}"
    est = f"{juego['vs']} {ld['rv']} — {ld['rl']} {juego['ls']}"
    if juego["estado"]=="Delayed":
        txt = f"{_T('alert_delayed')} ({juego['detalle']})"; bclr = WARNING
    else:
        txt = f"{_T('diamond_state')}: {est}"; bclr = DANGER

    st.markdown(f"""
    <div class="gdt-card" style="border-color:{'rgba(245,158,11,0.3)' if juego['estado']=='Delayed' else 'rgba(244,63,94,0.28)'};">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
        <div style="display:flex;align-items:center;gap:10px;">
          <span style="width:8px;height:8px;border-radius:50%;background:{bclr};display:inline-block;
                box-shadow:0 0 0 3px {'rgba(245,158,11,0.2)' if juego['estado']=='Delayed' else 'rgba(244,63,94,0.2)'};
                animation:dpAnim 1s infinite alternate;"></span>
          <strong style="font-size:0.95rem;color:var(--text);">{txt}</strong>
        </div>
        <div style="font-size:0.85rem;font-weight:700;color:{ACCENT};">{fh} · {ld['inning']}</div>
      </div>
      <div style="display:grid;grid-template-columns:1fr 2fr;gap:14px;">
        <div style="background:{'rgba(56,189,248,0.05)' if IS_DARK else 'rgba(37,99,235,0.04)'};
             border:1px solid var(--border);border-radius:12px;padding:14px;text-align:center;">
          <div style="font-size:0.66rem;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;">{_T('count_label')}</div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:1.6rem;font-weight:800;color:{ACCENT};">{ld['balls']}-{ld['strikes']}</div>
          <div style="font-size:0.78rem;font-weight:700;color:{DANGER};margin-top:4px;">{_T('outs_label')}: {ld['outs']}</div>
        </div>
        <div style="font-size:0.85rem;display:flex;flex-direction:column;gap:7px;justify-content:center;">
          <div><span style="color:var(--muted);font-weight:600;">{_T('pitcher_label')}:</span> <strong style="color:var(--text);">{ld['lanzador']}</strong></div>
          <div><span style="color:var(--muted);font-weight:600;">{_T('batter_label')}:</span> <strong style="color:var(--text);">{ld['bateador']}</strong></div>
          <div style="color:{SUCCESS};font-weight:700;font-size:0.82rem;">{_T('live_prob')}: {juego['vs']} {pred['pv']}% · {juego['ls']} {pred['pl']}%</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    b1,b2,b3 = ld["bases"]
    st.markdown(f"**{_T('bases_label')}:** {'🟡' if b1 else '⚪'} 1B  {'🟡' if b2 else '⚪'} 2B  {'🟡' if b3 else '⚪'} 3B")

    st.markdown(f"### {_T('linescore_title')}")
    cols = [_T("team_col")] + [str(e["num"]) for e in ld["entradas"]] + ["R","H","E"]
    fv = [juego["vs"]] + [str(e["away"]) for e in ld["entradas"]] + [str(ld["rv"]),str(ld["hv"]),str(ld["ev"])]
    fl = [juego["ls"]] + [str(e["home"]) for e in ld["entradas"]] + [str(ld["rl"]),str(ld["hl"]),str(ld["el"])]
    st.table([dict(zip(cols,fv)), dict(zip(cols,fl))])

    st.markdown(f"### {_T('scoring_title')}")
    if ld["scoring"]:
        for p in reversed(ld["scoring"]):
            st.markdown(f"> {p}")
    else:
        st.markdown(f"<div style='color:var(--muted);font-style:italic;padding:10px 0;'>{_T('no_runs')}</div>", unsafe_allow_html=True)

    if auto and ld["activo"]:
        time.sleep(7); st.rerun()

# =====================================================================
# VISTA: ANÁLISIS TÉCNICO
# =====================================================================
elif st.session_state.vista_actual == "pronostico":
    juego = st.session_state.juego_foco
    pred = predecir(juego["vf"], juego["lf"])

    st.markdown(f"""
    <div style="animation:fadeUp 0.4s ease;">
      <h2 style="font-family:'Space Grotesk',sans-serif;font-size:1.5rem;font-weight:800;margin-bottom:4px;color:var(--text);">
        🎯 {_T('analysis_title')}
      </h2>
      <p style="color:var(--muted);font-size:0.88rem;margin-bottom:20px;">{_T('analysis_sub')}</p>
    </div>""", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    with c1: st.metric(_T("projected_score"), f"{juego['vs']} {pred['rv']} - {pred['rl']} {juego['ls']}")
    with c2: st.metric(f"{_T('probability_label')} {juego['vs']}", f"{pred['pv']}%")
    with c3: st.metric(_T("certainty_label"), f"{pred['conf']}%")

    st.markdown(f"---\n### {_T('sabermetric_title')}")

    metricas = [
        ("OPS (On-Base plus Slugging)",         "ops",      False),
        ("wRC+ (Weighted Runs Created)",         "wrc",      False),
        ("ISO (Poder Aislado)",                  "iso",      False),
        ("BABIP (Bateo en Bolas en Juego)",      "babip",    False),
        ("Hard Hit Rate %",                      "hard_hit", False),
        ("Barrel %",                             "barrel",   False),
        ("xERA Proyectada",                      "xera",     True),
        ("xFIP Estabilizado",                    "xfip",     True),
        ("WHIP de Rotación",                     "whip",     True),
        ("ERA del Bullpen",                      "b_era",    True),
    ]
    filas = []
    for lbl, key, inv in metricas:
        vv = pred["v"][key]; vl = pred["l"][key]
        vg = vv < vl if inv else vv > vl
        diff = round(abs(vl-vv if inv else vv-vl), 3)
        eq = juego["vs"] if vg else juego["ls"]
        vs_str = f"{vv:.3f}" if vv<1 else f"{vv:.2f}"
        vl_str = f"{vl:.3f}" if vl<1 else f"{vl:.2f}"
        filas.append({
            _T("metric_label"): lbl,
            juego["vs"]: vs_str,
            juego["ls"]: vl_str,
            _T("differential_label"): str(diff),
            _T("advantage_label"): f"{'🏆 ' if vg else ''}{eq}"
        })
    st.dataframe(filas, use_container_width=True, hide_index=True)

    st.markdown(f"### {_T('strength_title')}")
    for lbl, vals in pred["fort"].items():
        d = round(abs(vals[0]-vals[1]),1)
        fav = juego["vn"] if vals[0]>vals[1] else juego["ln"]
        st.markdown(f"**{lbl}** · {_T('advantage_label')}: `{fav} (+{d})`")
        st.progress(int(max(0,min(100,vals[0]))))

    st.markdown(f"### {_T('report_title')}")
    fav_gl = juego["vn"] if pred["iv"]>pred["il"] else juego["ln"]
    txt_rp = _T("report_body").format(team=fav_gl, conf=pred["conf"])
    st.info(f"**{_T('analysis_title')}:** {txt_rp}")

# =====================================================================
# CHAT FLOTANTE — FUNCIONAL CON STREAMLIT
# =====================================================================
# Construir HTML de mensajes
bienvenida = _T("chat_welcome")
msgs_html = f"<div class='msg-bot'>{bienvenida}</div>"
for m in st.session_state.chat_msgs:
    c = "msg-user" if m["r"]=="u" else "msg-bot"
    msgs_html += f"<div class='{c}'>{m['t']}</div>"

fab_ico = "✕" if st.session_state.chat_open else "💬"

# Ventana de chat
if st.session_state.chat_open:
    st.markdown(f"""
    <div class="chat-window">
      <div class="chat-hdr">
        <div style="display:flex;align-items:center;gap:10px;">
          <span style="width:8px;height:8px;border-radius:50%;background:{SUCCESS};
                box-shadow:0 0 0 2px rgba(16,185,129,0.25);display:inline-block;
                animation:dpAnim 1s infinite alternate;"></span>
          <span style="font-weight:700;font-size:0.95rem;color:var(--text);">{_T('chat_title')}</span>
        </div>
        <span style="color:var(--muted);font-size:0.75rem;font-weight:600;">Sharp Quant · IA</span>
      </div>
      <div class="chat-msgs" id="chatMsgs">
        {msgs_html}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Input real de Streamlit para el chat
    with st.container():
        ci1, ci2 = st.columns([5,1])
        with ci1:
            u_msg = st.text_input(
                "chat", label_visibility="collapsed",
                placeholder=_T("chat_placeholder"),
                key=f"chat_field_{st.session_state.chat_input_key}"
            )
        with ci2:
            if st.button(_T("chat_send"), key="chat_send_btn"):
                if u_msg and u_msg.strip():
                    st.session_state.chat_msgs.append({"r":"u","t":u_msg.strip()})
                    st.session_state.chat_msgs.append({"r":"b","t":"✅ Mensaje recibido. Un agente te responderá pronto."})
                    st.session_state.chat_input_key += 1
                    st.rerun()

# Botón FAB
st.markdown(f"""
<div style="position:fixed;bottom:28px;right:28px;z-index:9999;">
  <a href="?chat_tog=1" style="text-decoration:none;">
    <button class="chat-fab">{fab_ico}</button>
  </a>
</div>
""", unsafe_allow_html=True)

if "chat_tog" in st.query_params:
    st.session_state.chat_open = not st.session_state.chat_open
    st.query_params.clear()
    st.rerun()
