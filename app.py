import streamlit as st
import pdfplumber
import google.generativeai as genai

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="SyncStudy IA",
    page_icon="🧠",
    layout="centered"
)

st.markdown('<h1 style="text-align: center; color: #1E3A8A;">🧠 SyncStudy IA</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #4B5563; text-align: center;">Optimiza tu material de estudio con IA</p>', unsafe_allow_html=True)

# 2. SELECCIÓN DE CREDENCIALES
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
else:
    api_key = None

# Barra lateral informativa requerida para la entrega
st.sidebar.header("Información del Proyecto")
st.sidebar.markdown("**Estudiante:** Magali Heinermann")
st.sidebar.markdown("**Comisión:** 95840")
st.sidebar.markdown("---")
if api_key:
    st.sidebar.success("🔑 API de Gemini vinculada en Secrets")
else:
    st.sidebar.warning("⚠️ Esperando configuración de API Key...")

# 3. COMPONENTES DE ENTRADA
texto_manual = st.text_area("Copia tu texto de estudio aquí:", height=150)
archivo_pdf = st.file_uploader("O sube un archivo PDF", type=["pdf"])

texto_final = ""
if archivo_pdf is not None:
    with pdfplumber.open(archivo_pdf) as pdf:
        texto_final = "\n".join([pagina.extract_text() for pagina in pdf.pages if pagina.extract_text()])
    st.success("¡PDF cargado exitosamente en memoria!")
elif texto_manual:
    texto_final = texto_manual

# 4. BOTÓN DE ACCIÓN Y PROCESAMIENTO
boton_procesar = st.button("🚀 Procesar Material de Estudio")

system_prompt = (
    "Eres un experto instruccional y pedagógico avanzado. Tu objetivo es optimizar el material de estudio "
    "provisto por el usuario para facilitar el aprendizaje autónomo.\n"
    "1. Genera una estructura jerárquica con los conceptos centrales y sus definiciones analíticas.\n"
    "2. Diseña un cuestionario de autoevaluación de 5 preguntas clave basadas estrictamente en el texto para validar la comprensión lectora."
)

if boton_procesar:
    if not api_key:
        st.error("Error: Falta la API Key en los Secrets de Streamlit.")
    elif not texto_final:
        st.warning("Por favor, ingresa contenido para analizar.")
    else:
        with st.spinner("Gemini está analizando tu material..."):
            try:
                # LLAMADA ESTÁNDAR COMPATIBLE DE PRODUCCIÓN
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt_completo = f"{system_prompt}\n\nTexto a procesar:\n{texto_final}"
                
                response = model.generate_content(prompt_completo)
                st.session_state['resultado_analisis'] = response.text
            except Exception as e:
                # Muestra el error crudo del servidor para diagnóstico preciso
                st.error(f"Error devuelto por el servidor de Google: {e}")

# 5. DESPLIEGUE DE RESULTADOS
if 'resultado_analisis' in st.session_state:
    st.markdown("---")
    st.markdown("### ✨ Material de Estudio Optimizado")
    st.write(st.session_state['resultado_analisis'])

st.markdown("---")
st.markdown("<p style='text-align: center; color: #9CA3AF; font-size: 0.8rem;'>SyncStudy IA © 2026</p>", unsafe_allow_html=True)