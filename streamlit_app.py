
import streamlit as st
import google.generativeai as genai
from docx import Document
from docx.shared import Pt
import pandas as pd
import io
import os
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Evaluación de Relaciones Sociales", layout="centered", page_icon="📝")

# --- CONSTANTES Y BAREMOS ---
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

HISTORY_FILE = "historico_evaluaciones.csv"

def get_percentile(score, table):
    for centile, min_score in table:
        if score >= min_score:
            return centile
    return 1

def update_history(student_data, results_data):
    """Actualiza y devuelve el dataframe histórico guardado en CSV local."""
    new_entry = {
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Nombre": student_data["nombre"],
        "Apellidos": student_data["apellidos"],
        "Edad": student_data["edad"],
        "Sexo": student_data["sexo"],
        "Curso": student_data["curso"],
        "Grupo": student_data["grupo"],
        "Instituto": student_data["instituto"],
        "PC_Confianza": results_data["pc"]["Confianza"],
        "PC_Comunicacion": results_data["pc"]["Comunicación"],
        "PC_Alienacion": results_data["pc"]["Alienación"],
        "PC_Total": results_data["pc"]["Total"]
    }
    
    if os.path.exists(HISTORY_FILE):
        try:
            df = pd.read_csv(HISTORY_FILE)
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        except:
            df = pd.DataFrame([new_entry])
    else:
        df = pd.DataFrame([new_entry])
    
    df.to_csv(HISTORY_FILE, index=False)
    return df

# --- INTERFAZ STREAMLIT ---

st.title("📝 Evaluación de Relaciones Sociales")
st.markdown("Herramienta para la Evaluación de Apego a Iguales (16-17 años)")

if 'step' not in st.session_state:
    st.session_state.step = 1

if st.session_state.step == 1:
    with st.form("datos_iniciales"):
        st.subheader("Datos del Alumno/a")
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre")
            apellidos = st.text_input("Apellidos")
            edad = st.selectbox("Edad", [16, 17])
        with c2:
            curso = st.text_input("Curso (ej: 1º Bach)")
            grupo = st.text_input("Grupo (ej: A, B)")
            sexo = st.radio("Sexo", ["Chica", "Chico"])
            
        instituto = st.text_input("Instituto / Centro Educativo")
        
        st.divider()
        st.subheader("Notificaciones")
        email1 = st.text_input("Email adicional 1 (opcional)")
        email2 = st.text_input("Email adicional 2 (opcional)")
        
        if st.form_submit_button("Siguiente: Realizar Test"):
            if not (nombre and apellidos and curso and grupo and instituto):
                st.error("Por favor, completa todos los campos obligatorios.")
            else:
                st.session_state.student = {
                    "nombre": nombre, "apellidos": apellidos, "edad": edad,
                    "curso": curso, "grupo": grupo, "sexo": sexo, "instituto": instituto,
                    "emails": [e for e in ["jctejedor@educa.jcyl.es", email1, email2] if e]
                }
                st.session_state.step = 2
                st.rerun()

elif st.session_state.step == 2:
    st.info("Valora cada enunciado de 1 (Totalmente en desacuerdo) a 7 (Totalmente de acuerdo).")
    
    respuestas = {}
    for id, txt, dim in TEST_ITEMS:
        respuestas[id] = st.select_slider(f"{id}. {txt}", options=[1, 2, 3, 4, 5, 6, 7], value=4, key=f"q_{id}")
    
    if st.button("Finalizar y Generar Informe", type="primary"):
        # Cálculos de puntuaciones
        c_val = sum(respuestas[id] for id, t, dim in TEST_ITEMS if dim == "Confianza")
        m_val = sum(respuestas[id] for id, t, dim in TEST_ITEMS if dim == "Comunicación")
        a_val = sum(respuestas[id] for id, t, dim in TEST_ITEMS if dim == "Alienación")
        t_raw = c_val + m_val - a_val
        
        n_table = NORMS[st.session_state.student["sexo"]]
        st.session_state.results = {
            "raw": {"Confianza": c_val, "Comunicación": m_val, "Alienación": a_val, "Total": t_raw},
            "pc": {
                "Confianza": get_percentile(c_val, n_table["confianza"]),
                "Comunicación": get_percentile(m_val, n_table["comunicacion"]),
                "Alienación": get_percentile(a_val, n_table["alienacion"]),
                "Total": get_percentile(t_raw, n_table["total"])
            }
        }
        
        # Registrar en Histórico
        st.session_state.history_df = update_history(st.session_state.student, st.session_state.results)
        
        # Informe IA (Gemini)
        with st.spinner("Analizando resultados con IA..."):
            try:
                genai.configure(api_key=os.environ.get("API_KEY"))
                model = genai.GenerativeModel('gemini-1.5-flash')
                p_text = f"Genera un informe psicopedagógico formal para el alumno {st.session_state.student['nombre']} con estos percentiles: Confianza PC {st.session_state.results['pc']['Confianza']}, Comunicación PC {st.session_state.results['pc']['Comunicación']}, Alienación PC {st.session_state.results['pc']['Alienación']}, Total PC {st.session_state.results['pc']['Total']}. Analiza el apego a iguales y da consejos. Sin saludos."
                st.session_state.report_text = model.generate_content(p_text).text
            except:
                st.session_state.report_text = "Interpretación cualitativa manual requerida."
        
        st.session_state.step = 3
        st.rerun()

