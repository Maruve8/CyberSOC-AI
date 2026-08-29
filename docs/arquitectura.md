# Arquitectura de CyberSOC-AI

## Objetivo

CyberSOC-AI es una aplicación de apoyo a un analista SOC para detectar tráfico
potencialmente malicioso mediante modelos de Inteligencia Artificial.

La aplicación combina dos enfoques:

- Random Forest como detector principal de ataques conocidos.
- Autoencoder como detector complementario de anomalías.

## Flujo general

1. La aplicación recibe o selecciona registros de tráfico de red.
2. Los datos se preparan utilizando las mismas características empleadas durante
   el entrenamiento.
3. El Random Forest genera una predicción binaria:
   - 0: tráfico benigno.
   - 1: posible ataque.
4. El Autoencoder calcula el error de reconstrucción del registro.
5. Si el error supera el umbral definido durante la validación, el registro se
   considera anómalo.
6. La aplicación combina ambos resultados y genera una alerta cuando procede.
7. El dashboard muestra:
   - número de registros analizados,
   - alertas detectadas,
   - nivel de riesgo,
   - resultado de cada modelo,
   - detalle de los eventos analizados.

## Componentes

### app/app.py

Interfaz principal desarrollada con Streamlit.

Responsabilidades:

- mostrar el dashboard,
- permitir lanzar una simulación,
- visualizar alertas y resultados,
- presentar información comprensible para un analista SOC.

### src/detector.py

Contiene la lógica de inferencia de los modelos.

Responsabilidades:

- cargar los modelos almacenados,
- preparar los datos de entrada,
- ejecutar Random Forest,
- ejecutar Autoencoder,
- calcular el error de reconstrucción,
- devolver el resultado de detección.

### src/simulator.py

Genera los datos utilizados durante la demostración.

La simulación se construye a partir de registros del dataset CIC-IDS2017,
permitiendo reproducir tráfico benigno y distintos tipos de ataque sin necesidad
de capturar tráfico de red en tiempo real.

## Modelos

### Random Forest

Modelo supervisado utilizado como detector principal.

Su función es identificar patrones correspondientes a ataques conocidos a partir
de las 48 características seleccionadas durante el entrenamiento.

### Autoencoder

Modelo entrenado exclusivamente con tráfico benigno.

Su función es actuar como detector complementario de anomalías utilizando el
error de reconstrucción como indicador de desviación respecto al comportamiento
normal aprendido.

## Estrategia de detección

La primera versión del sistema utilizará una lógica sencilla:

- Random Forest detecta ataque -> alerta.
- Autoencoder detecta anomalía -> indicador adicional de anomalía.
- Ambos detectan comportamiento sospechoso -> alerta de mayor confianza.

Esta estrategia permite aprovechar el elevado rendimiento del modelo supervisado
sin renunciar a la capacidad del Autoencoder para identificar comportamientos
diferentes al tráfico normal.

## Alcance del MVP

El MVP incluirá:

- dashboard web,
- simulación de tráfico,
- detección mediante Random Forest,
- detección de anomalías mediante Autoencoder,
- generación de alertas,
- visualización de métricas básicas,
- detalle de eventos detectados.

Quedan fuera del MVP inicial:

- captura de tráfico de red en tiempo real,
- integración con un SIEM real,
- gestión de usuarios,
- persistencia en base de datos,
- despliegue distribuido,
- automatización de respuestas ante incidentes.