
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

# Estilos visuales
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #4f46e5; color: white; font-weight: 600; border: none; }
    .metric-card { background: white; padding: 24px; border-radius: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); text-align: center; border: 1px solid #e2e8f0; }
    .metric-value { font-size: 2.8rem; font-weight: 800; color: #4f46e5; }
    .metric-label { font-size: 0.9rem; color: #64748b; text-transform: uppercase; font-weight: 600; margin-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# Configuración API y Email
API_KEY = os.environ.get("API_KEY")
SMTP_USER = "josecarlostejedor@gmail.com"
SMTP_PASS = "laquujmjoiuopzwv"
DEST_EMAIL = "josecarlostejedor@gmail.com"

# Baremos