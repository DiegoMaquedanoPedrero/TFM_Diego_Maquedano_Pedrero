### Módulo que contiene las funciones para llevar a cabo el proceso de inserción en la base de datos remota ###

# Se importan los paquetes necesarios
import mysql.connector
from mysql.connector import Error
from sqlalchemy import create_engine
import re

def create_db(dict, multiple, name):
    """
    Función para crear una base de datos de Mysql en un repositorio remoto hosteado por AWS

    Toma como input el diccionario que contiene la información de cada uno de los tickers con los
    datos financieros, si la inserción va a ser multiple o no (para la inserción del dataframe combinado en vez de
    la de todos los tickers) y el nombre que se le va a dar a la base de datos cuando esta sea creada
    """

    try:
        # Dentro del statement try se crea la conexión con la base de datos hosteada por AWS pasando el usuario
        # y la contraseña
        connection = mysql.connector.connect(host = 'databasetfm.ct7rynr68acs.eu-west-2.rds.amazonaws.com',
                                             user = 'admin',
                                             password = 'tfm_master')

        # Si se ha establecido la conexión correctamente, se muestra por consola
        if connection.is_connected():
            db_Info = connection.get_server_info()
            print("Connected to MySQL Server version ", db_Info)

        # Se crea el cursor para ejecutar instrucciones de sql
        mycursor = connection.cursor()

        # Se eliminan las bases de datos (si existen) con datos combinados para evitar duplicidades
        mycursor.execute(f"DROP DATABASE IF EXISTS market_merged")
        mycursor.execute(f"DROP DATABASE IF EXISTS revenues_merged")
        mycursor.execute(f"DROP DATABASE IF EXISTS employees_merged")
        mycursor.execute(f"DROP DATABASE IF EXISTS oldest_merged")
        mycursor.execute(f"DROP DATABASE IF EXISTS customized_merged")

        # Si la inserción múltiple está activada
        if multiple==True:
            # Se itera por cada una de las claves (tickers) del diccionario que se ha pasado como argumento
            for key in dict:
                # Se eliminan mediante Regex los caracteres no alfanuméricos
                key_clean = re.sub(r'[^a-zA-Z0-9]', '', key)

                # Se ejecuta la sentencia de SQL para eliminar la base de datos con el nombre de ese mismo ticker
                # si ya existía con la finalidad de que se disponga de los últimos datos disponibles
                mycursor.execute(f"DROP DATABASE IF EXISTS {key_clean}")

                # Después de borrar se crea la base de datos con el nombre del ticker por el que se itera
                mycursor.execute(f"CREATE DATABASE {key_clean}")

                # Por cada clave (dataframe) dentro del ticker se crea una tabla dentro de la base de datos con el
                # nombre del ticker mediante la llamada a la función insert_table_df
                for key2 in dict[key]:
                    insert_table_db(db_name=key_clean, table=dict[key][key2], table_name=key2)
                    print("Tabla insertada")
        else:
            # Si la selección no es múltiple, simplemente se elimina de la base de datos el nombre que se ha pasado
            # como argumento
            mycursor.execute(f"DROP DATABASE IF EXISTS {name}")

            # Se crea la base de datos
            mycursor.execute(f"CREATE DATABASE {name}")
            print("Base de datos creada")

            # Para cada dataframe dentro del diccionario se crea una tabla dentro de la base de datos con el
            # nombre del ticker mediante la llamada a la función insert_table_df
            for key in dict:
                insert_table_db(db_name=name, table=dict[key], table_name=key)

        # Se elimina el cursor y se cierra la conexión con la base de datos tras terminar
        mycursor.close()
        connection.close()

    except Error as e:
        print("Error while connecting to MySQL", e)

#############################################################################################################
#############################################################################################################

def insert_table_db(db_name, table, table_name):
    """
    Función para insertar un dataframe a modo de tabla en la base de datos hosteada por AWS

    Toma como input el nombre de la base de datos en la que se debe insertar la tabla, la propia tabla (dataframe)
    a insertar y el nombre que se va a dar a esa tabla
    """

    # Se indican los argumentos necesarios para la conexión
    host = 'databasetfm.ct7rynr68acs.eu-west-2.rds.amazonaws.com'
    user = "admin"
    password = "tfm_master"

    dbname = db_name

    # Se crea el motor de inserción con sql alchemy
    engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}"
                           .format(host = host, db = dbname, user = user, pw = password))

    # Se inserta el df como tabla en la base de datos
    table.to_sql(table_name,engine, if_exists='replace', index = False)