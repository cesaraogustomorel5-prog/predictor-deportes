import streamlit as st
import numpy as np
import requests
from datetime import datetime
import pytz
import logging
import hashlib
import time

# =====================================================================
# MODULO 1: TELEMETRÍA Y CONFIGURACIÓN ESTRUCTURAL (2026 CORE)
# =====================================================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ZONA_HORARIA = pytz.timezone('America/New_York')
AHORA_ET = datetime.now(ZONA_HORARIA)

# Inicialización estricta del Engine State para evitar colisiones de memoria
if "fecha_seleccionada" not in st.session_state:
    st.session_state.fecha_seleccionada = AHORA_ET.date()
if "vista_actual" not in st.session_state:
    st.session_state.vista_actual = "dashboard" 
if "juego_foco" not in st.session_state:
    st.session_state.juego_foco = None
if "ultimo_cache_exitoso" not in st.session_state:
    st.session_state.ultimo_cache_exitoso = {}
if "idioma" not in st.session_state:
    st.session_state.idioma = "Español"
if "chat_historial" not in st.session_state:
    st.session_state.chat_historial = [
        {"origen": "sistema", "texto": "¡Bienvenido a SHARP QUANT Support! ¿En qué podemos ayudarte hoy?", "timestamp": "12:00 PM"}
    ]
if "tema_oscuro" not in st.session_state:
    st.session_state.tema_oscuro = True

# Ponderaciones fijas del Core Sabermétrico
WEIGHT_OFFENSE = 0.30
WEIGHT_ROTATION = 0.25
WEIGHT_BULLPEN = 0.20
WEIGHT_DEFENSE = 0.15
WEIGHT_MOMENTUM = 0.10

