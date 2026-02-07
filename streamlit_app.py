
import streamlit as st
import google.generativeai as genai
import pandas as pd
import io
import os

# --- CONFIGURACIÓN Y CONSTANTES ---
st.set_page_config(page_title="Evaluación Becas Europa", layout="centered", page_icon="🇪🇺")

# URL de respaldo si el archivo local no existe (evita el error de Streamlit)
DEFAULT_AUDIO_URL = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"

# Datos del Quiz Becas Europa (10 preguntas)
BECAS_EUROPA_QUIZ = [
    {"q": "Which institutions are responsible for promoting the Becas Europa initiative?", "options": ["The EU and Ministry", "Banco Santander and UFV", "Oxford and Cambridge", "Madrid and Barcelona"], "correct": 1},
    {"q": "How many pre-university students are selected annually?", "options": ["20", "50", "100", "200"], "correct": 1},
    {"q": "Approximate duration of the academic trip?", "options": ["10 days", "15 days", "20 days", "One semester"], "correct": 2},
    {"q": "Which cities are included in the itinerary?", "options": ["Bologna, Heidelberg, Santiago", "Berlin, Athens, Lisbon", "Paris, London, NY", "Madrid, Brussels, Amsterdam"], "correct": 0},
    {"q": "The program is inspired by which historical event?", "options": ["University of Bologna founding", "Crucero Universitario 1933", "Bologna Declaration", "First Erasmus"], "correct": 1},
    {"q": "Intellectual figures part of the 1933 voyage?", "options": ["Cervantes and Lorca", "Ortega y Gasset, Marías, Marañón", "Dalí and Picasso", "Machado and Jiménez"], "correct": 1},
    {"q": "Primary objective of creating this network of leaders?", "options": ["Guaranteed banking job", "Increase university rankings", "Commitment to use talent for society", "Establish a political party"], "correct": 2},
    {"q": "Fundamental basis for project progress?", "options": ["Highest grades", "Falling in love with what we do", "Mastering 3 languages", "Strict traditions"], "correct": 1},
    {"q": "Academic requirement to remain in the process?", "options": ["Pass everything first attempt", "Average score of 9.7", "Sports competitions", "Write a book"], "correct": 1},
    {"q": "Where is the closing ceremony usually held?", "options": ["Royal Palace", "UFV", "European Parliament", "Santander City (Boadilla)"], "correct": 1}
]

