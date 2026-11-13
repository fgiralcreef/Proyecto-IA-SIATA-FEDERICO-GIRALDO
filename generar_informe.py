from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import cm
from pathlib import Path
from src.modelo import evaluar
import pandas as pd
ROOT=Path(__file__).parent
m,metricas,prueba=evaluar(pd.read_csv(ROOT/'data'/'siata_pm25_disponibilidad_feb2020.csv'))
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='TituloIA',parent=styles['Title'],fontSize=17,leading=22,textColor=colors.HexColor('#163b4b'),spaceAfter=13))
styles.add(ParagraphStyle(name='SubIA',parent=styles['Heading2'],fontSize=11,leading=14,textColor=colors.HexColor('#166779'),spaceBefore=10,spaceAfter=5))
styles.add(ParagraphStyle(name='CuerpoIA',parent=styles['BodyText'],fontSize=9.1,leading=13,spaceAfter=7))
styles.add(ParagraphStyle(name='MinIA',parent=styles['BodyText'],fontSize=8,leading=11,spaceAfter=5))
doc=SimpleDocTemplate(str(ROOT/'informe.pdf'),pagesize=(21*cm,29.7*cm),leftMargin=2.1*cm,rightMargin=2.1*cm,topMargin=1.8*cm,bottomMargin=1.7*cm)
story=[]
def p(t):story.append(Paragraph(t,styles['CuerpoIA']))
def h(t):story.append(Paragraph(t,styles['SubIA']))
story.append(Paragraph('Proyecto final SI3003 | Monitor SIATA',styles['TituloIA']))
p('<b>Universidad EAFIT · Inteligencia Artificial · MVP · 13 de noviembre de 2026</b>')
p('<b>Alcance:</b> análisis de disponibilidad histórica de registros válidos de PM2.5 en ocho estaciones del Valle de Aburrá. Este sistema no estima concentraciones de PM2.5, exposición ambiental ni niveles de contaminación.')
h('1. Problema y datos reales')
p('Las mediciones ambientales necesitan registros suficientemente completos para poder analizarse. La solución permite consultar por estación y fecha la fracción diaria de mediciones PM2.5 válidas y experimentar con la predicción de su disponibilidad al día siguiente. Se adoptó una variante limitada de la propuesta de calidad del aire (3.1), que debe ser aceptada por el docente si exige predicción directa de contaminación.')
p('Fuente: SIATA, sección PM2.5 de los indicadores de porcentaje de datos de febrero de 2020. Se transcribieron los valores publicados para ocho estaciones durante 29 días: <b>232 registros históricos</b>. La base se conserva como CSV y puede regenerarse con <font face="Courier">python data/crear_datos.py</font>. La URL de la fuente se documenta íntegra en el README.')
h('2. Técnica clásica implementada por el equipo')
p('Se programó Naive Bayes categórico desde cero, con conteos y suavizado de Laplace. Variables predictoras: código de estación, categoría del porcentaje válido del día y tipo de día (laboral/fin de semana). Variable objetivo: categoría de disponibilidad del día siguiente. Categorías: alta &gt;90%, media 75–90%, baja &lt;75%; son los rangos de presentación del indicador SIATA, no umbrales de PM2.5 en µg/m³.')
p('La probabilidad posterior se obtiene multiplicando la frecuencia previa de clase y las probabilidades condicionales suavizadas de los atributos, utilizando logaritmos por estabilidad. El modelo no llama a una librería que resuelva Naive Bayes.')
h('3. Validación temporal y resultados')
p('Se construyeron 224 parejas día–día siguiente por estación. El entrenamiento contiene fechas del 1 al 20 de febrero (160 parejas); la evaluación separada fechas del 21 al 28 de febrero (64 parejas). No se mezclan filas de fechas futuras en entrenamiento. La línea base siempre predice la clase mayoritaria del entrenamiento.')
data=[['Indicador','Modelo propio','Línea base'],['Exactitud de prueba',f"{metricas['accuracy_modelo']*100:.2f}%",f"{metricas['accuracy_baseline']*100:.2f}%"],['Ejemplos de prueba','64','64']]
t=Table(data,colWidths=[6.4*cm,4.6*cm,4.6*cm]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dce9ec')),('GRID',(0,0),(-1,-1),0.3,colors.lightgrey),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]));story.append(t);story.append(Spacer(1,7))
p('En la matriz de confusión se observaron 57 casos altos correctamente clasificados, uno alto predicho bajo y seis bajos correctamente clasificados. El conjunto presenta <b>predominio de clase alta</b>: la exactitud por sí sola no garantiza capacidad de generalización. El resultado es retrospectivo, no una predicción validada para otros meses.')
h('4. Agente, recuperación documental y herramientas')
p('La capa documental contiene cuatro fragmentos relacionados con SIATA, SISAIRE y las limitaciones. La recuperación RAG se implementó con tokenización, TF-IDF y similitud coseno en <font face="Courier">src/rag.py</font>, devolviendo título, fragmento, identificador y URL. El agente dispone de tres funciones: <font face="Courier">consultar_estacion</font>, <font face="Courier">predecir_disponibilidad</font> y <font face="Courier">buscar_documentos</font>.')
p('Con <font face="Courier">LLM_API_KEY</font> configurada, un LLM compatible con OpenAI realiza tool calling en un bucle acotado a cuatro iteraciones; recibe las observaciones de las herramientas y debe citar las fuentes. Ante error externo se presenta el error y pasa al modo local. Sin clave el sistema ofrece <b>chat local determinista</b>, que no se describe como LLM. No se ha comprobado aquí una llamada al proveedor remoto.')
h('5. Dashboard, interacción y evaluación del agente')
p('Streamlit permite seleccionar estación y fecha, ver el porcentaje y la categoría, consultar la serie diaria y comparar barras entre estaciones. Presenta métricas de Naive Bayes frente a línea base, tabla de evaluación y chat. El archivo <font face="Courier">evaluacion_agente.csv</font> contiene 12 consultas fijas: <b>12/12</b> llamadas esperadas y <b>12/12</b> respuestas con URL en el enrutador local. Esas pruebas <b>no evalúan</b> la fiabilidad de las respuestas del LLM remoto.')
h('6. Reproducibilidad, ética y limitaciones')
p('El README incluye instalación, ejecución, pruebas y origen de datos. Se adjuntan código, requirements.txt, CSV, informe y declaración explícita de asistencia con IA generativa. Las pruebas unitarias fueron ejecutadas en el entorno de desarrollo, pero la interfaz Streamlit no se pudo abrir en este entorno sin instalar sus dependencias; debe ejecutarse el README en el equipo de presentación antes de entregar.')
p('La muestra tiene solo 29 días, ocho estaciones y una distribución desbalanceada. No se usan datos actuales, no se proporcionan recomendaciones médicas y no se debe confundir disponibilidad con aire limpio o contaminado. El agente real necesita un proveedor externo y puede fallar si su clave, conectividad o modelo no están disponibles.')
h('Fuentes')
for s in ['SIATA, Indicadores de porcentaje de datos, febrero 2020, sección PM2.5 (URL exacta en README).','SIATA, Verificación de estaciones de la red de aire (URL exacta en README).','IDEAM, SISAIRE, consultas de PM2.5 (URL exacta en README).']:
 story.append(Paragraph('• '+s,styles['MinIA']))
def footer(canvas,document):
 canvas.setFont('Helvetica',8);canvas.setFillColor(colors.grey);canvas.drawRightString(19*cm,1.1*cm,f'Página {document.page}')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(ROOT/'informe.pdf')
