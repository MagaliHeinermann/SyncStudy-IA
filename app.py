import streamlit as st
import pdfplumber
import requests

# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS
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
else:
    api_key = None

# Barra lateral informativa requerida por la consigna
st.sidebar.header("Información del Proyecto")
st.sidebar.markdown("**Estudiante:** Magali Heinermann")
st.sidebar.markdown("**Curso:** IA: Prompt Engineering")
st.sidebar.markdown("**Comisión:** 95840")
st.sidebar.markdown("---")
if api_key:
    st.sidebar.success("🔑 API de Gemini vinculada correctamente")
else:
    st.sidebar.warning("⚠️ Esperando configuración...")

# 3. EXPANDER INFORMATIVO "CÓMO FUNCIONA"
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
Mantén un tono académico, preciso y de alta claridad pedagógica.
"""

if boton_procesar:
    if not api_key:
        st.error("Error: Configura 'GEMINI_API_KEY' en el panel de Secrets de Streamlit Cloud.")
    elif not texto_final:
        st.warning("Por favor, ingresa texto o sube un archivo PDF.")
    else:
        with st.spinner("Gemini está analizando tu material de estudio..."):
            try:
                # CAMBIO CLAVE: Usamos la versión v1 estable de producción
                url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
                
                headers = {'Content-Type': 'application/json'}
                
                payload = {
                    "contents": [{
                        "parts": [{
                            "text": f"{system_prompt}\n\nTexto de estudio a analizar:\n{texto_final}"
                        }]
                    }],
                    "generationConfig": {
                        "temperature": 0.3
                    }
                }
                
                response = requests.post(url, json=payload, headers=headers)
                response_data = response.json()
                
                if response.status_code == 200:
                    text_output = response_data['candidates'][0]['content']['parts'][0]['text']
                    st.session_state['resultado_analisis'] = text_output
                else:
                    st.error(f"Error del servidor de Google ({response.status_code}): {response_data.get('error', {}).get('message', 'Error de enrutamiento')}")
                    
            except Exception as e:
                st.error(f"Error inesperado en la solicitud: {e}")

# 6. ENTRADA DE RESULTADOS (OUTPUTS)
if 'resultado_analisis' in st.session_state:
    st.markdown("---")
    st.markdown("### ✨ Material de Estudio Optimizado")
    st.write(st.session_state['resultado_analisis'])

st.markdown("---")
st.markdown("<p style='text-align: center; color: #9CA3AF; font-size: 0.8rem;'>SyncStudy IA © 2026 - Desarrollado con fines educativos.</p>", unsafe_allow_html=True)