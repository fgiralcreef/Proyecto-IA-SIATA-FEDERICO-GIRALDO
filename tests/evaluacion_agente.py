"""12 casos fijos; evalúa selección de herramienta y presencia de fuente en modo local."""
import sys,csv
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
from src.modelo import evaluar
from src.agente import local
ROOT=Path(__file__).resolve().parents[1]
df=pd.read_csv(ROOT/'data'/'siata_pm25_disponibilidad_feb2020.csv');modelo,_,_=evaluar(df)
casos=[('¿Cuál es el porcentaje de la estación?','consultar_estacion'),('Dame el último dato','consultar_estacion'),('¿Qué valor tiene?','consultar_estacion'),('¿Cuál es el promedio?','consultar_estacion'),('¿Puedes predecir mañana?','predecir_disponibilidad'),('Predice el día siguiente','predecir_disponibilidad'),('¿Qué probabilidades hay?','predecir_disponibilidad'),('Dame un pronóstico','predecir_disponibilidad'),('¿Qué es PM2.5?','buscar_documentos'),('¿Cómo define SIATA el indicador OK?','buscar_documentos'),('¿Qué significa dato válido?','buscar_documentos'),('¿Cuáles son las limitaciones?','buscar_documentos')]
rows=[]
for pregunta,esperada in casos:
 r=local(pregunta,df,modelo,'MED-FISC');rows.append({'pregunta':pregunta,'esperada':esperada,'llamada':','.join(r['herramientas']),'herramienta_correcta':esperada in r['herramientas'],'fuente_citada':'http' in r['respuesta']})
out=ROOT/'evaluacion_agente.csv'
with out.open('w',encoding='utf-8',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
print('Casos:',len(rows),'Aciertos herramienta:',sum(x['herramienta_correcta'] for x in rows),'Citas:',sum(x['fuente_citada'] for x in rows));print(out)
