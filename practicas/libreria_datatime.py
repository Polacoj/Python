#'DATETIME'------administra fecha y horario todo en uno  -----------
from datetime import datetime

ahora = datetime.now()
print(ahora)

print(ahora.year)
print(ahora.month)
print(ahora.day)
print(ahora.hour)
print(ahora.minute)
print(ahora.second)

timestmp = ahora.timestamp() #---asigna a la variable 'timestmp' y le otorga el METODO TIMESTAMP al dato guardado en la variable 'ahora (que contiene la fecha actual)' 
print (timestmp)

from datetime import date

mi_year = date(2022, 1, 1)
actual = date.today()

print(actual)
print(actual.year)
print(actual.month)
print(actual.day)
#------modificar fecha con operaciones --------
actual = date(actual.year + 3, actual.month - 4, int(actual.day /2))
print(f"suma de fecha fijada {actual}")

from datetime import time

actual = time(20, 12, 45)
print(actual)
print(actual.hour)
print(actual.minute)
print(actual.second)

diferencia = date.year() - mi_year
print(diferencia)

from datetime import timedelta

delta = timedelta()

