"""Simula respuestas Groq sin clave ni Internet para comprobar el loop real."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
from unittest.mock import patch
from src.modelo import evaluar
from src.agente import responder, ejecutar_herramienta, DEFAULT_MODEL
ROOT=Path(__file__).resolve().parents[1]
df=pd.read_csv(ROOT/'data'/'siata_pm25_disponibilidad_feb2020.csv')
modelo,_,_=evaluar(df)
class FakeResponse:
 def __init__(self,message): self.message=message
 def raise_for_status(self): pass
 def json(self):return {'choices':[{'message':self.message}]}
def test_tool_call_llm_y_citas():
 respuestas=iter([
  FakeResponse({'role':'assistant','content':None,'tool_calls':[{'id':'1','type':'function','function':{'name':'consultar_estacion','arguments':'{"estacion":"MED-FISC"}'}}]}),
  FakeResponse({'role':'assistant','content':'La disponibilidad es histórica, no es concentración. [S1]'})])
 with patch('src.agente.requests.post',side_effect=lambda *a,**kw:next(respuestas)) as post:
  r=responder('Porcentaje de la estación',df,modelo,'MED-FISC',fecha='2020-02-15',api_key='clave-de-prueba')
 assert r['herramientas']==['consultar_estacion']
 assert r['modo']==f'LLM ({DEFAULT_MODEL})'
 assert 'siata.gov.co' in r['respuesta']
 assert post.call_count==2
 assert any(m['role']=='tool' for m in post.call_args.kwargs['json']['messages'])
def test_fecha_filtro_tool():
 r=ejecutar_herramienta('consultar_estacion',{},df,modelo,'MED-FISC','2020-02-15')
 assert r['fecha']=='2020-02-15'
def test_fallback_sin_clave():
 assert responder('Predice mañana',df,modelo,'MED-FISC',api_key='')['modo']=='Local (sin LLM)'
def test_herramienta_desconocida():
 assert 'error' in ejecutar_herramienta('eliminar_todo',{},df,modelo,'MED-FISC')
