# CyberSOC-AI

CyberSOC-AI es un prototipo de sistema inteligente de apoyo a un Centro de Operaciones de Seguridad (SOC) para la detección y análisis de amenazas en tráfico de red.

El proyecto combina técnicas de Machine Learning, Deep Learning e Inteligencia Artificial generativa:

- **Random Forest** como detector supervisado principal de patrones de ataques conocidos.
- **Autoencoder** como detector no supervisado complementario de comportamientos anómalos.
- **Qwen3 1.7B mediante Ollama** como capa de IA generativa local para asistir al analista en la interpretación de las alertas.
- **Streamlit** como interfaz de usuario para visualizar eventos, alertas y análisis.

El desarrollo se ha realizado utilizando el dataset **CIC-IDS2017**.

## Arquitectura

El flujo simplificado de CyberSOC-AI es:

```text
Tráfico CIC-IDS2017
        |
        v
Preparación de características
        |
        +-------------------+
        |                   |
        v                   v
 Random Forest          Autoencoder
        |                   |
        +---------+---------+
                  |
                  v
          Nivel de alerta
                  |
                  v
        Dashboard Streamlit
                  |
                  v
       IA generativa local
        Ollama + Qwen3 1.7B
```

La IA generativa no determina si un evento constituye un ataque. La detección se realiza mediante Random Forest y Autoencoder. El modelo generativo actúa sólo como apoyo al analista para explicar los resultados y proponer comprobaciones adicionales.

## Requisitos

El proyecto se ha desarrollado y probado con:

- Python 3.12.2
- Streamlit 1.62.0
- TensorFlow 2.21.0
- Ollama 0.33.2
- Qwen3 1.7B

Las dependencias Python necesarias se encuentran en `requirements.txt`.

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/Maruve8/CyberSOC-AI.git
cd CyberSOC-AI
```

### 2. Crear un entorno virtual

En Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar las dependencias

```powershell
pip install -r requirements.txt
```

## Dataset

CyberSOC-AI utiliza **CIC-IDS2017** como base para el entrenamiento, evaluación y simulación de tráfico.

El dataset procesado utilizado por la aplicación es:

```text
data/processed/cic_ids2017_clean.parquet
```

Este archivo contiene aproximadamente 2,52 millones de registros después del proceso de limpieza realizado durante el proyecto.

Debido a que su tamaño supera el límite permitido para archivos individuales en el repositorio Git, no se incluye directamente.

### Opción rápida: descargar el dataset procesado

El archivo utilizado por la aplicación puede descargarse desde:

https://drive.google.com/file/d/1HA_9AUsO9dvVslnl9ZxLm_zODR5Z6yMj/view?usp=sharing

Una vez descargado, debe colocarse en:

```text
CyberSOC-AI/
└── data/
    └── processed/
        └── cic_ids2017_clean.parquet
```

### Reproducción del procesamiento

Los notebooks incluidos en `notebooks/` documentan el proceso seguido durante el proyecto, incluyendo exploración, limpieza, análisis, selección de características, modelado y evaluación.

El dataset original CIC-IDS2017 puede obtenerse en su fuente oficial:

https://www.unb.ca/cic/datasets/ids-2017.html

## Modelos entrenados

Los modelos y artefactos necesarios para realizar la inferencia se encuentran en `models/`:

```text
models/
├── random_forest.joblib
├── autoencoder.keras
├── autoencoder_scaler.joblib
└── autoencoder_config.json
```

Por tanto, no es necesario volver a entrenar los modelos para ejecutar la aplicación.

## IA generativa local

CyberSOC-AI utiliza un modelo generativo ejecutado localmente mediante **Ollama**.

Esto permite generar explicaciones para el analista sin enviar los datos analizados a una API externa.

### 1. Instalar Ollama

Descargar e instalar Ollama para Windows desde:

https://ollama.com/download/windows

La versión utilizada durante el desarrollo ha sido:

```text
Ollama 0.33.2
```

### 2. Descargar el modelo

CyberSOC-AI utiliza:

```text
qwen3:1.7b
```

Después de instalar Ollama, ejecutar:

```powershell
ollama pull qwen3:1.7b
```

Se puede comprobar la instalación con:

```powershell
ollama --version
```

### 3. Funcionamiento

La aplicación se comunica con Ollama localmente a través de:

```text
http://localhost:11434
```

No es necesaria ninguna API key ni servicio de pago.

Si Ollama no está disponible, los modelos de detección Random Forest y Autoencoder pueden seguir realizando el análisis, pero no estará disponible la explicación generativa.

## Ejecutar CyberSOC-AI

Con el entorno virtual activado:

```powershell
streamlit run app/app.py
```

Streamlit abrirá la aplicación en el navegador.

En caso de no abrirse automáticamente, la dirección habitual es:

```text
http://localhost:8501
```

## Uso de la aplicación

1. Pulsar **Ejecutar simulación**.
2. CyberSOC-AI selecciona tráfico del dataset y lo analiza mediante ambos modelos.
3. El dashboard muestra los eventos y niveles de alerta.
4. Seleccionar una alerta en **Detalle de alerta**.
5. Consultar la interpretación y recomendación generadas por el sistema.
6. Opcionalmente, pulsar **Generar análisis con IA** para obtener una explicación adicional mediante Qwen3 ejecutado localmente.

Los niveles de riesgo utilizados son:

- **Normal:** ninguno de los modelos identifica comportamiento sospechoso.
- **Medio:** el Autoencoder detecta una anomalía que el Random Forest no identifica como ataque conocido.
- **Alto:** el Random Forest identifica un patrón compatible con ataque conocido, pero el Autoencoder no detecta anomalía.
- **Crítico:** ambos modelos identifican comportamiento sospechoso.

## Estructura principal

```text
CyberSOC-AI/
├── app/
│   └── app.py
├── data/
│   ├── raw/
│   └── processed/
├── docs/
│   └── arquitectura.md
├── models/
├── notebooks/
├── src/
│   ├── detector.py
│   ├── generative.py
│   └── simulator.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Notebooks

El trabajo experimental está organizado principalmente en:

```text
01_exploracion_dataset.ipynb
02_analisis_exploratorio.ipynb
03_modelado.ipynb
04_autoencoder.ipynb
```

Estos notebooks recogen el proceso de análisis y construcción de los modelos utilizado en el proyecto.

## Consideraciones

CyberSOC-AI es un prototipo académico y no un sistema SOC preparado para entornos de producción.

La clasificación del Random Forest es binaria y distingue entre tráfico benigno y tráfico asociado a ataque; no clasifica directamente la familia concreta del ataque.

La etiqueta real de CIC-IDS2017 mostrada en la interfaz se utiliza exclusivamente para validar visualmente los resultados durante la simulación.

Los resultados obtenidos sobre CIC-IDS2017 deben interpretarse teniendo en cuenta las características y limitaciones propias del dataset y del procedimiento experimental utilizado.