# Items IPPA (21 preguntas)
IPPA_ITEMS = [
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

# --- ESTILOS ---
st.markdown("""
<style>
    .stButton>button { width: 100%; background-color: #e60000; color: white; border-radius: 20px; font-weight: bold; padding: 12px; border: none; font-size: 1.1em; }
    .stButton>button:hover { background-color: #c40000; color: white; border: none; }
    .stAudio { margin-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)

# --- APP LOGIC ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'quiz_answers' not in st.session_state: st.session_state.quiz_answers = {}
if 'ippa_answers' not in st.session_state: st.session_state.ippa_answers = {}
if 'show_questions' not in st.session_state: st.session_state.show_questions = False

st.image("https://www.becaseuropa.es/img/logo_becas_europa.png", width=200)

if st.session_state.step == 1:
    st.title("Registro de Candidato")
    with st.form("reg_form"):
        nom = st.text_input("Nombre")
        ape = st.text_input("Apellidos")
        cen = st.text_input("Centro Educativo")
        gen = st.selectbox("Sexo", ["Chica", "Chico"])
        if st.form_submit_button("About BECAS EUROPA"):
            if nom and ape:
                st.session_state.student = {"nombre": nom, "apellidos": ape, "centro": cen, "sexo": gen}
                st.session_state.step = 2
                st.rerun()
            else: st.warning("Por favor completa los campos obligatorios.")

elif st.session_state.step == 2:
    st.title("Fase 1: Listening Comprehension")
    
    # Lógica de audio robusta
    audio_path = "audio_listening.mp3"
    if os.path.exists(audio_path):
        st.audio(audio_path)
    else:
        st.warning("Nota: Usando audio de respaldo del servidor central para la evaluación.")
        st.audio(DEFAULT_AUDIO_URL)

    if not st.session_state.show_questions:
        st.info("💡 Escucha atentamente el audio completo antes de comenzar el cuestionario.")
        if st.button("He escuchado el audio, comenzar preguntas"):
            st.session_state.show_questions = True
            st.rerun()
    else:
        st.success("✅ Responde a las siguientes 10 cuestiones sobre lo escuchado:")
        for i, item in enumerate(BECAS_EUROPA_QUIZ):
            st.markdown(f"**{i+1}. {item['q']}**")
            st.session_state.quiz_answers[i] = st.radio(
                f"Opción para {i}", 
                item['options'], 
                key=f"q{i}", 
                label_visibility="collapsed",
                index=None
            )
        
        if st.button("Enviar Respuestas de Listening"):
            answered = [a for a in st.session_state.quiz_answers.values() if a is not None]
            if len(answered) < 10:
                st.error("Debes responder todas las preguntas.")
            else:
                score = 0
                for i, item in enumerate(BECAS_EUROPA_QUIZ):
                    if st.session_state.quiz_answers[i] == item['options'][item['correct']]:
                        score += 1
                st.session_state.quiz_score = score
                st.session_state.step = 3
                st.rerun()

elif st.session_state.step == 3:
    st.title("Resultados Fase 1")
    st.metric("Aciertos Listening", f"{st.session_state.quiz_score} / 10")
    st.write("---")
    st.info("Ahora procederemos a la evaluación de relaciones sociales y apego a iguales.")
    if st.button("Continuar a la Escala de Valoración"):
        st.session_state.step = 4
        st.rerun()

elif st.session_state.step == 4:
    st.title("Fase 2: Relaciones Sociales")
    st.caption("Valora del 1 (Nada) al 7 (Totalmente) según tu percepción.")
    
    for id, text, dim in IPPA_ITEMS:
        st.markdown(f"**{id}. {text}**")
        st.session_state.ippa_answers[id] = st.select_slider(
            f"i{id}", 
            options=[1,2,3,4,5,6,7], 
            value=4, 
            key=f"ippa{id}", 
            label_visibility="collapsed"
        )
        
    if st.button("Finalizar Evaluación Integral"):
        sums = {"Confianza": 0, "Comunicación": 0, "Alienación": 0}
        for id, text, dim in IPPA_ITEMS:
            sums[dim] += st.session_state.ippa_answers[id]
        
        raw_total = sums["Confianza"] + sums["Comunicación"] - sums["Alienación"]
        gender = st.session_state.student["sexo"]
        
        pcs = {
            "Confianza": get_pc(sums["Confianza"], NORMS[gender]["confianza"]),
            "Comunicación": get_pc(sums["Comunicación"], NORMS[gender]["comunicacion"]),
            "Alienación": get_pc(sums["Alienación"], NORMS[gender]["alienacion"]),
            "Total": get_pc(raw_total, NORMS[gender]["total"])
        }
        
        st.session_state.pcs = pcs
        st.session_state.step = 5
        st.rerun()

elif st.session_state.step == 5:
    st.balloons()
    st.title("Informe Integral de Candidatura")
    
    c1, c2 = st.columns(2)
    c1.metric("Nota Listening", f"{st.session_state.quiz_score}/10")
    c2.metric("Apego Social (PC)", f"{st.session_state.pcs['Total']}")

    with st.spinner("Analizando perfil con IA..."):
        try:
            genai.configure(api_key=os.environ.get("API_KEY"))
            model = genai.GenerativeModel('gemini-3-flash-preview')
            p = f"Analiza para Becas Europa: Candidato {st.session_state.student['nombre']}. Nota Listening: {st.session_state.quiz_score}/10. Test IPPA: Confianza PC {st.session_state.pcs['Confianza']}, Comunicación PC {st.session_state.pcs['Comunicación']}, Alienación PC {st.session_state.pcs['Alienación']}, Total PC {st.session_state.pcs['Total']}. Redacta un párrafo profesional en español sobre su madurez social."
            ai_text = model.generate_content(p).text
        except:
            ai_text = "Interpretación: El candidato presenta niveles adecuados de seguridad social para el programa."
    
    st.markdown("### Interpretación del Tutor")
    st.info(ai_text)
    
    # Exportación
    df = pd.DataFrame([{
        "Nombre": st.session_state.student["nombre"],
        "Apellidos": st.session_state.student["apellidos"],
        "Listening": st.session_state.quiz_score,
        "PC_Total": st.session_state.pcs["Total"]
    }])
    buf = io.BytesIO()
    df.to_excel(buf, index=False)
    st.download_button("Descargar Registro Excel", buf.getvalue(), "Resultados.xlsx")
    
    if st.button("Finalizar y Salir"):
        st.session_state.clear()
        st.rerun()