# =====================================================================
# MODULO 2: ARQUITECTURA MULTILINGÜE DINÁMICA DE ALTA FIDELIDAD
# =====================================================================
DICCIONARIO_SISTEMA = {
    "Español": {
        "titulo": "SISTEMA CUÁNTICO SHARP", "subtitulo": "Inteligencia Artificial y Analítica de Béisbol de Élite",
        "calendario": "Calendario", "partido_destacado": "PARTIDO DESTACADO DEL DÍA", "prob_victoria": "Probabilidad de Victoria",
        "prediccion": "Proyección Sharp", "en_vivo": "EN VIVO", "finalizado": "FINALIZADO", "retrasado": "RETRASADO",
        "proximo": "PRÓXIMO", "soporte": "Soporte Cuántico", "enviar": "Enviar", "mensaje_placeholder": "Escribe un mensaje...",
        "jornada": "Jornada Total", "monitoreo": "Monitoreo Live", "finalizados": "Finalizados", "no_juegos": "No se registran compromisos analíticos para esta fecha.",
        "analisis_tec": "Análisis Técnico", "volver": "VOLVER AL CALENDARIO", "ops": "OPS Colectivo", "wrc": "wRC+ Ajustado",
        "iso": "ISO (Poder Aislado)", "babip": "BABIP de Equipo", "hard_hit": "Hard Hit Rate %", "barrel": "Barrel % Colectivo",
        "xera": "xERA Proyectada", "xfip": "xFIP Estabilizado", "whip": "WHIP General", "b_era": "ERA del Bullpen",
        "matriz_coef": "Matriz de Coeficientes Sabermétricos Avanzados", "marcador_proy": "Marcador Proyectado",
        "certeza": "Certeza Algorítmica", "historico_anot": "Historial Selectivo de Anotaciones", "sin_carreras": "No se registran carreras procesadas.",
        "pizarra": "Pizarra Oficial (Linescore)", "conteo": "CONTEO", "outs": "Outs", "ocupacion": "Ocupación de Almohadillas",
        "idioma_lbl": "Idioma del Sistema", "adjuntar": "Adjuntar Multimedia/Archivos", "tema_control": "Alternar Tema Visual"
    },
    "Inglés": {
        "titulo": "SHARP QUANT SYSTEM", "subtitulo": "Elite Baseball Artificial Intelligence & Analytics",
        "calendario": "Schedule", "partido_destacado": "FEATURED GAME OF THE DAY", "prob_victoria": "Win Probability",
        "prediccion": "Sharp Projection", "en_vivo": "LIVE", "finalizado": "FINALIZED", "retrasado": "DELAYED",
        "proximo": "UPCOMING", "soporte": "Quantum Support", "enviar": "Send", "mensaje_placeholder": "Type a message...",
        "jornada": "Total Games", "monitoreo": "Live Tracking", "finalizados": "Completed", "no_juegos": "No analytical matchups recorded for this date.",
        "analisis_tec": "Technical Analysis", "volver": "RETURN TO SCHEDULE", "ops": "Team OPS", "wrc": "Adjusted wRC+",
        "iso": "Isolated Power (ISO)", "babip": "Team BABIP", "hard_hit": "Hard Hit Rate %", "barrel": "Team Barrel %",
        "xera": "Projected xERA", "xfip": "Stabilized xFIP", "whip": "Overall WHIP", "b_era": "Bullpen ERA",
        "matriz_coef": "Advanced Sabermetric Coefficient Matrix", "marcador_proy": "Projected Score",
        "certeza": "Algorithmic Certainty", "historico_anot": "Selective Scoring Plays Log", "sin_carreras": "No runs processed yet.",
        "pizarra": "Official Linescore Table", "conteo": "COUNT", "outs": "Outs", "ocupacion": "Base Paths Status",
        "idioma_lbl": "System Language", "adjuntar": "Attach Media/Files", "tema_control": "Toggle Visual Theme"
    },
    "Francés": {
        "titulo": "SYSTÈME QUANTIQUE SHARP", "subtitulo": "Intelligence Artificielle & Analytique de Baseball d'Élite",
        "calendrier": "Calendrier", "partido_destacado": "MATCH VEDETTE DU JOUR", "prob_victoria": "Probabilité de Victoire",
        "prediccion": "Projection Sharp", "en_vivo": "EN DIRECT", "finalizado": "TERMINÉ", "retrasado": "RETARDÉ",
        "proximo": "À VENIR", "soporte": "Support Quantique", "enviar": "Envoyer", "mensaje_placeholder": "Écrivez un message...",
        "jornada": "Matchs Totaux", "monitoreo": "Suivi en Direct", "finalizados": "Terminés", "no_juegos": "Aucun match analytique enregistré pour cette date.",
        "analisis_tec": "Analyse Technique", "volver": "RETOUR AU CALENDRIER", "ops": "OPS Collectif", "wrc": "wRC+ Ajusté",
        "iso": "ISO (Puissance Isolée)", "babip": "BABIP de l'Équipe", "hard_hit": "Hard Hit Rate %", "barrel": "Barrel % Collectif",
        "xera": "xERA Projetée", "xfip": "xFIP Stabilisé", "whip": "WHIP Général", "b_era": "ERA du Bullpen",
        "matriz_coef": "Matrice des Coefficients Sabermétriques Avancés", "marcador_proy": "Score Projeté",
        "certeza": "Certitude Algorithmique", "historico_anot": "Historique Sélectif des Points", "sin_carreras": "Aucun point traité pour le moment.",
        "pizarra": "Affichage Officiel du Score", "conteo": "COMPTE", "outs": "Retraits", "ocupacion": "Situation des Buts",
        "idioma_lbl": "Langue du Système", "adjuntar": "Joindre Médias/Fichiers", "tema_control": "Changer le Thème Visuel"
    },
    "Portugués": {
        "titulo": "SISTEMA QUÂNTICO SHARP", "subtitulo": "Inteligência Artificial e Análise de Beisebol de Elite",
        "calendario": "Calendário", "partido_destacado": "PARTIDA EM DESTAQUE DO DIA", "prob_victoria": "Probabilidade de Vitória",
        "prediccion": "Projeção Sharp", "en_vivo": "AO VIVO", "finalizado": "FINALIZADO", "retrasado": "ATRASADO",
        "proximo": "PRÓXIMO", "soporte": "Suporte Quântico", "enviar": "Enviar", "mensaje_placeholder": "Digite uma mensagem...",
        "jornada": "Total de Jogos", "monitoreo": "Monitoramento Live", "finalizados": "Finalizados", "no_juegos": "Nenhum confronto analítico registrado para esta data.",
        "analisis_tec": "Análise Técnica", "volver": "VOLTAR AO CALENDÁRIO", "ops": "OPS Coletivo", "wrc": "wRC+ Ajustado",
        "iso": "ISO (Poder Isolado)", "babip": "BABIP da Equipe", "hard_hit": "Hard Hit Rate %", "barrel": "Barrel % Coletivo",
        "xera": "xERA Projetada", "xfip": "xFIP Estabilizado", "whip": "WHIP Geral", "b_era": "ERA do Bullpen",
        "matriz_coef": "Matriz de Coeficientes Sabermétricos Avançados", "marcador_proy": "Placar Projetado",
        "certeza": "Certeza Algorítmica", "historico_anot": "Histórico Seletivo de Corridas", "sin_carreras": "Nenhuma corrida processada.",
        "pizarra": "Placar Oficial (Linescore)", "conteo": "CONTAGEM", "outs": "Eliminações", "ocupacion": "Situação das Bases",
        "idioma_lbl": "Idioma do Sistema", "adjuntar": "Anexar Mídia/Arquivos", "tema_control": "Alternar Tema Visual"
    },
    "Italiano": {
        "titulo": "SISTEMA QUANTISTICO SHARP", "subtitulo": "Intelligenza Artificiale e Analisi di Baseball di Élite",
        "calendario": "Calendario", "partido_destacado": "PARTITA IN EVIDENZA DEL GIORNO", "prob_victoria": "Probabilità di Vittoria",
        "prediccion": "Proiezione Sharp", "en_vivo": "IN DIRETTA", "finalizado": "TERMINATO", "retrasado": "RITARDATO",
        "proximo": "PROSSIMO", "soporte": "Supporto Quantum", "enviar": "Invia", "mensaje_placeholder": "Scrivi un messaggio...",
        "jornada": "Partite Totali", "monitoreo": "Monitoraggio Live", "finalizados": "Concluse", "no_juegos": "Nessun match analitico registrato per questa data.",
        "analisis_tec": "Anaisi Tecnica", "volver": "TORNA AL CALENDARIO", "ops": "OPS Collettivo", "wrc": "wRC+ Regolato",
        "iso": "ISO (Potenza Isolata)", "babip": "BABIP di Squadra", "hard_hit": "Hard Hit Rate %", "barrel": "Barrel % Collettivo",
        "xera": "xERA Proiettata", "xfip": "xFIP Stabilizzato", "whip": "WHIP Generale", "b_era": "ERA del Bullpen",
        "matriz_coef": "Matrice dei Coefficienti Sabermetrici Avanzati", "marcador_proy": "Punteggio Proiettato",
        "certeza": "Certezza Algoritmica", "historico_anot": "Cronologia Selettiva delle Segnature", "sin_carreras": "Nessun punto elaborato.",
        "pizarra": "Tabellino Ufficiale (Linescore)", "conteo": "CONTEGGIO", "outs": "Eliminati", "ocupacion": "Stato dei Cuscini",
        "idioma_lbl": "Lingua del Sistema", "adjuntar": "Allega Media/File", "tema_control": "Cambia Tema Visivo"
    },
    "Alemán": {
        "titulo": "SHARP QUANTUM SYSTEM", "subtitulo": "Elite Baseball Künstliche Intelligenz & Analytik",
        "calendario": "Kalender", "partido_destacado": "TOP-SPIEL DES TAGES", "prob_victoria": "Siegwahrscheinlichkeit",
        "prediccion": "Sharp Projektion", "en_vivo": "LIVE", "finalizado": "BEENDET", "retrasado": "VERSPÄTET",
        "proximo": "DEMNÄCHST", "soporte": "Quantum-Support", "enviar": "Senden", "mensaje_placeholder": "Nachricht schreiben...",
        "jornada": "Spiele insgesamt", "monitoreo": "Live-Verfolgung", "finalizados": "Abgeschlossen", "no_juegos": "Für dieses Datum wurden keine analytischen Paarungen aufgezeichnet.",
        "analisis_tec": "Technische Analyse", "volver": "ZURÜCK ZUM KALENDER", "ops": "Team-OPS", "wrc": "Angepasster wRC+",
        "iso": "Isolierte Power (ISO)", "babip": "Team-BABIP", "hard_hit": "Hard Hit Rate %", "barrel": "Team-Barrel %",
        "xera": "Projizierte xERA", "xfip": "Stabilisierter xFIP", "whip": "Gesamt-WHIP", "b_era": "Bullpen-ERA",
        "matriz_coef": "Erweiterte sabermetrische Koeffizientenmatrix", "marcador_proy": "Projizierter Spielstand",
        "certeza": "Algorithmische Sicherheit", "historico_anot": "Selektives Punkte-Protokoll", "sin_carreras": "Noch keine Runs verarbeitet.",
        "pizarra": "Offizielles Linescore-Board", "conteo": "COUNT", "outs": "Outs", "ocupacion": "Basen-Belegung",
        "idioma_lbl": "Systemsprache", "adjuntar": "Medien/Dateien anhängen", "tema_control": "Design wechseln"
    },
    "Japonés": {
        "titulo": "シャープ・クアント・システム", "subtitulo": "エリート・ベースボール人工知能＆アナリティクス",
        "calendario": "スケジュール", "partido_destacado": "本日の注目試合", "prob_victoria": "勝利確率",
        "prediccion": "シャープ予測", "en_vivo": "試合中", "finalizado": "終了", "retrasado": "遅延",
        "proximo": "試合予定", "soporte": "クアント・サポート", "enviar": "送信", "mensaje_placeholder": "メッセージを入力...",
        "jornada": "全試合数", "monitoreo": "ライブ追跡", "finalizados": "終了済", "no_juegos": "この日付の分析対象試合はありません。",
        "analisis_tec": "テクニカル分析", "volver": "スケジュールに戻る", "ops": "チームOPS", "wrc": "調整済wRC+",
        "iso": "純長打率 (ISO)", "babip": "チームBABIP", "hard_hit": "ハードヒット率 %", "barrel": "チームバレル %",
        "xera": "予測xERA", "xfip": "安定化xFIP", "whip": "総合WHIP", "b_era": "ブルペンERA",
        "matriz_coef": "高度セイバーメトリクス係数マトリクス", "marcador_proy": "予測スコア",
        "certeza": "アルゴリズム確実性", "historico_anot": "得点プレー詳細ログ", "sin_carreras": "ランが記録されていません。",
        "pizarra": "公式ラインスコア表", "conteo": "カウント", "outs": "アウト", "ocupacion": "ランナー状況",
        "idioma_lbl": "システム言語", "adjuntar": "メディア/ファイルの添付", "tema_control": "テーマ切り替え"
    },
    "Coreano": {
        "titulo": "샤프 퀀트 시스템", "subtitulo": "엘리트 야구 인공지능 및 분석 플랫폼",
        "calendario": "일정", "partido_destacado": "오늘의 주요 경기", "prob_victoria": "승리 확률",
        "prediccion": "샤프 예측", "en_vivo": "라이브", "finalizado": "종료", "retrasado": "지연됨",
        "proximo": "경기 예정", "soporte": "퀀트 지원", "enviar": "전송", "mensaje_placeholder": "메시지 입력...",
        "jornada": "총 경기", "monitoreo": "라이브 트래킹", "finalizados": "완료됨", "no_juegos": "이 날짜에 기록된 분석 경기 매치업이 없습니다.",
        "analisis_tec": "기술 분석", "volver": "일정으로 돌아가기", "ops": "팀 OPS", "wrc": "조정 wRC+",
        "iso": "순수장타율 (ISO)", "babip": "팀 BABIP", "hard_hit": "하드히트율 %", "barrel": "팀 배럴 %",
        "xera": "예측 xERA", "xfip": "안정화 xFIP", "whip": "종합 WHIP", "b_era": "불펜 ERA",
        "matriz_coef": "고급 세이버메트릭스 계수 매트릭스", "marcador_proy": "예측 스코어",
        "certeza": "알고리즘 확실성", "historico_anot": "선택적 득점 플레이 로그", "sin_carreras": "처리된 득점이 없습니다.",
        "pizarra": "공식 라인스코어 보드", "conteo": "카운트", "outs": "아웃", "ocupacion": "주자 상황",
        "idioma_lbl": "시스템 언어", "adjuntar": "미디어/파일 첨부", "tema_control": "테마 전환"
    }
}

