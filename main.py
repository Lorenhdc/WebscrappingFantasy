from code import Dataframe_downloading
import os
from valores import URL_PICAS, URL_SOFASCORE, url_jugadores,url_lesionados

os.chdir(os.path.dirname(__file__))


Dataframe_downloading.preparacion_tabla(url_lesionados, url_jugadores, URL_SOFASCORE, URL_PICAS)