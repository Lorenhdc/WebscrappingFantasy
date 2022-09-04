import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import html
import numpy as np
import re
import math
from cmath import nan
import os

os.chdir(os.path.dirname(__file__))


def obtener_soup(url):
    r = requests.get(url)
    content = r.content
    soup = bs(content, 'lxml')
    return soup

def obtener_urls_jugadores(listado):
    url_finales_jugadores = []

    for i in listado:
        soup = obtener_soup(i)
        soup_tabla_jugadores = soup.find_all('div', class_="ficha-jugadores-tabla")

        n = 0
        for a in soup_tabla_jugadores[0].find_all('a', href = True):
            n += 1
            if n<=7:
                continue
            if n%3 == 0:
                url_finales_jugadores.append(a['href'])
    return url_finales_jugadores

def obtener_nombre_precio(listado):
    lista_id = []
    lista_valores = []
    lista_posiciones = []

    for i in listado:
        soup = obtener_soup(i)
        ficha = soup.find_all('div', class_='jugador-perfil team-card')
        player_name = ficha[0].find('span').text
        equipo = ficha[0].find_all('div', class_='player-team-shield')[0]
        player_equipo = equipo.find('img')['title']
        id = player_name + '*' + player_equipo
        lista_id.append(id)
        pattern = re.compile(r"[A-Z]\w*")
        posicion = ficha[0].find_all('div', class_='jp-pos')[0]
        match = re.search(pattern, posicion.text)
        pos = match.group(0)
        lista_posiciones.append(pos)
        valor = soup.find_all('div', class_='jugador-datos-cifra')
        valor_player = int(valor[3].text.replace('.',''))
        lista_valores.append((valor_player/1000))
    return lista_id, lista_valores,lista_posiciones

def obtención_diccionario_players(soup_princial, soup_equipo, jornada_actual,loc_vis, Título_puntos):
    n=0
    listado_jugadores = []
    for i in soup_equipo:
        n += 1
        nombre = i.find('a').text
        puntos = i.find_all('div', class_="puntos-jugador-puntuacion")[0].text
        puntos = int(puntos[:2])        
        equipo = soup_princial.find_all('div', class_="mobile-col-4-12")[loc_vis].find('img')['title']
        id = nombre + '*' + equipo
        if n<12:
            titular = 1
        else: 
            titular = 0
        diccionario_datos = {'Jornada':jornada_actual, 'Id':id, 'Nombre':nombre, 'Equipo':equipo, 'Titular':titular, 'Jugado':1, Título_puntos:puntos}
        listado_jugadores.append(diccionario_datos)
    return listado_jugadores

def lista_de_dic_players(url_partidos, lista_all_players, Título_puntos):
    lista_jugadores = []
    j = 0
    for i in url_partidos:
        j +=1
        jornada = math.ceil(j/10)
        soup = obtener_soup(i)
        soup_puntos = soup.find_all('div', class_="col-6-12 mobile-col-6-12")
        try:
            equipo_local = soup_puntos[0].find_all('div', class_="puntos-jugador")
            equipo_visitante = soup_puntos[1].find_all('div', class_="puntos-jugador")
            listado_local = obtención_diccionario_players(soup, equipo_local, jornada,0, Título_puntos)
            lista_jugadores.extend(listado_local)
            listado_visitante = obtención_diccionario_players(soup, equipo_visitante, jornada,1, Título_puntos)
            lista_jugadores.extend(listado_visitante)
        except:
            "no hacer nada"
        if j%10 ==0:
            Dataframe_jugadores = pd.DataFrame(lista_jugadores)
            jugadores_puntuados = list(Dataframe_jugadores[Dataframe_jugadores['Jornada'] == jornada]['Id'])
            jugadores_no_puntuados = set(jugadores_puntuados) ^ set(lista_all_players)
            for i in jugadores_no_puntuados:
                pos_dash = i.index('*')
                diccionario_datos = {'Jornada':jornada, 'Id':i, 'Nombre':i[:pos_dash], 'Equipo':i[(pos_dash+1):], 'Titular':0,'Jugado':0, Título_puntos:0 }
                lista_jugadores.append(diccionario_datos)
    return lista_jugadores

