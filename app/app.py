import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# ---------------------------------------------------------
# Configuración de la interfaz
# ---------------------------------------------------------

st.set_page_config(
    page_title="CyberSOC-AI",
    page_icon="🛡️",
    layout="wide"
)


# ---------------------------------------------------------
# Configuración del proyecto
# ---------------------------------------------------------

#Añadir raíz del proyecto al path para poder importar desde src
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

#Cargar los estilos
CSS_FILE = BASE_DIR / "app" / "style.css"

with open(CSS_FILE, encoding="utf-8") as css_file:
    st.markdown(
        f"<style>{css_file.read()}</style>",
        unsafe_allow_html=True
    )


from src.detector import load_models, predict_events
from src.simulator import load_simulation_sample
from src.generative import generate_soc_analysis




# ---------------------------------------------------------
# Cabecera principal
# ---------------------------------------------------------

st.markdown(
    """
<div class="cyber-hero">
    <div class="cyber-shield">🛡️</div>
    <div class="cyber-title">CyberSOC<span>-AI</span></div>
    <p class="cyber-subtitle">
        Inteligencia artificial aplicada a la detección
        y análisis de amenazas de red
    </p>
    <div class="cyber-tech">
        <span>Random Forest</span>
        <span>Autoencoder</span>
        <span>Detección de anomalías</span>
        <span>IA generativa local</span>
    </div>
</div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# Carga de modelos
# ---------------------------------------------------------

# Streamlit mantiene los modelos en memoria para no cargarlos
# de nuevo cada vez que se actualiza la pantalla.
@st.cache_resource
def get_models():
    return load_models()


models = get_models()


# ---------------------------------------------------------
# Presentación
# ---------------------------------------------------------

st.markdown(
    """
<div class="soc-intro">
    <div class="soc-intro-title">Centro de operaciones de seguridad</div>
    <div class="soc-intro-text">
        CyberSOC-AI combina aprendizaje supervisado y Deep Learning
        para identificar patrones asociados a ataques conocidos
        y detectar comportamientos anómalos en el tráfico de red.
    </div>
</div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# Simulación
# ---------------------------------------------------------

# Centrar el botón principal
button_left, button_center, button_right = st.columns([1, 1, 1])

with button_center:
    run_simulation = st.button(
        "▶ Analizar tráfico",
        type="primary",
        width="stretch"
    )

if run_simulation:

    with st.spinner("Analizando tráfico de red..."):

        #Generar tráfico de demostración: 10 registros benignos + 10 ataques
        events = load_simulation_sample(
            benign_count=10,
            attack_count=10
        )

        #Ejecutar los dos modelos de detección
        predictions = predict_events(
            events,
            models
        )

        #Combinar resultados con la información de la simulación
        results = predictions.copy()
        results.insert(
            0,
            "tipo_real",
            events["Label"].values
        )
        results.insert(
            1,
            "es_ataque_real",
            events["is_attack"].values
        )
        #Guardar los resultados para mantenerlos al interactuar con el dashboard
        st.session_state["results"] = results


#Mostrar el dashboard si ya existe una simulación ejecutada
if "results" in st.session_state:
    results = st.session_state["results"]

    # -----------------------------------------------------
    # Indicadores principales
    # -----------------------------------------------------

    total_events = len(results)

    detected_alerts = (
        results["alert_level"] > 0
    ).sum()

    critical_alerts = (
        results["alert_level"] == 3
    ).sum()

    normal_events = (
        results["alert_level"] == 0
    ).sum()



    st.subheader("Resumen de actividad")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Eventos analizados",
        total_events
    )

    col2.metric(
        "Alertas detectadas",
        detected_alerts
    )

    col3.metric(
        "Críticas",
        critical_alerts
    )

    col4.metric(
        "Sin alerta",
        normal_events
    )

    # -----------------------------------------------------
    # Leyenda de severidad
    # -----------------------------------------------------

    st.markdown(
        """<div class="severity-legend">
<div class="severity-legend-title">NIVELES DE SEVERIDAD</div>
<div class="severity-items">
<span class="severity normal">Normal</span>
<span class="severity medium">Medio</span>
<span class="severity high">Alto</span>
<span class="severity critical">Crítico</span>
</div>
<div class="severity-note">
El Autoencoder considera anómalo un evento cuando el error de reconstrucción supera el umbral 0.5459.
</div>
</div>""",
        unsafe_allow_html=True
    )


    # -----------------------------------------------------
    # Preparar resultados para el analista
    # -----------------------------------------------------

    display_results = results.copy()

    #Convertir los valores técnicos 0/1 en textos comprensibles
    display_results["Random Forest"] = display_results[
        "random_forest"
    ].map({
        0: "Normal",
        1: "Ataque"
    })

    display_results["Autoencoder"] = display_results[
        "autoencoder"
    ].map({
        0: "Normal",
        1: "Anomalía"
    })

    #Traducir el nivel numérico a una severidad comprensible
    display_results["Estado"] = display_results[
        "alert_level"
    ].map({
        0: "Normal",
        1: "Medio",
        2: "Alto",
        3: "Crítico"
    })

    #Redondear el error para facilitar su lectura
    display_results["Error de reconstrucción"] = display_results[
        "reconstruction_error"
    ].round(4)


    # -----------------------------------------------------
    # Tabla de eventos
    # -----------------------------------------------------

    st.subheader("Eventos analizados")

    st.dataframe(
        display_results[
            [
                "tipo_real",
                "Random Forest",
                "Autoencoder",
                "Error de reconstrucción",
                "Estado"
            ]
        ].rename(
            columns={
                "tipo_real": "Tipo de tráfico (demo)"
            }
        ),
        width="stretch",
        hide_index=True
    )

    # -----------------------------------------------------
    # Detalle de alertas
    # -----------------------------------------------------

    st.subheader("Detalle de alerta")

    #Trabajamos solo con los eventos que han generado nivel de alerta
    alert_rows = display_results[
        display_results["alert_level"] > 0
    ].copy()

    if alert_rows.empty:
        st.info("No se han detectado alertas en esta simulación.")

    else:
        #El selector muestra sólo la información generada por el sistema
        #La etiqueta real del dataset se enseñará aparte como dato de validación
        alert_rows["selector"] = alert_rows.apply(
            lambda row: (
                f"Evento {row.name + 1} - "
                f"Riesgo {row['Estado']}"
            ),
            axis=1
        )

        selected_alert = st.selectbox(
            "Selecciona una alerta para analizarla",
            alert_rows["selector"].tolist()
        )

        #Recuperar la fila seleccionada
        selected_row = alert_rows[
            alert_rows["selector"] == selected_alert
        ].iloc[0]

        col_a, col_b, col_c, col_d = st.columns(4)

        col_a.metric(
            "Severidad",
            selected_row["Estado"]
        )

        col_b.metric(
            "Random Forest",
            selected_row["Random Forest"]
        )

        col_c.metric(
            "Autoencoder",
            selected_row["Autoencoder"]
        )

        col_d.metric(
            "Error reconstrucción",
            f"{selected_row['Error de reconstrucción']:.4f}"
        )

        #En modo demo conocemos la etiqueta real de CIC-IDS2017
        #Se muestra solo para comparar la detección con la realidad
        st.caption(
            f"Validación de la simulación — Etiqueta real CIC-IDS2017: "
            f"**{selected_row['tipo_real']}**"
        )

        # -----------------------------------------------------
        # Interpretación y recomendación
        # -----------------------------------------------------

        if selected_row["alert_level"] == 3:
            interpretation = (
                "CyberSOC-AI ha detectado indicios compatibles con actividad maliciosa "
                "junto con un comportamiento anómalo significativo. "
                "El evento presenta un nivel de riesgo crítico y debe priorizarse."
            )

            recommendation = (
                "Priorizar la investigación del evento, revisar las evidencias disponibles "
                "y valorar medidas de contención si se confirma la amenaza."
            )

            recommendation_class = "critical"

        elif selected_row["alert_level"] == 2:
            interpretation = (
                "CyberSOC-AI ha detectado indicios compatibles con actividad maliciosa. "
                "El evento presenta un nivel de riesgo alto y requiere revisión."
            )

            recommendation = (
                "Revisar el evento y contrastarlo con otras evidencias de seguridad "
                "antes de determinar si se trata de una amenaza real."
            )

            recommendation_class = "high"

        else:
            interpretation = (
                "CyberSOC-AI ha detectado un comportamiento anómalo que no coincide "
                "claramente con patrones de ataque conocidos. "
                "El evento presenta un nivel de riesgo medio."
            )

            recommendation = (
                "Investigar el comportamiento detectado y contrastarlo con otras fuentes "
                "de seguridad para determinar si corresponde a actividad legítima "
                "o a una posible amenaza."
            )

            recommendation_class = "medium"

        st.markdown(
            f"""
<div class="soc-analysis-panel interpretation-panel">
    <div class="soc-panel-header">
        <span class="soc-panel-label">INTERPRETACIÓN DEL SISTEMA</span>
    </div>
    <div class="soc-panel-text">
        {interpretation}
    </div>
</div>

<div class="soc-analysis-panel recommendation-panel {recommendation_class}">
    <div class="soc-panel-header">
        <span class="soc-panel-label">ACCIÓN RECOMENDADA</span>
    </div>
    <div class="soc-panel-text">
        {recommendation}
    </div>
</div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("#### Análisis con IA generativa")

        if st.button("Generar análisis con IA", key="generate_ai_analysis"):
            with st.spinner("Generando análisis con IA..."):
                ai_analysis = generate_soc_analysis(
                    selected_row["Estado"],
                    selected_row["Random Forest"],
                    selected_row["Autoencoder"],
                    selected_row["Error de reconstrucción"],
                    models["threshold"],
                )

            if ai_analysis:
                st.session_state["ai_analysis"] = ai_analysis
                st.session_state["ai_analysis_alert"] = selected_alert
            else:
                st.warning(
                    "No se pudo generar el análisis con IA. "
                    "Comprueba que Ollama esté disponible."
                )

        if (
            "ai_analysis" in st.session_state
            and st.session_state.get("ai_analysis_alert") == selected_alert
        ):
            st.markdown(st.session_state["ai_analysis"])

    