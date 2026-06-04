import streamlit as st
import pdfplumber
import cohere

# 1. CONFIGURACIÓN DE LA INTERFAZ
st.set_page_config(
    page_title="SyncStudy IA",
    page_icon="🧠",
    layout="centered"
)

st.markdown('<h1 style="text-align: center; color: #1E3A8A;">🧠 SyncStudy IA</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #4B5563; text-align: center;">Optimización de material de estudio con Inteligencia Artificial (Engine: Cohere)</p>', unsafe_allow_html=True)

# 2. CAPA DE AUTENTICACIÓN (COHERE API)
if "COHERE_API_KEY" in st.secrets:
    api_key = st.secrets["COHERE_API_KEY"]
    co = cohere.ClientV2(api_key=api_key)
else:
    api_key = None
    co = None

# Sidebar informativa requerida para la entrega
st.sidebar.header("Control de Despliegue")
st.sidebar.markdown("**Estudiante:** Magali Heinermann")
st.sidebar.markdown("**Comisión:** 95840")
st.sidebar.markdown("---")
if api_key:
    st.sidebar.success("🔑 Motor Cohere listo y autenticado")
else:
    st.sidebar.warning("⚠️ Esperando COHERE_API_KEY en Secrets...")

# 3. COMPONENTES DE ENTRADA DE DATOS (INPUT LAYER)
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
st.markdown("### 2. Ejecutar Análisis Pedagógico")
boton_procesar = st.button("🚀 Procesar Material de Estudio")

system_prompt = (
    "Actúas como un experto en diseño instruccional y pedagogía avanzada.\n"
    "A partir del texto provisto por el usuario, debes generar de forma estructurada:\n"
    "1. Una síntesis jerárquica con los conceptos centrales perfectamente definidos de forma analítica.\n"
    "2. Un cuestionario interactivo de autoevaluación compuesto por 5 preguntas clave basadas estrictamente en la lectura."
)

if boton_procesar:
    if not api_key or not co:
        st.error("Error de Backend: No se detectaron credenciales válidas de Cohere en st.secrets.")
