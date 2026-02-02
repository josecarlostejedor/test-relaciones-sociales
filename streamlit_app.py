
import streamlit as st
import google.generativeai as genai
from docx import Document
import pandas as pd
import io
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Relaciones Sociales - Automatizado", layout="centered", page_icon="✉️")

# --- CREDENCIALES (HARDCODED PARA SOLUCIONAR EL FALLO ACTUAL) ---
# En producción final, usa st.secrets por seguridad
SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587
SMTP_USER = "jctejedor@educa.jcyl.es"
SMTP_PASS = "pumacarinoso55@3"
API_KEY_GEMINI = "AIzaSyCKNTFjKb7iTclVck0E3w0zBp4wQLzj4v4"

# --- BAREMOS Y CONSTANTES ---
TEST_ITEMS = [
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
    "Chica": {
        "total": [(95, 96), (90, 93), (85, 90), (80, 88), (75, 86), (50, 77), (25, 67), (10, 53)],
        "confianza": [(95, 56), (80, 54), (50, 49), (10, 40)],
        "comunicacion": [(95, 49), (80, 46), (50, 42), (10, 34)],
        "alienacion": [(95, 26), (80, 19), (10, 7)]
    },
    "Chico": {
        "total": [(95, 92), (90, 90), (80, 84), (75, 83), (50, 71), (25, 59), (10, 48)],
        "confianza": [(95, 56), (80, 52), (50, 48), (10, 38)],
        "comunicacion": [(95, 48), (80, 45), (10, 30)],
        "alienacion": [(95, 27), (80, 21), (50, 15), (10, 8)]
    }
}

HISTORY_FILE = "historico_global_apego.csv"

def get_percentile(score, table):
    for centile, min_score in table:
        if score >= min_score:
            return centile
    return 1

def send_automated_emails(student, report_bytes, history_df):
    """Envío SMTP robusto para Office 365"""
    try:
        # 1. Preparar Excel en memoria
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            history_df.to_excel(writer, index=False, sheet_name='Historial_Global')
        excel_bytes = excel_buffer.getvalue()

        # 2. Configurar Mensaje
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = ", ".join(student["emails"])
        msg['Subject'] = f"RESULTADOS TEST: {student['nombre']} {student['apellidos']} - {student['grupo']}"
        
        body = f"Hola,\n\nSe ha completado una nueva evaluación de Relaciones Sociales para el alumno {student['nombre']} {student['apellidos']}.\n\nAdjuntamos:\n- Informe psicopedagógico (Word)\n- Historial acumulado (Excel)\n\nSaludos."
        msg.attach(MIMEText(body, 'plain'))

        # Adjuntar Word
        part_word = MIMEBase('application', 'octet-stream')
        part_word.set_payload(report_bytes)
        encoders.encode_base64(part_word)
        part_word.add_header('Content-Disposition', f'attachment; filename="Informe_{student["apellidos"]}.docx"')
        msg.attach(part_word)

        # Adjuntar Excel
        part_excel = MIMEBase('application', 'octet-stream')
        part_excel.set_payload(excel_bytes)
        encoders.encode_base64(part_excel)
        part_excel.add_header('Content-Disposition', 'attachment; filename="Historico_Total.xlsx"')
        msg.attach(part_excel)

        # 3. CONEXIÓN SMTP OFFICE 365 (CON EHLO EXPLICITO)
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
        server.ehlo()  # Identificación inicial
        server.starttls()  # Cifrado
        server.ehlo()  # Identificación post-cifrado
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        return True, "Enviado con éxito"
    except Exception as e:
        return False, str(e)

# --- APP FLOW ---
if 'step' not in st.session_state:
    st.session_state.step = 1

st.title("✉️ Evaluación de Relaciones Sociales")

