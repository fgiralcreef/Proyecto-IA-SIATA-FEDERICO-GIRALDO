"""Transcripción verificable de tabla HTML de indicadores diarios SIATA febrero 2020.
Valores: PORCENTAJE de mediciones PM2.5 consideradas válidas (NO concentración).
Fuente: https://siata.gov.co/CalidadAire/IndicadoresDatosMes/verificacionIndicadoresDatosMesRedAire_2020_02_01_00_00_00_a_2020_02_29_00_00_00.html
"""
import csv
from datetime import date
from pathlib import Path

SERIES = {
 'ITA-CJUS': '100 95.83 100 100 100 100 100 100 100 100 91.67 100 100 100 100 100 100 100 100 100 95.83 100 100 100 100 100 100 100 100',
 'ITA-CONC': '100 100 100 100 100 100 100 100 100 100 100 95.83 100 100 100 100 100 100 91.67 100 100 100 100 100 100 100 100 100 100',
 'CAL-LASA': '100 100 100 100 100 100 100 100 100 100 95.83 100 100 100 100 100 100 100 100 100 100 100 100 100 100 100 100 100 100',
 'SUR-TRAF': '45.83 100 100 100 100 100 91.67 100 100 100 100 100 100 100 100 100 100 100 87.50 100 100 100 100 100 100 100 100 100 100',
 'CEN-TRAF': '100 100 100 100 91.67 100 100 100 100 100 100 100 100 100 100 100 95.83 100 95.83 83.33 100 100 100 100 100 100 100 100 100',
 'GIR-SOSN': '100 100 100 100 100 100 100 100 100 100 100 100 100 100 100 100 100 95.83 100 100 100 100 100 100 100 100 100 100 100',
 'MED-LAYE': '100 100 95.83 100 100 100 95.83 100 95.83 91.67 100 100 100 91.67 100 100 100 100 100 100 100 100 100 100 100 100 100 100 100',
 'MED-FISC': '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 37.50 100 100',
}
NOMBRES = {'ITA-CJUS':'Casa de Justicia, Itagüí','ITA-CONC':'Concejo Municipal, Itagüí','CAL-LASA':'Lasallista, Caldas','SUR-TRAF':'Tráfico Sur','CEN-TRAF':'Tráfico Centro','GIR-SOSN':'SOS Aburrá Norte, Girardota','MED-LAYE':'Tanques La Ye, Medellín','MED-FISC':'Fiscalía, Medellín'}
OUT = Path(__file__).with_name('siata_pm25_disponibilidad_feb2020.csv')
with OUT.open('w',newline='',encoding='utf-8') as f:
 w=csv.writer(f);w.writerow(['fecha','estacion','nombre','porcentaje_valido'])
 for code,serie in SERIES.items():
  vals=[float(x) for x in serie.split()]
  assert len(vals)==29,(code,len(vals))
  for d,v in enumerate(vals,1):w.writerow([date(2020,2,d).isoformat(),code,NOMBRES[code],v])
print('Generado',OUT)
