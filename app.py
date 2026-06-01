import streamlit as st
import pdfplumber
import requests

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
                # ENDPOINT DEFINITIVO CON NOMBRE ENRUTADO DE MODELO ESTABLE
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                
                headers = {'Content-Type': 'application/json'}
                
                # Payload estructurado de forma nativa para la API REST de Google
                payload = {
                    "contents": [{
                        "parts": [{
                            "text": f"{system_prompt}\n\nTexto de estudio a analizar:\n{texto_final}"
                        }]
                    }]
                }
                
                response = requests.post(url, json=payload, headers=headers)
                response_data = response.json()
                
                if response.status_code == 200:
                    # Extracción del contenido de manera segura
                    if 'candidates' in response_data and response_data['candidates']:
                        text_output = response_data['candidates'][0]['content']['parts'][0]['text']
                        st.session_state['resultado_analisis'] = text_output
                    else:
                        st.error("Google procesó la solicitud pero no devolvió texto. Revisa el formato de entrada.")
                else:
                    # Te muestra en pantalla el error exacto que da Google para saber qué pasa
                    st.error(f"Error de Google (Código {response.status_code}): {response_data}")
                    
            except Exception as e:
                st.error(f"Error de conexión: {e}")

# 6. ENTRADA DE RESULTADOS
if 'resultado_analisis' in st.session_state:
    st.markdown("---")
    st.markdown("### ✨ Material de Estudio Optimizado")
    st.write(st.session_state['resultado_analisis'])

st.markdown("---")
st.markdown("<p style='text-align: center; color: #9CA3AF; font-size: 0.8rem;'>SyncStudy IA © 2026</p>", unsafe_allow_html=True)