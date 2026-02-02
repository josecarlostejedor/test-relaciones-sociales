
import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt, RGBColor
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
    page_title="Evaluación Apego JCYL",
    layout="centered",
    page_icon="👥",
    initial_sidebar_state="collapsed"
)

# Estilos visuales
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #4f46e5; color: white; font-weight: 600; border: none; }
    .metric-card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center; border: 1px solid #e2e8f0; }
    .metric-value { font-size: 2rem; font-weight: 800; color: #4f46e5; }
    .metric-label { font-size: 0.75rem; color: #64748b; text-transform: uppercase; font-weight: 600; }
    .success-banner { background-color: #f0fdf4; border: 1px solid #bbf7d0; padding: 20px; border-radius: 12px; color: #166534; text-align: center; margin-bottom: 30px; }
</style>
""", unsafe_allow_html=True)

# Configuración API
API_KEY = os.environ.get("API_KEY")
genai.configure(api_key=API_KEY)

# Configuración Email
SMTP_USER = "josecarlostejedor@gmail.com"
SMTP_PASS = "laquujmjoiuopzwv"
DEST_EMAIL = "josecarlostejedor@gmail.com"

# Baremos
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

def get_pc(score, table):
    for threshold, pc in table:
        if score >= threshold: return pc
    return 1

def send_dual_email(student, word_bytes, excel_bytes):
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = DEST_EMAIL
        msg['Subject'] = f"🔴 URGENTE: INFORME APEGO - {student['nombre']} {student['apellidos']}"
        
        body = f"Evaluación de apego completada.\n\nAlumno: {student['nombre']} {student['apellidos']}\nCentro: {student['centro']}\n\nSe adjunta el informe Word con interpretación clínica y la base de datos Excel actualizada."
        msg.attach(MIMEText(body, 'plain'))

        part_word = MIMEBase('application', 'octet-stream')
        part_word.set_payload(word_bytes)
        encoders.encode_base64(part_word)
        part_word.add_header('Content-Disposition', f'attachment; filename="Informe_{student["apellidos"]}.docx"')
        msg.attach(part_word)

        part_excel = MIMEBase('application', 'octet-stream')
        part_excel.set_payload(excel_bytes)
        encoders.encode_base64(part_excel)
        part_excel.add_header('Content-Disposition', 'attachment; filename="Historico_Apego.xlsx"')
        msg.attach(part_excel)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error al enviar email: {e}")
        return False

# App Logic
if 'step' not in st.session_state: st.session_state.step = 1

st.markdown('<h1 style="text-align:center;">Evaluación de Relaciones Sociales (IPPA)</h1>', unsafe_allow_html=True)

if st.session_state.step == 1:
    with st.form("id_form"):
        st.subheader("Ficha del Estudiante")
        c1, c2 = st.columns(2)
        with c1:
            nom = st.text_input("Nombre")
            ape = st.text_input("Apellidos")
            sex = st.selectbox("Sexo", ["Chica", "Chico"])
        with c2:
            cur = st.text_input("Curso", value="1º Bachillerato")
            ins = st.text_input("Centro")
        
        if st.form_submit_button("EMPEZAR"):
            if nom and ape:
                st.session_state.student = {"nombre": nom, "apellidos": ape, "sexo": sex, "curso": cur, "centro": ins}
                st.session_state.step = 2
                st.rerun()
            else: st.warning("Nombre y apellidos obligatorios.")

elif st.session_state.step == 2:
    resp = {}
    for id, txt, dim in TEST_ITEMS:
        st.write(f"**{id}. {txt}**")
        resp[id] = st.select_slider(f"S{id}", options=[1,2,3,4,5,6,7], value=4, key=f"q_{id}", label_visibility="collapsed")
    
    if st.button("ENVIAR RESPUESTAS"):
        with st.spinner("Generando informe para el tutor..."):
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

            # IA Interpretation (para el tutor)
            try:
                model = genai.GenerativeModel('gemini-3-pro-preview')
                prompt = f"""Analiza estos percentiles de apego (Armsden y Greenberg) para un/a {gender} de 16-17 años:
                - Confianza: PC {pcs['Confianza']} (Bajo es riesgo)
                - Comunicación: PC {pcs['Comunicación']} (Bajo es riesgo)
                - Alienación: PC {pcs['Alienación']} (ALTO ES RIESGO/AISLAMIENTO)
                - Seguridad Global (Total): PC {pcs['Total']} (Bajo es riesgo extremo)

                CASO ACTUAL: El alumno tiene PC {pcs['Total']} en Seguridad Global y PC {pcs['Alienación']} en Alienación. 
                Si PC Total es 1 y Alienación es 90, describe un estado de ALERTA MÁXIMA por aislamiento social y falta de base segura.
                Explica detalladamente qué significan estos números para el tutor académico."""
                
                resp_ai = model.generate_content(prompt)
                ai_text = resp_ai.text
            except Exception as e:
                ai_text = f"Error en IA: {str(e)}. Por favor, interprete los percentiles manualmente: Confianza PC {pcs['Confianza']}, Comunicación PC {pcs['Comunicación']}, Alienación PC {pcs['Alienación']}, Total Seguridad PC {pcs['Total']}."

            # Word creation
            doc = Document()
            doc.add_heading('INFORME TÉCNICO DE APEGO', 0)
            doc.add_paragraph(f"Estudiante: {st.session_state.student['nombre']} {st.session_state.student['apellidos']}")
            doc.add_paragraph(f"Centro: {st.session_state.student['centro']} | Fecha: {datetime.now().strftime('%d/%m/%Y')}")
            
            doc.add_heading('1. Resultados de la Evaluación', level=1)
            t = doc.add_table(rows=1, cols=2); t.style = 'Table Grid'
            hdr = t.rows[0].cells; hdr[0].text = 'Dimensión'; hdr[1].text = 'Percentil (PC)'
            for k, v in pcs.items():
                r = t.add_row().cells; r[0].text = k; r[1].text = str(v)

            doc.add_heading('2. Interpretación del Resultado Global', level=1)
            p_total = doc.add_paragraph()
            run = p_total.add_run(f"El PC TOTAL ({pcs['Total']}) indica la Seguridad Global del Apego.")
            run.bold = True
            
            doc.add_heading('3. Análisis Clínico y Pedagógico', level=1)
            doc.add_paragraph(ai_text)
            
            word_buf = io.BytesIO(); doc.save(word_buf)
            
            # Excel cumulative history
            HIST_FILE = "historico_global_apego.csv"
            new_data = {
                "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Nombre": st.session_state.student["nombre"],
                "Apellidos": st.session_state.student["apellidos"],
                "Sexo": st.session_state.student["sexo"],
                "PC_Confianza": pcs["Confianza"],
                "PC_Comunicacion": pcs["Comunicación"],
                "PC_Alienacion": pcs["Alienación"],
                "PC_Total_Seguridad": pcs["Total"]
            }
            if os.path.exists(HIST_FILE):
                df = pd.read_csv(HIST_FILE)
                df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            else:
                df = pd.DataFrame([new_data])
            df.to_csv(HIST_FILE, index=False)
            
            excel_buf = io.BytesIO()
            with pd.ExcelWriter(excel_buf) as writer: df.to_excel(writer, index=False)
            
            # Send email
            send_dual_email(st.session_state.student, word_buf.getvalue(), excel_buf.getvalue())
            st.session_state.step = 3
            st.rerun()

elif st.session_state.step == 3:
    st.balloons()
    st.markdown('<div class="success-banner">✅ Evaluación procesada correctamente.<br>Toda la información ha sido enviada al tutor josecarlostejedor@gmail.com</div>', unsafe_allow_html=True)
    
    st.subheader("Resumen de Percentiles")
    cols = st.columns(4)
    dims = ["Confianza", "Comunicación", "Alienación", "Total"]
    for i, d in enumerate(dims):
        with cols[i]:
            st.markdown(f'<div class="metric-card"><div class="metric-label">{d}</div><div class="metric-value">{st.session_state.pcs[d]}</div></div>', unsafe_allow_html=True)
    
    st.info("El percentil 'Total' representa tu nivel de Seguridad Global de Apego.")
    
    if st.button("NUEVA EVALUACIÓN"):
        st.session_state.step = 1
        st.rerun()
