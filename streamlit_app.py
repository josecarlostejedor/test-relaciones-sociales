
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

# Configuración de la página
st.set_page_config(
    page_title="Evaluación de Apego JCYL",
    layout="centered",
    page_icon="👥",
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
        height: 3.5em;
        background-color: #4f46e5;
        color: white;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #4338ca;
        box-shadow: 0 10px 15px -3px rgba(79, 70, 229, 0.4);
    }
    
    .metric-card {
        background: white;
        padding: 24px;
        border-radius: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        text-align: center;
        border: 1px solid #e2e8f0;
    }
    
    .metric-value {
        font-size: 2.8rem;
        font-weight: 800;
        color: #4f46e5;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #64748b;
        text-transform: uppercase;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    .interpretation-container {
        background-color: white;
        padding: 2.5rem;
        border-radius: 24px;
        border-left: 8px solid #4f46e5;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- CONFIGURACIÓN ---
SMTP_USER = "josecarlostejedor@gmail.com" 
SMTP_PASS = "laquujmjoiuopzwv" 
API_KEY = os.environ.get("API_KEY")

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

NORMS = {
    "Chica": {
        "total": [(95, 96), (90, 93), (85, 90), (80, 88), (75, 86), (50, 77), (10, 53)],
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
        msg['Subject'] = f"INFORME APEGO: {student['nombre']} {student['apellidos']} - {student['grupo']}"
        
        body = f"Evaluación de Relaciones Sociales completada.\n\nAlumno/a: {student['nombre']} {student['apellidos']}\nCentro: {student['instituto']}\n\nSe adjunta el informe detallado en Word y el historial actualizado en Excel."
        msg.attach(MIMEText(body, 'plain'))

        part_word = MIMEBase('application', 'octet-stream')
        part_word.set_payload(report_bytes)
        encoders.encode_base64(part_word)
        part_word.add_header('Content-Disposition', f'attachment; filename="Informe_{student["apellidos"]}.docx"')
        msg.attach(part_word)

        part_excel = MIMEBase('application', 'octet-stream')
        part_excel.set_payload(excel_bytes)
        encoders.encode_base64(part_excel)
        part_excel.add_header('Content-Disposition', 'attachment; filename="Historico_Apego_Global.xlsx"')
        msg.attach(part_excel)

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        return True, "Enviado con éxito"
    except Exception as e:
        return False, str(e)

# --- FLUJO ---
if 'step' not in st.session_state:
    st.session_state.step = 1

st.markdown('<div style="text-align: center; margin-bottom: 2rem;"><h1>👥 Escala de Valoración de Habilidades Sociales y Apego entre iguales</h1><p style="color: #64748b;">Protocolo de Evaluación Psicopedagógica JCYL</p></div>', unsafe_allow_html=True)

if st.session_state.step == 1:
    with st.container():
        st.markdown('<div style="background: white; padding: 2rem; border-radius: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;">', unsafe_allow_html=True)
        with st.form("id_form"):
            st.subheader("Datos del Estudiante")
            c1, c2 = st.columns(2)
            with c1:
                nombre = st.text_input("Nombre")
                apellidos = st.text_input("Apellidos")
                sexo = st.selectbox("Sexo", ["Chica", "Chico"])
            with c2:
                curso = st.text_input("Curso", value="1º Bachillerato")
                grupo = st.text_input("Grupo")
                inst = st.text_input("Centro Educativo")
            
            e1 = st.text_input("Email para copia del informe", value=SMTP_USER)
            
            if st.form_submit_button("EMPEZAR EVALUACIÓN"):
                if nombre and apellidos:
                    st.session_state.student = {
                        "nombre": nombre, "apellidos": apellidos, "curso": curso, "grupo": grupo, "sexo": sexo, "instituto": inst,
                        "emails": [e1, "jctejedor@educa.jcyl.es"]
                    }
                    st.session_state.step = 2
                    st.rerun()
                else:
                    st.error("Nombre y apellidos son obligatorios.")
        st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.step == 2:
    resp = {}
    st.markdown("### Cuestionario de Relaciones Sociales")
    st.info("Responde con sinceridad. No hay respuestas correctas o incorrectas.")
    
    for id, txt, dim in TEST_ITEMS:
        st.markdown(f"**{id}. {txt}**")
        resp[id] = st.select_slider(
            f"Escala para {id}",
            options=[1, 2, 3, 4, 5, 6, 7],
            value=4,
            key=f"q_{id}",
            label_visibility="collapsed"
        )
        st.markdown("---")
    
    if st.button("GENERAR INFORME CLÍNICO"):
        with st.spinner("La IA está analizando los resultados psicopedagógicos..."):
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

            # IA Interpretation
            try:
                ai = genai.GoogleGenAI(api_key=API_KEY)
                prompt = f"""Actúa como un psicopedagogo experto. Analiza estos resultados del Test de Apego a Iguales (Armsden y Greenberg) para un alumno de {st.session_state.student['curso']}:
                - Percentil Confianza: {results['Confianza']} (Seguridad y respeto sentido con amigos)
                - Percentil Comunicación: {results['Comunicación']} (Calidad y frecuencia de intercambio verbal)
                - Percentil Alienación: {results['Alienación']} (Sentimiento de aislamiento o vergüenza)
                - Percentil Total: {results['Total']} (Seguridad global del apego)

                Instrucciones detalladas:
                1. Explica a un padre o tutor (que no es experto) qué significa cada una de estas dimensiones.
                2. Explica que el 'Total' es el indicador de la seguridad global en las relaciones sociales del adolescente (cuanto más alto, mayor seguridad).
                3. Interpreta el perfil específico de este alumno basándote en los números.
                4. Proporciona 3 recomendaciones prácticas para fomentar un desarrollo positivo.
                5. Usa un tono empático, claro y profesional.
                6. Divide el texto en secciones claras con títulos."""
                
                response = ai.models.generateContent(
                    model='gemini-3-pro-preview',
                    contents=prompt
                )
                st.session_state.ai_text = response.text
            except Exception as e:
                st.session_state.ai_text = "Interpretación clínica detallada temporalmente no disponible. Los resultados cuantitativos son válidos y pueden consultarse en la tabla de baremos."

            # Document Word
            doc = Document()
            doc.add_heading('INFORME PSICOPEDAGÓGICO DE RELACIONES SOCIALES', 0)
            
            header_p = doc.add_paragraph()
            header_p.add_run(f"Estudiante: {st.session_state.student['nombre']} {st.session_state.student['apellidos']}").bold = True
            doc.add_paragraph(f"Centro: {st.session_state.student['instituto']} | Curso: {st.session_state.student['curso']}")
            doc.add_paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")

            doc.add_heading('1. Resultados Cuantitativos (Percentiles)', level=1)
            table = doc.add_table(rows=1, cols=2)
            table.style = 'Light Grid Accent 1'
            hdr_cells = table.rows[0].cells
            hdr_cells[0].text = 'Dimensión'
            hdr_cells[1].text = 'Percentil (PC)'
            for k, v in results.items():
                row_cells = table.add_row().cells
                row_cells[0].text = k
                row_cells[1].text = str(v)

            doc.add_heading('2. Interpretación Clínica Detallada', level=1)
            doc.add_paragraph(st.session_state.ai_text)
            
            doc.add_paragraph("\n" + "—" * 20)
            footer = doc.add_paragraph()
            footer.add_run("Los datos de este informe resultan de aplicar la siguiente escala de Valoración para ver las relaciones sociales entre iguales y que la fuente de información es esta:").italic = True
            doc.add_paragraph("Escala para la evaluación del apego a iguales. (The inventory of parent and peer attachment). Amrsden, G. C. y Greemberg, M. T. (1987)").bold = True

            b_word = io.BytesIO()
            doc.save(b_word)
            st.session_state.word_file = b_word.getvalue()

            # Historico
            new_data = {**st.session_state.student, **results, "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M")}
            HISTORY_FILE = "historico_global_apego.csv"
            if os.path.exists(HISTORY_FILE):
                df = pd.read_csv(HISTORY_FILE)
                df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            else:
                df = pd.DataFrame([new_data])
            df.to_csv(HISTORY_FILE, index=False)
            
            ok, msg = send_automated_emails(st.session_state.student, st.session_state.word_file, df)
            st.session_state.email_status = (ok, msg)
            st.session_state.step = 3
            st.rerun()

elif st.session_state.step == 3:
    st.balloons()
    st.success("✅ Informe procesado con éxito")
    
    res = st.session_state.final_results
    cols = st.columns(4)
    labels = ["Confianza", "Comunicación", "Alienación", "Total"]
    for i, label in enumerate(labels):
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{res[label]}</div>
                <div style="font-size: 0.8rem; color: #94a3b8;">Percentil (PC)</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="interpretation-container">', unsafe_allow_html=True)
    st.subheader("🧠 Interpretación Clínica Detallada")
    st.markdown(st.session_state.ai_text)
    st.markdown('</div>', unsafe_allow_html=True)

    st.download_button(
        label="📥 DESCARGAR INFORME WORD (.DOCX)",
        data=st.session_state.word_file,
        file_name=f"Informe_{st.session_state.student['apellidos']}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    if st.button("REALIZAR NUEVA EVALUACIÓN"):
        st.session_state.step = 1
        st.rerun()
