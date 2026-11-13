"""Naive Bayes categórico programado desde cero, sin sklearn."""
from collections import Counter
import math
import pandas as pd

CLASES = ('baja', 'media', 'alta')
def categoria(p):
    return 'alta' if p>90 else 'media' if p>=75 else 'baja'

def preparar(df):
    df=df.copy().sort_values(['estacion','fecha']);df['estado']=df.porcentaje_valido.map(categoria)
    df['siguiente']=df.groupby('estacion')['estado'].shift(-1)
    df['dia_semana']=pd.to_datetime(df.fecha).dt.dayofweek.map(lambda x:'fin_semana' if x>=5 else 'laboral')
    return df.dropna(subset=['siguiente']).copy()

class NaiveBayesPropio:
    atributos=('estacion','estado','dia_semana')
    def fit(self,df):
        self.n=len(df);self.clases=tuple(sorted(df.siguiente.unique()));self.conteo=Counter(df.siguiente)
        self.valores={c:set(df[c].astype(str)) for c in self.atributos}
        self.freq={(cl,a):Counter(df.loc[df.siguiente==cl,a].astype(str)) for cl in self.clases for a in self.atributos}
        return self
    def probabilidades(self,registro):
        scores={}
        for cl in self.clases:
            log=math.log((self.conteo[cl]+1)/(self.n+len(self.clases)))
            for a in self.atributos:
                nvals=len(self.valores[a])+1
                log+=math.log((self.freq[(cl,a)][str(registro[a])]+1)/(self.conteo[cl]+nvals))
            scores[cl]=log
        mx=max(scores.values());p={c:math.exp(x-mx) for c,x in scores.items()};total=sum(p.values())
        return {c:round(p[c]/total,4) for c in p}
    def predict(self,registro):
        p=self.probabilidades(registro);return max(p,key=p.get)

def evaluar(df):
    datos=preparar(df)
    # Sin fuga: todos los ejemplos de entrenamiento hasta 20 feb; pruebas 21-28 feb.
    train=datos[datos.fecha<='2020-02-20'];test=datos[datos.fecha>'2020-02-20']
    modelo=NaiveBayesPropio().fit(train)
    pred=[modelo.predict(r) for r in test.to_dict('records')]
    principal=train.siguiente.mode().iloc[0]
    baseline=[principal]*len(test)
    acc=lambda ps:sum(a==b for a,b in zip(ps,test.siguiente))/len(test)
    resultado={'n_entrenamiento':len(train),'n_prueba':len(test),'accuracy_modelo':round(acc(pred),4), 'accuracy_baseline':round(acc(baseline),4), 'baseline_clase':principal}
    return modelo,resultado,test.assign(prediccion=pred,baseline=baseline)
