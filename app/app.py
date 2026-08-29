import sys
from pathlib import Path

import pandas as pd
import streamlit as st


# ---------------------------------------------------------
# Configuración del proyecto
# ---------------------------------------------------------

#Añadir raíz del proyecto al path para poder importar desde src
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.detector import load_models, predict_events
from src.simulator import load_simulation_sample


# ---------------------------------------------------------
# Configuración de la interfaz
# ---------------------------------------------------------

st.set_page_config(
    page_title="CyberSOC-AI",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ CyberSOC-AI")
st.caption("Sistema inteligente de apoyo a la detección de amenazas de red")

st.divider()


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

st.subheader("Centro de operaciones de seguridad")

st.write(
    "CyberSOC-AI analiza tráfico de red mediante dos modelos de Inteligencia "
    "Artificial: **Random Forest**, como detector principal de ataques conocidos, "
    "y **Autoencoder**, como detector complementario de anomalías."
)


# ---------------------------------------------------------
# Simulación
# ---------------------------------------------------------

if st.button(
    "▶ Ejecutar simulación",
    type="primary"
):

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


        st.success("Análisis completado")

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
            use_container_width=True,
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

        st.markdown("#### Interpretación")

        #Explicación del resultado antes IA generativa
        if selected_row["alert_level"] == 3:
            st.warning(
                "Los dos modelos coinciden en identificar comportamiento "
                "sospechoso. El evento debe priorizarse para su revisión."
            )

        elif selected_row["alert_level"] == 2:
            st.warning(
                "El Random Forest identifica un patrón compatible con tráfico "
                "malicioso, aunque el Autoencoder no supera su umbral de anomalía."
            )

        elif selected_row["alert_level"] == 1:
            st.warning(
                "El Autoencoder detecta un comportamiento anómalo que no coincide "
                "con los patrones de ataque conocidos por el Random Forest."
            )

        st.markdown("#### Recomendación")

        # Recomendación básica para el analista según la severidad detectada
        if selected_row["alert_level"] == 3:
            st.error(
                "Priorizar la investigación del evento. Revisar el tráfico asociado, "
                "comprobar posibles fuentes maliciosas y valorar medidas inmediatas "
                "de contención si se confirma la amenaza."
            )

        elif selected_row["alert_level"] == 2:
            st.info(
                "Revisar el evento y contrastarlo con otras evidencias disponibles. "
                "El modelo supervisado identifica un patrón de ataque conocido, "
                "por lo que conviene analizar su origen y destino."
            )

        elif selected_row["alert_level"] == 1:
            st.info(
                "Investigar el comportamiento anómalo y comprobar si corresponde "
                "a una actividad legítima no observada durante el entrenamiento "
                "o a una posible amenaza desconocida."
            )

        # -----------------------------------------------------
        # Información del sistema
        # -----------------------------------------------------

        with st.expander("¿Cómo se interpreta el análisis?"):

            st.markdown(
                """
                **Normal**  
                Ninguno de los modelos identifica comportamiento sospechoso.

                **Medio**  
                El Autoencoder detecta una anomalía, aunque el Random Forest
                no identifica un ataque conocido.

                **Alto**  
                El Random Forest identifica un patrón de tráfico malicioso,
                aunque el Autoencoder no lo considera anómalo.

                **Crítico**  
                Random Forest y Autoencoder coinciden en identificar
                comportamiento sospechoso.

                El Autoencoder utiliza un umbral de error de reconstrucción de
                **0.5459**. Los valores superiores a este umbral se consideran
                anómalos.
                """
            )