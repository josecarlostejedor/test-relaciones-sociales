
import streamlit as st
import time

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Evaluación Becas Europa", page_icon="🇪🇺", layout="centered")
TUTOR_EMAIL = "josecarlostejedor@gmail.com"

# --- ESTILOS ---
st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; background-color: #e60000; color: white; }
    .metric-card { background: white; padding: 30px; border-radius: 20px; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #edf2f7; }
</style>
""", unsafe_allow_html=True)

# --- ESTADO ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'student' not in st.session_state: st.session_state.student = {}

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
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3")
    st.write("Responde a las 8 cuestiones planteadas en el material.")
    if st.button("Finalizar Listening y pasar a Relaciones"):
        st.session_state.listening_score = 7 # Simulado
        st.session_state.step = 3
        st.rerun()

elif st.session_state.step == 3:
    st.title("Fase 2: Relaciones")
    st.slider("Grado de satisfacción social (Test IPPA)", 1, 7, 4)
    if st.button("Finalizar Evaluación Total"):
        st.session_state.pc_social = 78 # Simulado
        st.session_state.step = 4
        st.rerun()

elif st.session_state.step == 4:
    st.title("Resumen de Resultados")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="metric-card"><small>LISTENING</small><h2>{st.session_state.listening_score}/8</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><small>APEGO SOCIAL</small><h2>PC {st.session_state.pc_social}</h2></div>', unsafe_allow_html=True)
    
    st.warning("⚠️ Recuerda usar la aplicación de React para enviar el informe completo al tutor por email.")
    
    if st.button("Cerrar Sesión"):
        st.session_state.clear()
        st.rerun()
