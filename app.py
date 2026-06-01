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

# Barra lateral informativa
st.sidebar.header("Información del Proyecto")
st.sidebar.markdown("**Estudiante:** Magali Heinermann")
st.sidebar.markdown("**Comisión:** 95840")

# 3. COMPONENTES DE ENTRADA
texto_manual = st.text_area("Copia tu texto de estudio aquí:", height=150)
archivo_pdf = st.file_uploader("O sube un archivo PDF", type=["pdf"])

texto_final = ""
if archivo_pdf is not None:
    with pdfplumber.open(archivo_pdf) as pdf:
        texto_final = "\n".join([pagina.extract_text() for pagina in pdf.pages if pagina.extract_text()])
    st.success("¡PDF cargado exitosamente!")
elif texto_manual:
    texto_final = texto_manual

# 4. BOTÓN DE ACCIÓN
boton_procesar = st.button("🚀 Procesar Material de Estudio")

system_prompt = "Eres un experto instruccional. Genera una estructura jerárquica con los conceptos centrales y diseña un cuestionario de autoevaluación de 5 preguntas clave basadas estrictamente en el texto."

if boton_procesar:
    if not api_key:
        st.error("Error: Falta la API Key en los Secrets de Streamlit.")
    elif not texto_final:
        st.warning("Por favor, ingresa contenido para analizar.")
    else:
        with st.spinner("Gemini está analizando tu material..."):
            try:
                # LLAMADA ESTÁNDAR COMPATIBLE
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt_completo = f"{system_prompt}\n\nTexto:\n{texto_final}"
                
                response = model.generate_content(prompt_completo)
                st.session_state['resultado_analisis'] = response.text
            except Exception as e:
                st.error(f"Error en la llamada a la API: {e}")

# 5. RESULTADOS
if 'resultado_analisis' in st.session_state:
    st.markdown("---")
    st.markdown("### ✨ Material de Estudio Optimizado")
    st.write(st.session_state['resultado_analisis'])