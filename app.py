import streamlit as st
import pdfplumber
import cohere

# 1. CONFIGURACIÓN DE LA INTERFAZ Y ESTILOS NATIVOS
st.set_page_config(
    page_title="SyncStudy IA",
    page_icon="🧠",
    layout="centered"
)

st.markdown('<h1 style="text-align: center; color: #1E3A8A;">🧠 SyncStudy IA</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #4B5563; text-align: center;">Plataforma de Optimización de Material de Estudio con IA</p>', unsafe_allow_html=True)

# 2. CAPA DE AUTENTICACIÓN
if "COHERE_API_KEY" in st.secrets:
    api_key = st.secrets["COHERE_API_KEY"]
    co = cohere.ClientV2(api_key=api_key)
else:
    api_key = None
    co = None

# Sidebar informativa obligatoria para la entrega
st.sidebar.header("Control de Despliegue")
st.sidebar.markdown("**Estudiante:** Magali Heinermann")
st.sidebar.markdown("**Comisión:** 95840")
st.sidebar.markdown("---")
if api_key:
    st.sidebar.success("🔑 Motor Cohere conectado y activo")
else:
    st.sidebar.warning("⚠️ Falta COHERE_API_KEY en los Secrets")

# 3. DESPLEGABLE DE INFORMACIÓN DE USO (REQUISITO REQUERIDO)
with st.expander("ℹ️ Guía de uso de SyncStudy IA — ¡Leé esto antes de empezar!"):
    st.markdown("""
    ### 📌 Pasos importantes para el correcto funcionamiento:
    1. **Carga de Datos:** Pegá tu texto o subí tu archivo PDF en la sección correspondiente.
    2. **Confirmación de Carga (Crucial):** Antes de presionar cualquier botón de análisis, **debés esperar a que aparezca el mensaje de éxito en verde** (`¡PDF cargado exitosamente!` o el indicador de texto listo). Si presionás el botón antes de esto, el sistema procesará un campo vacío.
    3. **Procesamiento de Archivos Largos:** Si tu material es extenso, la app lo fragmentará automáticamente en bloques óptimos para la API. Podrás analizar y leer las siguientes partes de manera secuencial presionando el botón de navegación que aparecerá abajo.
    4. **Tiempos de Espera:** Las solicitudes pueden demorar unos segundos dependiendo del tráfico de la API. No recargues la página mientras veas el indicador de carga (*Spinner*).
    """)

# 4. CAPA DE ENTRADA DE DATOS (INPUT LAYER)
st.markdown("### 1. Carga de Material Académico")
texto_manual = st.text_area("Pega tus apuntes o extractos de texto aquí:", height=150, placeholder="Escribe o pega el contenido aquí...")
archivo_pdf = st.file_uploader("O sube tu material en formato académico (PDF)", type=["pdf"])

texto_final = ""
if archivo_pdf is not None:
    with pdfplumber.open(archivo_pdf) as pdf:
        texto_final = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    st.success("¡PDF cargado exitosamente en memoria! El material está listo para procesarse.")
elif texto_manual:
    texto_final = texto_manual
    st.info("Texto insertado correctamente y listo para procesarse.")

# Tamaño máximo de caracteres por bloque para no saturar la ventana de tokens de la API (aprox 40.000 palabras)
TAMANO_CHUNK = 150000

# 5. PIPELINE DE INFERENCIA SEGMENTADA (CORE PAGINATION LAYER)
st.markdown("### 2. Ejecutar Análisis Pedagógico")

# Si el usuario cambia el texto o archivo de entrada, reseteamos el paginado de la sesión
if 'texto_previo' not in st.session_state or st.session_state['texto_previo'] != texto_final:
    st.session_state['texto_previo'] = texto_final
    st.session_state['indice_bloque'] = 0
    if 'bloques_texto' in st.session_state:
        del st.session_state['bloques_texto']
    if 'historial_analisis' in st.session_state:
        del st.session_state['historial_analisis']

system_prompt = (
    "Actúas como un experto en diseño instruccional y pedagogía avanzada.\n"
    "A partir del fragmento de texto de estudio provisto por el usuario, debes generar de forma estructurada:\n"
    "1. Una síntesis jerárquica con los conceptos centrales de esta parte perfectamente definidos de forma analítica.\n"
    "2. Un cuestionario interactivo de autoevaluación compuesto por 5 preguntas clave basadas estrictamente en la lectura de esta sección."
)

# Inicializamos las variables de control si hay texto válido
if texto_final and 'bloques_texto' not in st.session_state:
    # Dividimos el texto en bloques respetando el límite de tamaño
    st.session_state['bloques_texto'] = [texto_final[i:i+TAMANO_CHUNK] for i in range(0, len(texto_final), TAMANO_CHUNK)]
    st.session_state['historial_analisis'] = {}

# Mostrar información de bloques detectados si el archivo es grande
if texto_final and 'bloques_texto' in st.session_state:
    total_bloques = len(st.session_state['bloques_texto'])
    bloque_actual = st.session_state['indice_bloque'] + 1
    if total_bloques > 1:
        st.warning(f"📋 Documento extenso detectado. Se fragmentó en {total_bloques} partes. Estás procesando la parte {bloque_actual} de {total_bloques}.")

col1, col2 = st.columns(2)

with col1:
    boton_procesar = st.button("🚀 Analizar Bloque Actual")

with col2:
    # Desplegar botón para pasar a la siguiente parte si existen bloques restantes
    if texto_final and 'bloques_texto' in st.session_state and len(st.session_state['bloques_texto']) > 1:
        if st.session_state['indice_bloque'] < len(st.session_state['bloques_texto']) - 1:
            if st.button("⏭️ Cargar Siguiente Parte"):
                st.session_state['indice_bloque'] += 1
                st.rerun()

# Lógica de llamada a la API
if boton_procesar:
    if not api_key or not co:
        st.error("Error de Backend: No se detectaron credenciales válidas de Cohere en los Secrets.")
    elif not texto_final:
        st.warning("Validación fallida: Por favor, asegurate de esperar la confirmación de carga e ingresar contenido válido.")
    else:
        idx = st.session_state['indice_bloque']
        texto_a
