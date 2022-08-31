### Módulo que contiene las funciones de uso general para los distintos módulos ###
import sys
# sys.path.append(folder_files+'/')

# Se importan las librerías necesarias a emplear por las funciones aquí definidas
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import pandas_datareader as pdr
from datetime import date
from dateutil.relativedelta import relativedelta
from fake_data import create_customers_dataframe
import re
from tkinter import filedialog, messagebox
from tkinter import *
from tkinter import Tk

#############################################################################################################
#############################################################################################################

def get_data_from_web(ticker, headers):
    """
    Función para obtener los datos financieros de una empresa en particular desde la web.

    Primero se construyen los URL en los que se encontrará la información.
    De los contenidos de la página, se extraen los datos de las tablas específicas.
    Se extraen además las cotizaciones de los últimos 5 años de esa empresa.
    Se simula una base de datos de clientes para cada empresa.
    Se limpian y formatean todos los datos para insertarlos en un diccionario.
    """

    urls = {}
    df_dict={}
    # Los url se construyen con el tag que se pasa como argumento
    urls['income_annually'] = f"https://stockanalysis.com/stocks/{ticker}/financials/"
    urls['balance_annually'] = f"https://stockanalysis.com/stocks/{ticker}/financials/balance-sheet/"
    urls['cashflow_annually'] = f"https://stockanalysis.com/stocks/{ticker}/financials/cash-flow-statement/"
    urls['ratio_annually'] = f"https://stockanalysis.com/stocks/{ticker}/financials/ratios/"
    urls['directives'] = f"https://stockanalysis.com/stocks/{ticker}/company/"

    # Se itera por cada uno de los URL
    for key in urls.keys():
        response = requests.get(urls[key], headers=headers)
        # Si la respuesta es 429, esperar el tiempo indicado por el server de la página antes de volver a enviar una
        # request
        if response.status_code == 429:
            time.sleep(int(response.headers["Retry-After"])+2)
            response = requests.get(urls[key], headers=headers)

        # Se obtiene la "sopa" de html de la página
        soup = BeautifulSoup(response.content, 'html.parser')

        # Como los nombres de las tablas en la página van variando, se buscan todos los elementos "table" de la
        # misma para extraer el primero de ellos que contendrá los datos buscados. En el caso de directives
        # hay otras tablas previas por lo que se extraerá la tercera que se encuentre
        table = soup.find_all("table")
        if key != "directives":
            df = pd.read_html(str(table))[0]
        else:
            df = pd.read_html(str(table))[3]

        # Se elimina la última columna de los dataframes porque no aporta información
        if "income" in key:
            df_dict["NET_INCOME"] = df.iloc[:,:-1]

            # Se eliminan aquellas rows que contengan variaciones porque sólo interesan datos numéricos
            # y se convierte a numérico (previamente strings)
            df_dict["NET_INCOME"] = df_dict["NET_INCOME"].loc[~df_dict["NET_INCOME"].iloc[:, 1].str.contains("%")].\
                apply(pd.to_numeric, errors='ignore')

        elif "balance" in key:
            df_dict["BALANCE"] = df.iloc[:,:-1]
            df_dict["BALANCE"] = df_dict["BALANCE"].loc[~df_dict["BALANCE"].iloc[:, 1].str.contains("%")].\
                apply(pd.to_numeric, errors='ignore')

        elif "cashflow" in key:
            df_dict["CASHFLOW"] = df.iloc[:,:-1]
            df_dict["CASHFLOW"] = df_dict["CASHFLOW"].loc[~df_dict["CASHFLOW"].iloc[:, 1].str.contains("%")].\
                apply(pd.to_numeric, errors='ignore')

        # Para ratios se elimina la columna current ya que sólo se buscan datos históricos y uniformar el total
        # de columnas entre todos los dataframes
        elif "ratio" in key:
            df_dict["RATIOS"] = df.iloc[:,:-1]
            df_dict["RATIOS"].drop(['Current'], axis=1, inplace=True)
            df_dict["RATIOS"] = df_dict["RATIOS"].loc[~df_dict["RATIOS"].iloc[:, 1].str.contains("%")].\
                apply(pd.to_numeric, errors='ignore')
        # Para los directivos el tratamiento es únicamente eliminar la última columna
        elif "directives" in key:
            df_dict["DIRECTIVES"] = df.iloc[:,:-1]

        # Se define la ventana temporal para la cual se extraerán los datos del stock correpsondiente
        start = date.today() - relativedelta(years=5)
        end = date.today()

        try:
            # Algunos de los tickers de la página StockAnalysis aparecen con puntos mientras que lo que se extrae de
            # Yahoo finance viene con guiones, por ello se modifica el ticker con replace. Se usa un try except
            # porque si da error al hacer replace es debido a que no es necesraio tomar acciones
            ticker = re.sub(r'[\W_]+', '-', ticker)
            ticker = ticker.replace(".","-")
            df_dict["stocks"] = pdr.get_data_yahoo(symbols=ticker, start=start, end=end)
        except:
            df_dict["stocks"] = pd.DataFrame()

        # Se añade el dataframe de los clientes simulados haciendo un llamada a la función designada para ello.
        # Se pasa como argumento 30000 que será el total de clientes imulados por empresa
        df_dict["CUSTOMERS"]= pd.DataFrame(create_customers_dataframe(30000))

        # En el dataframe de clientes se crea la columna enterprise con el identificativo de la empresa por la que
        # se está iterando (el ticker)
        df_dict["CUSTOMERS"]["enterprise"] = ticker

    return df_dict

