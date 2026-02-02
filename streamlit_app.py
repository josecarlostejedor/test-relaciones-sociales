
import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt
import pandas as pd
import io
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="Escala de Valoración JCYL",
    layout="centered",
    page_icon="👥",
    initial_sidebar_state="collapsed"
)

# Estilos
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }
    .main { background-color: #f8fafc; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #4f46e5; color: white; font-weight: 600; border: none; }
    .metric-card { background: white; padding: 24px; border-radius: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); text-align: center; border: 1px solid #e2e8f0; }
    .metric-value { font-size: 2.8rem; font-weight: 800; color: #4f46e5; }
    .metric-label { font-size: 0.9rem; color: #64748b; text-transform: uppercase; font-weight: 600; margin-bottom: 0.5rem; }
    .interpretation-box { background-color: white; padding: 2.5rem; border-radius: 24px; border-left: 8px solid #4f46e5; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); margin-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# Configuración API y Email
API_KEY = os.environ.get("API_KEY")
SMTP_USER = "josecarlostejedor@gmail.com"
SMTP_PASS = "laquujmjoiuopzwv"
TUTOR_EMAIL = "jctejedor@educa.jcyl.es"

# Definición de Ítems
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

# Baremos 16-17 años (Manual)
NORMS = {
    "Chica": {
        "total": [(96,95), (93,90), (90,85), (88,80), (86,75), (83,70), (81,65), (79,60), (78,55), (77,50), (75,45), (73,40), (71,35), (69,30), (67,25), (65,20), (61,15), (53,10), (46,5)],
        "confianza": [(56,95), (55,85), (54,80), (53,75), (52,70), (51,60), (50,55), (49,50), (48,45), (47,35), (45,25), (44,20), (42,15), (40,10), (35,5)],
        "comunicacion": [(49,95), (48,90), (46,80), (45,75), (44,65), (43,60), (42,50), (41,45), (40,35), (39,30), (38,20), (36,15), (34,10), (30,5)],
        "alienacion": [(26,95), (22,90), (21,85), (19,80), (18,75), (17,65), (16,60), (15,55), (14,45), (13,40), (12,35), (11,25), (10,20), (9,15), (7,10), (6,5)]
    },
    "Chico": {
        "total": [(92,95), (90,90), (86,85), (84,80), (83,75), (80,70), (78,65), (75,60), (74,55), (71,50), (69,45), (67,40), (64,35), (62,30), (59,25), (56,20), (53,15), (48,10), (40,5)],
        "confianza": [(56,95), (55,90), (54,85), (52,80), (51,70), (50,65), (49,60), (48,50), (47,45), (46,40), (45,35), (44,30), (43,25), (42,20), (40,15), (38,10), (34,5)],
        "comunicacion": [(48,95), (47,90), (46,85), (45,80), (44,75), (43,70), (42,65), (41,60), (40,55), (39,45), (38,40), (37,35), (36,30), (35,25), (34,20), (32,15), (30,10), (27,5)],
        "alienacion": [(27,95), (24,90), (22,85), (21,80), (20,75), (19,70), (18,65), (17,60), (16,55), (15,50), (14,45), (13,35), (12,30), (11,25), (10,20), (8,10), (7,5)]
    }
}

def get_pc(score, table):
    for threshold, pc in table:
        if score >= threshold: return pc
    return 1

def send_email(student, word_bytes, history_df):
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        destinatarios = [student["email_target"], TUTOR_EMAIL]
        msg['To'] = ", ".join(destinatarios)
        msg['Subject'] = f"INFORME APEGO: {student['nombre']} {student['apellidos']} - {student['grupo']}"
        
        body = f"Evaluación de Relaciones Sociales Finalizada.\n\nSe adjunta el informe técnico con interpretación clínica detallada para el alumno/a {student['nombre']} {student['apellidos']}."
        msg.attach(MIMEText(body, 'plain'))

        # Adjunto Word
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(word_bytes)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="Informe_Apego_{student["apellidos"]}.docx"')
        msg.attach(part)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except:
        return False

# UI
st.markdown('<div style="text-align: center;"><h1>👥 Escala de Valoración de Habilidades Sociales y Apego entre iguales</h1></div>', unsafe_allow_html=True)

if st.session_state.get('step') is None: st.session_state.step = 1

if st.session_state.step == 1:
    with st.form("id_form"):
        st.subheader("Datos del Alumno/a")
        c1, c2 = st.columns(2)
        with c1:
            nom = st.text_input("Nombre")
            ape = st.text_input("Apellidos")
            sex = st.selectbox("Sexo", ["Chica", "Chico"])
        with c2:
            cur = st.text_input("Curso", value="1º Bachillerato")
            gru = st.text_input("Grupo")
            ins = st.text_input("Centro")
        
        email_dest = st.text_input("Enviar informe a (Email):", placeholder="ejemplo@email.com")
        
        if st.form_submit_button("CONTINUAR"):
            if nom and ape and email_dest:
                st.session_state.student = {"nombre": nom, "apellidos": ape, "curso": cur, "grupo": gru, "sexo": sex, "instituto": ins, "email_target": email_dest}
                st.session_state.step = 2
                st.rerun()
            else: st.warning("Completa los campos obligatorios.")

elif st.session_state.step == 2:
    resp = {}
    st.info("Puntúa del 1 (Totalmente en desacuerdo) al 7 (Totalmente de acuerdo)")
    for id, txt, dim in TEST_ITEMS:
        st.write(f"**{id}. {txt}**")
        resp[id] = st.select_slider(f"S{id}", options=[1,2,3,4,5,6,7], value=4, key=f"q_{id}", label_visibility="collapsed")
        st.markdown("---")
    
    if st.button("GENERAR INFORME"):
        with st.spinner("Calculando y redactando informe..."):
            sums = {"Confianza": 0, "Comunicación": 0, "Alienación": 0}
            for id, txt, dim in TEST_ITEMS: sums[dim] += resp[id]
            
            raw_total = sums["Confianza"] + sums["Comunicación"] - sums["Alienación"]
            gender = st.session_state.student["sexo"]
            
            pcs = {
                "Confianza": get_pc(sums["Confianza"], NORMS[gender]["confianza"]),
                "Comunicación": get_pc(sums["Comunicación"], NORMS[gender]["comunicacion"]),
                "Alienación": get_pc(sums["Alienación"], NORMS[gender]["alienacion"]),
                "Total": get_pc(raw_total, NORMS[gender]["total"])
            }
            st.session_state.pcs = pcs

            # IA Interpretation
            try:
                genai.configure(api_key=API_KEY)
                model = genai.GenerativeModel('gemini-3-pro-preview')
                prompt = f"""Actúa como psicopedagogo. Analiza estos percentiles de apego (Armsden y Greenberg, 1987) para un alumno/a de 16-17 años:
                - Confianza: PC {pcs['Confianza']} (Seguridad y respeto)
                - Comunicación: PC {pcs['Comunicación']} (Calidad de diálogo)
                - Alienación: PC {pcs['Alienación']} (Aislamiento o rechazo)
                - Total: PC {pcs['Total']} (Seguridad global del apego)

                Instrucciones:
                1. Explica en lenguaje sencillo para padres qué significa cada dimensión.
                2. Destaca que el Total es el balance global de seguridad.
                3. Proporciona una interpretación clínica profesional del perfil.
                4. Da 3 consejos prácticos pedagógicos.
                Tono: Empático y profesional."""
                
                interpretation = model.generate_content(prompt).text
                st.session_state.ai_text = interpretation
            except:
                st.session_state.ai_text = "Interpretación detallada no disponible. Consulte los percentiles en la tabla."

            # Word
            doc = Document()
            doc.add_heading('INFORME PSICOPEDAGÓGICO DE RELACIONES SOCIALES', 0)
            p = doc.add_paragraph()
            p.add_run(f"Alumno/a: {st.session_state.student['nombre']} {st.session_state.student['apellidos']}").bold = True
            doc.add_paragraph(f"Centro: {st.session_state.student['instituto']} | Curso: {st.session_state.student['curso']}")
            doc.add_paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")

            doc.add_heading('1. Resultados Cuantitativos', level=1)
            t = doc.add_table(rows=1, cols=2); t.style = 'Light Grid Accent 1'
            hdr = t.rows[0].cells; hdr[0].text = 'Dimensión'; hdr[1].text = 'Percentil (PC)'
            for k, v in pcs.items():
                row = t.add_row().cells; row[0].text = k; row[1].text = f"PC {v}"

            doc.add_heading('2. Interpretación Clínica Detallada', level=1)
            doc.add_paragraph(st.session_state.ai_text)
            
            doc.add_paragraph("\n" + "_"*30)
            footer = doc.add_paragraph()
            footer.add_run("Nota Técnica: ").bold = True
            footer.add_run("Los datos de este informe resultan de aplicar la siguiente escala de Valoración para ver las relaciones sociales entre iguales y que la fuente de información es esta:")
            doc.add_paragraph("Escala para la evaluación del apego a iguales. (The inventory of parent and peer attachment). Amrsden, G. C. y Greemberg, M. T. (1987)").bold = True

            buf = io.BytesIO(); doc.save(buf)
            st.session_state.word_bytes = buf.getvalue()
            
            send_email(st.session_state.student, st.session_state.word_bytes, None)
            st.session_state.step = 3
            st.rerun()

elif st.session_state.step == 3:
    st.success("✅ Evaluación Procesada")
    cols = st.columns(4)
    for i, (k, v) in enumerate(st.session_state.pcs.items()):
        with cols[i]: st.markdown(f'<div class="metric-card"><div class="metric-label">{k}</div><div class="metric-value">{v}</div></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="interpretation-box">', unsafe_allow_html=True)
    st.subheader("🧠 Interpretación Clínica Detallada")
    st.markdown(st.session_state.ai_text)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.download_button("📥 DESCARGAR INFORME WORD", data=st.session_state.word_bytes, file_name=f"Informe_{st.session_state.student['apellidos']}.docx")
    if st.button("NUEVA EVALUACIÓN"): st.session_state.step = 1; st.rerun()
