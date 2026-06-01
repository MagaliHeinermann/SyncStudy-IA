import streamlit as st
import pdfplumber
from google import genai
from google.genai import types

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="SyncStudy IA",
    page_icon="🧠",
    layout="centered"
)

st.markdown('<h1 style="text-align: center; color: #1E3A8A;">🧠 SyncStudy IA</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #4B5563;">Optimiza tu material de estudio y genera cuestionarios interactivos con IA</p>', unsafe_allow_html=True)

# 2. VALIDACIÓN DE CREDENCIALES (SECRETS)
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
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
    st.sidebar.warning("⚠️ Esperando configuración de API Key...")

# 3. EXPANDER INFORMATIVO
with st.expander("ℹ️ ¿Cómo funciona tu producto?"):
    st.markdown("""
    * **Síntesis Jerárquica:** Reduce textos densos a conceptos clave ordenados pedagógicamente.
    * **Estudio Activo:** Genera un cuestionario de 5 preguntas automatizadas para medir tu comprensión.
    """)

# 4. ENTRADA DE DATOS
st.markdown("### 1. Carga tu Material de Estudio")
texto_manual = st.text_area("Copia y pega el texto de tu apunte aquí:", height=150)
archivo_pdf = st.file_uploader("O sube un archivo académico (Formato PDF)", type=["pdf"])

texto_final = ""
if archivo_pdf is not None:
    with pdfplumber.open(archivo_pdf) as pdf:
        texto_final = "\n".join([pagina.extract_text() for pagina in pdf.pages if pagina.extract_text()])
    st.success("¡PDF cargado exitosamente en memoria!")
elif texto_manual:
    texto_final = texto_manual

# 5. LÓGICA DE PROCESAMIENTO
st.markdown("### 2. Ejecutar Análisis Inteligente")
boton_procesar = st.button("🚀 Procesar Material de Estudio")

system_prompt = """
Eres un experto instruccional y pedagógico avanzado. Tu objetivo es optimizar el material de estudio provisto por el usuario para facilitar el aprendizaje autónomo.
1. Genera una estructura jerárquica con los conceptos centrales y sus definiciones analíticas.
2. Diseña un cuestionario de autoevaluación de 5 preguntas clave basadas estrictamente en el texto para validar la comprensión lectora.
"""

if boton_procesar:
    if not api_key:
        st.error("Error: Configura 'GEMINI_API_KEY' en el panel de Secrets de Streamlit Cloud.")
    elif not texto_final:
        st.warning("Por favor, ingresa texto o sube un archivo PDF.")
    else:
        with st.spinner("Gemini está analizando tu material de estudio..."):
            try:
                # Inicialización explícita con la SDK moderna
                client = genai.Client(api_key=api_key)
                
                # Llamada limpia al modelo oficial estable
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=texto_final,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.3
                    )
                )
                
                st.session_state['resultado_analisis'] = response.text
                
            except Exception as e:
                st.error(f"Error de comunicación con la API de Gemini: {e}")

# 6. ENTRADA DE RESULTADOS
if 'resultado_analisis' in st.session_state:
    st.markdown("---")
    st.markdown("### ✨ Material de Estudio Optimizado")
    st.write(st.session_state['resultado_analisis'])

st.markdown("---")
st.markdown("<p style='text-align: center; color: #9CA3AF; font-size: 0.8rem;'>SyncStudy IA © 2026</p>", unsafe_allow_html=True)