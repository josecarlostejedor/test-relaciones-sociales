
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
st.set_page_config(page_title="Evaluación Relaciones - JCYL", layout="centered", page_icon="📝")

# --- CREDENCIALES ---
SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587
SMTP_USER = "jctejedor@educa.jcyl.es"
# Intenta usar contraseña de aplicación si tienes MFA activo
SMTP_PASS = "pumacarinoso55@3" 
API_KEY_GEMINI = "AIzaSyCKNTFjKb7iTclVck0E3w0zBp4wQLzj4v4"

# --- BAREMOS ---
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
    """Envío SMTP para Office 365 con manejo de error 535 explícito"""
    try:
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            history_df.to_excel(writer, index=False, sheet_name='Historial')
        excel_bytes = excel_buffer.getvalue()

        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = ", ".join(student["emails"])
        msg['Subject'] = f"TEST APEGO: {student['nombre']} {student['apellidos']} - {student['grupo']}"
        
        body = f"Nueva evaluación recibida.\nAlumno: {student['nombre']} {student['apellidos']}\nCurso: {student['curso']} {student['grupo']}"
        msg.attach(MIMEText(body, 'plain'))

        part_word = MIMEBase('application', 'octet-stream')
        part_word.set_payload(report_bytes)
        encoders.encode_base64(part_word)
        part_word.add_header('Content-Disposition', f'attachment; filename="Informe_{student["apellidos"]}.docx"')
        msg.attach(part_word)

        part_excel = MIMEBase('application', 'octet-stream')
        part_excel.set_payload(excel_bytes)
        encoders.encode_base64(part_excel)
        part_excel.add_header('Content-Disposition', 'attachment; filename="Historico_Total.xlsx"')
        msg.attach(part_excel)

        # Conexión secuencial para evitar bloqueos
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=20)
        server.set_debuglevel(1) # Esto saldrá en los logs de la consola
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        return True, "Enviado con éxito"
    except smtplib.SMTPAuthenticationError:
        return False, "ERROR_AUTH: Microsoft ha rechazado la contraseña. Necesitas una 'Contraseña de Aplicación' o habilitar SMTP AUTH en tu cuenta de educa.jcyl.es."
    except Exception as e:
        return False, str(e)

# --- APP ---
if 'step' not in st.session_state:
    st.session_state.step = 1

st.title("Sistema de Evaluación JCYL")

if st.session_state.step == 1:
    with st.form("id"):
        st.subheader("Datos Alumno/a")
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre")
            apellidos = st.text_input("Apellidos")
            sexo = st.radio("Sexo", ["Chica", "Chico"])
        with c2:
            curso = st.text_input("Curso")
            grupo = st.text_input("Grupo")
            inst = st.text_input("Centro")
        
        e1 = st.text_input("Copia a email 1")
        if st.form_submit_button("Siguiente"):
            if not (nombre and apellidos and curso and grupo):
                st.error("Faltan datos obligatorios")
            else:
                st.session_state.student = {
                    "nombre": nombre, "apellidos": apellidos, "curso": curso, "grupo": grupo, "sexo": sexo, "instituto": inst,
                    "emails": [e for e in ["jctejedor@educa.jcyl.es", e1] if e]
                }
                st.session_state.step = 2
                st.rerun()

elif st.session_state.step == 2:
    resp = {}
    st.info("Puntúa del 1 al 7")
    for id, txt, dim in TEST_ITEMS:
        resp[id] = st.select_slider(f"{id}. {txt}", options=[1,2,3,4,5,6,7], value=4, key=f"it_{id}")
    
    if st.button("CALCULAR Y ENVIAR"):
        # Cálculos
        c_val = sum(resp[id] for id, t, dim in TEST_ITEMS if dim == "Confianza")
        m_val = sum(resp[id] for id, t, dim in TEST_ITEMS if dim == "Comunicación")
        a_val = sum(resp[id] for id, t, dim in TEST_ITEMS if dim == "Alienación")
        t_raw = c_val + m_val - a_val
        n_tab = NORMS[st.session_state.student["sexo"]]
        
        results = {
            "Confianza": get_percentile(c_val, n_tab["confianza"]),
            "Comunicación": get_percentile(m_val, n_tab["comunicacion"]),
            "Alienación": get_percentile(a_val, n_tab["alienacion"]),
            "Total": get_percentile(t_raw, n_tab["total"])
        }
        st.session_state.final_results = results

        # Generar Word e Historial
        doc = Document()
        doc.add_heading('Informe Relaciones Sociales', 0)
        doc.add_paragraph(f"Alumno: {st.session_state.student['nombre']} {st.session_state.student['apellidos']}")
        for k, v in results.items(): doc.add_paragraph(f"{k}: PC {v}")

        try:
            ai = genai.GoogleGenAI(apiKey=API_KEY_GEMINI)
            response = ai.models.generateContent(
                model='gemini-1.5-flash',
                contents=f"Explica brevemente estos resultados de apego adolescente: {results}. En español profesional."
            )
            doc.add_heading('Análisis Cualitativo', level=1)
            doc.add_paragraph(response.text)
        except: pass

        b_word = io.BytesIO()
        doc.save(b_word)
        st.session_state.word_file = b_word.getvalue()

        # Historial
        new_data = {**st.session_state.student, **results, "Fecha": datetime.now()}
        if os.path.exists(HISTORY_FILE):
            df = pd.read_csv(HISTORY_FILE)
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        else:
            df = pd.DataFrame([new_data])
        df.to_csv(HISTORY_FILE, index=False)
        st.session_state.history_df = df

        # Envío
        with st.spinner("Conectando con Office 365..."):
            ok, msg = send_automated_emails(st.session_state.student, st.session_state.word_file, df)
            if ok:
                st.session_state.step = 3
                st.rerun()
            else:
                st.error("⚠️ EL ENVÍO AUTOMÁTICO HA FALLADO")
                st.warning(f"Motivo: {msg}")
                st.info("Microsoft bloquea el acceso. Puedes descargar el informe aquí mismo para no perderlo:")
                st.download_button("Descargar Informe (Word)", st.session_state.word_file, f"Informe_{st.session_state.student['apellidos']}.docx")
                st.session_state.step = 3

elif st.session_state.step == 3:
    st.success("Evaluación finalizada.")
    res = st.session_state.final_results
    cols = st.columns(4)
    for i, (k, v) in enumerate(res.items()):
        cols[i].metric(k, f"PC {v}")
    
    if st.button("Nueva Evaluación"):
        st.session_state.step = 1
        st.rerun()
