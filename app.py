import streamlit as st
import pdfplumber
import google.generativeai as genai

# 1. Configuración de Entorno y Estilos Nativos
st.set_page_config(
    page_title="SyncStudy IA",
    page_icon="🧠",
    layout="centered"
)

st.markdown('<h1 style="text-align: center; color: #1E3A8A;">🧠 SyncStudy IA</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #4B5563; text-align: center;">Optimización de material de estudio con Inteligencia Artificial</p>', unsafe_allow_html=True)

# 2. Inicialización de Capa de Autenticación
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
else:
    api_key = None

# Componente de depuración lateral para la entrega
st.sidebar.header("Control de Despliegue")
st.sidebar.markdown("**Desarrolladora:** Magali Heinermann")
st.sidebar.markdown("**Comisión:** 95840")
st.sidebar.markdown("---")
if api_key:
    st.sidebar.success("🔑 Credenciales cargadas en st.secrets")
else:
    st.sidebar.warning("⚠️ Esperando token de autenticación...")

# 3. Módulos de Entrada de Datos
st.markdown("### 1. Carga de Material Académico")
texto_manual = st.text_area("Pega el texto del apunte aquí:", height=150)
archivo_pdf = st.file_uploader("O procesa un documento en formato PDF", type=["pdf"])

texto_final = ""
if archivo_pdf is not None:
    with pdfplumber.open(archivo_pdf) as pdf:
        texto_final = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    st.success("Documento PDF parseado correctamente en memoria.")
elif texto_manual:
    texto_final = texto_manual

# 4. Pipeline de Inferencia
st.markdown("### 2. Procesamiento de Información")
boton_procesar = st.button("🚀 Ejecutar Análisis Jerárquico")

system_prompt = (
    "Actúa como un diseñador instruccional experto. Analiza el texto provisto y genera:\n"
    "1. Una estructura jerárquica con los conceptos centrales y sus respectivas definiciones analíticas.\n"
    "2. Un cuestionario de autoevaluación interactivo compuesto por 5 preguntas clave basadas estrictamente en el texto."
)

if boton_procesar:
    if not api_key:
        st.error("Error de configuración: GEMINI_API_KEY no inicializada en los secretos del servidor.")
    elif not texto_final:
        st.warning("Entrada de datos vacía. Por favor provee un texto o archivo válido.")
    else:
        with st.spinner("Procesando consulta con el clúster de Gemini..."):
            try:
                # Instanciación limpia sobre el modelo estable de producción masiva
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt_estructurado = f"{system_prompt}\n\n[TEXTO DE ESTUDIO]\n{texto_final}"
                
                response = model.generate_content(prompt_estructurado)
                st.session_state['payload_respuesta'] = response.text
            except Exception as e:
                st.error(f"Excepción controlada del SDK de Google: {e}")

# 5. Despliegue de Resultados (Output)
if 'payload_respuesta' in st.session_state:
    st.markdown("---")
    st.markdown("### ✨ Resultados del Análisis Pedagógico")
    st.write(st.session_state['payload_respuesta'])
