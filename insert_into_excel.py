### Módulo que contiene la función para generar el excel con los datos de la empresa combinada ###

import sys
# sys.path.append(folder_files+'/')

# Se importan los módulos necesarios
import pandas as pd
from tkinter import filedialog
from general_functions import mbox

def insert_into_excel(dict):
    """
    Función para crear un excel que contenga los datos de la empresa combinada

    Toma como input el diccionario con los tickers de la empresa combinada
    """

    # Se muestra un cuadro de diálogo mediante la llamada a la función mbox con título y mensaje personalizado
    mbox(title="Mensaje informativo",
                        message="Seleccione la carpeta en la que guardar el archivo excel con el resultado")

    # Se abre el selector para escoger la carpeta en la que guardar el excel resultado
    folder_selected = filedialog.askdirectory()

    # El path para guardar el resultado es la combinación de la carpeta elegida por el usuario y el nombre que se
    # le da al excel (por defecto merged_enterprise)
    path = folder_selected + "/merged_enterprise.xlsx"

    # Se crea el excel writer para almacenar en cada pestaña del resultado uno de los dataframes (estados
    # financieros) de la empresa combinada. En los dataframes relacionados con stocks, los índices son necesarios
    # porque muestran las fechas de manera que se hace una distinción al exportar entre esos 2 y el resto
    with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
        for key in dict:
            if (key == "DAILY_RETURNS") | (key =="DAILY_PRICES"):
                dict[key].to_excel(writer, sheet_name=key, index=True)
            else:
                dict[key].to_excel(writer, sheet_name=key, index=False)

    # Mensaje para indicar que ha finalizado el proceso
    mbox(title="Mensaje informativo",
                        message="Archivo generado correctamente")