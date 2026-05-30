import streamlit as st
import pdfplumber
from google import genai
from google.genai import types

# 1. CONFIGURACIÓN DE LA PÁGINA Y PALETA DE COLORES (HEADER)
st.set_page_config(
    page_title="SyncStudy IA",
    page_icon="🧠",
    layout="centered"
)

# Estilos CSS personalizados para una paleta limpia y tipografía legible
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

# 2. BARRA LATERAL: CREDENCIALES Y DATOS (SIDEBAR)
st.sidebar.header("Configuración del Entorno")

# Input seguro para la API Key de Google AI Studio
api_key = st.sidebar.text_input("Ingresa tu Gemini API Key:", type="password", help="Obtenla en Google AI Studio")

st.sidebar.markdown("---")
st.sidebar.markdown("**Estudiante:** Magali Heinermann")
st.sidebar.markdown("**Curso:** IA: Prompt Engineering")
st.sidebar.markdown("**Comisión:** 95840")

# 3. SECCIÓN "CÓMO FUNCIONA" (REQUISITO DE LA CONSIGNA)
with st.expander("ℹ️ ¿Cómo funciona tu producto? ¡Lee esto antes de empezar!"):
    st.markdown("""
    ### Características clave:
    * **Síntesis Jerárquica:** Reduce textos densos a conceptos clave ordenados pedagógicamente.
    * **Estudio Activo:** Genera un cuestionario de 5 preguntas automatizadas para medir tu comprensión.
    * **Chat con el Documento:** Resuelve dudas puntuales basándose *únicamente* en el texto provisto.
    
    ### Cómo realizar solicitudes:
    1. Introduce tu **API Key** en la barra lateral izquierda.
    2. Copia y pega tu texto en el cuadro inferior o sube un archivo **PDF** académico.
    3. Haz clic en el botón **"Procesar Material de Estudio"**.
    
    ### ¿Qué esperar como resultado?
    Obtendrás una estructura limpia con el resumen formal, seguido de una sección interactiva de autoevaluación. Además, se habilitará un chat interactivo para que interrogues al documento.
    """)

# 4. COMPONENTES DE ENTRADA DE DATOS (INPUTS)
st.markdown("### 1. Carga tu Material de Estudio")

# Dos vías de entrada: pegado manual o carga de archivo PDF
texto_manual = st.text_area("Copia y pega el texto de tu apunte aquí:", height=150, placeholder="Escribe o pega el contenido...")
archivo_pdf = st.file_uploader("O sube un archivo académico (Formato PDF)", type=["pdf"])

# Variable unificada para consolidar el texto final a procesar
texto_final = ""

if archivo_pdf is not None:
    # Extracción de texto del PDF usando pdfplumber
    with pdfplumber.open(archivo_pdf) as pdf:
        paginas = [pagina.extract_text() for pagina in pdf.pages if pagina.extract_text()]
        texto_final = "\n".join(paginas)
    st.success("¡PDF cargado y procesado exitosamente en memoria!")
elif texto_manual:
    texto_final = texto_manual

# 5. LÓGICA DE PROCESAMIENTO Y BOTÓN DE ACCIÓN
st.markdown("### 2. Ejecutar Análisis Inteligente")
boton_procesar = st.button("🚀 Procesar Material de Estudio")

# Definición estricta del System Prompt diseñado para mitigar alucinaciones
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
        st.error("Por favor, ingresa tu Gemini API Key en la barra lateral para continuar.")
    elif not texto_final:
        st.warning("Debes ingresar texto o subir un archivo PDF para poder procesarlo.")
    else:
        with st.spinner("Gemini está analizando y estructurando tu material pedagógico..."):
            try:
                # Inicialización del cliente oficial de GenAI usando la API Key provista
                client = genai.Client(api_key=api_key)
                
                # Llamada al modelo gemini-1.5-flash optimizado para velocidad y costo nulo en Free Tier
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=texto_final,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.3 # Temperatura baja para mantener respuestas objetivas y precisas
                    )
                )
                
                # Guardar el resultado en el estado de la sesión para mantenerlo visible si el usuario interactúa
                st.session_state['resultado_analisis'] = response.text
                st.session_state['contexto_documento'] = texto_final
                
            except Exception as e:
                st.error(f"Ocurrió un error al conectar con Gemini API: {e}")

# 6. DESPLIEGUE DE RESULTADOS (OUTPUTS)
if 'resultado_analisis' in st.session_state:
    st.markdown("---")
    st.markdown("### ✨ Material de Estudio Optimizado")
    st.write(st.session_state['resultado_analisis'])
    
    # 7. COMPONENTE INTERACTIVO ADICIONAL: CHAT CON EL DOCUMENTO
    st.markdown("---")
    st.markdown("### 💬 Pregúntale dudas específicas a tu documento")
    pregunta_usuario = st.text_input("Haz una pregunta sobre el texto analizado:")
    
    if pregunta_usuario:
        with st.spinner("Buscando en el documento..."):
            try:
                client = genai.Client(api_key=api_key)
                # Concatenamos el texto original como contexto para asegurar que responda sobre el documento
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

# FOOTER (PIE DE PÁGINA)
st.markdown("---")
st.markdown("<p style='text-align: center; color: #9CA3AF; font-size: 0.8rem;'>SyncStudy IA © 2026 - Desarrollado con fines educativos. Las respuestas se generan exclusivamente en base al material provisto por el usuario.</p>", unsafe_allow_html=True)