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

    # CyberSOC-AI consolida el resultado de los modelos antes de llamar al LLM.
    # La IA generativa explica el resultado final, pero no modifica la detección.
    if severity == "Crítico":
        system_interpretation = (
            "CyberSOC-AI ha detectado indicios compatibles con actividad maliciosa "
            "junto con un comportamiento anómalo significativo. "
            "El nivel de riesgo asignado es crítico."
        )

    elif severity == "Alto":
        system_interpretation = (
            "CyberSOC-AI ha detectado indicios compatibles con actividad maliciosa. "
            "El nivel de riesgo asignado es alto."
        )

    elif severity == "Medio":
        system_interpretation = (
            "CyberSOC-AI ha detectado un comportamiento anómalo que no coincide "
            "claramente con patrones de ataque conocidos. "
            "El nivel de riesgo asignado es medio."
        )

    else:
        system_interpretation = (
            "CyberSOC-AI no ha identificado indicios suficientes para generar "
            "una alerta sobre este evento."
        )

    prompt = f"""
Actúa como analista senior de un Security Operations Center (SOC).

Explica el resultado consolidado generado por CyberSOC-AI.

Datos del evento:
- Severidad: {severity}

Interpretación calculada por CyberSOC-AI:
{system_interpretation}

Esta interpretación es un hecho proporcionado por el sistema.
No la contradigas ni vuelvas a decidir la severidad.

CyberSOC-AI utiliza internamente Random Forest y Autoencoder como componentes
complementarios de detección. Tu respuesta debe centrarse en el resultado global
del sistema y no en comparar ambos modelos.

No interpretes métricas internas de los modelos ni intentes explicar cómo se ha
calculado la severidad. La clasificación y la severidad ya han sido determinadas
por CyberSOC-AI.

Genera una respuesta breve, clara y profesional en español.

Incluye exactamente estos apartados y escríbelos exactamente así:

ANÁLISIS:
Explica qué significa el nivel de riesgo detectado por CyberSOC-AI y por qué
el evento merece o no atención.

RECOMENDACIÓN:
Indica qué debería revisar el analista a continuación.

No afirmes que existe un ataque confirmado ni que se ha detectado actividad
maliciosa de forma concluyente. Utiliza expresiones como "indicios compatibles
con actividad maliciosa", "posible amenaza" o "evento sospechoso".
La severidad indica el nivel de prioridad asignado por CyberSOC-AI,
no la confirmación de una amenaza.
No inventes datos que no hayan sido proporcionados.
No menciones IP, puertos, usuarios, protocolos, equipos, procesos
ni otros datos que no hayan sido proporcionados.

Utiliza recomendaciones generales como:
"revisar evidencias adicionales del evento" o
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