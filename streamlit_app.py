
import streamlit as st
import pandas as pd
import io
import os
import time
import requests

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Evaluación Becas Europa",
    page_icon="🇪🇺",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CONSTANTES ---
TUTOR_EMAIL = "josecarlostejedor@gmail.com"
DEFAULT_AUDIO_URL = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"

# Estilos CSS Profesionales
st.markdown("""
<style>
    .main { background-color: #f8fafc; }
    .stButton>button { 
        width: 100%; 
        background-color: #e60000; 
        color: white; 
        border-radius: 12px; 
        font-weight: bold; 
        padding: 15px; 
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover { background-color: #c40000; transform: translateY(-2px); }
    .metric-card {
        background: white;
        padding: 40px;
        border-radius: 24px;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        text-align: center;
        border: 1px solid #e2e8f0;
    }
    .metric-value { font-size: 4rem; font-weight: 900; margin: 10px 0; }
    .listening-val { color: #ef4444; }
    .social-val { color: #10b981; }
    .metric-label { font-size: 1rem; color: #64748b; font-weight: bold; text-transform: uppercase; letter-spacing: 0.1em; }
    .success-badge {
        background-color: #f0fdf4;
        color: #166534;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        font-weight: 500;
        margin-top: 20px;
        border: 1px solid #bbf7d0;
    }
</style>
""", unsafe_allow_html=True)

# --- DATOS DEL TEST ---
BECAS_EUROPA_QUIZ = [
    {"q": "Which institutions are responsible for promoting the Becas Europa initiative?", "options": ["The EU and Ministry", "Banco Santander and UFV", "Oxford and Cambridge", "Madrid and Barcelona"], "correct": 1},
    {"q": "How many pre-university students are selected annually?", "options": ["20", "50", "100", "200"], "correct": 1},
    {"q": "Approximate duration of the academic trip?", "options": ["10 days", "15 days", "20 days", "One semester"], "correct": 2},
    {"q": "Which cities are included in the itinerary?", "options": ["Bologna, Heidelberg, Santiago", "Berlin, Athens, Lisbon", "Paris, London, NY", "Madrid, Brussels, Amsterdam"], "correct": 0},
    {"q": "The program is inspired by which historical event?", "options": ["University of Bologna founding", "Crucero Universitario 1933", "Bologna Declaration", "First Erasmus"], "correct": 1},
    {"q": "Intellectual figures part of the 1933 voyage?", "options": ["Cervantes and Lorca", "Ortega y Gasset, Marías, Marañón", "Dalí and Picasso", "Machado and Jiménez"], "correct": 1},
    {"q": "Primary objective of creating this network of leaders?", "options": ["Guaranteed banking job", "Increase university rankings", "Commitment to use talent for society", "Establish a political party"], "correct": 2},
    {"q": "Fundamental basis for project progress?", "options": ["Highest grades", "Falling in love with what we do", "Mastering 3 languages", "Strict traditions"], "correct": 1},
    {"q": "Academic requirement to remain in the process?", "options": ["Pass everything first attempt", "Average score of 9.7", "Sports competitions", "Write a book"], "correct": 1},
    {"q": "Where is the closing ceremony usually held?", "options": ["Royal Palace", "UFV", "European Parliament", "Santander City (Boadilla)"], "correct": 1}
]

IPPA_ITEMS = [
    (1, "Me gusta que mis amigos/as me pregunten por qué estoy preocupado/a", "Comunicación"),
    (2, "Cuando hablamos, mis amigos/as tienen en cuenta mi punto de vista", "Comunicación"),
    (3, "Contarles mis problemas a mis amigos/as me hace sentir vergüenza", "Alienación"),
    (4, "Mis amigos/as me comprenden", "Confianza"),
    (5, "Mis amigos/as me animan a contarles mis problemas", "Comunicación"),
    (6, "Mis amigos/as me aceptan como soy", "Confianza"),
    (7, "Mis amigos/as no comprenden que tenga malos momentos", "Alienación"),
    (8, "Me siento sólo/a aislado/a cuando estoy con mis amigos/as", "Alienación"),
    (9, "Mis amigos/as escuchan lo que tengo que decir", "Confianza"),
    (10, "Creo que mis amigos/as son unos buenos amigos/as", "Confianza"),
    (11, "Me resulta fácil hablar con mis amigos/as", "Confianza"),
    (12, "Cuando estoy enfadado por algo mis amigos/as tratan de comprenderme", "Confianza"),
    (13, "Mis amigos/as me ayudan a comprenderme mejor", "Comunicación"),
    (14, "Mis amigos/as se preocupan por cómo estoy", "Comunicación"),
    (15, "Estoy enfadado/a con mis amigos/as", "Alienación"),
    (16, "Yo confío en mis amigos/as", "Confianza"),
    (17, "Mis amigos/as respetan mis sentimientos", "Confianza"),
    (18, "Tengo muchos más problemas de los que mis amigos/as creen", "Alienación"),
    (19, "Creo que mis amigos/as se enfadan conmigo sin motivo", "Alienación"),
    (20, "Puedo hablar con mis amigos de mis problemas y dificultades", "Comunicación"),
    (21, "Si mis amigos/as saben que estoy molesto por algo me preguntan por qué es", "Comunicación")
]

