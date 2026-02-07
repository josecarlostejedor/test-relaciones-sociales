
import streamlit as st
import urllib.parse

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Evaluación Becas Europa", page_icon="🇪🇺", layout="centered")
TUTOR_EMAIL = "josecarlostejedor@gmail.com"

# --- DATOS DEL CUESTIONARIO (8 PREGUNTAS) ---
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

# --- ESTILOS ---
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; background-color: #e60000; color: white; border: none; }
    .stButton>button:hover { background-color: #cc0000; color: white; }
    .metric-card { background: white; padding: 30px; border-radius: 20px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #edf2f7; }
    .question-box { background: white; padding: 20px; border-radius: 15px; border-left: 5px solid #e60000; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
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
</style>
""", unsafe_allow_html=True)

# --- ESTADO ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'student' not in st.session_state: st.session_state.student = {}
if 'quiz_answers' not in st.session_state: st.session_state.quiz_answers = {}

st.image("https://www.becaseuropa.es/img/logo_becas_europa.png", width=180)

# --- NAVEGACIÓN ---
if st.session_state.step == 1:
    st.title("Registro del Candidato")
    with st.form("ident"):
        nom = st.text_input("Nombre")
        ape = st.text_input("Apellidos")
        gen = st.selectbox("Sexo", ["Femenino", "Masculino"])
        if st.form_submit_button("Siguiente"):
            if nom and ape:
                st.session_state.student = {"nombre": nom, "apellidos": ape, "sexo": gen}
                st.session_state.step = 2
                st.rerun()

elif st.session_state.step == 2:
    st.title("Fase 1: Listening")
    st.info("Escucha el audio atentamente antes de responder a las 8 preguntas.")
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")
    
    with st.form("quiz_form"):
        st.subheader("Cuestionario de Comprensión")
        temp_answers = {}
        for item in BECAS_EUROPA_QUIZ:
            st.markdown(f"**{item['id']}. {item['q']}**")
            temp_answers[item['id']] = st.radio(
                f"Selecciona una opción para la pregunta {item['id']}", 
                item['options'], 
                key=f"q_{item['id']}",
                label_visibility="collapsed"
            )
            st.divider()
            
        if st.form_submit_button("Finalizar Listening y pasar a Relaciones"):
            score = 0
            for item in BECAS_EUROPA_QUIZ:
                selected_idx = item['options'].index(temp_answers[item['id']])
                if selected_idx == item['correct']:
                    score += 1
            st.session_state.listening_score = score
            st.session_state.step = 3
            st.rerun()

elif st.session_state.step == 3:
    st.title("Fase 2: Relaciones")
    st.write("Valora tu grado de satisfacción general con tus relaciones sociales (1-7).")
    social_val = st.select_slider(
        "Desliza para puntuar",
        options=[1, 2, 3, 4, 5, 6, 7],
        value=4
    )
    if st.button("Finalizar Evaluación Total"):
        # Simulamos un cálculo de percentil basado en la respuesta simplificada
        # En una versión real, esto usaría la lógica de evaluationEngine.ts
        st.session_state.pc_social = 50 + (social_val * 5) 
        st.session_state.step = 4
        st.rerun()

elif st.session_state.step == 4:
    st.title("Resumen de Resultados")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="metric-card"><small>LISTENING</small><h2>{st.session_state.listening_score}/8</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><small>APEGO SOCIAL</small><h2>PC {st.session_state.pc_social}</h2></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("Acción Requerida: Envío al Tutor")
    st.write("Pulsa el botón de abajo para preparar el correo con tus resultados para el tutor.")

    # Generación del cuerpo del mensaje para el mailto
    subject = f"Informe Evaluación Becas Europa - {st.session_state.student['nombre']} {st.session_state.student['apellidos']}"
    body = f"""
INFORME DE EVALUACIÓN (STREAMLIT)
---------------------------------
Alumno: {st.session_state.student['nombre']} {st.session_state.student['apellidos']}
Sexo: {st.session_state.student['sexo']}

RESULTADOS:
- Listening: {st.session_state.listening_score}/8
- Estimación Apego Social: PC {st.session_state.pc_social}

Nota: Este es un resumen simplificado.
---------------------------------
    """
    
    mailto_url = f"mailto:{TUTOR_EMAIL}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
    
    st.markdown(f'<a href="{mailto_url}" class="mailto-btn">📩 REDACTAR EMAIL AL TUTOR</a>', unsafe_allow_html=True)
    
    if st.button("Finalizar y Reiniciar"):
        st.session_state.clear()
        st.rerun()
