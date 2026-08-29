import sys
from pathlib import Path

import streamlit as st


#añadir la raiz del proyecto al path para importar desde src
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.detector import load_models, predict_events
from src.simulator import load_simulation_sample


#Configuración
st.set_page_config(
    page_title="CyberSOC-AI",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ CyberSOC-AI")
st.subheader("Detección inteligente de amenazas de red")


#Cargar los modelos una vez mientras la app esté activa
@st.cache_resource
def get_models():
    return load_models()


models = get_models()


st.write(
    "Esta versión inicial simula tráfico de red utilizando registros reales "
    "del dataset CIC-IDS2017 y analiza cada evento con Random Forest "
    "y Autoencoder."
)


#ejecutar la simulación desde un botón
if st.button("Ejecutar simulación"):

    with st.spinner("Analizando tráfico..."):

        #Generar una muestra con tráfico benigno y ataques
        events = load_simulation_sample(
            benign_count=10,
            attack_count=10
        )

        #Ejecutar ambos modelos
        predictions = predict_events(
            events,
            models
        )

        #Añadir información del dataset al resultado
        results = predictions.copy()
        results.insert(0, "tipo_real", events["Label"].values)
        results.insert(1, "es_ataque_real", events["is_attack"].values)

    st.success("Simulación completada")

    st.dataframe(
        results,
        use_container_width=True
    )