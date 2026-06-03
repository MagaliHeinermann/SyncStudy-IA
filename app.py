import streamlit as st
import pdfplumber
import time

from google import genai
from google.genai import types

# =====================================================
# CONFIGURACIÓN GENERAL
# =====================================================

st.set_page_config(
    page_title="SyncStudy IA",
    page_icon="🧠",
    layout="centered"
)

st.markdown(
    """
    <h1 style="text-align:center; color:#1E3A8A;">
        🧠 SyncStudy IA
    </h1>

    <p style="text-align:center; color:#4B5563;">
        Optimización de material de estudio con Inteligencia Artificial
    </p>
    """,
    unsafe_allow_html=True
)

# =====================================================
# API KEY
# =====================================================

api_key = st.secrets.get("GEMINI_API_KEY", None)

# =====================================================
# CACHE DEL CLIENTE
# =====================================================

@st.cache_resource
def get_client():
    return genai.Client(api_key=api_key)

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header("Control de Despliegue")

st.sidebar.markdown("**Estudiante:** Magali Heinermann")
st.sidebar.markdown("**Comisión:** 95840")

st.sidebar.markdown("---")

if api_key:
    st.sidebar.success("🔑 GEMINI_API_KEY detectada")
else:
    st.sidebar.error("❌ GEMINI_API_KEY no encontrada")

# =====================================================
# ENTRADA DE DATOS
# =====================================================

st.markdown("### 1. Carga de Material Académico")

texto_manual = st.text_area(
    "Pega tus apuntes o extractos aquí:",
    height=180
)

archivo_pdf = st.file_uploader(
    "O sube un archivo PDF",
    type=["pdf"]
)

texto_final = ""

# =====================================================
# LECTURA PDF
# =====================================================

if archivo_pdf is not None:

    try:

        with pdfplumber.open(archivo_pdf) as pdf:

            paginas = []

            for page in pdf.pages:

                contenido = page.extract_text()

                if contenido:
                    paginas.append(contenido)

            texto_final = "\n".join(paginas)

        st.success("✅ PDF procesado correctamente.")

    except Exception as e:

        st.error(f"❌ Error al procesar PDF: {e}")

elif texto_manual:

    texto_final = texto_manual

# =====================================================
# INFO TEXTO
# =====================================================

if texto_final:

    st.info(
        f"📄 Caracteres cargados: {len(texto_final):,}"
    )

# =====================================================
# PROMPT DEL SISTEMA
# =====================================================

system_prompt = """
Actúa como un experto en diseño instruccional y pedagogía avanzada.

A partir del texto proporcionado por el usuario debes generar:

1. Una síntesis jerárquica con los conceptos centrales.
2. Explicaciones claras y analíticas.
3. Un cuestionario de autoevaluación con 5 preguntas.
4. Una sección de conceptos clave para memorizar.
5. Consejos de estudio basados en el contenido analizado.

La respuesta debe estar perfectamente organizada mediante títulos y subtítulos.
"""

# =====================================================
# DIVIDIR TEXTO
# =====================================================

def dividir_texto(texto, tamaño=30000):

    return [
        texto[i:i+tamaño]
        for i in range(0, len(texto), tamaño)
    ]

# =====================================================
# BOTÓN
# =====================================================

st.markdown("### 2. Ejecutar Análisis Cognitivo")

boton_procesar = st.button(
    "🚀 Procesar Material de Estudio",
    use_container_width=True
)

# =====================================================
# PROCESAMIENTO IA
# =====================================================

if boton_procesar:

    if not api_key:

        st.error(
            "❌ No se encontró GEMINI_API_KEY."
        )

    elif not texto_final.strip():

        st.warning(
            "⚠️ Debes ingresar texto o subir un PDF."
        )

    else:

        try:

            with st.spinner(
                "🧠 Analizando material..."
            ):

                client = get_client()

                # =====================================
                # DIVIDIR EN PARTES
                # =====================================

                partes = dividir_texto(
                    texto_final,
                    tamaño=30000
                )

                respuestas = []

                progreso = st.progress(0)

                for i, parte in enumerate(partes):

                    response = client.models.generate_content(

                        # =================================
                        # MODELO GEMINI
                        # =================================

                        model="gemini-1.5-flash-8b",

                        contents=parte,

                        config=types.GenerateContentConfig(
                            system_instruction=system_prompt,
                            temperature=0.3,
                        )
                    )

                    respuestas.append(
                        response.text
                    )

                    progreso.progress(
                        (i + 1) / len(partes)
                    )

                    # =================================
                    # EVITA MUCHAS REQUESTS
                    # =================================

                    time.sleep(2)

                resultado_final = "\n\n".join(
                    respuestas
                )

                st.session_state[
                    "data_output"
                ] = resultado_final

                st.success(
                    "✅ Material procesado correctamente."
                )

        except Exception as e:

            st.error(
                f"""
❌ Error al comunicarse con Gemini:

{str(e)}
"""
            )

# =====================================================
# SALIDA
# =====================================================

if "data_output" in st.session_state:

    st.markdown("---")

    st.markdown(
        "## ✨ Material de Estudio Optimizado"
    )

    st.markdown(
        st.session_state["data_output"]
    )

# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.markdown(
    """
    <p style='text-align:center;
              color:#9CA3AF;
              font-size:0.8rem;'>

        SyncStudy IA © 2026

    </p>
    """,
    unsafe_allow_html=True
)