elif st.session_state.step == 3:
    st.success("Test finalizado y guardado en el historial.")
    
    r = st.session_state.results
    s = st.session_state.student
    
    # Métrica visual
    m_cols = st.columns(4)
    m_cols[0].metric("Confianza", f"PC {r['pc']['Confianza']}")
    m_cols[1].metric("Comunicación", f"PC {r['pc']['Comunicación']}")
    m_cols[2].metric("Alienación", f"PC {r['pc']['Alienación']}")
    m_cols[3].metric("TOTAL", f"PC {r['pc']['Total']}")

    # --- WORD ---
    doc = Document()
    doc.add_heading('INFORME EVALUACIÓN RELACIONES SOCIALES', 0)
    info = doc.add_paragraph()
    info.add_run(f"Alumno: {s['nombre']} {s['apellidos']}\n").bold = True
    info.add_run(f"Curso: {s['curso']} {s['grupo']} | Centro: {s['instituto']}\n")
    info.add_run(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}")
    
    doc.add_heading('Resultados', level=1)
    tbl = doc.add_table(rows=1, cols=3)
    tbl.style = 'Table Grid'
    h_cells = tbl.rows[0].cells
    h_cells[0].text = 'Dimensión'; h_cells[1].text = 'PD'; h_cells[2].text = 'Centil'
    for d in ["Confianza", "Comunicación", "Alienación", "Total"]:
        row = tbl.add_row().cells
        row[0].text = d
        row[1].text = str(r["raw"][d])
        row[2].text = str(r["pc"][d])

    doc.add_heading('Interpretación', level=1)
    doc.add_paragraph(st.session_state.report_text)
    doc.add_paragraph("\nAtentamente,\nEl profesor Evaluador").alignment = 2
    
    b_word = io.BytesIO()
    doc.save(b_word)

    # --- EXCEL ---
    b_excel = io.BytesIO()
    with pd.ExcelWriter(b_excel, engine='openpyxl') as writer:
        st.session_state.history_df.to_excel(writer, index=False, sheet_name='Historial')
    
    st.divider()
    
    # Descargas
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button("📥 Descargar Informe (WORD)", data=b_word.getvalue(), file_name=f"Informe_{s['apellidos']}.docx", use_container_width=True)
    with col_d2:
        st.download_button("📊 Descargar Histórico (EXCEL)", data=b_excel.getvalue(), file_name="Historico_Clase.xlsx", use_container_width=True)

    # Email
    dest = ",".join(s["emails"])
    sub = f"Evaluación Relaciones Sociales - {s['nombre']}"
    txt = f"Hola,\n\nSe adjunta informe de {s['nombre']} y el histórico Excel actualizado.\n\nAtentamente,\nEl profesor Evaluador"
    link = f"mailto:{dest}?subject={sub}&body={txt}".replace(" ", "%20").replace("\n", "%0D%0A")
    st.markdown(f'<a href="{link}" target="_blank" style="text-decoration:none;"><div style="background-color:#4F46E5;color:white;padding:15px;border-radius:10px;text-align:center;font-weight:bold;">📧 Enviar al Tutor (Adjuntar archivos)</div></a>', unsafe_allow_html=True)

    if st.button("🔄 Nueva Evaluación"):
        for k in ["student", "results", "report_text", "step"]:
            if k in st.session_state: del st.session_state[k]
        st.rerun()
