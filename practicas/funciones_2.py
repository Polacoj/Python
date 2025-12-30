#funciones con parateros posicionales y por defecto
def posicional(nombre, edad, ciudad):
    """funcion que recibe parametros posicionales"""
    print(f"Hola {nombre}, tienes {edad} años y vives en {ciudad}")

posicional("alexis", 30, "cordoba")
posicional(30, "cordoba", "alexis") #cambia el orden y no tiene sentido

#argumentos por clave y valor
posicional(ciudad="buenos aires", nombre="alexis", edad=47) #no importa el orden


#Argumentos de longitud variable
def variable(*args):
    """funcion que recibe una cantidad variable de argumentos"""
    suma = 0
    for i in args:
        suma += i
    return suma
        
print(f"la suma de 3, 5, 8, 4 es {variable(3, 5, 8, 4)}")
        
        
#--------Argumentos de longitud variable con clave y valor
def variable_kv(**kwargs):
    """funcion que recibe una cantidad variable de argumentos con clave y valor"""
    for clave, valor in kwargs.items():
        print(f"{clave} : {valor}") 

variable_kv(nombre="alexis", edad=30, ciudad="cordoba")
variable_kv(marca="ford", modelo="fiesta", anio=2020)
variable_kv(pais="argentina", capital="buenos aires", poblacion=45000000)