import streamlit as st
import pdfplumber
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
# AUTENTICACIÓN
# =====================================================

api_key = st.secrets.get("GEMINI_API_KEY", None)

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

# Lectura de PDF
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
        st.error(f"Error al procesar PDF: {e}")

elif texto_manual:
    texto_final = texto_manual

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
# BOTÓN DE PROCESAMIENTO
# =====================================================

st.markdown("### 2. Ejecutar Análisis Cognitivo")

boton_procesar = st.button(
    "🚀 Procesar Material de Estudio",
    use_container_width=True
)

# =====================================================
# INFERENCIA IA
# =====================================================

if boton_procesar:

    if not api_key:
        st.error(
            "No se encontró GEMINI_API_KEY en los Secrets de Streamlit."
        )

    elif not texto_final.strip():
        st.warning(
            "Debes ingresar texto o subir un PDF antes de procesar."
        )

    else:
        try:
            with st.spinner("🧠 Analizando material de estudio..."):

                client = genai.Client(
                    api_key=api_key
                )

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=texto_final,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=0.3,
                    )
                )

                st.session_state["data_output"] = response.text

        except Exception as e:
            st.error(
                f"Error al comunicarse con Gemini:\n\n{str(e)}"
            )

# =====================================================
# SALIDA
# =====================================================

if "data_output" in st.session_state:

    st.markdown("---")
    st.markdown("## ✨ Material de Estudio Optimizado")

    st.markdown(st.session_state["data_output"])

# =====================================================
# DEPURACIÓN OPCIONAL
# =====================================================

if api_key:
    with st.sidebar.expander("🔍 Diagnóstico de Gemini"):

        try:
            client = genai.Client(api_key=api_key)

            modelos = []

            for model in client.models.list():
                modelos.append(model.name)

            st.success(f"{len(modelos)} modelos detectados")

            for modelo in modelos[:20]:
                st.text(modelo)

        except Exception as e:
            st.error(f"No fue posible listar modelos: {e}")

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
