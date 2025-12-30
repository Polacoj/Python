from datetime import datetime, timedelta
import locale

print(f"Fecha y hora actual: {datetime.now()}")

fecha_precisa = datetime(2025, 12, 25, 15, 30)
print(fecha_precisa)

#formateo de fecha y hora ---> .strftime
fecha = datetime.now()
fecha_formateada = fecha.strftime("%d-%m/%y %H:%M:%S")
print(fecha_formateada)

#convertir fecha a otro idioma ---> locale
locale.setlocale(locale.LC_TIME, "es_AR.UTF-8")
fecha = datetime.now()
fecha_formateada_es = fecha.strftime("%A, %d de %B de %Y")
print(fecha_formateada_es)

#operaciones con fechas y horas ---> timedelta
hoy = datetime.now()
manana = hoy + timedelta(days=1)
ayer = hoy - timedelta(days=1)
print(f"Hoy: {hoy}")
print(f"Fecha actual: {hoy.strftime("%d-%m-%y")}")
print(f"Mañana: {manana}")
print(f"Fecha de mañana: {manana.strftime("%d-%m-%y")}")
print(f"Ayer: {ayer}")

#obtener componentes individuales de fecha y hora
fecha = datetime.now()
print(f"Año: {fecha.year}")
print(f"Mes: {fecha.month}")
print(f"Día: {fecha.day}")
print(f"Hora: {fecha.hour}")