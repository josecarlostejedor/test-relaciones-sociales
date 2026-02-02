
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
    page_title="Evaluación Apego JCYL",
    layout="centered",
    page_icon="👥",
    initial_sidebar_state="collapsed"
)

# Estilos visuales optimizados
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #4f46e5; color: white; font-weight: 600; border: none; transition: all 0.2s; }
    .stButton>button:hover { background-color: #4338ca; transform: translateY(-2px); }
    .metric-card { background: white; padding: 24px; border-radius: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); text-align: center; border: 1px solid #e2e8f0; margin-bottom: 1rem; }
    .metric-value { font-size: 2.2rem; font-weight: 800; color: #4f46e5; }
    .metric-label { font-size: 0.8rem; color: #64748b; text-transform: uppercase; font-weight: 600; margin-bottom: 0.5rem; }
    .success-box { background-color: #f0fdf4; border: 1px solid #bbf7d0; padding: 1.5rem; border-radius: 1rem; color: #166534; text-align: center; margin-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

# Configuración API y Email
API_KEY = os.environ.get("API_KEY")
SMTP_USER = "josecarlostejedor@gmail.com"
SMTP_PASS = "laquujmjoiuopzwv"
DEST_EMAIL = "josecarlostejedor@gmail.com"

# Baremos actualizados
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
        msg['Subject'] = f"INFORME APEGO: {student['nombre']} {student['apellidos']} - {student['centro']}"
        
        body = f"Test finalizado correctamente.\n\nAlumno: {student['nombre']} {student['apellidos']}\nCentro: {student['centro']}\n\nAdjuntos:\n1. Informe clínico detallado (Word)\n2. Base de datos histórica (Excel)"
        msg.attach(MIMEText(body, 'plain'))

        part_word = MIMEBase('application', 'octet-stream')
        part_word.set_payload(word_bytes)
        encoders.encode_base64(part_word)
        part_word.add_header('Content-Disposition', f'attachment; filename="Informe_{student["apellidos"]}.docx"')
        msg.attach(part_word)

        part_excel = MIMEBase('application', 'octet-stream')
        part_excel.set_payload(excel_bytes)
        encoders.encode_base64(part_excel)
        part_excel.add_header('Content-Disposition', 'attachment; filename="Historial_Apego_JCYL.xlsx"')
        msg.attach(part_excel)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except:
        return False

# UI Principal
st.markdown('<div style="text-align:center;"><h1>👥 Evaluación de Apego a Iguales</h1></div>', unsafe_allow_html=True)

if 'step' not in st.session_state: st.session_state.step = 1

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
        
        if st.form_submit_button("CONTINUAR"):
            if nom and ape:
                st.session_state.student = {"nombre": nom, "apellidos": ape, "curso": cur, "grupo": gru, "sexo": sex, "centro": ins}
                st.session_state.step = 2
                st.rerun()
            else: st.warning("Completa nombre y apellidos.")

elif st.session_state.step == 2:
    resp = {}
    st.info("Puntúa del 1 al 7 según tu grado de acuerdo con cada frase.")
    for id, txt, dim in TEST_ITEMS:
        st.write(f"**{id}. {txt}**")
        resp[id] = st.select_slider(f"S{id}", options=[1,2,3,4,5,6,7], value=4, key=f"q_{id}", label_visibility="collapsed")
        st.markdown("---")
    
    if st.button("FINALIZAR"):
        with st.spinner("Procesando datos y enviando informe al tutor..."):
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

            # Generación de Informe Clínico con IA (para el Word)
            try:
                genai.configure(api_key=API_KEY)
                model = genai.GenerativeModel('gemini-3-pro-preview')
                prompt = f"""Interpreta estos resultados para un/a {gender} de 16-17 años:
                Confianza: PC {pcs['Confianza']}, Comunicación: PC {pcs['Comunicación']}, Alienación: PC {pcs['Alienación']}, Total: PC {pcs['Total']}.
                Explica que el Total es la SEGURIDAD GLOBAL DEL APEGO. Da conclusiones y 3 consejos pedagógicos."""
                resp_ai = model.generate_content(prompt)
                ai_interpretation = resp_ai.text
            except:
                ai_interpretation = "Análisis técnico: Consulte los percentiles en el informe."

            # Creación Documento Word
            doc = Document()
            doc.add_heading('INFORME PSICOPEDAGÓGICO DE APEGO', 0)
            doc.add_paragraph(f"Alumno: {st.session_state.student['nombre']} {st.session_state.student['apellidos']}")
            doc.add_paragraph(f"Centro: {st.session_state.student['centro']} | Fecha: {datetime.now().strftime('%d/%m/%Y')}")
            
            doc.add_heading('Resultados (Percentiles)', level=1)
            t = doc.add_table(rows=1, cols=2); t.style = 'Light Grid Accent 1'
            hdr = t.rows[0].cells; hdr[0].text = 'Dimensión'; hdr[1].text = 'PC'
            for k, v in pcs.items():
                r = t.add_row().cells; r[0].text = k; r[1].text = f"{v}"
            
            doc.add_heading('Significado del Total', level=2)
            doc.add_paragraph(f"La puntuación Total (PC {pcs['Total']}) representa la Seguridad Global del Apego. Valores altos indican una base segura con el grupo de pares.")
            
            doc.add_heading('Interpretación Clínica', level=1)
            doc.add_paragraph(ai_interpretation)

            word_buf = io.BytesIO(); doc.save(word_buf)
            word_bytes = word_buf.getvalue()

            # Histórico Excel
            HISTORY_FILE = "historico_global.csv"
            new_entry = {
                "Fecha": datetime.now().strftime("%Y-%m-%d"),
                "Nombre": st.session_state.student["nombre"],
                "Apellidos": st.session_state.student["apellidos"],
                "Centro": st.session_state.student["centro"],
                "Sexo": st.session_state.student["sexo"],
                "PC_Confianza": pcs["Confianza"],
                "PC_Comunicacion": pcs["Comunicación"],
                "PC_Alienacion": pcs["Alienación"],
                "PC_Total": pcs["Total"]
            }
            if os.path.exists(HISTORY_FILE):
                df = pd.read_csv(HISTORY_FILE)
                df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            else:
                df = pd.DataFrame([new_entry])
            df.to_csv(HISTORY_FILE, index=False)
            
            excel_buf = io.BytesIO()
            with pd.ExcelWriter(excel_buf, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            excel_bytes = excel_buf.getvalue()

            # Envío Email
            send_dual_email(st.session_state.student, word_bytes, excel_bytes)
            st.session_state.step = 3
            st.rerun()

elif st.session_state.step == 3:
    st.balloons()
    st.markdown('<div class="success-box">✅ Evaluación finalizada con éxito.<br>Los resultados han sido enviados al tutor para su revisión.</div>', unsafe_allow_html=True)
    
    st.write("### Resumen de Percentiles Obtenidos")
    cols = st.columns(4)
    dimensions = ["Confianza", "Comunicación", "Alienación", "Total"]
    for i, dim in enumerate(dimensions):
        with cols[i]:
            st.markdown(f'<div class="metric-card"><div class="metric-label">{dim}</div><div class="metric-value">{st.session_state.pcs[dim]}</div></div>', unsafe_allow_html=True)
    
    st.caption("ℹ️ El valor 'Total' representa la Seguridad Global del Apego del alumno/a.")
    st.markdown("---")
    
    if st.button("NUEVA EVALUACIÓN"):
        st.session_state.step = 1
        st.rerun()