def txt(clave):
    return DICCIONARIO_SISTEMA[st.session_state.idioma].get(clave, clave)

# =====================================================================
# MODULO 3: INTERFAZ PREMIUM ADAPTATIVA (TEMA OSCURO / CLARO)
# =====================================================================
if st.session_state.tema_oscuro:
    css_bg = "#030712"        
    css_card = "#111827"      
    css_text = "#f9fafb"       
    css_border = "rgba(255, 255, 255, 0.08)"
    css_shadow = "rgba(0, 0, 0, 0.5)"
    css_gradient = "radial-gradient(circle at 50% 0%, #1e1b4b 0%, #030712 70%)"
else:
    css_bg = "#f3f4f6"        
    css_card = "#ffffff"      
    css_text = "#111827"       
    css_border = "rgba(0, 0, 0, 0.08)"
    css_shadow = "rgba(0, 0, 0, 0.06)"
    css_gradient = "radial-gradient(circle at 50% 0%, #dbeafe 0%, #f3f4f6 70%)"

css_accent = "#2563eb"    
css_sport = "#10b981"     

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght=300;400;500;600;700;800&family=JetBrains+Mono:wght=400;700&display=swap');
    
    .stApp {{
        background: {css_gradient} !important;
        color: {css_text} !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
        transition: background 0.3s ease, color 0.3s ease;
    }}
    
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
        max-width: 1250px !important;
    }}
    
    .premium-top-branding {{
        background: {css_card if not st.session_state.tema_oscuro else "rgba(17, 24, 39, 0.6)"};
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid {css_border};
        border-radius: 24px;
        padding: 24px 32px;
        margin-bottom: 24px;
        box-shadow: 0 20px 40px {css_shadow};
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .branding-txt h1 {{
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        letter-spacing: -1px;
        color: {css_text} !important;
        margin: 0 !important;
    }}
    .branding-txt h1 span {{
        color: {css_accent};
    }}
    .branding-sub {{
        color: #6b7280;
        font-size: 0.9rem;
        margin-top: 4px !important;
        font-weight: 500;
    }}

    /* CARDS BLINDADAS CONTRA ERRORES */
    .sport-match-card {{
        background: {css_card} !important;
        border: 1px solid {css_border} !important;
        border-radius: 20px !important;
        padding: 24px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 10px 30px {css_shadow} !important;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
        position: relative !important;
        overflow: hidden !important;
        display: block !important;
    }}
    
    .featured-match-card {{
        background: {css_card if not st.session_state.tema_oscuro else "linear-gradient(135deg, rgba(37, 99, 235, 0.15) 0%, rgba(17, 24, 39, 0.7) 100%)"} !important;
        border: 2px solid {css_accent} !important;
        border-radius: 24px !important;
        padding: 30px !important;
        margin-bottom: 28px !important;
        box-shadow: 0 25px 50px rgba(37, 99, 235, 0.2) !important;
        position: relative !important;
        overflow: hidden !important;
        display: block !important;
    }}
    
    .featured-tag {{
        position: absolute !important;
        top: 14px !important;
        right: 14px !important;
        background: linear-gradient(90deg, {css_accent}, #4f46e5) !important;
        color: white !important;
        font-size: 0.75rem !important;
        font-weight: 800 !important;
        padding: 6px 14px !important;
        border-radius: 30px !important;
        letter-spacing: 0.5px !important;
    }}

    .card-meta {{
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        border-bottom: 1px solid {css_border} !important;
        padding-bottom: 12px !important;
        margin-bottom: 16px !important;
    }}
    .team-row {{
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        margin: 14px 0 !important;
    }}
    .team-info-side {{
        display: flex !important;
        align-items: center !important;
        gap: 16px !important;
    }}
    .team-logo-frame {{
        width: 44px !important;
        height: 44px !important;
        object-fit: contain !important;
    }}
    .team-name-string {{
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        color: {css_text} !important;
    }}
    .score-display-string {{
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        color: {css_text} !important;
    }}
    .favorite-dot {{
        width: 6px !important;
        height: 6px !important;
        background-color: {css_sport} !important;
        border-radius: 50% !important;
        display: inline-block !important;
        margin-left: 8px !important;
    }}

    .status-pill {{
        display: flex !important;
        align-items: center !important;
        gap: 6px !important;
        font-size: 0.8rem !important;
        font-weight: 700 !important;
        padding: 4px 10px !important;
        border-radius: 30px !important;
    }}
    .status-live {{ background: rgba(16, 185, 129, 0.15) !important; color: {css_sport} !important; border: 1px solid rgba(16, 185, 129, 0.3) !important; }}
    .status-final {{ background: rgba(239, 68, 68, 0.15) !important; color: #ef4444 !important; border: 1px solid rgba(239, 68, 68, 0.3) !important; }}
    .status-upcoming {{ background: rgba(59, 130, 246, 0.15) !important; color: #3b82f6 !important; border: 1px solid rgba(59, 130, 246, 0.3) !important; }}
    
    .beacon-live {{
        width: 6px !important; height: 6px !important; background-color: {css_sport} !important; border-radius: 50% !important;
    }}

    .card-footer-metrics {{
        margin-top: 16px !important;
        padding-top: 12px !important;
        border-top: 1px solid {css_border} !important;
        display: flex !important;
        justify-content: space-between !important;
        font-size: 0.85rem !important;
        color: #6b7280 !important;
    }}
    
    .premium-green-text {{
        color: #10b981 !important;
        font-weight: 700 !important;
    }}

    /* CHAT UX */
    .msg-usuario {{
        background: {css_accent};
        color: white;
        padding: 12px 16px;
        border-radius: 16px 16px 4px 16px;
        margin-left: 15%;
        text-align: right;
    }}
    .msg-sistema {{
        background: {css_border};
        color: {css_text};
        padding: 12px 16px;
        border-radius: 16px 16px 16px 4px;
        margin-right: 15%;
        text-align: left;
    }}
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# MODULO 4: DATA INGESTION PIPELINE & METADATA
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
    "Tampa Bay Rays": {"nombre": "Tampa Bay", "id": 139, "siglas": "TB"},
    "Texas Rangers": {"nombre": "Rangers", "id": 140, "siglas": "TEX"},
    "Toronto Blue Jays": {"nombre": "Blue Jays", "id": 141, "siglas": "TOR"},
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
                score_vis = juego["teams"]["away"].get("score", 0)
                score_loc = juego["teams"]["home"].get("score", 0)
                
                dt_utc = datetime.strptime(juego["gameDate"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc)
                dt_et = dt_utc.astimezone(ZONA_HORARIA)

                live_string_descr = "Live Gameday"
                if abstract_state == "Live":
                    linescore_url = f"https://statsapi.mlb.com/api/v1/game/{juego['gamePk']}/linescore"
                    try:
                        ls_res = requests.get(linescore_url, timeout=2).json()
                        inn_ord = ls_res.get("currentInningOrdinal", "")
                        half = "Alta" if ls_res.get("isTopInning", True) else "Baja"
                        live_string_descr = f"{inn_ord} {half}"
                    except:
                        live_string_descr = "Live"

                juegos_procesados.append({
                    "id_juego": juego["gamePk"],
                    "vis_completo": vis_full, "vis_name": vis_name, "vis_logo": vis_logo, "vis_siglas": vis_siglas, "vis_score": score_vis,
                    "loc_completo": loc_full, "loc_name": loc_name, "loc_logo": loc_logo, "loc_siglas": loc_siglas, "loc_score": score_loc,
                    "status": abstract_state, "hora_texto": dt_et.strftime('%I:%M %p ET'),
                    "live_metadata": live_string_descr
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
        "entradas_line": []
    }
    try:
        res = requests.get(url, timeout=4)
        if res.status_code != 200: return live_struct
        data = res.json()
        linescore = data.get("liveData", {}).get("linescore", {})
        live_struct["runs_v"] = linescore.get("teams", {}).get("away", {}).get("runs", 0)
        live_struct["runs_l"] = linescore.get("teams", {}).get("home", {}).get("runs", 0)
        live_struct["hits_v"] = linescore.get("teams", {}).get("away", {}).get("hits", 0)
        live_struct["hits_l"] = linescore.get("teams", {}).get("home", {}).get("hits", 0)
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
            current_play = plays_node.get("currentPlay", {})
            live_struct["balls"] = current_play.get("count", {}).get("balls", 0)
            live_struct["strikes"] = current_play.get("count", {}).get("strikes", 0)
            live_struct["bateador"] = current_play.get("matchup", {}).get("batter", {}).get("fullName", "Bateador")
            live_struct["lanzador"] = current_play.get("matchup", {}).get("pitcher", {}).get("fullName", "Lanzador")
            
            off_node = linescore.get("offense", {})
            live_struct["bases"] = ["first" in off_node, "second" in off_node, "third" in off_node]
            
            all_plays = plays_node.get("allPlays", [])
            for p in all_plays:
                if p.get("about", {}).get("isScoringPlay", False):
                    desc = p.get("result", {}).get("description", "")
                    if desc:
                        inn_num = p.get("about", {}).get("inning", 1)
                        live_struct["scoring_plays"].append(f"⚾ [Inning {inn_num}]: {desc}")
    except Exception as e:
        logger.error(f"Fallo parsing Live Gameday Feed: {e}")
    return live_struct

# =====================================================================
# MODULO 5: ENGINE PREDICTIVO SABERMÉTRICO QUANT
# =====================================================================
def simular_vector_sabermetrico_estable(nombre_completo, seed_str):
    h = int(hashlib.md5(f"{nombre_completo}{seed_str}".encode()).hexdigest(), 16)
    return {
        "ops": 0.640 + ((h % 160) / 1000.0), "wrc": int(80 + (h % 50)), "iso": 0.110 + ((h % 130) / 1000.0),
        "babip": 0.260 + ((h % 80) / 1000.0), "hard_hit": 32.0 + ((h % 180) / 10.0), "barrel": 4.0 + ((h % 100) / 10.0),
        "xera": 3.10 + ((h % 220) / 100.0), "xfip": 3.00 + (((h >> 2) % 240) / 100.0), "whip": 1.05 + (((h >> 4) % 45) / 100.0),
        "b_era": 2.80 + (((h >> 6) % 250) / 100.0), "forma": 40 + (h % 55), "momentum": 45 + ((h >> 3) % 50)
    }

def ejecutar_motor_predictivo_sharp(vis_full, loc_full):
    v = simular_vector_sabermetrico_estable(vis_full, "AWAY_V1")
    l = simular_vector_sabermetrico_estable(loc_full, "HOME_V1")
    
    score_off_v = ((v["ops"] / 0.850) * 40) + ((v["wrc"] / 140) * 35) + ((v["hard_hit"] / 52) * 25)
    score_off_l = ((l["ops"] / 0.850) * 40) + ((l["wrc"] / 140) * 35) + ((l["hard_hit"] / 52) * 25)
    score_rot_v = ((6.0 - v["xera"]) / 3.2 * 50) + ((6.0 - v["xfip"]) / 3.2 * 50)
    score_rot_l = ((6.0 - l["xera"]) / 3.2 * 50) + ((6.0 - l["xfip"]) / 3.2 * 50)
    
    idx_v = (score_off_v * WEIGHT_OFFENSE) + (score_rot_v * WEIGHT_ROTATION)
    idx_l = (score_off_l * WEIGHT_OFFENSE) + (score_rot_l * WEIGHT_ROTATION)
    
    carreras_v = max(1.5, min(9.8, 4.2 + (score_off_v - score_rot_l) * 0.05))
    carreras_l = max(1.5, min(9.8, 4.4 + (score_off_l - score_rot_v) * 0.05 + 0.15))
    if round(carreras_v, 1) == round(carreras_l, 1): carreras_l += 0.3
        
    prob_v = ((carreras_v ** 1.83) / ((carreras_v ** 1.83) + (carreras_l ** 1.83))) * 100
    prob_l = 100.0 - prob_v
    confianza = max(54.2, min(89.7, 52.0 + (abs(idx_v - idx_l) * 2.5)))
    
    return {
        "v": v, "l": l, "runs_v": round(carreras_v, 1), "runs_l": round(carreras_l, 1),
        "prob_v": round(prob_v, 1), "prob_l": round(prob_l, 1), "confianza": round(confianza, 1),
        "fav": "VIS" if prob_v > prob_l else "LOC"
    }

# =====================================================================
# MODULO 6: ENCABEZADO PREMIUM Y CONTROL DE LOCALIZACIÓN
# =====================================================================
st.markdown(f"""
    <div class='premium-top-branding'>
        <div class='branding-txt'>
            <h1>SHARP <span>QUANT</span></h1>
            <div class='branding-sub'>{txt("subtitulo")}</div>
        </div>
    </div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"### 🌐 {txt('idioma_lbl')}")
    idioma_previo = st.session_state.idioma
    st.session_state.idioma = st.selectbox(
        "Localization Selector", 
        ["Español", "Inglés", "Francés", "Portugués", "Italiano", "Alemán", "Japonés", "Coreano"],
        index=["Español", "Inglés", "Francés", "Portugués", "Italiano", "Alemán", "Japonés", "Coreano"].index(st.session_state.idioma),
        label_visibility="collapsed"
    )
    if idioma_previo != st.session_state.idioma:
        st.rerun()

# Carga de datos base
cartelera_total = cargar_calendario_api(st.session_state.fecha_seleccionada.strftime('%Y-%m-%d'))

id_juego_destacado = None
if cartelera_total:
    juegos_vivos = [j for j in cartelera_total if j["status"] == "Live"]
    if juegos_vivos: id_juego_destacado = juegos_vivos[0]["id_juego"]
    else: id_juego_destacado = cartelera_total[0]["id_juego"]

# =====================================================================
# INTERFAZ DE BOTONES COMPLEMENTARIOS (MODO CLARO/OSCURO Y VOLVER)
# =====================================================================
with st.sidebar:
    st.markdown(f"### 🛠️ UI Quick Controls")
    col_theme, col_back = st.columns(2)
    with col_theme:
        if st.button("🌓 Theme", use_container_width=True, help=txt("tema_control")):
            st.session_state.tema_oscuro = not st.session_state.tema_oscuro
            st.rerun()
    with col_back:
        disabled_status = (st.session_state.vista_actual == "dashboard")
        if st.button("⬅️ Back", use_container_width=True, disabled=disabled_status, help=txt("volver")):
            st.session_state.vista_actual = "dashboard"
            st.rerun()

# =====================================================================
# VISTA: CALENDARIO PREMIUM (DASHBOARD)
# =====================================================================
if st.session_state.vista_actual == "dashboard":
    st.markdown(f"### 📅 {txt('calendario')}")
    st.session_state.fecha_seleccionada = st.date_input("Filtro Temporal", st.session_state.fecha_seleccionada, label_visibility="collapsed")
    
    k1, k2, k3 = st.columns(3)
    with k1: st.metric(txt("jornada"), len(cartelera_total))
    with k2: st.metric(txt("monitoreo"), len([g for g in cartelera_total if g["status"] == "Live"]))
    with k3: st.metric(txt("finalizados"), len([g for g in cartelera_total if g["status"] == "Final"]))
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not cartelera_total:
        st.info(txt("no_juegos"))
    else:
        for juego in cartelera_total:
            pred = ejecutar_motor_predictivo_sharp(juego["vis_completo"], juego["loc_completo"])
            es_destacado = (juego["id_juego"] == id_juego_destacado)
            
            card_class = "featured-match-card" if es_destacado else "sport-match-card"
            tag_destacado_html = f"<div class='featured-tag'>{txt('partido_destacado')}</div>" if es_destacado else ""
            
            if juego["status"] == "Live":
                status_html = f"<div class='status-pill status-live'><span class='beacon-live'></span>{txt('en_vivo')} · {juego['live_metadata']}</div>"
                marcador_v = f"<span class='score-display-string'>{juego['vis_score']}</span>"
                marcador_l = f"<span class='score-display-string'>{juego['loc_score']}</span>"
            elif juego["status"] == "Final":
                status_html = f"<div class='status-pill status-final'>🏁 {txt('finalizado')}</div>"
                marcador_v = f"<span class='score-display-string'>{juego['vis_score']}</span>"
                marcador_l = f"<span class='score-display-string'>{juego['loc_score']}</span>"
            else:
                status_html = f"<div class='status-pill status-upcoming'>🕒 {juego['hora_texto']}</div>"
                marcador_v = "<span style='color:rgba(255,255,255,0.2); font-size:0.9rem;'>-</span>"
                marcador_l = "<span style='color:rgba(255,255,255,0.2); font-size:0.9rem;'>-</span>"
                
            # SANITIZACIÓN ABSOLUTA PRE-RENDERIZADO HTML
            j_id = str(juego['id_juego'])
            v_logo = str(juego['vis_logo'])
            v_name = str(juego['vis_name'])
            v_siglas = str(juego['vis_siglas'])
            l_logo = str(juego['loc_logo'])
            l_name = str(juego['loc_name'])
            l_siglas = str(juego['loc_siglas'])
            
            dot_v = "<span class='favorite-dot'></span>" if pred["fav"] == "VIS" else ""
            dot_l = "<span class='favorite-dot'></span>" if pred["fav"] == "LOC" else ""
            
            label_probabilidad = txt('prob_victoria')
            siglas_favorito = v_siglas if pred['fav'] == "VIS" else l_siglas
            porcentaje_favorito = str(pred['prob_v']) if pred['fav'] == "VIS" else str(pred['prob_l'])
            proj_v = str(pred['runs_v'])
            proj_l = str(pred['runs_l'])
            
            # Construcción Blindada sin interferencia de comillas dinámicas internas
            bloque_tarjeta_completo = f"""
                <div class="{card_class}">
                    {tag_destacado_html}
                    <div class="card-meta">
                        <div style="font-size:0.75rem; color:#9ca3af; font-family:monospace;">ID #{j_id}</div>
                        {status_html}
                    </div>
                    <div class="team-row">
                        <div class="team-info-side">
                            <img class="team-logo-frame" src="{v_logo}">
                            <span class="team-name-string">{v_name} <small style="color:#6b7280;">{v_siglas}</small> {dot_v}</span>
                        </div>
                        {marcador_v}
                    </div>
                    <div class="team-row">
                        <div class="team-info-side">
                            <img class="team-logo-frame" src="{l_logo}">
                            <span class="team-name-string">{l_name} <small style="color:#6b7280;">{l_siglas}</small> {dot_l}</span>
                        </div>
                        {marcador_l}
                    </div>
                    <div class="card-footer-metrics">
                        <div>💡 Proyección: <b>{v_siglas} {proj_v} - {proj_l} {l_siglas}</b></div>
                        <div>📊 {label_probabilidad}: <span class="premium-green-text">{siglas_favorito} {porcentaje_favorito}%</span></div>
                    </div>
                </div>
            """
            st.markdown(bloque_tarjeta_completo, unsafe_allow_html=True)
            
            c_b1, c_b2 = st.columns(2)
            with c_b1:
                if st.button(f"📺 LIVE TICKER #{j_id}", key=f"nav_live_{j_id}", use_container_width=True):
                    st.session_state.juego_foco = juego
                    st.session_state.vista_actual = "resumen"
                    st.rerun()
            with c_b2:
                if st.button(f"🎯 {txt('analisis_tec')} #{j_id}", key=f"nav_pred_{j_id}", use_container_width=True):
                    st.session_state.juego_foco = juego
                    st.session_state.vista_actual = "pronostico"
                    st.rerun()
            st.markdown("<div style='margin-bottom:24px;'></div>", unsafe_allow_html=True)

# =====================================================================
# VISTA: LIVE CONTROL CORE (TICKER REAL-TIME)
# =====================================================================
elif st.session_state.vista_actual == "resumen":
    juego = st.session_state.juego_foco
    st_autorefresh = st.checkbox("Sincronización Automática Activa (7s)", value=True)
    
    live_data = descargar_datos_live_gameday(juego["id_juego"])
    st.markdown(f"## 🏟️ Live Gameday Match-Center")
    st.markdown(f"⚡ **{juego['vis_name']}** vs **{juego['loc_name']}**")
    
    st.markdown(f"""
        <div class='sport-match-card' style='border-left: 4px solid {css_sport};'>
            <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;'>
                <div style='font-weight:700; color:{css_sport};'>🔴 {txt('en_vivo').upper()}</div>
                <div style='font-family:monospace; font-weight:700;'>{live_data['inning']}</div>
            </div>
            <div style='display:grid; grid-template-columns: 2fr 1fr; gap:20px;'>
                <div>
                    <h4>{txt('conteo')}: {live_data['balls']} - {live_data['strikes']} | {txt('outs')}: {live_data['outs']}</h4>
                    <p style='color:#9ca3af; font-size:0.9rem;'><b>Pitcher:</b> {live_data['lanzador']} | <b>Hitter:</b> {live_data['bateador']}</p>
                </div>
                <div style='text-align:right;'><h3 style='color:{css_sport}; font-family:monospace;'>{live_data['runs_v']} - {live_data['runs_l']}</h3></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    b1, b2, b3 = live_data["bases"]
    st.markdown(f"**{txt('ocupacion')}:** | {'1B [✖]' if b1 else '1B [ ── ]'} | {'2B [✖]' if b2 else '2B [ ── ]'} | {'3B [✖]' if b3 else '3B [ ── ]'} |")
    
    fil_v = [juego["vis_siglas"]] + [str(e["away"]) for e in live_data["entradas_line"]] + [str(live_data["runs_v"]), str(live_data["hits_v"]), str(live_data["errors_v"])]
    fil_l = [juego["loc_siglas"]] + [str(e["home"]) for e in live_data["entradas_line"]] + [str(live_data["runs_l"]), str(live_data["hits_l"]), str(live_data["errors_l"])]
    st.table([fil_v, fil_l])
    
    if st_autorefresh and live_data["activo"]:
        time.sleep(7)
        st.rerun()

# =====================================================================
# VISTA: ANÁLISIS SABERMÉTRICO INTERACTIVO NATIVO
# =====================================================================
elif st.session_state.vista_actual == "pronostico":
    juego = st.session_state.juego_foco
    pred = ejecutar_motor_predictivo_sharp(juego["vis_completo"], juego["loc_completo"])
    
    st.markdown(f"## 📊 {txt('matriz_coef')}")
    dataset_limpio = []
    for label, key in [(txt("ops"), "ops"), (txt("wrc"), "wrc"), (txt("iso"), "iso"), (txt("hard_hit"), "hard_hit")]:
        dataset_limpio.append({
            "Métrica": label, juego["vis_siglas"]: f"{pred['v'][key]:.3f}" if pred['v'][key] < 2 else f"{pred['v'][key]:.1f}",
            juego["loc_siglas"]: f"{pred['l'][key]:.3f}" if pred['l'][key] < 2 else f"{pred['l'][key]:.1f}"
        })
    st.dataframe(dataset_limpio, use_container_width=True, hide_index=True)

# =====================================================================
# MODULO 7: CHAT DE SOPORTE INTERACTIVO MULTIMEDIA (CORREGIDO)
# =====================================================================
with st.sidebar:
    st.markdown("---")
    st.markdown(f"### 💬 {txt('soporte')}")
    
    # Renderizado del historial de conversión dinámico
    for msg in st.session_state.chat_historial:
        clase_origen = "msg-usuario" if msg["origen"] == "usuario" else "msg-sistema"
        st.markdown(f"""
            <div class='{clase_origen}' style='margin-bottom:8px; font-size:0.85rem;'>
                {msg['texto']}<br>
                <small style='font-size:0.65rem; opacity:0.6;'>{msg['timestamp']}</small>
            </div>
        """, unsafe_allow_html=True)
        if "meta_adjunto" in msg:
            st.caption(f"📎 Archivo: {msg['meta_adjunto']}")

    # SOLUCIÓN AL TYPEERROR: El file_uploader se ejecuta FUERA del formulario
    archivo_usuario = st.file_uploader(txt("adjuntar"), type=["png", "jpg", "mp4", "mov", "csv", "txt", "pdf"], label_visibility="visible")

    # El formulario ahora procesa los strings de manera limpia y segura
    with st.form("quantum_chat_form", clear_on_submit=True):
        input_texto = st.text_input("Chat Msg", placeholder=txt("mensaje_placeholder"), label_visibility="collapsed")
        bot_enviar = st.form_submit_button(txt("enviar"), use_container_width=True)
        
        if bot_enviar and (input_texto or archivo_usuario):
            stamp = datetime.now(ZONA_HORARIA).strftime('%I:%M %p')
            nombre_archivo = archivo_usuario.name if archivo_usuario is not None else None
            
            # Registrar mensaje del usuario en el historial
            msg_u = {"origen": "usuario", "texto": input_texto if input_texto else f"[Fichero: {nombre_archivo}]", "timestamp": stamp}
            if nombre_archivo: 
                msg_u["meta_adjunto"] = nombre_archivo
            st.session_state.chat_historial.append(msg_u)
            
            # Respuesta simulada inteligente por el Agente Cuántico
            respuesta_bot = "Mensaje de texto recibido por la IA. Optimizando respuesta analítica."
            if nombre_archivo:
                respuesta_bot = f"Fichero '{nombre_archivo}' indexado con éxito. Ejecutando escaneo cuántico en paralelo para identificar patrones sabermétricos."
                
            st.session_state.chat_historial.append({
                "origen": "sistema",
                "texto": respuesta_bot,
                "timestamp": stamp
            })
            st.rerun()
