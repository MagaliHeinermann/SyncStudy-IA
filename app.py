import streamlit as st
import pdfplumber
import google.generativeai as genai

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="SyncStudy IA", page_icon="🧠", layout="centered")

st.markdown('<h1 style="text-align: center; color: #1E3A8A;">🧠 SyncStudy IA</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #4B5563;">Optimiza tu material de estudio y genera cuestionarios interactivos con IA</p>', unsafe_allow_html=True)

# SELECCIÓN SEGURA DE LA API KEY INTEGRADA (SECRETS)
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
else:
    api_key = None

# Barra lateral informativa
st.sidebar.header("Información del Proyecto")
st.sidebar.markdown("**Estudiante:** Magali Heinermann")
st.sidebar.markdown("**Comisión:** 95840")
st.sidebar.markdown("---")
if api_key:
    st.sidebar.success("🔑 API de Gemini vinculada correctamente")
else:
    st.sidebar.warning("⚠️ Esperando configuración...")

# COMPONENTES DE ENTRADA DE DATOS
st.markdown("### 1. Carga tu Material de Estudio")
texto_manual = st.text_area("Copia y pega tu texto aquí:", height=150)
archivo_pdf = st.file_uploader("O sube un archivo académico (PDF)", type=["pdf"])

texto_final = ""
if archivo_pdf is not None:
    with pdfplumber.open(archivo_pdf) as pdf:
        texto_final = "\n".join([pagina.extract_text() for pagina in pdf.pages if pagina.extract_text()])
    st.success("¡PDF cargado exitosamente en memoria!")
elif texto_manual:
    texto_final = texto_manual

# BOTÓN DE ACCIÓN
st.markdown("### 2. Ejecutar Análisis Inteligente")
boton_procesar = st.button("🚀 Procesar Material de Estudio")

system_prompt = """
Eres un experto instruccional y pedagógico avanzado. Tu objetivo es optimizar el material de estudio provisto por el usuario para facilitar el aprendizaje autónomo.
Genera una estructura jerárquica con los conceptos centrales y diseña un cuestionario de autoevaluación de 5 preguntas clave basadas estrictamente en el texto.
"""

if boton_procesar:
    if not api_key:
        st.error("Error: Falta la API Key en los Secrets.")
    elif not texto_final:
        st.warning("Por favor, ingresa texto o sube un archivo PDF.")
    else:
        with st.spinner("Gemini está analizando tu material de estudio..."):
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt_completo = f"{system_prompt}\n\nMaterial a estudiar:\n{texto_final}"
            response = model.generate_content(prompt_completo)
            st.session_state['resultado_analisis'] = response.text

# DESPLIEGUE DE RESULTADOS
if 'resultado_analisis' in st.session_state:
    st.markdown("---")
    st.markdown("### ✨ Material de Estudio Optimizado")
    st.write(st.session_state['resultado_analisis'])

st.markdown("---")
st.markdown("<p style='text-align: center; color: #9CA3AF; font-size: 0.8rem;'>SyncStudy IA © 2026</p>", unsafe_allow_html=True)