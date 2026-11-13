"""Recuperación TF-IDF sencilla implementada localmente; devuelve fuentes trazables."""
import json,math,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DOCS=json.loads((ROOT/'docs'/'corpus.json').read_text(encoding='utf-8'))
def tokens(s):return re.findall(r'[a-záéíóúñ0-9]+',s.lower())
def buscar(pregunta,k=2):
    textos=[tokens(d['texto']+' '+d['titulo']) for d in DOCS];consulta=tokens(pregunta)
    if not consulta:return []
    n=len(DOCS);df=Counter(t for doc in textos for t in set(doc))
    idf={t:math.log((n+1)/(df[t]+1))+1 for t in set(consulta)|set(df)}
    def vector(ts):
        c=Counter(ts);return {t:f*idf[t] for t,f in c.items()}
    vq=vector(consulta)
    def cos(a,b):
        dot=sum(x*b.get(t,0) for t,x in a.items())
        na=math.sqrt(sum(x*x for x in a.values()));nb=math.sqrt(sum(x*x for x in b.values()))
        return dot/(na*nb) if na*nb else 0
    ranked=sorted(((cos(vq,vector(ts)),d) for ts,d in zip(textos,DOCS)),key=lambda x:x[0],reverse=True)
    return [dict(d,puntaje=round(sc,3)) for sc,d in ranked[:k] if sc>0]
