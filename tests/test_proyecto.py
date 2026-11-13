import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
from src.modelo import evaluar,preparar,categoria
from src.rag import buscar
from src.agente import local,ejecutar_herramienta
ROOT=Path(__file__).resolve().parents[1]
df=pd.read_csv(ROOT/'data'/'siata_pm25_disponibilidad_feb2020.csv')
modelo,metricas,prueba=evaluar(df)
def test_serie_real():
 assert len(df)==232 and len(df.estacion.unique())==8
 assert (df.porcentaje_valido.between(0,100)).all()
def test_categorias():
 assert categoria(90)=='media' and categoria(90.01)=='alta' and categoria(74)=='baja'
def test_temporal():
 assert metricas['n_entrenamiento']==160 and metricas['n_prueba']==64
 assert 0<=metricas['accuracy_modelo']<=1
def test_rag():
 assert buscar('porcentaje calidad datos SIATA')[0]['id']=='S1'
def test_herramientas():
 assert 'porcentaje_valido' in ejecutar_herramienta('consultar_estacion',{},df,modelo,'MED-FISC')
 assert 'probabilidades' in ejecutar_herramienta('predecir_disponibilidad',{},df,modelo,'MED-FISC')
def test_chat():
 for q in ['¿Cuál es el porcentaje de la estación?','Predice el día siguiente','¿Qué es PM2.5?']:
  r=local(q,df,modelo,'MED-FISC');assert r['herramientas'] and ('http' in r['respuesta'])
