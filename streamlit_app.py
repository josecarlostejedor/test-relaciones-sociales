
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

# Configuración de la página con estilo moderno
st.set_page_config(
    page_title="Evaluación Relaciones JCYL",
    layout="centered",
    page_icon="📝",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background-color: #f8fafc;
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background-color: #4f46e5;
        color: white;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #4338ca;
        box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.4);
        transform: translateY(-2px);
    }
    
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        text-align: center;
        border: 1px solid #e2e8f0;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #4f46e5;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }
    
    .interpretation-box {
        background: white; 
        padding: 2rem; 
        border-radius: 16px; 
        border-left: 6px solid #4f46e5; 
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);
        line-height: 1.8;
        color: #1e293b;
    }
</style>
""", unsafe_allow_html=True)

# --- CREDENCIALES ---
SMTP_USER = "josecarlostejedor@gmail.com" 
SMTP_PASS = "laquujmjoiuopzwv" 
# Según directrices actualizadas
API_KEY_GEMINI = os.environ.get("API_KEY", "AIzaSyCKNTFjKb7iTclVck0E3w0zBp4wQLzj4v4")

# --- BAREMOS DEL TEST ---
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

NORMS_16_17 = {
    "Chica": {
        "total": [(95, 96), (90, 93), (85, 90), (80, 88), (75, 86), (50, 77), (10, 53)],
        "confianza": [(95, 56), (80, 54), (50, 49), (10, 40)],
        "comunicacion": [(95, 49), (80, 46), (50, 42), (10, 34)],
        "alienacion": [(95, 26), (80, 19), (10, 7)]
    },
    "Chico": {
        "total": [(95, 92), (90, 90), (80, 84), (75, 83), (50, 71), (10, 48)],
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
    try:
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            history_df.to_excel(writer, index=False, sheet_name='Historial')
        excel_bytes = excel_buffer.getvalue()

        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = ", ".join(student["emails"])
        msg['Subject'] = f"INFORME PSICOPEDAGÓGICO: {student['nombre']} {student['apellidos']}"
        
        body = f"Se adjunta el informe de evaluación de relaciones sociales.\n\nAlumno: {student['nombre']} {student['apellidos']}\nCurso: {student['curso']}\n\nEste correo incluye el informe Word con interpretación clínica y el histórico consolidado."
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

        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=20)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        return True, "Enviado con éxito"
    except Exception as e:
        return False, str(e)

# --- FLUJO ---
if 'step' not in st.session_state:
    st.session_state.step = 1

st.markdown('<div style="text-align: center; margin-bottom: 2rem;"><h1>📝 Evaluación Relaciones JCYL</h1><p style="color: #64748b;">Protocolo Profesional de Análisis de Apego (16-17 años)</p></div>', unsafe_allow_html=True)

if st.session_state.step == 1:
    with st.container():
        st.markdown('<div style="background: white; padding: 2rem; border-radius: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">', unsafe_allow_html=True)
        with st.form("id_form"):
            st.subheader("Datos de Identificación")
            c1, c2 = st.columns(2)
            with c1:
                nombre = st.text_input("Nombre")
                apellidos = st.text_input("Apellidos")
                sexo = st.selectbox("Sexo", ["Chica", "Chico"])
            with c2:
                curso = st.text_input("Curso", value="1º Bachillerato")
                grupo = st.text_input("Grupo")
                inst = st.text_input("Centro Educativo")
            
            e1 = st.text_input("Email para el informe (Copia)", value=SMTP_USER)
            
            submit = st.form_submit_button("INICIAR CUESTIONARIO")
            if submit:
                if nombre and apellidos and e1:
                    st.session_state.student = {
                        "nombre": nombre, "apellidos": apellidos, "curso": curso, "grupo": grupo, "sexo": sexo, "instituto": inst,
                        "emails": [e1, "jctejedor@educa.jcyl.es"]
                    }
                    st.session_state.step = 2
                    st.rerun()
                else:
                    st.error("Por favor, rellene los campos obligatorios.")
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.step == 2:
    resp = {}
    st.markdown("### Test de Apego a Iguales (Armsden y Greenberg)")
    st.info("Puntúa cada frase según tu grado de acuerdo (1: Nada, 7: Totalmente)")
    
    for id, txt, dim in TEST_ITEMS:
        st.markdown(f"**{id}. {txt}**")
        resp[id] = st.select_slider(
            f"Valor para {id}",
            options=[1, 2, 3, 4, 5, 6, 7],
            value=4,
            key=f"q_{id}",
            label_visibility="collapsed"
        )
        st.markdown("---")
    
    if st.button("FINALIZAR Y GENERAR INFORME"):
        with st.spinner("Analizando resultados con Inteligencia Artificial..."):
            c_val = sum(resp[id] for id, t, dim in TEST_ITEMS if dim == "Confianza")
            m_val = sum(resp[id] for id, t, dim in TEST_ITEMS if dim == "Comunicación")
            a_val = sum(resp[id] for id, t, dim in TEST_ITEMS if dim == "Alienación")
            t_raw = c_val + m_val - a_val
            n_tab = NORMS_16_17[st.session_state.student["sexo"]]
            
            results = {
                "Confianza": get_percentile(c_val, n_tab["confianza"]),
                "Comunicación": get_percentile(m_val, n_tab["comunicacion"]),
                "Alienación": get_percentile(a_val, n_tab["alienacion"]),
                "Total": get_percentile(t_raw, n_tab["total"])
            }
            st.session_state.final_results = results

            # IA Analysis - Gemini 3 Pro
            try:
                ai = genai.GenerativeAI(api_key=API_KEY_GEMINI)
                prompt = f"""Actúa como psicopedagogo experto. Analiza estos percentiles (PC) de un adolescente en el Test de Apego a Iguales:
                Resultados: {results}
                
                Instrucciones:
                1. Explica qué significa cada dimensión (Confianza, Comunicación, Alienación) para un lector no experto.
                2. El 'Total' indica la seguridad global del apego: explica qué significa un PC de {results['Total']}.
                3. Proporciona una interpretación clínica detallada y 3 recomendaciones prácticas.
                4. Usa un lenguaje empático y profesional."""
                
                response = ai.models.generateContent(
                    model='gemini-3-pro-preview',
                    contents=prompt
                )
                st.session_state.ai_text = response.text
            except:
                st.session_state.ai_text = "La interpretación detallada no pudo generarse. Por favor, analice los percentiles manualmente siguiendo el manual."

            # Documento Word
            doc = Document()
            doc.add_heading('INFORME TÉCNICO DE EVALUACIÓN SOCIAL', 0)
            p = doc.add_paragraph()
            p.add_run(f"Estudiante: {st.session_state.student['nombre']} {st.session_state.student['apellidos']}").bold = True
            doc.add_paragraph(f"Curso: {st.session_state.student['curso']} | Centro: {st.session_state.student['instituto']}")
            
            doc.add_heading('1. Resultados Cuantitativos (Percentiles)', level=1)
            table = doc.add_table(rows=1, cols=2)
            table.style = 'Light Grid Accent 1'
            hdr_cells = table.rows[0].cells
            hdr_cells[0].text = 'Dimensión de Apego'
            hdr_cells[1].text = 'Percentil (PC)'
            for k, v in results.items():
                row_cells = table.add_row().cells
                row_cells[0].text = k
                row_cells[1].text = f"PC {v}"

            doc.add_heading('2. Interpretación Clínica Detallada (IA)', level=1)
            doc.add_paragraph(st.session_state.ai_text)
            
            b_word = io.BytesIO()
            doc.save(b_word)
            st.session_state.word_file = b_word.getvalue()

            # Histórico
            new_data = {**st.session_state.student, **results, "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M")}
            if os.path.exists(HISTORY_FILE):
                df = pd.read_csv(HISTORY_FILE)
                df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            else:
                df = pd.DataFrame([new_data])
            df.to_csv(HISTORY_FILE, index=False)

            # Envío
            ok, msg = send_automated_emails(st.session_state.student, st.session_state.word_file, df)
            st.session_state.email_status = (ok, msg)
            st.session_state.step = 3
            st.rerun()

elif st.session_state.step == 3:
    st.balloons()
    st.success("✅ Informe Generado y Enviado")
    
    res = st.session_state.final_results
    cols = st.columns(4)
    labels = ["Confianza", "Comunicación", "Alienación", "Total"]
    for i, label in enumerate(labels):
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{res[label]}</div>
                <div style="font-size: 0.8rem; color: #94a3b8;">PC (Percentil)</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### 🧠 Interpretación Clínica Detallada")
    st.markdown(f'<div class="interpretation-box">{st.session_state.ai_text}</div>', unsafe_allow_html=True)

    st.download_button(
        label="📥 DESCARGAR INFORME COMPLETO (.DOCX)",
        data=st.session_state.word_file,
        file_name=f"Informe_{st.session_state.student['apellidos']}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    if st.button("NUEVA EVALUACIÓN"):
        st.session_state.step = 1
        st.rerun()
