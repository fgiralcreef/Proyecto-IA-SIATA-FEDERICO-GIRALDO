# SIATA: monitor de disponibilidad de mediciones PM2.5

Proyecto MVP SI3003 (EAFIT). **Analiza porcentaje de mediciones válidas**. Variante acotada de la idea 3.1; confirmar con el docente si la evaluación requiere específicamente predicción de concentración.

## Ejecutar (Python 3.10 o superior; probado también con Python 3.13)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q
python tests/evaluacion_agente.py
python -m streamlit run app.py
```

No necesita conexión para consultar el CSV incluido. Abra la URL local que indique Streamlit. El chat local responde sin cuenta:

1. Crea una clave de API en https://console.groq.com/keys (la disponibilidad del servicio y de cuotas depende del proveedor).
2. Abre el dashboard y busca **Conexión LLM (Groq)** en la barra lateral izquierda.
3. Pega tu clave en el campo protegido **API key de Groq**; selecciona `openai/gpt-oss-20b`.
4. Pregunta en el chat: `¿Cuál es el porcentaje de la estación y qué significa este indicador?`
5. Comprueba que debajo de la respuesta aparezca **LLM (openai/gpt-oss-20b)** y nombres de herramientas, NO **Local (sin LLM)** ni **Respaldo local**.

La clave se introduce en el navegador local, no se escribe ni guarda en archivos del proyecto. No la subas a GitHub. Alternativamente, en Linux puedes usar `export LLM_API_KEY="TU_CLAVE"` antes de ejecutar Streamlit. La conexión requiere Internet.

**Cambio de proveedor (noviembre 2026):** el modelo viejo `llama-3.3-70b-versatile` está retirado para cuentas gratuitas de Groq. Se usa `openai/gpt-oss-20b` con tool calling compatible. Fuentes: https://console.groq.com/docs/deprecations y https://console.groq.com/docs/tool-use/overview.

Si el proveedor falla, se presenta el error y el sistema cambia explícitamente a un asistente determinista local.

En Linux (Debian/Ubuntu), si `pip` devuelve `externally-managed-environment`, instala `sudo apt install python3-venv`, activa `.venv` y vuelve a usar `python -m pip install -r requirements.txt`; evita `--break-system-packages`.

## Comprobaciones antes de entregar

```bash
python -m pytest -q
python tests/evaluacion_agente.py
python -m streamlit run app.py
```

Las pruebas `tests/test_llm.py` simulan el proveedor para comprobar tool calling; **no certifican la conexión real a Groq**. La tabla de 12 preguntas (`evaluacion_agente.csv`) evalúa el **modo local** y sus fuentes; no confundir con una evaluación del LLM remoto. Para evaluar el LLM, usar las mismas 12 preguntas con API key y registrar el modo y las herramientas de cada respuesta.

## Fuentes y datos

- Fuente principal real, sin API: [SIATA, porcentaje diario de datos válidos, febrero de 2020](https://siata.gov.co/CalidadAire/IndicadoresDatosMes/verificacionIndicadoresDatosMesRedAire_2020_02_01_00_00_00_a_2020_02_29_00_00_00.html), sección **PM2.5**, columnas 01 a 29, filas de estaciones.
- Reproducción local: `python data/crear_datos.py` genera `data/siata_pm25_disponibilidad_feb2020.csv` (232 filas, 8 estaciones, 29 días). Los valores están transcritos de la tabla oficial; comparar con el enlace fuente ante dudas.
- [SIATA estado de estaciones](https://siata.gov.co/CalidadAire/verificacionEstacionesRedAireValidadoSIATA.php).
- [IDEAM SISAIRE](https://sisaire.ideam.gov.co/ideam-sisaire-web/consultas.xhtml?est=31916&param=PM2.5).

## Arquitectura

`CSV SIATA → categorías según porcentajes → Naive Bayes categórico propio → evaluación cronológica` y `corpus documental → TF-IDF propio → RAG → agente LLM con tool calling (o fallback local)` → dashboard Streamlit.

- Modelo Parte 1: Naive Bayes categórico con suavizado Laplace, programado desde cero en `src/modelo.py`. Variables: estación, categoría de hoy y tipo de día; objetivo: categoría de **disponibilidad** del día siguiente. División temporal 1–20 feb para entrenar y 21–28 para probar. Métrica accuracy; línea base: clase más frecuente de entrenamiento.
- Agente Parte 2: `src/agente.py`, máximo 4 iteraciones, 3 herramientas: `consultar_estacion`, `predecir_disponibilidad`, `buscar_documentos`. RAG TF-IDF en `src/rag.py`; corpus con identificadores S1–S4 y URL. La llamada real LLM depende de una clave del usuario.
- Interfaz: selección de estación y fecha, línea de tiempo, barras por estación, métrica, comparación y conversación.
- `tests/evaluacion_agente.py`: 12 preguntas fijas, tabla de herramienta correcta y presencia de URL (evalúa enrutador local; **no** certifica comportamiento del LLM remoto).

## Límites

La muestra es breve (solo febrero 2020). Los porcentajes reflejan disponibilidad/validez, no mediciones de contaminación. Hay predominio de clase alta, por lo que la exactitud puede resultar engañosa. No es predicción operacional, consejo médico ni valoración de calidad del aire actual. Ningún secreto incluido en archivos. El funcionamiento remoto depende del proveedor de LLM; el programa conserva un modo local.

