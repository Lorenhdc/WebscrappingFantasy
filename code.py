from funciones import dataframe_lesionados, dataframe_valores, creacion_df_sofaspicas, conjunto_funciones_final
import pandas as pd
import os
os.chdir(os.path.dirname(__file__))

class Dataframe_downloading():

    def preparacion_tabla(lesionados_link, jugadores_link, sofas_link, picas_link):

        print('Your code is being executed (downloading...)')

        outname = 'fantasy_dataframe.csv'

        outdir = './dir'

        if not os.path.exists(outdir):
            os.mkdir(outdir)

        fullname = os.path.join(outdir, outname)

        dataframes_lesionados = dataframe_lesionados(lesionados_link)

        Dataframe_valor = dataframe_valores(jugadores_link)

        df_completo = creacion_df_sofaspicas(sofas_link,picas_link,list(Dataframe_valor['Id'].unique()))

        df_final = conjunto_funciones_final(df_completo,Dataframe_valor,dataframes_lesionados)
        df_final.to_csv(fullname, index=False)

        print("Executed succesfully, go and check it!")
