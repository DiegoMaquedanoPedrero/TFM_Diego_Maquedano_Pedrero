### Módulo principal que define la interfaz de usuario completa y se llaman a las funciones que permiten ###
### el funcionamiento de la herramienta ###

from custom_requirements import install_custom_requirements

print("Instalando los paquetes necesarios... En la primera ejecución el proceso puede demorarse unos minutos")
install_custom_requirements()

from tkinter.filedialog import askdirectory
from tkinter import *
from tkinter import Tk
from tkinter import filedialog
import sys
global folder_files

Tk().withdraw()
folder_files = filedialog.askdirectory(title="Seleccione la carpeta donde se encuentran los scripts descargados para la ejecución")

sys.path.append(folder_files+'/')

# Se importan las librerías necesarias
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QMessageBox
from PyQt5 import QtGui, uic, QtWidgets,QtCore
import requests
from bs4 import BeautifulSoup
import pandas as pd
from tkinter import messagebox
from tkinter import Tk
from get_from_web import importing_module
from general_functions import mbox
from stocks_report import generate_report

try:
    # Definir los headers para llevar a cabo el web scrapping
    headers= {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    # Definir la variable estados financieros que luego se pasará como argumento de las funciones
    financial_statements = ["NET_INCOME", "BALANCE", "CASHFLOW", "RATIOS"]

    # Las siguientes líneas permiten extraer las principales compañías que se muestran al usuario para que las elija
    # en la interfaz
    url = f"https://stockanalysis.com/list/biggest-companies/"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find_all("table")
    df = pd.read_html(str(table))[0]
    list_tickers = df["Symbol"].unique().tolist()

    # En las siguientes líneas se irá definiendo la estructura y funcionamiento de la interfaz de usuario
    # Se crea primero la clase MainDialog que será la pantalla principal
    class MainWindow(QDialog):

        # Con este código se llama al archivo home_window.ui creado con Qt Designer y que da formato a esta pantalla.
        # Se define también el evento de click en el botón y llamada a la función
        def __init__(self):
            super(MainWindow, self).__init__()
            uic.loadUi(folder_files+"/home_window.ui", self)
            self.pushButton.clicked.connect(self.gotoScreen2)

        # Esta función se utiliza para cuando el usuario clique en el botón pushButton se muestre la siguiente pantalla
        def gotoScreen2(self):
            screen2 = Screen2()
            widget.addWidget(screen2)
            widget.setCurrentIndex(widget.currentIndex()+1)

    # Definición de la segunda pantalla
    class Screen2(QDialog):
        # Se llama al archivo ui que da formato a esta segunda pantalla y los eventos que llaman a funciones al pulsar
        # botones
        def __init__(self):
            super(Screen2, self).__init__()
            uic.loadUi(folder_files+"/selector_window.ui", self)
            self.returnButton.clicked.connect(self.gotoScreen1)
            self.otherButton.clicked.connect(self.gotoScreen3)
            self.acceptButton.clicked.connect(self.closeme)

        # El botón de aceptar comprueba primero si se ha marcado alguna de las opciones disponibles. En caso positivo
        # se asigna el valor a la variable y se cierra la interfaz de usuario.
        # En caso contrario se muestra un mensaje informativo y se vuelve a la pantalla
        def closeme(self):
            global selection
            selection = {}
            if self.marketButton.isChecked():
                selection["name"] = "market_cap"
                QtCore.QCoreApplication.instance().quit()

            elif self.incomeButton.isChecked():
                selection["name"] = "most_revenues"
                QtCore.QCoreApplication.instance().quit()

            elif self.employeeButton.isChecked():
                selection["name"] = "most_employees"
                QtCore.QCoreApplication.instance().quit()

            elif self.oldButton.isChecked():
                selection["name"] = "oldest"
                QtCore.QCoreApplication.instance().quit()

            else:
                selection["name"]= ""
                Tk().withdraw()
                messagebox.showwarning(title="Información", message="Debe seleccionar alguna de las opciones o clicar en selección personalizada")

        # Se define la función para volver a la pantalla principal (return button)
        def gotoScreen1(self):
            mainwindow=MainWindow()
            widget.addWidget(mainwindow)
            widget.setCurrentIndex(widget.currentIndex()+1)

        # Se define la función para avanzar a la 3 pantalla en caso de elegir búsqueda personalizada
        def gotoScreen3(self):
            screen3=Screen3()
            widget.addWidget(screen3)
            widget.setCurrentIndex(widget.currentIndex()+1)

    # Se define la clase para la búsqueda personalizada
    class Screen3(QDialog):
        # Se carga el ui que da formato a esta página
        def __init__(self):
            super(Screen3, self).__init__()
            uic.loadUi(folder_files+"/custom_search.ui", self)

            # Se añaden al elemento lista del ui los tickers extraídos al comienzo de este módulo
            self.listWidget.addItems(list_tickers)

            # Se definen los eventos y funciones asociados
            self.returnButton3.clicked.connect(self.gotoScreen2)
            self.acceptButton3.clicked.connect(self.closeme)

        # En caso de pulsar aceptar se comprueba si se ha seleccionado algún elemento de la lista. En caso positivo,
        # se añade el valor customized al diccionario resultado junto con los tickers escogidos a modo de lista para
        # su posterior uso en las funciones. En caso contrario se muestra mensaje informativo
        def closeme(self):
            if self.listWidget.selectedItems() != []:
                global selection
                selection={}
                selection["name"] ="customized"
                selection["values"] = [item.text() for item in self.listWidget.selectedItems()]
                QtCore.QCoreApplication.instance().quit()
            else:
                Tk().withdraw()
                messagebox.showwarning(title="Información", message="Debe seleccionar alguno de los tickers de la lista o volver atrás")

        # Si se clica en volver, se vuelve a la pantalla 2
        def gotoScreen2(self):
            screen2=Screen2()
            widget.addWidget(screen2)
            widget.setCurrentIndex(widget.currentIndex()+1)

    # Estas líneas de código permiten configurar la app y mostrar la pantalla principal cuando se ejecute
    app = QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()
    mainwindow=MainWindow()
    widget.addWidget(mainwindow)
    widget.show()

    # Se procede a la ejecución de la app
    try:
        app.exec()
        # Si se ha seleccionado alguna de las opciones de la aplicación se ejecuta llamando a la función principal
        # que se encargará de llamar a las demás y cuyo funcionamiento está comentado en sus respectivos módulos.
        # Posteriormente se finaliza el proceso mostrando mensaje informativo
        if selection["name"] != "":

            # Se asigna a la variable el resultado de la función que ejecuta la aplicación
            merged_returns = importing_module(selection=selection, headers=headers,
                             financial_statements=financial_statements)
            mbox(title="Mensaje informativo", message="Generando reporte html")

            # Se convierte a lista la selección de tickers usados para pasarse como argumento de la función encargada
            # de generar el reporte
            my_list = list(selection["values"])

            # Llamada a la función para generar el reporte
            generate_report(my_list, merged_returns)
            mbox(title="Mensaje informativo", message="Proceso finalizado")
            sys.exit()
        else:
            sys.exit()
    except:
        print("Exiting")

except Exception as e:
    messagebox.showinfo(message=e, title="Error")
