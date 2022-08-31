### Módulo que contiene la función para generar el reporte en html ###

import sys
# sys.path.append(folder_files+'/')

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import plotly.graph_objects as go
import plotly
from plotly.subplots import make_subplots
import plotly.io as pio
import plotly.express as px
import datapane as dp
from general_functions import mbox
from tkinter.filedialog import askopenfilename, askdirectory
import ffn


def generate_report(my_list, merged_returns):

    # Se convierten los daily returns de seire a dataframe y se fija el Index como una nueva columns
    daily_returns = pd.DataFrame(merged_returns).reset_index()

    # Se obtienen la fecha más antigua y más actual del dataframe
    ini_date = min(daily_returns["Date"])
    last_date = max(daily_returns["Date"])

    # Se crea el lineplot de rendimientos con plotly express
    returns_plot = px.line(daily_returns, x="Date", y="Adj Close",
                           title=f'Rendimientos desde {ini_date} hasta {last_date}')
    #returns_plot.show()

    # Se crea el histograma distribución de rendimientos
    returns_hist = px.histogram(daily_returns, x="Adj Close")
    #returns_hist.show()

    # Colocar en el formato adecuado los tickers seleccionados
    tickers = ", ".join(my_list)

    # Extraer las cotizaciones con la librería ffn
    prices = ffn.get(tickers, start=ini_date)

    # Gráfico cotizaciones empresas seleccionadas
    prices_plot = px.line(prices, x=prices.index, y=prices.columns,
                  labels={
                      "value": "Prices",
                  })
    #prices_plot.show()

    # Obtención de métricas útiles en stocks
    stats = prices.calc_stats()
    #stats.display()

    # Bloques de texto en markdown para añadir al reporte de datapanes
    md3 = """
    La librería ffn permite calcular todo tipo de métricas útiles de los stocks:
    """

    md4 = """
    También las caídas más acusadas en los precios con la función to_drawdown():
    """

    md5 = """
    En cuanto a la empresa combinada, se dispone de los rendimientos de la misma, los cuales se pueden visualizar en forma
    de serie temporal o histograma:
    """

    # Gráfico drawdowns empresas seleccionadas
    ax = stats.prices.to_drawdown_series()
    drawdowns_plot = px.line(ax, x=prices.index, y=prices.columns,
                  labels={
                      "value": "Prices",
                  })
    #drawdowns_plot.show()

    # Mostrar mensaje y cuadro de diálogo para elegir la carpeta en la que guardar el reporte en formato html
    mbox(message="Seleccione la carpeta en la que guardar el reporte",
                        title="Mensaje informativo")

    folder_reporte = askdirectory(title="Seleccione la carpeta en la que guardar el reporte")

    # Creación del reporte intercalando los bloques de texto con las tablas y gráficos que lo componen.
    # En los bloques formados con select se incluyen pestañas con distintos elementos como gráficos y tablas de
    # datos interactivas
    dp.Report(
        "# **Reporte stocks merged enterprise**",
        "Reporte generado a: {fecha}".format(fecha=datetime.now()),
        "En primer lugar, se muestra un gráfico con la representación de las cotizaciones de los tickers seleccionados así como"
        "la tabla con dichos valores",
        dp.Select(blocks=[
            dp.Table(prices, label='Cotizaciones empresas seleccionadas'),
            dp.Plot(prices_plot, label='Gráfico Cotizaciones')
        ]),
        dp.Text(md3),
        dp.Table(stats.stats, label='Estadísticas stocks'),
        dp.Text(md4),
        dp.Plot(drawdowns_plot, label='Drawdowns empresas seleccionadas'),
        dp.Text(md5),
        dp.Select(blocks=[
            dp.Plot(returns_plot, label='Gráfico rendimientos empresa combinada'),
            dp.Plot(returns_hist, label='Histograma rendimientos empresa combinada')
        ])
    ).save(path=folder_reporte+'/stocks_report.html', open=False)