def dataframe_lesionados(URL):    
    soup = obtener_soup(URL)
    soup_lesionados = soup.find_all('div', class_ = 'lesionados')
    lista_id = []
    equipos_lista = []
    jugadores_nombres = []
    lesiones_lista = []
    for i in soup_lesionados:
        equipo = i.find_all('div', class_ = 'lesionados-equipo-nombre')[0].text
        if len(i.find_all('div', class_ = 'lesionados-jugador-sanos')) > 0:
            continue
        soup_jugador = i.find_all('div', class_ = 'lesionados-jugador-nombre')
        for h in range(len(soup_jugador)):
            name_player = soup_jugador[h].find('a').text
            jugadores_nombres.append(name_player)
            equipos_lista.append(equipo)
            id = name_player +'*'+ equipo
            lista_id.append(id)
        soup_lesión = i.find_all('div', class_ = 'lesionados-jugador-iconos')
        for j in range(len(soup_lesión)):
            lesion_player = soup_lesión[j].find('img')['title']
            lesiones_lista.append(lesion_player)
    Dataframe_lesionados = pd.DataFrame(list(zip(lista_id, jugadores_nombres, equipos_lista, lesiones_lista)), columns=['Id', 'Nombre', 'Equipo', 'Estado'])
    return Dataframe_lesionados

def dataframe_valores(url_jugadores):
    links_jugadores = obtener_urls_jugadores(url_jugadores)
    lista_jugadores, lista_valores, lista_posiciones = obtener_nombre_precio(links_jugadores)
    Dataframe_valor = pd.DataFrame(list(zip(lista_jugadores,lista_valores,lista_posiciones)),columns=['Id','Valor [En miles]', 'Posicion'])
    return Dataframe_valor


def url_partidos_jugados(lista_url_jornadas):
    listados_url_partidos = []

    for i in lista_url_jornadas:
        soup = obtener_soup(i)
        soup_goles = soup.find_all('div', class_="col-4-12 mobile-col-6-12 marcador-wrapper")
        listados_url_partidos_jornadas = [i.find('a')['href'] for i in soup_goles]
        listados_url_partidos.extend(listados_url_partidos_jornadas)

    URL_PICAS =  [i + '?puntuacion=1' for i in listados_url_partidos]
    URL_SOFASCORE= [i + '?puntuacion=2' for i in listados_url_partidos]

    return URL_PICAS, URL_SOFASCORE

def creacion_df_sofaspicas(lista1,lista2,lista3):
    Dataframe_jugadores_sofascore = pd.DataFrame(lista_de_dic_players(lista1,lista3, Título_puntos = 'Puntos Sofas'))
    Dataframe_jugadores_picas = pd.DataFrame(lista_de_dic_players(lista2,lista3,  Título_puntos = 'Puntos Picas'))
    df_final = pd.merge(Dataframe_jugadores_picas, Dataframe_jugadores_sofascore)
    df_final["Puntos Medias"] = np.where(df_final["Titular"] == np.nan, np.nan, round((df_final['Puntos Picas']+df_final['Puntos Sofas']+0.2)/2))
    return df_final

def jornadas_jugadas_funcion(url):
    soup = obtener_soup(url)
    soup_nueva = soup.find_all('select', class_='push-right')
    valor = int(soup_nueva[0].find('option')['value']) - 1
    return valor

def obtencion_listas_consolidacion(df, campo, tipo):
    lista_datos = []
    for a in df['Id'].unique():
        if tipo == 'valor':
            valor = list(df[df['Id'] == a][campo].unique())[0]
            lista_datos.append(valor)
        else:
            valor = list(df[df['Id'] == a][campo])
            lista_datos.append(valor)            
    return lista_datos

def obtencion_listas_finales(df, campo, tipo, jornadas_played):
    lista_datos = []
    for a in range(len(df)):
        if tipo == 'promedio':
            valor = sum(df.loc[a,campo])/jornadas_played
        elif tipo == 'suma':
            valor = sum(df.loc[a,campo])
        elif tipo == 'forma':
            valor = sum(df.loc[a,campo][-5:])
        lista_datos.append(valor)
    return lista_datos    

