import streamlit as st
import pdfplumber
import cohere

# 1. CONFIGURACIÓN DE LA INTERFAZ VISUAL
st.set_page_config(
    page_title="SyncStudy IA",
    page_icon="🧠",
    layout="centered"
)

st.markdown('<h1 style="text-align: center; color: #1E3A8A;">🧠 SyncStudy IA</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #4B5563; text-align: center;">Optimización de material de estudio con Inteligencia Artificial</p>', unsafe_allow_html=True)

# 2. CAPA DE AUTENTICACIÓN (COHERE CLIENT V2)
if "COHERE_API_KEY" in st.secrets:
    api_key = st.secrets["COHERE_API_KEY"]
    co = cohere.ClientV2(api_key=api_key)
else:
    api_key = None
    co = None

# Sidebar obligatoria para auditoría académica
st.sidebar.header("Control de Despliegue")
st.sidebar.markdown("**Estudiante:** Magali Heinermann")
st.sidebar.markdown("**Comisión:** 95840")
st.sidebar.markdown("---")
if api_key:
    st.sidebar.success("🔑 Motor Cohere conectado y activo")
else:
    st.sidebar.warning("⚠️ Falta COHERE_API_KEY en los Secrets")

# 3. CAPA DE ENTRADA DE DATOS (INPUT LAYER)
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
        st.error("Error de Backend: No se detectaron credenciales válidas en st.secrets.")
    elif not texto_final:
        st.warning("Validación fallida: El campo de entrada de datos no puede estar vacío.")
    else:
        with st.spinner("Cohere está procesando tu material de estudio..."):
            try:
                # LLAMADA AL MODELO VIGENTE DE PRODUCCIÓN
                response = co.chat(
                    model="command-r7b-12-2024",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Por favor optimiza el siguiente material de estudio:\n\n{texto_final}"}
                    ]
                )
                
                # Extracción segura de la estructura V2
                if response and response.message and response.message.content:
                    st.session_state['data_output'] = response.message.content[0].text
                else:
                    st.error("El servidor procesó la solicitud pero devolvió un cuerpo vacío.")
                    
            except Exception as e:
                st.error(f"Falla en el pipeline de ejecución: {e}")

# 5. CAPA DE SALIDA (OUTPUT LAYER)
if 'data_output' in st.session_state:
    st.markdown("---")
    st.markdown("### ✨ Material de Estudio Optimizado")
    st.write(st.session_state['data_output'])

st.markdown("---")
st.markdown("<p style='text-align: center; color: #9CA3AF; font-size: 0.8rem;'>SyncStudy IA © 2026</p>", unsafe_allow_html=True)