#############################################################################################################
#############################################################################################################

def data_to_dict(identifier, headers):
    """
    Función para almacenar en un diccionario los estados financieros y cotizaciones por empresa

    Primero se construye la url según la opción escogida por el usuario de tal manera que se seleccionen
    de la página los nombres de aquellas empresas asociadas al identifier
    """

    # Se almacena en la variable url el string con el URL de la página StockAnalysis y se mete a modo de f string
    # el ticker por el que estemos iterando
    url = f"https://stockanalysis.com/list/{identifier}/"

    # Se obtiene la respuesta y se encuentran todos los elementos tabla de la página, extrayendo el primero de ellos
    # pues será el que contenga los tickers de la categoría que se haya especificado en el UI
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find_all("table")
    df = pd.read_html(str(table))[0]

    # Se fija la extracción en 3 empresas para no tardar excesivo tiempo
    tickers_list = df["Symbol"].tolist()[:3]

    # Se define un diccionario global dentro de la función el cual contendrá los datos financieros
    # de los 5 tickers obtenidos mediante llamadas a la función get_data_from_web
    global_dict = {}
    for ticker in tickers_list:
        # Se hace la llamada a la función pasando como argumentos el ticker sobre el que se itera y los headers
        # usados para el navegador que están definidos en el módulo main
        ticker_dict = get_data_from_web(ticker, headers)
        global_dict[ticker] = ticker_dict
        print(f"{ticker} scrapeada correctamente")

    # Se devuelve el diccionario completado con los datos
    return global_dict

#############################################################################################################
#############################################################################################################

