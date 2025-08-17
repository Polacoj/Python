# Dada una URL con parámetros, crea una función que obtenga sus valores.
# No se pueden usar operaciones del lenguaje que realicen esta tarea directamente.

# Ejemplo: En la url https://retosdeprogramacion.com?year=2023&challenge=0
# los parámetros serían ["2023", "0"]

# def url(direccion):
#     valor = ""
#     num = str([0,1,2,3,4,5,6,7,8,9])
#     print("hola")
#     for i in direccion:
#         if i not in num:
#             continue
#         if i in num:
#             valor += i
#         valor += "/"
            
#     print(valor)
    
def url(url):    
    components = url.split("&")

    for component in components:
        if "=" in component:
            param = component.split("=")
            if len(param) == 2 and param[1] != "":
                print(param[1])
    
url(input("ingrese la direccion web: "))