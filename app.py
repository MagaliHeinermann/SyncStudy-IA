from http import client

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

# Barra lateral informativa
st.sidebar.header("Información del Proyecto")
st.sidebar.markdown("**Estudiante:** Magali Heinermann")
st.sidebar.markdown("**Curso:** IA: Prompt Engineering")
st.sidebar.markdown("**Comisión:** 95840")
st.sidebar.markdown("---")
if api_key:
    st.sidebar.success("🔑 API de Gemini vinculada de forma segura")
else:
    st.sidebar.warning("⚠️ Esperando configuración de API Key")

# 3. EXPANDER EXPLICATIVO
with st.expander("ℹ️ ¿Cómo funciona tu producto? ¡Lee esto antes de empezar!"):
    st.markdown("""
    ### Características clave:
    * **Síntesis Jerárquica:** Reduce textos densos a conceptos clave ordenados pedagógicamente.
    * **Estudio Activo:** Genera un cuestionario de 5 preguntas automatizadas para medir tu comprensión.
    * **Chat con el Documento:** Resuelve dudas puntuales basándose *únicamente* en el texto provisto.
    """)

# 4. ENTRADAS DE DATOS
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

# 5. PROCESAMIENTO CON LA API DE GEMINI
st.markdown("### 2. Ejecutar Análisis Inteligente")
boton_procesar = st.button("🚀 Procesar Material de Estudio")

system_prompt = """
Eres un experto instruccional y pedagógico avanzado. Tu objetivo es optimizar el material de estudio provisto por el usuario para facilitar el aprendizaje autónomo.

Al recibir el texto o documento:
1. Genera una estructura jerárquica con los conceptos centrales y sus definiciones analíticas.
2. Diseña un cuestionario de autoevaluación de 5 preguntas clave basadas estrictamente en el texto para validar la comprensión lectora.
3. Responde a las dudas del usuario limitándote exclusivamente al contexto provisto. Si una respuesta no se encuentra en el material, indícalo de forma clara y no inventes información.

Mantén un tono académico, preciso y de alta claridad pedagógica.
"""

if boton_procesar:
    if not api_key:
        st.error("Error: Configura 'GEMINI_API_KEY' en el panel de Secrets de Streamlit Cloud.")
    elif not texto_final:
        st.warning("Por favor, ingresa texto o sube un archivo PDF.")
    else:
        with st.spinner("Gemini está analizando tu material..."):
            try:
                # LLAMADA LIMPIA CORREGIDA UTILIZANDO LA NUEVA SDK DE GOOGLE
                response = client.models.generate_content(
                     response = client.models.generate_content(
                        model='gemini-1.5-pro',  # Cambiamos flash por pro para saltar el error de ruta 404
                        contents=texto_final,
                        config=types.GenerateContentConfig(
                            system_instruction=system_prompt,
                            temperature=0.3
                            )
                        )
                )
                st.session_state['resultado_analisis'] = response.text
                st.session_state['contexto_documento'] = texto_final
            except Exception as e:
                st.error(f"Error de conexión con la API de Gemini: {e}")

# 6. MUESTRA DE RESULTADOS Y CHAT COMPLEMENTARIO
if 'resultado_analisis' in st.session_state:
    st.markdown("---")
    st.markdown("### ✨ Material de Estudio Optimizado")
    st.write(st.session_state['resultado_analisis'])
    
    st.markdown("---")
    st.markdown("### 💬 Chat con el Documento")
    pregunta_usuario = st.text_input("Haz una pregunta específica sobre el texto:")
    
    if pregunta_usuario:
        with st.spinner("Buscando respuestas..."):
            try:
                client = genai.Client(api_key=api_key)
                prompt_consulta = f"Contexto del documento:\n{st.session_state['contexto_documento']}\n\nPregunta: {pregunta_usuario}"
                response_chat = client.models.generate_content(
                     model='gemini-1.5-pro',  # Cambiamos aquí también a pro
                     contents=prompt_consulta,
                     config=types.GenerateContentConfig(
                          system_instruction=system_prompt,
                         temperature=0.2
                          )
                        )
                st.info(response_chat.text)
            except Exception as e:
                st.error(f"Error en el chat: {e}")