def get_merged_fin_state(dictionary, df_name):
    """
    Función para hacer la combinación de los estados financieros presentes en cada ticker.
    Toma como inputs el diccionario global con todos los tickers y los nombres de los dataframes que van a
    ser tratados "NET_INCOME", "BALANCE", "CASHFLOW", "RATIOS".

    El resultado es un diccionario con los estados financieros arriba mencionados combinados mediante una suma por
    años
    """

    # Se define un dataframe resultado vacío
    merged_df = pd.DataFrame()

    # Se itera por las claves del diccionario que
    for key in dictionary:
        # Se guarda en una variable el dataframe correspondiente a la clave y el nombre del estado financiero
        # que se desea extraer
        indiv_df = dictionary[key][df_name]

        # Si es la primera iteración se concatenan el dataframe dispuesto para el merge y el nuevo dataframe que
        # que se ha extraído con la clave y el nombre del estado financiero (de forma que es como si quedase sólo el
        # del estado financiero.
        if merged_df.empty:
            merged_df = pd.concat([merged_df, indiv_df], axis=1)
            # Se extraen los nombres de las columnas y se convierten a tipo lista
            cols_to_convert = merged_df.columns.to_list()[1:]
            # Se aplica a todos ellos la conversión a tipo numérico sustituyendo por NA aquellos datos que no sean
            #válidos
            merged_df[cols_to_convert] = merged_df[cols_to_convert].apply(pd.to_numeric, errors='coerce', axis=1)
            merged_df = merged_df.groupby(level=0, axis=1).sum()
        else:
            # Si el datafame no está vacío significa que ya hay estados financieros por lo que se hace un merge de
            # los estado que ya estaban y los nuevos tomando como clave la columna ["año"] idéntica para todos los
            # estados y haciendo un outer join porque en algunas de las empresas no coinciden todos los estados
            # contables o ratios
            merged_df= pd.merge(merged_df, indiv_df, on=['Year'], how = "outer")

            # Se seleccionan únicamente las primeras 10 columnas para convertir a dato numérico porque en la última
            # se sitúan los propios registros
            cols_to_convert = merged_df.columns.to_list()[:10]
            # merged_df[cols_to_convert] = merged_df[cols_to_convert].apply(pd.to_numeric, errors='coerce', axis=1)

            cols = [i for i in merged_df.columns if i not in ["Year"]]
            for col in cols:
                merged_df[col] = pd.to_numeric(merged_df[col], errors="coerce")

            # Para las columnas se extraen los primeros 4 caracteres del nombre (correspondientes únicamente al año)
            merged_df.columns = merged_df.columns.str[:4]

            # En el dataframe combinado se suman las columnas numéricas presentes anteriormente y las nuevas añadidas.
            merged_df = merged_df.groupby(level=0, axis=1).sum()

    # Se devuelve el dataframe combinado
    return merged_df

#############################################################################################################
#############################################################################################################

def get_merged_stocks(dictionary, df_name):
    """
    Función para hacer la combinación de las rentabilidades diarias presentes en cada ticker.
    Toma como inputs el diccionario global con todos los tickers y el nombre del dataframe que va a ser tratado:
    "stocks".

    El resultado que devuelve es dataframe de las rentabilidades diarias acumuladas acumulados sumados por años
    de los distintos tickers presentes en el diccionario el cual se ha pasado como argumento
    """

    # Se define un dataframe vacío para almacenar el resultado del merge
    merged_stocks = pd.DataFrame()
    for key in dictionary:
        # Se asigna a una variable el dataframe en cuestión de la iteración
        stock = dictionary[key][df_name]

        # Se obtienen las rentabilidades diarias de dicho dataframe del precio de cierre
        daily_returns = stock['Adj Close'].pct_change()

        if merged_stocks.empty:
            # Si el dataframe resultado está vacío simplemente pasa a ser el dataframe con las rentabilidades
            # diarias
            merged_stocks = daily_returns
        else:
            # Si el dataframe resultado no está vacío, ya tiene stocks almacenados y se realizará un merge por
            # el índice de ambos dataframes
            merged_stocks = pd.merge(merged_stocks, daily_returns, left_index=True, right_index=True, how="left")

            # Se extraen los primeros 10 caracteres del nombre de las columnas para evitar el _x y _y del merge
            merged_stocks.columns = merged_stocks.columns.str[:9]

            # Se cambinan los 2 stocks que se han incluido calculando su media, no sumando
            merged_stocks = merged_stocks.groupby(level=0, axis=1).mean()

    return merged_stocks

#############################################################################################################
#############################################################################################################

def get_merged_directives(dictionary, df_name):
    """
    Función para hacer la combinación de los directivos presentes en cada ticker.
    Toma como inputs el diccionario global con todos los tickers y el nombre del dataframe que va a ser tratado:
    "directives".

    El resultado es un dataframe que contiene a los directivos de todas las empresas cuyo ticker se encuentra
    entre las keys del diccionario que se ha pasado como argumento
    """

    # Se crea un dataframe vacío que almacenará el resultado
    merged_directives = pd.DataFrame()
    for key in dictionary:
        # Para cada ticker en el diccionario pasado como argumento se almacena en la variable directives
        # el dataframe con los directivos de ese ticker
        directives = dictionary[key][df_name]

        # Se concatenan los directivos de cada empresa en un dataframe a lo largo del eje vertical
        merged_directives = pd.concat([merged_directives, directives], axis=0, ignore_index=True)

    return merged_directives

