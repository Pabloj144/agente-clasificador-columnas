\# 🤖 Agente Clasificador de Columnas por Lotes y Benchmark de Confiabilidad



Este proyecto implementa un agente de inteligencia artificial capaz de analizar esquemas de datasets tabulares y clasificar sus columnas en útiles, secundarias o descartables según reglas de negocio, utilizando la API de OpenRouter (`google/gemini-3.8-flash`, `openai/gpt-4o-mini`, etc.).



\## 🚀 Características Principales

\- \*\*Payload Optimizado (Extracto JSON Ligero):\*\* Envía únicamente metadatos de las columnas y 3 filas de muestra para reducir el consumo de tokens y acelerar las respuestas.

\- \*\*Procesamiento por Lotes (Batching):\*\* División automática en lotes de máximo 30 columnas para prevenir la omisión de datos por saturación de atención (\*Lost in the Middle\*).

\- \*\*Benchmark de Confiabilidad:\*\* Matriz de evaluación comparativa entre clasificación humana (\*Ground Truth\*) y la respuesta del agente midiendo la precisión mediante el \*\*Índice de Jaccard\*\*.

\- \*\*Configuración Dinámica:\*\* Evaluación de diferentes técnicas de prompt (`zero-shot`, `few-shot`, `chain of thought`) y niveles de esfuerzo de razonamiento (`low`, `medium`, `high`).



\## 📁 Estructura del Repositorio

\- `agente\_clasificador.py`: Script interactivo principal del agente clasificador.

\- `benchmark\_lotes.py`: Motor de pruebas para medir tiempos y riesgos de omisión por tamaño de lote.

\- `evaluar\_excel.py`: Script para calcular automáticamente el porcentaje de precisión Jaccard en la matriz.

\- `Matriz\_Benchmark\_Agente.xlsx`: Matriz ejecutable con los resultados del benchmark y tablas comparativas.

\- `data/`: Carpeta con los datasets de prueba (`dataset\_benchmark.csv`).



\## 🛠️ Instalación y Uso



1\. \*\*Clonar este repositorio:\*\*

&#x20;  ```bash

&#x20;  git clone \[https://github.com/TU-USUARIO/agente-clasificador-columnas.git](https://github.com/TU-USUARIO/agente-clasificador-columnas.git)

&#x20;  cd agente-clasificador-columnas