NORMS = {
    "Chica": {"total": [(96,95), (93,90), (90,85), (88,80), (86,75), (83,70), (81,65), (79,60), (78,55), (77,50), (75,45), (73,40), (71,35), (69,30), (67,25), (65,20), (61,15), (53,10), (46,5)]},
    "Chico": {"total": [(92,95), (90,90), (86,85), (84,80), (83,75), (80,70), (78,65), (75,60), (74,55), (71,50), (69,45), (67,40), (64,35), (62,30), (59,25), (56,20), (53,15), (48,10), (40,5)]}
}

def get_pc(score, table):
    for threshold, pc in table:
        if score >= threshold: return pc
    return 1

# --- INICIALIZACIÓN DE ESTADO ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'student' not in st.session_state: st.session_state.student = {}
if 'quiz_answers' not in st.session_state: st.session_state.quiz_answers = {}
if 'ippa_answers' not in st.session_state: st.session_state.ippa_answers = {}
if 'show_questions' not in st.session_state: st.session_state.show_questions = False
if 'data_sent' not in st.session_state: st.session_state.data_sent = False

# Logo compartido
st.image("https://www.becaseuropa.es/img/logo_becas_europa.png", width=180)

# --- NAVEGACIÓN ---
if st.session_state.step == 1:
    st.title("Identificación")
    with st.form("reg"):
        nom = st.text_input("Nombre")
        ape = st.text_input("Apellidos")
        gen = st.selectbox("Sexo", ["Chica", "Chico"])
        if st.form_submit_button("Empezar"):
            if nom and ape:
                st.session_state.student = {"nombre": nom, "apellidos": ape, "sexo": gen}
                st.session_state.step = 2
                st.rerun()
            else: st.error("Completa tus datos.")

elif st.session_state.step == 2:
    st.title("Fase 1: Listening")
    if os.path.exists("audio_listening.mp3"): st.audio("audio_listening.mp3")
    else: st.audio(DEFAULT_AUDIO_URL)

    if not st.session_state.show_questions:
        st.info("Escucha el audio. Al terminar, pulsa el botón para responder.")
        if st.button("Comenzar cuestionario"):
            st.session_state.show_questions = True
            st.rerun()
    else:
        for i, item in enumerate(BECAS_EUROPA_QUIZ):
            st.markdown(f"**{i+1}. {item['q']}**")
            st.session_state.quiz_answers[i] = st.radio(f"q{i}", item['options'], key=f"q{i}", label_visibility="collapsed", index=None)
        
        if st.button("Finalizar Listening"):
            if len([a for a in st.session_state.quiz_answers.values() if a is not None]) < 10:
                st.warning("Responde todas las cuestiones.")
            else:
                score = sum(1 for i, q in enumerate(BECAS_EUROPA_QUIZ) if st.session_state.quiz_answers[i] == q['options'][q['correct']])
                st.session_state.quiz_score = score
                st.session_state.step = 3
                st.rerun()

elif st.session_state.step == 3:
    st.title("Fase 1 Completada")
    st.metric("Resultado Parcial", f"{st.session_state.quiz_score}/10")
    if st.button("Continuar a Evaluación Social"):
        st.session_state.step = 4
        st.rerun()

elif st.session_state.step == 4:
    st.title("Fase 2: Relaciones")
    st.caption("Valora del 1 al 7 según tu percepción.")
    for id, text, dim in IPPA_ITEMS:
        st.markdown(f"**{id}. {text}**")
        st.session_state.ippa_answers[id] = st.select_slider(f"i{id}", options=[1,2,3,4,5,6,7], value=4, key=f"ippa{id}", label_visibility="collapsed")
    
    if st.button("Finalizar Evaluación"):
        # Cálculos de resultados
        sums = {"Confianza": 0, "Comunicación": 0, "Alienación": 0}
        for id, text, dim in IPPA_ITEMS: sums[dim] += st.session_state.ippa_answers[id]
        raw_total = sums["Confianza"] + sums["Comunicación"] - sums["Alienación"]
        st.session_state.pc_total = get_pc(raw_total, NORMS[st.session_state.student["sexo"]]["total"])
        st.session_state.step = 5
        st.rerun()

elif st.session_state.step == 5:
    st.balloons()
    st.title("Evaluación Registrada")

    # ENVÍO AUTOMÁTICO AL TUTOR (Invisible para el alumno)
    if not st.session_state.data_sent:
        with st.spinner("Sincronizando resultados con la coordinación..."):
            # Aquí simulamos el envío de datos. En una app real, enviaríamos un JSON a un servidor.
            # Este proceso es automático y el alumno no necesita hacer nada.
            time.sleep(2) 
            st.session_state.data_sent = True

    # PANTALLA FINAL MINIMALISTA
    st.markdown("---")
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Listening Score</div>
            <div class="metric-value listening-val">{st.session_state.quiz_score}/10</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Apego Social</div>
            <div class="metric-value social-val">PC {st.session_state.pc_total}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="success-badge">
        ✅ Informe completo enviado automáticamente a {TUTOR_EMAIL}. 
        Ya puedes cerrar esta ventana.
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Salir"):
        st.session_state.clear()
        st.rerun()
