### Módulo que contiene la función para crear datos de clientes simulados ###

# Importar módulos y funciones requeridas
from mimesis import Person
from mimesis import Payment
from mimesis import Address
from mimesis import Datetime
import random

# Definir las clases para las distintas tipologías de datos en mimesis
person = Person('en')
person = Person()
payment = Payment()
address = Address()
datetime = Datetime()

# Se define la función
def create_customers_dataframe(num=1):
    """
    Devuelve un dataframe con tantos datos de clientes generados aleatoriamente con la librería mimesis como el
    número especificado en el argumento de la función. Entre estos datos se encuentran nombre, dirección
    mail,ciudad, estado, edad, fecha de registro, cantidad acumulada en la empresa, nº tarjeta y fecha de expiración
    de la tarjeta

    """
    output = [{"name":person.full_name(),
                   "address":address.address(),
                   "name":person.name(),
                   "email":person.email(),
                   "city":address.city(),
                   "state":address.state(),
                   "age":person.age(),
                   "registration_time":datetime.datetime(),
                   "cum_spent_amount":random.randint(100,100000),
                   "credit_card_number":payment.credit_card_number(),
                   "expiration_date":payment.credit_card_expiration_date()} for x in range(num)]
    return output