#############################################################################################################
#############################################################################################################

def get_merged_customers(dictionary, df_name):
    """
    Función para hacer la combinación de los clientes presentes en cada ticker.
    Toma como inputs el diccionario global con todos los tickers y el nombre del dataframe que va a ser tratado:
    "customers".

    El resultado es un dataframe que contiene a los customers de todas las empresas cuyo ticker se encuentra
    entre las keys del diccionario que se ha pasado como argumento
    """

    # Se crea un dataframe vacío que contendrá el resultado
    merged_customers = pd.DataFrame()
    for key in dictionary:
        # Se almacenan los clientes en una variable
        customers = dictionary[key][df_name]

        # Se van concatenando los clientes de cada ticker en el dataframe resultado
        merged_customers = pd.concat([merged_customers,customers], axis=0, ignore_index=True)

    return merged_customers

#############################################################################################################
#############################################################################################################

def get_merged_price(dictionary, df_name):
    """
    Función para hacer la combinación de los precios diarios de cierre presentes en cada ticker.
    Toma como inputs el diccionario global con todos los tickers y el nombre del dataframe que va a ser tratado:
    "stocks".

    El resultado es un dataframe que contiene a los precios diarios de cierre de todas las empresas cuyo ticker
     se encuentra entre las keys del diccionario que se ha pasado como argumento
    """

    # Se crea un dataframe vacío que servirá como resultado del acumulado
    merged_stocks_price = pd.DataFrame()
    for key in dictionary:
        # Se almacena en una variable el dataframe de los stocks del ticker por el que se itera
        stock = dictionary[key][df_name]
        # Se almacena en daily_price el dataframe sin el index
        daily_price = stock['Adj Close'].reset_index()

        # Se renombra la columna Adj Close con el ticker por el que estemos iterando
        daily_price.rename(columns = {'Adj Close':key}, inplace = True)

        if merged_stocks_price.empty:
            # Si el dataframe resultado está vacío se asigna al mismo el dataframe con los precios diarios
            merged_stocks_price = daily_price
        else:
            # Si no está vacío, se hace un merge en base a la columna Date para que se vayan situando en columnas
            # los precios de cierre de los distintos tickers
            merged_stocks_price = pd.merge(merged_stocks_price, daily_price, on="Date", how="left")

    return merged_stocks_price

#############################################################################################################
#############################################################################################################

def get_global_dict(financial_statements, dict):
    """
    Devuelve como resultado un diccionario con los estados financieros, clientes y stocks combinados.

    Recibe como inputs los nombres de los dataframes (estados financieros) y el diccionario que contiene los
    estados financieros por ticker

    """

    # Se define un diccionario vacío
    global_dict_merged = {}

    # Se itera por los estados financieros que se han pasado como input llamando a la función para
    # combinarlos
    for financial_statement in financial_statements:
        global_dict_merged[financial_statement] = get_merged_fin_state(dict, financial_statement)

    # Se van añadiendo keys por cada uno de los dataframes que nos interesa tener en la empresa combinada que será
    # el resultado final
    global_dict_merged["DAILY_RETURNS"] = get_merged_stocks(dict, "stocks")
    global_dict_merged["DAILY_PRICES"] = get_merged_price(dict, "stocks")
    global_dict_merged["DAILY_PRICES"].set_index("Date", inplace=True)
    global_dict_merged["DIRECTIVES"] = get_merged_directives(dict, "DIRECTIVES")
    global_dict_merged["CUSTOMERS"] = get_merged_customers(dict, "CUSTOMERS")

    return global_dict_merged

#############################################################################################################
#############################################################################################################

def mbox(title, message):
    """
    Devuelve un cuadro de diálogo con un título y mensaje personalizados

    Recibe como inputs el título del cuadro de diálogo y el mensaje que se mostrará en él

    """
    root = Tk()
    root.withdraw()
    messagebox.showinfo(title=title,
                        message=message)
