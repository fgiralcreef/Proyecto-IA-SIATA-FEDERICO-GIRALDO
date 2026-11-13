"""Ejecutar: streamlit run app.py"""
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from src.modelo import evaluar,categoria
from src.agente import responder
ROOT=Path(__file__).parent
st.set_page_config(page_title='SIATA | Disponibilidad PM2.5',layout='wide',page_icon='🌿')
st.title('🌿 SIATA · Monitor de disponibilidad PM2.5')
st.caption('Datos reales de febrero de 2020 · Porcentaje de mediciones válidas, NO concentración ni índice de calidad del aire')
@st.cache_data
def cargar():return pd.read_csv(ROOT/'data'/'siata_pm25_disponibilidad_feb2020.csv')
@st.cache_resource
def cargar_modelo():return evaluar(cargar())
df=cargar();modelo,met,test=cargar_modelo()
seleccion=st.sidebar.selectbox('Estación',sorted(df.estacion.unique()))
st.sidebar.divider()
st.sidebar.subheader('Conexión LLM (Groq)')
st.sidebar.caption('Obtén una clave en https://console.groq.com/keys. La clave no se guarda en archivos.')
clave=st.sidebar.text_input('API key de Groq', type='password', help='Solo se usa durante esta sesión; no se muestra en el chat.')
modelo_llm=st.sidebar.selectbox('Modelo', ['openai/gpt-oss-20b','openai/gpt-oss-120b','qwen/qwen3.8-27b'])
clave_activa=clave.strip() or __import__('os').getenv('LLM_API_KEY','').strip()
st.sidebar.caption('LLM listo para consultar' if clave_activa else 'Modo local: falta API key')
fecha=st.sidebar.select_slider('Día de febrero',options=sorted(df.fecha.unique()),value='2020-02-29')
sub=df[(df.estacion==seleccion)&(df.fecha<=fecha)].sort_values('fecha')
ultimo=sub.iloc[-1]
a,b,c=st.columns(3)
a.metric('Fecha consultada',ultimo.fecha)
b.metric('Datos válidos PM2.5',f'{ultimo.porcentaje_valido:.2f}%')
c.metric('Categoría de disponibilidad',categoria(ultimo.porcentaje_valido).capitalize())
col1,col2=st.columns(2)
with col1:
    st.subheader('Serie diaria por estación')
    fig=px.line(sub,x='fecha',y='porcentaje_valido',markers=True,labels={'fecha':'Fecha','porcentaje_valido':'Datos válidos (%)'})
    fig.update_yaxes(range=[0,105]);st.plotly_chart(fig,use_container_width=True)
with col2:
    st.subheader('Comparación entre estaciones')
    comp=df[df.fecha==fecha].copy();comp['categoria']=comp.porcentaje_valido.map(categoria)
    fig=px.bar(comp.sort_values('porcentaje_valido'),x='estacion',y='porcentaje_valido',color='categoria',color_discrete_map={'alta':'#1a936f','media':'#f4a261','baja':'#d1495b'},labels={'estacion':'Estación','porcentaje_valido':'Datos válidos (%)'})
    fig.update_yaxes(range=[0,105]);st.plotly_chart(fig,use_container_width=True)
st.subheader('Modelo clásico: Naive Bayes propio')
m1,m2,m3=st.columns(3)
m1.metric('Exactitud en prueba',f"{met['accuracy_modelo']:.1%}")
m2.metric('Línea base (mayoría)',f"{met['accuracy_baseline']:.1%}")
m3.metric('Ejemplos prueba',str(met['n_prueba']))
st.caption('Entrenamiento: 1–20 febrero; prueba: 21–28 febrero. Una exactitud alta puede ser trivial por predominio de la clase alta.')
with st.expander('Ver predicción experimental y registros de evaluación'):
    ult=df[df.estacion==seleccion].sort_values('fecha').iloc[-1]
    from src.agente import ejecutar_herramienta
    st.json(ejecutar_herramienta('predecir_disponibilidad',{},df,modelo,seleccion))
    st.dataframe(test[['fecha','estacion','estado','siguiente','prediccion','baseline']],hide_index=True)
st.divider()
st.subheader('Asistente documental · RAG + herramientas')
if 'mensajes' not in st.session_state:st.session_state.mensajes=[]
modo='LLM real con tool calling (necesita Internet)' if clave_activa else 'Local, sin LLM (introduce API key en barra lateral)'
st.caption('Modo: '+modo)
for msg in st.session_state.mensajes:
    with st.chat_message(msg['role']):st.markdown(msg['texto'])
if pregunta:=st.chat_input('Pregunta por la estación, las categorías o la predicción...'):
    st.session_state.mensajes.append({'role':'user','texto':pregunta})
    result=responder(pregunta,df,modelo,seleccion,fecha=fecha,api_key=clave_activa,model_name=modelo_llm)
    st.session_state.mensajes.append({'role':'assistant','texto':result['respuesta']+'\n\n*Herramientas: '+', '.join(result['herramientas'])+' · '+result['modo']+'*'})
    st.rerun()
st.info('Importante: disponibilidad de datos ≠ niveles de contaminación. Los registros son históricos (2020). Sin una API key activa, el chat funciona en modo local, pero no cumple el requisito del LLM de la rúbrica.')
st.markdown('[Fuente oficial SIATA](https://siata.gov.co/CalidadAire/IndicadoresDatosMes/verificacionIndicadoresDatosMesRedAire_2020_02_01_00_00_00_a_2020_02_29_00_00_00.html)')