if st.session_state.step == 1:
    with st.form("registro"):
        st.subheader("Datos del Alumno/a")
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre")
            apellidos = st.text_input("Apellidos")
            edad = st.selectbox("Edad", [16, 17])
        with c2:
            curso = st.text_input("Curso")
            grupo = st.text_input("Grupo")
            sexo = st.radio("Sexo", ["Chica", "Chico"])
        
        inst = st.text_input("Instituto")
        e1 = st.text_input("Email adicional 1")
        e2 = st.text_input("Email adicional 2")

        if st.form_submit_button("Continuar"):
            if not (nombre and apellidos and curso and grupo and inst):
                st.warning("Rellena todos los campos obligatorios.")
            else:
                st.session_state.student = {
                    "nombre": nombre, "apellidos": apellidos, "edad": edad,
                    "curso": curso, "grupo": grupo, "sexo": sexo, "instituto": inst,
                    "emails": [e for e in ["jctejedor@educa.jcyl.es", e1, e2] if e]
                }
                st.session_state.step = 2
                st.rerun()

elif st.session_state.step == 2:
    resp = {}
    for id, txt, dim in TEST_ITEMS:
        resp[id] = st.select_slider(f"{id}. {txt}", options=[1, 2, 3, 4, 5, 6, 7], value=4, key=f"q_{id}")
    
    if st.button("FINALIZAR"):
        # Cálculos
        c_val = sum(resp[id] for id, t, dim in TEST_ITEMS if dim == "Confianza")
        m_val = sum(resp[id] for id, t, dim in TEST_ITEMS if dim == "Comunicación")
        a_val = sum(resp[id] for id, t, dim in TEST_ITEMS if dim == "Alienación")
        t_raw = c_val + m_val - a_val
        n_tab = NORMS[st.session_state.student["sexo"]]
        
        st.session_state.results = {
            "PC Confianza": get_percentile(c_val, n_tab["confianza"]),
            "PC Comunicación": get_percentile(m_val, n_tab["comunicacion"]),
            "PC Alienación": get_percentile(a_val, n_tab["alienacion"]),
            "PC Total": get_percentile(t_raw, n_tab["total"])
        }

        # Histórico
        new_row = {**st.session_state.student, **st.session_state.results, "Fecha": datetime.now().strftime("%d/%m/%Y")}
        if os.path.exists(HISTORY_FILE):
            df = pd.read_csv(HISTORY_FILE)
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        else:
            df = pd.DataFrame([new_row])
        df.to_csv(HISTORY_FILE, index=False)

        # Informe Word
        doc = Document()
        doc.add_heading('Informe de Relaciones Sociales', 0)
        doc.add_paragraph(f"Alumno: {st.session_state.student['nombre']} {st.session_state.student['apellidos']}")
        doc.add_paragraph(f"Percentiles: {st.session_state.results}")
        
        # IA Analysis
        try:
            genai.configure(api_key=API_KEY_GEMINI)
            model = genai.GenerativeModel('gemini-1.5-flash')
            analysis = model.generate_content(f"Analiza estos percentiles de apego: {st.session_state.results}. Haz un informe breve.").text
            doc.add_heading('Análisis IA', level=1)
            doc.add_paragraph(analysis)
        except:
            doc.add_paragraph("Análisis IA no disponible.")
        
        b_word = io.BytesIO()
        doc.save(b_word)
        
        # Envío Automático
        with st.spinner("Enviando resultados automáticamente..."):
            ok, msg = send_automated_emails(st.session_state.student, b_word.getvalue(), df)
            if ok:
                st.session_state.step = 3
                st.rerun()
            else:
                st.error(f"Error crítico en el servidor SMTP: {msg}")

elif st.session_state.step == 3:
    st.balloons()
    st.success("Test finalizado con éxito.")
    st.write("### Percentiles Obtenidos")
    res = st.session_state.results
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Confianza", f"PC {res['PC Confianza']}")
    c2.metric("Comunicación", f"PC {res['PC Comunicación']}")
    c3.metric("Alienación", f"PC {res['PC Alienación']}")
    c4.metric("TOTAL", f"PC {res['PC Total']}")
    
    st.info(f"Los informes han sido enviados a {', '.join(st.session_state.student['emails'])}")
    if st.button("Reiniciar"):
        st.session_state.step = 1
        st.rerun()
