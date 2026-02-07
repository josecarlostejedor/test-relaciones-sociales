
import streamlit as st
import urllib.parse

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Evaluación Becas Europa", page_icon="🇪🇺", layout="centered")
TUTOR_EMAIL = "josecarlostejedor@gmail.com"

# --- DATOS DEL CUESTIONARIO LISTENING (8 PREGUNTAS) ---
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

# --- DATOS TEST RELACIONES SOCIALES (21 PREGUNTAS) ---
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

# --- ESTILOS ---
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; background-color: #e60000; color: white; border: none; }
    .stButton>button:hover { background-color: #cc0000; color: white; }
    .metric-card { background: white; padding: 30px; border-radius: 20px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #edf2f7; }
    .mailto-btn {
        display: block;
        width: 100%;
        text-align: center;
        background-color: #f59e0b;
        color: white !important;
        padding: 20px;
        border-radius: 15px;
        text-decoration: none;
        font-weight: bold;
        font-size: 1.2rem;
        margin-top: 20px;
    }
    .mailto-btn:hover { background-color: #d97706; }
    .question-container {
        background: white;
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #e60000;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- ESTADO ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'student' not in st.session_state: st.session_state.student = {}
if 'listening_score' not in st.session_state: st.session_state.listening_score = 0

st.image("https://www.becaseuropa.es/img/logo_becas_europa.png", width=180)

# --- NAVEGACIÓN ---
if st.session_state.step == 1:
    st.title("Registro del Candidato")
    with st.form("ident_form"):
        nom = st.text_input("Nombre")
        ape = st.text_input("Apellidos")
        gen = st.selectbox("Sexo", ["Femenino", "Masculino"])
        if st.form_submit_button("Siguiente"):
            if nom and ape:
                st.session_state.student = {"nombre": nom, "apellidos": ape, "sexo": gen}
                st.session_state.step = 2
                st.rerun()
            else:
                st.error("Por favor, completa nombre y apellidos.")

elif st.session_state.step == 2:
    st.title("Fase 1: Listening")
    st.info("Escucha el audio atentamente antes de responder a las 8 preguntas.")
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")
    
    with st.form("listening_form"):
        st.subheader("Cuestionario de Comprensión")
        listening_answers = {}
        for item in BECAS_EUROPA_QUIZ:
            st.markdown(f"**{item['id']}. {item['q']}**")
            # index=None asegura que no haya ninguna opción seleccionada por defecto
            listening_answers[item['id']] = st.radio(
                f"Opciones para {item['id']}", 
                item['options'], 
                key=f"listen_q_{item['id']}",
                label_visibility="collapsed",
                index=None 
            )
            st.divider()
            
        if st.form_submit_button("Finalizar Listening y pasar a Relaciones"):
            # Validamos que se hayan respondido todas
            if any(val is None for val in listening_answers.values()):
                st.warning("Por favor, responde a todas las preguntas antes de continuar.")
            else:
                score = 0
                for item in BECAS_EUROPA_QUIZ:
                    selected_val = listening_answers[item['id']]
                    if item['options'].index(selected_val) == item['correct']:
                        score += 1
                st.session_state.listening_score = score
                st.session_state.step = 3
                st.rerun()

elif st.session_state.step == 3:
    st.title("Fase 2: Relaciones Sociales")
    st.write("Indica tu grado de acuerdo con las siguientes afirmaciones (1: Nada, 7: Totalmente).")
    
    with st.form("social_form"):
        social_responses = {}
        for i, text in enumerate(SOCIAL_ITEMS):
            st.markdown(f'<div class="question-container"><b>{i+1}. {text}</b></div>', unsafe_allow_html=True)
            social_responses[i] = st.select_slider(
                f"Respuesta para item {i+1}",
                options=[1, 2, 3, 4, 5, 6, 7],
                value=4,
                key=f"social_q_{i}",
                label_visibility="collapsed"
            )
            
        if st.form_submit_button("Finalizar Evaluación"):
            # Cálculo simplificado para Streamlit (el percentil real se calcularía con los baremos)
            # Aquí promediamos para dar un PC estimado
            avg_score = sum(social_responses.values()) / len(social_responses)
            st.session_state.pc_social = int(avg_score * 12) + 10 # Estimación visual
            if st.session_state.pc_social > 99: st.session_state.pc_social = 99
            
            st.session_state.step = 4
            st.rerun()

elif st.session_state.step == 4:
    st.title("Resultados Finales")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="metric-card"><small>LISTENING</small><h2>{st.session_state.listening_score}/8</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><small>APEGO SOCIAL (EST.)</small><h2>PC {st.session_state.pc_social}</h2></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("📩 Envío Manual al Tutor")
    st.write("Tus resultados están listos. Haz clic en el botón para abrir tu correo y enviarlos.")

    subject = f"Evaluación Becas Europa - {st.session_state.student['nombre']} {st.session_state.student['apellidos']}"
    body = f"""
INFORME DE EVALUACIÓN (SISTEMA STREAMLIT)
-----------------------------------------
Alumno: {st.session_state.student['nombre']} {st.session_state.student['apellidos']}
Sexo: {st.session_state.student['sexo']}

RESULTADOS OBTENIDOS:
- Comprensión Auditiva: {st.session_state.listening_score} / 8
- Percentil Apego Social: PC {st.session_state.pc_social} (Estimado)

Este informe ha sido generado manualmente por el alumno.
-----------------------------------------
    """
    
    mailto_url = f"mailto:{TUTOR_EMAIL}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
    
    st.markdown(f'<a href="{mailto_url}" class="mailto-btn">REDACTAR CORREO AL TUTOR</a>', unsafe_allow_html=True)
    
    if st.button("Finalizar Sesión"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
