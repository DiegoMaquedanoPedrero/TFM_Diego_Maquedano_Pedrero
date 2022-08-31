### Módulo que contiene la función principal para recopilar datos de la web llamando a las demás funciones ###
global selected_tickers
selected_tickers = []

import sys
# sys.path.append(folder_files+'/')

def importing_module(selection, headers, financial_statements):

    # Se define la variable global que devolverá la función y que servirá de output para la generación del reporte
    global merged_returns

    # Se importan las funciones definidas en cada uno de los módulos designados para tal fin
    from general_functions import data_to_dict, get_global_dict, get_data_from_web
    from insert_into_db import create_db
    from insert_into_excel import insert_into_excel

    # Mostrar por consola un mensaje informativo
    print("Scrapeando datos.......")

    # Según haya sido la opción escogida en el menú de inicio se ejecutarán procesos diferentes
    if selection["name"] == "market_cap":
        # Se define el tag propio para esta elección que identifica dentro del url de la página el apartado al que acceder
        identifier = "biggest-companies"

        # Se aplica la función para convertir los datos de la web a dataframes almacenados en un diccionario por cada empresa
        biggest_us_market_dict = data_to_dict(identifier, headers)
        selection["values"] = biggest_us_market_dict.keys()

        # Llamada a la función para introducir las empresas en la base de datos y mostrar por consola
        # mensaje informativo
        print("Insertando datos en la base de datos.......")
        create_db(biggest_us_market_dict,multiple = True, name="")

        # Llamada a la función para crear el diccionario combinado con todas las empresas
        market_dict_merged = get_global_dict(financial_statements, biggest_us_market_dict)

        # Se asigna a la variable merged_returns la tabla DAILY_RETURNS almacenada con dicha clave dentro del
        # diccionario de dataframes
        merged_returns = market_dict_merged["DAILY_RETURNS"]

        # Llamada de nuevo a la función para insertar en la base de datos un único dataframe (el de la empresa
        # combinada)
        create_db(market_dict_merged, multiple=False, name="market_merged")

        # Llamada a la función para crear un excel con cada pestaña siendo un resultado financiero de la empresa
        # combinada
        insert_into_excel(market_dict_merged)

    # Las mismas explicaciones que en el primer apartado se aplican a cada uno de los elementos siguientes del código
    elif selection["name"] == "most_revenues":
        identifier = "highest-revenue"
        biggest_us_revenues_dict = data_to_dict(identifier, headers)
        selection["values"] = biggest_us_revenues_dict.keys()
        print("Insertando datos en la base de datos.......")
        create_db(biggest_us_revenues_dict,multiple=True, name="")
        revenues_dict_merged = get_global_dict(financial_statements, biggest_us_revenues_dict)
        merged_returns = revenues_dict_merged["DAILY_RETURNS"]
        create_db(revenues_dict_merged, multiple=False, name="revenues_merged")
        insert_into_excel(revenues_dict_merged)

    elif selection["name"] == "most_employees":
        identifier = "most-employees"
        biggest_us_employees_dict = data_to_dict(identifier, headers)
        selection["values"] = biggest_us_employees_dict.keys()
        print("Insertando datos en la base de datos.......")
        create_db(biggest_us_employees_dict, multiple=True, name ="")
        most_emp_dict_merged = get_global_dict(financial_statements, biggest_us_employees_dict)
        merged_returns = most_emp_dict_merged["DAILY_RETURNS"]
        create_db(most_emp_dict_merged, multiple=False, name="employees_merged")
        insert_into_excel(most_emp_dict_merged)

    elif selection["name"] == "oldest":
        identifier = "oldest-companies"
        oldest_us_dict = data_to_dict(identifier, headers)
        selection["values"] = oldest_us_dict.keys()
        print("Insertando datos en la base de datos.......")
        create_db(oldest_us_dict,multiple=True, name="")
        oldest_dict_merged = get_global_dict(financial_statements, oldest_us_dict)
        merged_returns = oldest_dict_merged["DAILY_RETURNS"]
        create_db(oldest_dict_merged, multiple=False, name="oldest_merged")
        insert_into_excel(oldest_dict_merged)

    # Si se selecciona la opción personalizada el proceso es diferente a todos los anteriores que eran uniformes
    elif selection["name"] == "customized":
        # Se crea un diccionario vacío
        customized_dict = {}

        # Para cada ticker de entre los escogidos por el usuario se llama a la función para obtener sus datos
        for ticker in selection["values"]:
            ticker_dict = get_data_from_web(ticker, headers)

            # Se completa el diccionario colocando los tickers como claves
            customized_dict[ticker] = ticker_dict

            # Mostrar por consola mensaje informativo
            print(f"{ticker} scrapeada correctamente")

        # Tras terminar el proceso de construcción del diccionario se inicia el de inserción en base de datos
        print("Insertando datos en la base de datos.......")
        # A partir de este momento se siguen los mismos pasos que con el resto de diccionarios y estados financieros
        create_db(customized_dict, multiple=True, name="")
        customized_dict_merged = get_global_dict(financial_statements, customized_dict)
        merged_returns = customized_dict_merged["DAILY_RETURNS"]
        create_db(customized_dict_merged, multiple=False, name="customized_merged")
        insert_into_excel(customized_dict_merged)

    return merged_returns