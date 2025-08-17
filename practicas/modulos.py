from datetime import datetime
from math import pow as potencia
from math import pi

print(pi)


variable = potencia(2, 5)
print(variable)


ahora = datetime.now()  # -----variable en donde le asignamos el dia -----

print(ahora.timestamp())

fecha_stamp = datetime.fromtimestamp(timestamp=2000)

print(fecha_stamp)
