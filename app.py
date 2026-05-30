import streamlit as st
import pdfplumber
import google.generativeai as genai

# 1. CONFIGURACIÓN DE LA PÁGINA Y PALETA DE COLORES
st.set_page_config(
    page_title="SyncStudy IA",
    page_icon="🧠",
    layout="centered"
)

st.markdown("""
    <style>
    .main-title {
        font-family: 'Arial', sans-serif;
        color: #1E3A8A;
        text-align: center;
        font-weight: 700;
        margin-bottom: 5px;
    }
    .subtitle {
        font-family: 'Arial', sans-serif;
        color: #4B5563;
        text-align: center;
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">🧠 SyncStudy IA</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Optimiza tu material de estudio y genera cuestionarios interactivos con IA</p>', unsafe_allow_html=True)

# 2. VALIDACIÓN DE CREDENCIALES INTEGRADAS (SECRETS)
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
else:
    api_key = None

# Barra lateral informativa requerida por las pautas del proyecto
st.sidebar.header("Información del Proyecto")
st.sidebar.markdown("**Estudiante:** Magali Heinermann")
st.sidebar.markdown("**Curso:** IA: Prompt Engineering")
st.sidebar.markdown("**Comisión:** 95840")
st.sidebar.markdown("---")
if api_key:
    st.sidebar.success("🔑 API de Gemini vinculada correctamente")
else:
    st.sidebar.warning("⚠️ Esperando credenciales...")

# 3. EXPANDER INFORMATIVO "CÓMO FUNCIONA" (REQUISITO OBLIGATORIO)
with st.expander("ℹ️ ¿Cómo funciona tu producto? ¡Lee esto antes de empezar!"):
    st.markdown("""
    ### Características clave:
    * **Síntesis Jerárquica:** Reduce textos densos a conceptos clave ordenados pedagógicamente.
    * **Estudio Activo:** Genera un cuestionario de 5 preguntas automatizadas para medir tu comprensión.
    """)

# 4. COMPONENTES DE ENTRADA DE DATOS (INPUTS)
st.markdown("### 1. Carga tu Material de Estudio")
texto_manual = st.text_area("Copia y pega el texto de tu apunte aquí:", height=150, placeholder="Escribe o pega el contenido...")
archivo_pdf = st.file_uploader("O sube un archivo académico (Formato PDF)", type=["pdf"])

texto_final = ""

if archivo_pdf is not None:
    with pdfplumber.open(archivo_pdf) as pdf:
        paginas = [pagina.extract_text() for pagina in pdf.pages if pagina.extract_text()]
        texto_final = "\n".join(paginas)
    st.success("¡PDF cargado exitosamente en memoria!")
elif texto_manual:
    texto_final = texto_manual

# 5. LÓGICA DE PROCESAMIENTO Y BOTÓN DE ACCIÓN
st.markdown("### 2. Ejecutar Análisis Inteligente")
boton_procesar = st.button("🚀 Procesar Material de Estudio")

system_prompt = """
Eres un experto instruccional y pedagógico avanzado. Tu objetivo es optimizar el material de estudio provisto por el usuario para facilitar el aprendizaje autónomo.

Al recibir el texto o documento:
1. Genera una estructura jerárquica con los conceptos centrales y sus definiciones analíticas.
2. Diseña un cuestionario de autoevaluación de 5 preguntas clave basadas estrictamente en el texto para validar la comprensión lectora.
"""

if boton_procesar:
    if not api_key:
        st.error("Error: Configura 'GEMINI_API_KEY' in el panel de Secrets de Streamlit Cloud.")
    elif not texto_final:
        st.warning("Por favor, ingresa texto o sube un archivo PDF.")
    else:
        with st.spinner("Gemini está analizando tu material de estudio..."):
            # Inicialización clásica limpia con el modelo activo vigente
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Unimos las instrucciones y el texto en un único string plano para evitar fallas posicionales
            prompt_completo = f"{system_prompt}\n\nAnaliza el siguiente texto de estudio:\n{texto_final}"
            
            response = model.generate_content(prompt_completo)
            st.session_state['resultado_analisis'] = response.text

# 6. ENTRADA DE RESULTADOS (OUTPUTS)
if 'resultado_analisis' in st.session_state:
    st.markdown("---")
    st.markdown("### ✨ Material de Estudio Optimizado")
    st.write(st.session_state['resultado_analisis'])

st.markdown("---")
st.markdown("<p style='text-align: center; color: #9CA3AF; font-size: 0.8rem;'>SyncStudy IA © 2026 - Desarrollado con fines educativos.</p>", unsafe_allow_html=True)