def elaboracion_df_compilados(df, tipo):
    jornadas_jugadas = jornadas_jugadas_funcion('https://www.jornadaperfecta.com/puntos/')
    n = 0 
    Dataframe = pd.DataFrame()
    if tipo == 'normal':
        for i in df.columns:
            n+=1
            if i== 'Jornada':
                continue
            elif i == 'Id' or  i =='Nombre' or i =='Equipo':
                lista = obtencion_listas_consolidacion(df, campo=i, tipo ='valor')
                Dataframe[i] = lista
            else:
                lista = obtencion_listas_consolidacion(df, campo=i, tipo ='nada')
                Dataframe[i] = lista
    elif tipo == 'final':
        for i in df.columns:
            if i == 'Id':
                Dataframe[i]=df[i]
            elif i == 'Titular':
                lista = obtencion_listas_finales(df, campo =i , tipo = 'promedio',jornadas_played=jornadas_jugadas)               
                Dataframe['% ' + i] = lista
                Dataframe['% ' + i] = Dataframe['% ' + i].apply(lambda x:format(x, '.0%'))
            elif i == 'Jugado' or i == 'Puntos Medias':
                lista = obtencion_listas_finales(df, campo =i , tipo = 'suma',jornadas_played=jornadas_jugadas)               
                Dataframe['Total ' + i] = lista
                lista = obtencion_listas_finales(df, campo =i , tipo = 'forma',jornadas_played=jornadas_jugadas)
                Dataframe['Forma ' + i] = lista
                if i == 'Jugado':
                    lista = obtencion_listas_finales(df, campo =i , tipo = 'promedio',jornadas_played=jornadas_jugadas)               
                    Dataframe['% ' + i] = lista
                    Dataframe['% ' + i] = Dataframe['% ' + i].apply(lambda x:format(x, '.0%'))
            elif i == 'Puntos Picas' or i == 'Puntos Sofas':                
                lista = obtencion_listas_finales(df, campo =i , tipo = 'suma',jornadas_played=jornadas_jugadas)               
                Dataframe['Total ' + i] = lista
        Dataframe = pd.merge(df,Dataframe)
    return Dataframe
    

def ultimos_retoques(df, df1, df2):
   df['Promedio Picas'] = (df['Total Puntos Picas']/df['Total Jugado']).round(2).fillna(0)
   df['Promedio Sofas'] = (df['Total Puntos Sofas']/df['Total Jugado']).round(2).fillna(0)
   df['Promedio Media'] = (df['Total Puntos Medias']/df['Total Jugado']).round(2).fillna(0)
   df_v1 = pd.merge(df, df1)
   df_v2 = pd.merge(df_v1, df2, how='outer')
   df_v2['Estado'] = df_v2['Estado'].fillna('Disponible')
   df_v2 ['Comparativo'] = round(df_v2['Promedio Media']/(df_v2['Valor [En miles]']/1000),3)
   df_v2.drop(['Total Puntos Picas','Id', 'Total Puntos Sofas','Total Jugado','Titular', 'Jugado', 'Puntos Picas',
       'Puntos Sofas', 'Puntos Medias'], axis=1, inplace=True)
   df_v2 = df_v2.reindex(columns=['Nombre', 'Posicion', 'Equipo', 'Estado', '% Titular', '% Jugado', 'Forma Jugado','Promedio Picas',
       'Promedio Sofas', 'Promedio Media', 'Total Puntos Medias', 'Forma Puntos Medias', 'Valor [En miles]', 'Comparativo'])
   return df_v2

def normalize(s):
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
    )
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
    return s

def limpiar_columnas(df,columna):
    lista_nueva = []
    for i in df[columna]:
        nombra_nuevo = normalize(i)
        lista_nueva.append(nombra_nuevo)
    df[columna] = lista_nueva
    return df

def conjunto_funciones_final(df, df_valor, df_lesion):
    df_1 = elaboracion_df_compilados(df, tipo = 'normal')
    df_2 = elaboracion_df_compilados(df_1, tipo = 'final')
    df_3 = ultimos_retoques(df_2, df_valor, df_lesion)
    return df_3

