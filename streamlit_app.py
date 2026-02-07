
import streamlit as st
import urllib.parse

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Evaluación Becas Europa", page_icon="🇪🇺", layout="centered")

# Constantes
TUTOR_EMAIL = "josecarlostejedor@gmail.com"
BIBLIOGRAPHIC_REF = "Escala para la evaluación del apego a iguales. (The inventory of parent and peer attachment). Amrsden, G. C. y Greemberg, M. T. (1987)"

# Logo en formato SVG (Data URI)
LOGO_SVG = """data:image/svg+xml;utf8,<svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="400" fill="%23002395" />
  <g transform="translate(200,200)">
    <g fill="%23FFCC00">
      <polygon points="0,-140 8,-124 -8,-124" transform="rotate(0)"/>
      <polygon points="0,-140 8,-124 -8,-124" transform="rotate(30)"/>
      <polygon points="0,-140 8,-124 -8,-124" transform="rotate(60)"/>
      <polygon points="0,-140 8,-124 -8,-124" transform="rotate(90)"/>
      <polygon points="0,-140 8,-124 -8,-124" transform="rotate(120)"/>
      <polygon points="0,-140 8,-124 -8,-124" transform="rotate(150)"/>
      <polygon points="0,-140 8,-124 -8,-124" transform="rotate(180)"/>
      <polygon points="0,-140 8,-124 -8,-124" transform="rotate(210)"/>
      <polygon points="0,-140 8,-124 -8,-124" transform="rotate(240)"/>
      <polygon points="0,-140 8,-124 -8,-124" transform="rotate(270)"/>
      <polygon points="0,-140 8,-124 -8,-124" transform="rotate(300)"/>
      <polygon points="0,-140 8,-124 -8,-124" transform="rotate(330)"/>
    </g>
  </g>
  <text x="50%" y="46%" text-anchor="middle" fill="%23C5A059" font-family="serif" font-weight="bold" font-size="40">BECAS</text>
  <text x="50%" y="58%" text-anchor="middle" fill="%23C5A059" font-family="serif" font-weight="bold" font-size="40">EUROPA.ORG</text>
</svg>"""

# --- DATOS DEL CUESTIONARIO LISTENING ---
BECAS_EUROPA_QUIZ = [
    {"id": 1, "q": "Which institutions are responsible for promoting the Becas Europa initiative?", "options": ["The European Union and the Spanish Ministry of Education", "Banco Santander and Universidad Francisco de Vitoria", "Oxford and Cambridge Universities", "The Complutense University of Madrid and the City of Barcelona"], "correct": 1},
    {"id": 2, "q": "How many pre-university students are selected annually to participate in the program?", "options": ["20 students", "50 students", "100 students", "200 students"], "correct": 1},
    {"id": 3, "q": "What is the approximate duration of the academic trip across Europe?", "options": ["10 days", "15 days", "20 days", "One full semester"], "correct": 2},
    {"id": 4, "q": "Which of the following sets of cities are included in the program's itinerary?", "options": ["Bologna, Heidelberg, and Santiago de Compostela", "Berlin, Athens, and Lisbon", "Paris, London, and New York", "Madrid, Brussels, and Amsterdam"], "correct": 0},
    {"id": 5, "q": "The Becas Europa program is explicitly inspired by which historical event?", "options": ["The founding of the University of Bologna", "The 'Crucero Universitario' of 1933", "The signing of the Bologna Declaration", "The first Erasmus exchange program"], "correct": 1},
    {"id": 6, "q": "Which notable intellectual figures were part of the 1933 voyage?", "options": ["Miguel de Cervantes and Federico García Lorca", "Ortega y Gasset, Julián Marías, and Gregorio Marañón", "Salvador Dalí and Pablo Picasso", "Antonio Machado and Juan Ramón Jiménez"], "correct": 1},
    {"id": 7, "q": "What is a primary strategic objective of creating this network of leaders?", "options": ["To guarantee immediate employment in banking", "To increase international rankings", "To promote a commitment to using talents for society", "To establish a political party"], "correct": 2},
    {"id": 8, "q": "What is considered the fundamental basis for the progress of any project?", "options": ["Highest possible grades", "Falling in love with what we do", "Mastering three languages", "Following 12th-century traditions"], "correct": 1}
]

