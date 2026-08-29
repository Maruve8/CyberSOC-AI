from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf


#rutas principales del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"

#artefactos generados durante el entrenamiento
RANDOM_FOREST_FILE = MODELS_DIR / "random_forest.joblib"
AUTOENCODER_FILE = MODELS_DIR / "autoencoder.keras"
SCALER_FILE = MODELS_DIR / "autoencoder_scaler.joblib"
AUTOENCODER_CONFIG_FILE = MODELS_DIR / "autoencoder_config.json"


def load_models():
    """Carga los modelos y la configuración necesaria para realizar predicciones."""

    required_files = [
        RANDOM_FOREST_FILE,
        AUTOENCODER_FILE,
        SCALER_FILE,
        AUTOENCODER_CONFIG_FILE,
    ]

    #comprobar que todos los artefactos existen antes de cargarlos
    missing_files = [
        file_path
        for file_path in required_files
        if not file_path.exists()
    ]

    if missing_files:
        missing_names = ", ".join(
            file_path.name for file_path in missing_files
        )
        raise FileNotFoundError(
            f"Faltan archivos de modelo: {missing_names}"
        )

    #cargar los dos modelos entrenados
    random_forest = joblib.load(RANDOM_FOREST_FILE)
    autoencoder = tf.keras.models.load_model(AUTOENCODER_FILE)

    #Cargar el escalador utilizado por Autoencoder
    scaler = joblib.load(SCALER_FILE)

    #Cargar 48 características y umbral de anomalía
    with open(
        AUTOENCODER_CONFIG_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        autoencoder_config = json.load(file)

    return {
        "random_forest": random_forest,
        "autoencoder": autoencoder,
        "scaler": scaler,
        "features": autoencoder_config["features"],
        "threshold": autoencoder_config["threshold"],
    }




def predict_events(data, models):
    """
    Ejecuta Random Forest y Autoencoder sobre uno o varios registros.

    Parameters
    ----------
    data : pandas.DataFrame
        Registros que contienen las 48 características esperadas.
    models : dict
        Diccionario devuelto por load_models().

    Returns
    -------
    pandas.DataFrame
        Resultados de detección para cada registro.
    """

    features = models["features"]
    random_forest = models["random_forest"]
    autoencoder = models["autoencoder"]
    scaler = models["scaler"]
    threshold = models["threshold"]

    # se comprueba que están presentes las 48 características necesarias
    missing_features = [
        feature for feature in features
        if feature not in data.columns
    ]

    if missing_features:
        raise ValueError(
            f"Faltan características necesarias: {missing_features}"
        )

    #Autoencoder utiliza el orden de características guardado en su configuración
    X_autoencoder = data[features].copy()

    #Random forest conserva el orden utilizado al entrenarlo
    rf_features = list(random_forest.feature_names_in_)
    X_random_forest = data[rf_features].copy()

    #Predicción del modelo supervisado
    rf_prediction = random_forest.predict(X_random_forest)

    #Preparación de los datos para el autoencoder
    X_scaled = scaler.transform(X_autoencoder)      

    reconstructed = autoencoder.predict(
        X_scaled,
        batch_size=1024,
        verbose=0
    )

    #Error de reconstrucción de cada registro
    reconstruction_error = np.mean(
        np.square(X_scaled - reconstructed),
        axis=1
    )

    #registro anómalo si supera el umbral aprendido
    autoencoder_prediction = (
        reconstruction_error > threshold
    ).astype(int)

    #crear un resultado sencillo para la aplicación
    results = pd.DataFrame({
        "random_forest": rf_prediction,
        "autoencoder": autoencoder_prediction,
        "reconstruction_error": reconstruction_error,
    })

    # -----------------------------------------------------
    # Evaluación combinada del riesgo
    # -----------------------------------------------------
    # La severidad depende de qué modelo haya detectado el evento:
    # 0 = normal
    # 1 = medio: solo el Autoencoder detecta anomalía
    # 2 = alto: el Random Forest detecta ataque
    # 3 = crítico: ambos modelos coinciden

    results["alert_level"] = np.select(
        [
            # Ambos modelos detectan comportamiento sospechoso
            (results["random_forest"] == 1)
            & (results["autoencoder"] == 1),

            # El Random Forest detecta ataque, pero el Autoencoder no
            (results["random_forest"] == 1)
            & (results["autoencoder"] == 0),

            # Solo el Autoencoder detecta una anomalía
            (results["random_forest"] == 0)
            & (results["autoencoder"] == 1),
        ],
        [
            3,  # Crítico
            2,  # Alto
            1,  # Medio
        ],
        default=0,  # Normal
    )

    return results