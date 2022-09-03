import os
from funciones import url_partidos_jugados, jornadas_jugadas_funcion
import pandas as pd
os.chdir(os.path.dirname(__file__))

jornadas_jugadas = jornadas_jugadas_funcion('https://www.jornadaperfecta.com/puntos/')

url_lesionados = 'https://www.jornadaperfecta.com/lesionados/'

url_jugadores = ['https://www.jornadaperfecta.com/jugadores/?pagina={}'.format(i) for i in range(1,27)]

lista_url_jornadas = ['https://www.jornadaperfecta.com/puntos/?puntuacion=1&idJornada={}'.format(i) for i in range(1,jornadas_jugadas+1)] 

URL_PICAS, URL_SOFASCORE = url_partidos_jugados(lista_url_jornadas)