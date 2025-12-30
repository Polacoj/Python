#peticiones a una api sin dependencias externas, solo modulos estandar nativos
import urllib.request
import json 

api_url = "https://jsonplaceholder.typicode.com/posts"

repuesta = urllib.request.urlopen(api_url)#abrir la url
datos = repuesta.read()#leer los datos
json_datos = json.loads(datos.decode("utf-8"))#decodificar los datos a utf-8 y convertirlos a json
print(json_datos)#imprimir los datos
print(type(json_datos))
print(json_datos[3])   
repuesta.close()

#lo mismo con un try except
try:
    api_url = "https://jsonplaceholder.typicode.com/posts"
    repuesta = urllib.request.urlopen(api_url)#abrir la url
    datos = repuesta.read()#leer los datos
    json_datos = json.loads(datos.decode("utf-8"))#decodificar los datos a utf-8 y convertirlos a json
    print(json_datos)#imprimir los datos
    print(type(json_datos))
    print(json_datos[3])   
    repuesta.close()
except Exception as e:
    print("Error al conectar con la API:", e)

#request con dependencias externas
import requests

print("Haciendo GET con requests:")
api_url = "https://jsonplaceholder.typicode.com/posts"
repuesta = requests.get(api_url)
json_datos = repuesta.json()
print(json_datos)