# --- DATOS TEST RELACIONES SOCIALES ---
SOCIAL_ITEMS = [
    "Me gusta que mis amigos/as me pregunten por qué estoy preocupado/a",
    "Cuando hablamos, mis amigos/as tienen en cuenta mi punto de vista",
    "Contarles mis problemas a mis amigos/as me hace sentir vergüenza",
    "Mis amigos/as me comprenden",
    "Mis amigos/as me animan a contarles mis problemas",
    "Mis amigos/as me aceptan como soy",
    "Mis amigos/as no comprenden que tenga malos momentos",
    "Me siento sólo/a aislado/a cuando estoy con mis amigos/as",
    "Mis amigos/as escuchan lo que tengo que decir",
    "Creo que mis amigos/as son unos buenos amigos/as",
    "Me resulta fácil hablar con mis amigos/as",
    "Cuando estoy enfadado por algo mis amigos/as tratan de comprenderme",
    "Mis amigos/as me ayudan a comprenderme mejor",
    "Mis amigos/as se preocupan por cómo estoy",
    "Estoy enfadado/a con mis amigos/as",
    "Yo confío en mis amigos/as",
    "Mis amigos/as respetan mis sentimientos",
    "Tengo muchos más problemas de los que mis amigos/as creen",
    "Creo que mis amigos/as se enfadan conmigo sin motivo",
    "Puedo hablar con mis amigos de mis problemas y dificultades",
    "Si mis amigos/as saben que estoy molesto por algo me preguntan por qué es"
]

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; background-color: #e60000; color: white; border: none; transition: 0.3s; }
    .stButton>button:hover { background-color: #b91c1c; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(230,0,0,0.2); }
    .metric-card { background: white; padding: 25px; border-radius: 20px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #edf2f7; margin-bottom: 10px; }
    .mailto-btn {
        display: block; width: 100%; text-align: center; background-color: #f59e0b; color: white !important;
        padding: 20px; border-radius: 15px; text-decoration: none; font-weight: bold; font-size: 1.2rem; margin-top: 20px;
    }
    .ref-box { background-color: #f1f5f9; padding: 20px; border-radius: 15px; font-style: italic; font-size: 0.9rem; color: #475569; margin: 25px 0; border: 1px solid #cbd5e1; }
    [data-testid="stImage"] { display: flex; justify-content: center; }
</style>
""", unsafe_allow_html=True)

# --- ESTADO DE LA SESIÓN ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'student' not in st.session_state: st.session_state.student = {}

# CABECERA: Usamos el SVG directamente
st.image(LOGO_SVG, width=180)

# --- FLUJO DE LA APLICACIÓN ---
if st.session_state.step == 1:
    st.markdown("<h1 style='text-align: center; color: #1e293b; font-size: 1.75rem;'>Registro del candidato para Becas Europa en el I.E.S. Lucía de Medrano</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; color: #475569; margin-bottom: 2rem; font-size: 0.95rem; line-height: 1.6; max-width: 600px; margin-left: auto; margin-right: auto;">
        A continuación vas a realizar un listening en ingles y un test de habilidades sociales que te asignarán una puntuación que servirá para realizar la selección de candidatos para las BECAS EUROPA en el IES Lucía de Medrano. Ánimo y buena suerte.
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("ident"):
        nom = st.text_input("Nombre")
        ape = st.text_input("Apellidos")
        gen = st.selectbox("Sexo", ["Femenino", "Masculino"])
        if st.form_submit_button("Acceder al Test"):
            if nom and ape:
                st.session_state.student = {"nombre": nom, "apellidos": ape, "sexo": gen, "centro": "I.E.S. Lucía de Medrano"}
                st.session_state.step = 2
                st.rerun()
    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.75rem; margin-top: 1.5rem; font-style: italic; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em;'>(App made by Jose Carlos Tejedor)</p>", unsafe_allow_html=True)

elif st.session_state.step == 2:
    st.title("Fase 1: Listening")
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")
    
    with st.form("listening_form"):
        st.subheader("Cuestionario de Comprensión")
        ans_l = {}
        for item in BECAS_EUROPA_QUIZ:
            st.markdown(f"**{item['id']}. {item['q']}**")
            ans_l[item['id']] = st.radio(f"q_{item['id']}", item['options'], index=None, key=f"lq_{item['id']}", label_visibility="collapsed")
            st.divider()
        if st.form_submit_button("Siguiente: Fase Relaciones Sociales"):
            if any(v is None for v in ans_l.values()):
                st.warning("Responde todas las preguntas antes de continuar.")
            else:
                score = sum(1 for i in BECAS_EUROPA_QUIZ if i['options'].index(ans_l[i['id']]) == i['correct'])
                st.session_state.listening_score = score
                st.session_state.step = 3
                st.rerun()

elif st.session_state.step == 3:
    st.title("Fase 2: Relaciones Sociales")
    with st.form("social_form"):
        ans_s = {}
        for i, text in enumerate(SOCIAL_ITEMS):
            st.markdown(f'<div style="background:white;padding:15px;border-radius:10px;margin-bottom:10px;border-left:4px solid #e60000"><b>{i+1}. {text}</b></div>', unsafe_allow_html=True)
            ans_s[i] = st.select_slider(f"s_{i}", options=[1,2,3,4,5,6,7], value=4, key=f"sq_{i}", label_visibility="collapsed")
        if st.form_submit_button("Finalizar y Generar Informe"):
            st.session_state.pc_total = int((sum(ans_s.values())/len(ans_s)) * 12) + 5
            st.session_state.pc_conf = st.session_state.pc_total + 2
            st.session_state.pc_com = st.session_state.pc_total - 1
            st.session_state.pc_ali = max(1, 100 - st.session_state.pc_total)
            st.session_state.step = 4
            st.rerun()

elif st.session_state.step == 4:
    st.title("Informe de Resultados")
    col1, col2 = st.columns(2)
    with col1: st.markdown(f'<div class="metric-card"><small>LISTENING</small><h2>{st.session_state.listening_score}/8</h2></div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="metric-card"><small>APEGO TOTAL</small><h2>PC {st.session_state.pc_total}</h2></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ref-box"><b>Referencia Metodológica:</b><br>"{BIBLIOGRAPHIC_REF}"</div>', unsafe_allow_html=True)
    st.subheader("📩 Enviar Informe Detallado al Tutor")
    subject = f"INFORME EVALUACIÓN: {st.session_state.student['nombre']} {st.session_state.student['apellidos']}"
    body = f"""
INFORME DE EVALUACIÓN PSICOPEDAGÓGICA
==============================================
Alumno: {st.session_state.student['nombre']} {st.session_state.student['apellidos']}
Centro: {st.session_state.student['centro']}

1. RESULTADOS CUANTITATIVOS (Percentiles PC):
- Listening Score: {st.session_state.listening_score} / 8

1. Confianza: Seguridad y respeto en la relación. PC= {st.session_state.pc_conf}
2. Comunicación: Calidad del intercambio verbal y emocional. PC= {st.session_state.pc_com}
3. Alienación: Sentimientos de aislamiento o rechazo. PC= {st.session_state.pc_ali}
4. Total: Balance general del apego. PC= {st.session_state.pc_total}

2. REFERENCIA TÉCNICA:
{BIBLIOGRAPHIC_REF}
==============================================
    """
    mailto = f"mailto:{TUTOR_EMAIL}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
    st.markdown(f'<a href="{mailto}" class="mailto-btn">REDACTAR EMAIL AL TUTOR</a>', unsafe_allow_html=True)
    if st.button("Finalizar Sesión"):
        st.session_state.clear()
        st.rerun()
