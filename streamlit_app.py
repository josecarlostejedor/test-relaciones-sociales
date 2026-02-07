
import streamlit as st
import pandas as pd
import requests
import time
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Evaluación Becas Europa", page_icon="🇪🇺", layout="centered")
TUTOR_EMAIL = "josecarlostejedor@gmail.com"
WEBHOOK_URL = "https://formspree.io/f/xoqgjvzd" # Ejemplo de Webhook para envío real

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
    st.title("Identificación")
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
    if st.button("Finalizar Listening y pasar a Relaciones"):
        st.session_state.listening_score = 8 # Simulado
        st.session_state.step = 3
        st.rerun()

elif st.session_state.step == 3:
    st.title("Fase 2: Relaciones")
    st.slider("Grado de satisfacción con mi círculo social", 1, 7, 4)
    if st.button("Finalizar Evaluación Total"):
        st.session_state.pc_social = 85 # Simulado
        st.session_state.step = 4
        st.rerun()

elif st.session_state.step == 4:
    st.title("Resultados")
    
    # PROCESO DE ENVÍO REAL AL TUTOR
    with st.status("Transmitiendo informe al tutor...", expanded=True) as status:
        st.write("Conectando con el servidor de correo...")
        payload = {
            "email_tutor": TUTOR_EMAIL,
            "alumno": f"{st.session_state.student['nombre']} {st.session_state.student['apellidos']}",
            "listening": f"{st.session_state.listening_score}/10",
            "apego_social": f"PC {st.session_state.pc_social}"
        }
        try:
            # En Streamlit se usa requests para el envío real de datos
            requests.post(WEBHOOK_URL, json=payload, timeout=10)
            time.sleep(1)
            status.update(label=f"✅ Informe enviado correctamente a {TUTOR_EMAIL}", state="complete")
        except:
            status.update(label="⚠️ Error en el envío automático, contacte con soporte.", state="error")

    # VISTA ALUMNO
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="metric-card"><small>LISTENING</small><h2>{st.session_state.listening_score}/10</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><small>APEGO SOCIAL</small><h2>PC {st.session_state.pc_social}</h2></div>', unsafe_allow_html=True)
    
    if st.button("Cerrar Sesión"):
        st.session_state.clear()
        st.rerun()
