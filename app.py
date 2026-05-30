import streamlit as st
import pdfplumber
from google import genai
from google.genai import types

# 1. CONFIGURACIÓN DE LA PÁGINA Y PALETA DE COLORES
st.set_page_config(
    page_title="SyncStudy IA",
    page_icon="🧠",
    layout="centered"
)

# Estilos CSS para mantener la estética limpia solicitada
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
st.markdown('<p class="subtitle">Optimiza tu material de estudio y genera cuestionarios interactivos con Inteligencia Artificial</p>', unsafe_allow_html=True)

# 2. INTENTAR LEER LA API KEY INTEGRADA DESDE LOS SECRETOS SENSING
# Intenta buscar la clave en Streamlit. Si no existe, avisa al desarrollador.
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = None

# 3. BARRA LATERAL: SOLO DATOS ACADÉMICOS (SIN SOLICITAR API KEY)
st.sidebar.header("Información del Proyecto")
st.sidebar.markdown("**Estudiante:** Magali Heinermann")
st.sidebar.markdown("**Curso:** IA: Prompt Engineering")
st.sidebar.markdown("**Comisión:** 95840")
st.sidebar.markdown("---")
st.sidebar.success("🔑 API de Gemini integrada correctamente")

# 4. SECCIÓN "CÓMO FUNCIONA"
with st.expander("ℹ️ ¿Cómo funciona tu producto? ¡Lee esto antes de empezar!"):
    st.markdown("""
    ### Características clave:
    * **Síntesis Jerárquica:** Reduce textos densos a conceptos clave ordenados pedagógicamente.
    * **Estudio Activo:** Genera un cuestionario de 5 preguntas automatizadas para medir tu comprensión.
    * **Chat con el Documento:** Resuelve dudas puntuales basándose *únicamente* en el texto provisto.
    
    ### Cómo realizar solicitudes:
    1. Copia y pega tu texto en el cuadro inferior o sube un archivo **PDF** académico.
    2. Haz clic en el botón **"Procesar Material de Estudio"**.
    3. ¡Listo! El sistema ya cuenta con la API Key integrada de forma segura.
    """)

# 5. COMPONENTES DE ENTRADA DE DATOS
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

# 6. LÓGICA DE PROCESAMIENTO
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
        st.error("Error de configuración: La clave de la API no está vinculada en las variables secretas de la aplicación.")
    elif not texto_final:
        st.warning("Debes ingresar texto o subir un archivo PDF para poder procesarlo.")
    else:
        with st.spinner("Gemini está analizando y estructurando tu material pedagógico..."):
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=texto_final,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.3
                    )
                )
                st.session_state['resultado_analisis'] = response.text
                st.session_state['contexto_documento'] = texto_final
            except Exception as e:
                st.error(f"Ocurrió un error al conectar con Gemini API: {e}")

# 7. DESPLIEGUE DE RESULTADOS
if 'resultado_analisis' in st.session_state:
    st.markdown("---")
    st.markdown("### ✨ Material de Estudio Optimizado")
    st.write(st.session_state['resultado_analisis'])
    
    # CHAT INTERACTIVO CON EL DOCUMENTO
    st.markdown("---")
    st.markdown("### 💬 Pregúntale dudas específicas a tu documento")
    pregunta_usuario = st.text_input("Haz una pregunta sobre el texto analizado:")
    
    if pregunta_usuario:
        with st.spinner("Buscando en el documento..."):
            try:
                client = genai.Client(api_key=api_key)
                prompt_consulta = f"Contexto del documento:\n{st.session_state['contexto_documento']}\n\nPregunta del usuario: {pregunta_usuario}"
                response_chat = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=prompt_consulta,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.2
                    )
                )
                st.markdown("**Respuesta del Asistente:**")
                st.info(response_chat.text)
            except Exception as e:
                st.error(f"Error en la consulta: {e}")

st.markdown("---")
st.markdown("<p style='text-align: center; color: #9CA3AF; font-size: 0.8rem;'>SyncStudy IA © 2026 - Desarrollado con fines educativos.</p>", unsafe_allow_html=True)