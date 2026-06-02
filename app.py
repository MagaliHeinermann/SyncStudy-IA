import streamlit as st
import pdfplumber
from google import genai
from google.genai import types

# 1. CONFIGURACIÓN DE ENTORNO
st.set_page_config(
    page_title="SyncStudy IA",
    page_icon="🧠",
    layout="centered"
)

st.markdown('<h1 style="text-align: center; color: #1E3A8A;">🧠 SyncStudy IA</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #4B5563; text-align: center;">Optimización de material de estudio con Inteligencia Artificial</p>', unsafe_allow_html=True)

# 2. CAPA DE AUTENTICACIÓN
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = None

# Componente lateral informativo de auditoría
st.sidebar.header("Control de Despliegue")
st.sidebar.markdown("**Estudiante:** Magali Heinermann")
st.sidebar.markdown("**Comisión:** 95840")
st.sidebar.markdown("---")
if api_key:
    st.sidebar.success("🔑 Token de autenticación montado en Secrets")
else:
    st.sidebar.warning("⚠️ Variable GEMINI_API_KEY no detectada")

# 3. CAPA DE ENTRADA DE DATOS (INPUT LAYER)
st.markdown("### 1. Carga de Material Académico")
texto_manual = st.text_area("Pega tus apuntes o extractos de texto aquí:", height=150)
archivo_pdf = st.file_uploader("O sube tu material en formato académico (PDF)", type=["pdf"])

texto_final = ""
if archivo_pdf is not None:
    with pdfplumber.open(archivo_pdf) as pdf:
        texto_final = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    st.success("Parser: PDF procesado correctamente en la sesión.")
elif texto_manual:
    texto_final = texto_manual

# 4. PIPELINE DE INFERENCIA (CORE LAYER)
st.markdown("### 2. Ejecutar Análisis Cognitivo")
boton_procesar = st.button("🚀 Procesar Material de Estudio")

system_prompt = (
    "Actúa como un experto en diseño instruccional y pedagogía avanzada.\n"
    "A partir del texto provisto por el usuario, debes generar de forma estructurada:\n"
    "1. Una síntesis jerárquica con los conceptos centrales perfectamente definidos de forma analítica.\n"
    "2. Un cuestionario interactivo de autoevaluación compuesto por 5 preguntas clave basadas estrictamente en la lectura."
)

if boton_procesar:
    if not api_key:
        st.error("Error de Backend: GEMINI_API_KEY no inicializada en los secretos del servidor.")
    elif not texto_final:
        st.warning("Validación fallida: El campo de entrada de datos no puede estar vacío.")
    else:
        with st.spinner("Estableciendo conexión segura con el clúster de Google..."):
            try:
                # Inicialización limpia utilizando la SDK moderna oficial
                client = genai.Client(api_key=api_key)
                
                # Invocación explícita mediante configuración de tipos nativos
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=texto_final,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.3
                    )
                )
                st.session_state['data_output'] = response.text
            except Exception as e:
                st.error(f"Error crítico en el handshake de la API externa: {e}")

# 5. CAPA DE SALIDA (OUTPUT LAYER)
if 'data_output' in st.session_state:
    st.markdown("---")
    st.markdown("### ✨ Material de Estudio Optimizado")
    st.write(st.session_state['data_output'])

st.markdown("---")
st.markdown("<p style='text-align: center; color: #9CA3AF; font-size: 0.8rem;'>SyncStudy IA © 2026</p>", unsafe_allow_html=True)
