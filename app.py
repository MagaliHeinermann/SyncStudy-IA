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
st.markdown('<p style="text-align: center; color: #4B5563; text-align: center;">Plataforma de Optimización de Material de Estudio con IA</p>', unsafe_allow_html=True)

# 2. CAPA DE AUTENTICACIÓN (COHERE CLIENT V2)
if "COHERE_API_KEY" in st.secrets:
    api_key = st.secrets["COHERE_API_KEY"]
    co = cohere.ClientV2(api_key=api_key)
else:
    api_key = None
    co = None

# Sidebar informativa de auditoría académica obligatoria
st.sidebar.header("Control de Despliegue")
st.sidebar.markdown("**Estudiante:** Magali Heinermann")
st.sidebar.markdown("**Comisión:** 95840")
st.sidebar.markdown("---")
if api_key:
    st.sidebar.success("🔑 Motor Cohere conectado y activo")
else:
    st.sidebar.warning("⚠️ Falta COHERE_API_KEY en los Secrets")

# 3. DESPLEGABLE INFORMATIVO DE USO
with st.expander("ℹ️ Guía de uso de SyncStudy IA — ¡Leé esto antes de empezar!"):
    st.markdown("""
    ### 📌 Pasos importantes para el correcto funcionamiento:
    1. **Carga de Datos:** Pegá tu texto o subí tu archivo PDF en la sección correspondiente.
    2. **Confirmación de Carga:** Antes de presionar cualquier botón de análisis, **debés esperar a que aparezca el mensaje de éxito en verde**.
    3. **Procesamiento por Temas:** Si tu material es extenso, la app lo fragmentará automáticamente. Al presionar el botón de procesar, la IA leerá esa sección, le asignará un título representativo en base al contenido y pasará al siguiente bloque de forma secuencial.
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

# Tamaño máximo de caracteres por bloque para control de cuota (aprox 35.000 palabras)
TAMANO_CHUNK = 130000

# 5. PIPELINE DE INFERENCIA SEGMENTADA (CORE LAYER)
st.markdown("### 2. Ejecutar Análisis Pedagógico")

# Control de reseteo de estados si cambia el origen del texto o el archivo
if 'texto_previo' not in st.session_state or st.session_state['texto_previo'] != texto_final:
    st.session_state['texto_previo'] = texto_final
    st.session_state['indice_bloque'] = 0
    st.session_state['historial_analisis'] = {}
    if 'bloques_texto' in st.session_state:
        del st.session_state['bloques_texto']

system_prompt = (
    "Actúas como un experto en diseño instruccional y pedagogía avanzada.\n"
    "REQUISITO OBLIGATORIO DE ARQUITECTURA: La primerísima línea de tu respuesta debe ser SIEMPRE un título sintético y representativo "
    "del tema principal que trata el fragmento de texto provisto, envuelto exactamente con el formato: [TITULO: Nombre del Tema]. "
    "No pongas saludos ni introducciones antes de esa etiqueta.\n\n"
    "Luego de esa línea, genera de forma estructurada:\n"
    "1. Una síntesis jerárquica con los conceptos centrales perfectamente definidos de forma analítica.\n"
    "2. Un cuestionario interactivo de autoevaluación compuesto por 5 preguntas clave basadas estrictamente en la lectura de esta sección."
)

# Inicialización de bloques distribuidos
if texto_final and 'bloques_texto' not in st.session_state:
    st.session_state['bloques_texto'] = [texto_final[i:i+TAMANO_CHUNK] for i in range(0, len(texto_final), TAMANO_CHUNK)]

# Lógica y renderizado de la botonera secuencial única
if texto_final and 'bloques_texto' in st.session_state:
    bloques = st.session_state['bloques_texto']
    total_bloques = len(bloques)
    idx_actual = st.session_state['indice_bloque']
    
    if total_bloques > 1:
        st.warning(f"📋 Documento extenso detectado. Fragmentado en {total_bloques} partes.")
        progreso = (idx_actual) / total_bloques
        st.progress(progreso, text=f"Progreso del documento: Parte {idx_actual + 1} de {total_bloques}")

    # Botón dinámico único de procesamiento secuencial
    if idx_actual < total_bloques:
        texto_boton = f"🚀 Procesar y Analizar Parte {idx_actual + 1}"
        if st.button(texto_boton, use_container_width=True):
            if not api_key or not co:
                st.error("Error de Backend: Credenciales de Cohere no detectadas.")
            else:
                texto_a_enviar = bloques[idx_actual]
                with st.spinner(f"Cohere está analizando de forma inteligente la Parte {idx_actual + 1}..."):
                    try:
                        response = co.chat(
                            model="command-r7b-12-2024",
                            messages=[
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": f"Analizá el siguiente bloque de estudio:\n\n{texto_a_enviar}"}
                            ]
                        )
                        
                        if response and response.message and response.message.content:
                            # Guardamos de forma persistente en el historial el bloque resuelto
                            st.session_state['historial_analisis'][idx_actual] = response.message.content[0].text
                            st.session_state['indice_bloque'] += 1
                            st.rerun()
                        else:
                            st.error("La API de Cohere devolvió un cuerpo de texto vacío.")
                    except Exception as e:
                        st.error(f"Falla controlada en el pipeline de la API: {e}")
    else:
        st.success("✅ ¡Felicidades! Has completado el procesamiento y optimización de todo el documento de estudio.")
        if st.button("🔄 Reiniciar análisis desde el inicio"):
            st.session_state['indice_bloque'] = 0
            st.session_state['historial_analisis'] = {}
            st.rerun()

# 6. CAPA DE RENDERIZADO ACUMULATIVO DE RESULTADOS (OUTPUT LAYER)
if 'historial_analisis' in st.session_state and st.session_state['historial_analisis']:
    st.markdown("---")
    st.markdown("### ✨ Material de Estudio Optimizado")
    
    # Renderizamos secuencialmente los bloques procesados
    for index in sorted(st.session_state['historial_analisis'].keys()):
        respuesta_cruda = st.session_state['historial_analisis'][index]
        
        # Lógica de Extracción de Título Dinámico por Backend
        titulo_seccion = f"Parte {index + 1} - Contenido General"
        cuerpo_respuesta = respuesta_cruda
        
        if "[TITULO:" in respuesta_cruda and "]" in respuesta_cruda:
            try:
                inicio = respuesta_cruda.find("[TITULO:") + len("[TITULO:")
                fin = respuesta_cruda.find("]", inicio)
                extracted_title = respuesta_cruda[inicio:fin].strip()
                if extracted_title:
                    titulo_seccion = f"📚 {extracted_title}"
                # Removemos la etiqueta del título del cuerpo para que no se duplique visualmente
                cuerpo_respuesta = respuesta_cruda[fin + 1:].strip()
            except Exception:
                pass
                
        with st.container():
            # Encabezado estilizado con el tema real extraído por la IA
            st.markdown(f"""
                <div style="background-color: #F3F4F6; padding: 10px; border-left: 5px solid #1E3A8A; border-radius: 4px; margin-bottom: 15px; margin-top: 20px;">
                    <h4 style="margin: 0; color: #1E3A8A;">{titulo_seccion}</h4>
                </div>
            """, unsafe_allow_html=True)
            
            st.write(cuerpo_respuesta)
            st.markdown("<hr style='border: 1px dashed #D1D5DB;' />", unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #9CA3AF; font-size: 0
