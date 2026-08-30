import requests


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen3:1.7b"


def generate_soc_analysis(
    severity,
    random_forest_result,
    autoencoder_result,
    reconstruction_error,
    threshold,
):
    """
    Genera una explicación breve para el analista SOC
    utilizando un modelo generativo local con Ollama.
    """

    # La interpretación técnica se fija antes de llamar al LLM para evitar contradicciones o conclusiones inventadas.
    if random_forest_result == "Ataque" and autoencoder_result == "Anomalía":
        model_interpretation = (
            "El Random Forest identifica un patrón compatible con ataques conocidos "
            "y el Autoencoder también detecta un comportamiento anómalo."
        )

    elif random_forest_result == "Ataque" and autoencoder_result == "Normal":
        model_interpretation = (
            "El Random Forest identifica un patrón compatible con ataques conocidos, "
            "pero el Autoencoder no detecta un comportamiento anómalo."
        )

    elif random_forest_result == "Normal" and autoencoder_result == "Anomalía":
        model_interpretation = (
            "El Random Forest no identifica un patrón de ataque conocido, "
            "pero el Autoencoder sí detecta un comportamiento anómalo."
        )

    else:
        model_interpretation = (
            "Ninguno de los dos modelos identifica indicios de amenaza en el evento."
        )
    
    if reconstruction_error > threshold:
        threshold_interpretation = (
            "El error de reconstrucción supera el umbral del Autoencoder."
        )
    else:
        threshold_interpretation = (
            "El error de reconstrucción está por debajo del umbral del Autoencoder."
        )

    prompt = f"""
Actúa como analista senior de un Security Operations Center (SOC).

Analiza este resultado generado por CyberSOC-AI:

- Severidad: {severity}
- Random Forest: {random_forest_result}
- Autoencoder: {autoencoder_result}
- Error de reconstrucción: {reconstruction_error:.4f}
- Umbral del Autoencoder: {threshold:.4f}

Interpretación técnica calculada por CyberSOC-AI:
{model_interpretation}

Interpretación del umbral:
{threshold_interpretation}

Esta interpretación es un hecho proporcionado por el sistema.
No la modifiques, no la contradigas y no vuelvas a inferir el resultado de los modelos.

Reglas de interpretación obligatorias:
- Si Random Forest = "Ataque", el modelo supervisado ha identificado
  un patrón compatible con ataques conocidos.
- Si Random Forest = "Normal", el modelo supervisado no ha identificado
  un patrón de ataque conocido.
- Si Autoencoder = "Anomalía", el error de reconstrucción supera el umbral
  y existe un comportamiento anómalo según este modelo.
- Si Autoencoder = "Normal", el error de reconstrucción NO supera el umbral
  y este modelo NO considera el evento anómalo.
- No contradigas estas reglas.

Genera una respuesta breve y clara en español.

Incluye exactamente estos apartados:

ANÁLISIS:
Explica qué indican conjuntamente ambos modelos.

RECOMENDACIÓN:
Indica qué debería revisar el analista a continuación.

No afirmes que existe un ataque confirmado.

No menciones ni recomiendes revisar IP, puertos, usuarios, protocolos,
equipos, procesos o cualquier otro dato que no haya sido proporcionado.

La recomendación debe basarse únicamente en:
- la severidad,
- el resultado del Random Forest,
- el resultado del Autoencoder,
- el error de reconstrucción,
- el umbral del Autoencoder.

Si necesitas recomendar una comprobación adicional, utiliza expresiones generales
como "revisar evidencias adicionales del evento" o
"contrastar el resultado con otras fuentes de seguridad".

Máximo 120 palabras.
"""

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "stream": False,
        "think": False,
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=120,
        )
        response.raise_for_status()

        return response.json()["message"]["content"]

    except requests.RequestException:
        return None