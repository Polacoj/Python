'''
# ----------SIN retorno de valor-(MUESTRAN mensaje)--------
def Saludar():
    print("hola MUNDO")
    print("vamos todos".encode())


Saludar()


def NuevoSaludo(nombre):
    print(f"Como va {nombre}\n")
    if nombre == "no tengo":
        print("Que tal desconocido\n")


dato = input("nombre :? ")
NuevoSaludo(dato)


def Multi(num):
    for i in range(1, 11):
        print(f" {num} X {i} = {num*i}")


numero = int(input("Numero a multiplicar: "))
Multi(numero)

# ------------CON retorno de valor-----------

def Otro_multi(num_uno, num_dos):
    res = num_uno * num_dos
    return res

print(Otro_multi(4, 7)) # ----------OPCION 1 para ver el resultado de la funcion

valor = Otro_multi(7, 9)    # ------- OPCION 2 pra mostrar el resultado
print(valor)


def Valores_Multi():
    return "cadena de texto", 34, ['l', 'i', 's', 't', 'a']

c, n, l = Valores_Multi()  # ----tomamos una variable para cada una las operaciones de la funcion (cadena-numero-lista)

print(c)
print(n)
print(l)


# ------ARGUMENTO por valor------

def doblar_numero(numero):
    numero *= 2
    print(numero)

n = 5
doblar_numero(n) # se le pasa una copia del valor de N, por lo que el VALOR original de N no se altera
print(n)

# -------ARGUMENTO por referencia--Se usa para listas----tuplas----diccionarios-----

def doblar_numeros(numeros):
    #for i in range(len(lista)):         ---------Son el mismo proceso que enumerate------
    for i, lista in enumerate(numeros):
        numeros[i] *= 2

lista = [3, 6, 8, 23]

doblar_numeros(lista[:])    # -------solo toma una copia de la lista y no la modifica
print(lista)

doblar_numeros(lista)       # ----- modifica la lista
print(lista)

# --------Funciones recursivas-----------
def cuenta_regresiva(num):
    if num > 0:
        print(num)
        cuenta_regresiva(num - 1)
    else:
        print("Caboooom !!!!!")

cuenta_regresiva(7)

def func():
    return "hola"

frase = func()
print(frase)

# ------funcion con varios PARAMETROS y MAIN------
def saludo(nombre):
    print('Hola', nombre)

def saludo_dos(*nombre):
    for i in nombre:
        print("hola", i)

def main():
    saludo("juan")
    saludo_dos("alexis", "paola", "ernesto")

if __name__ == '__name__':
    main()

main()'''

"""# --------------funcion para PARAMETROS dobles tipo DICCIONARIO---------
def agenda(**datos):
    datos = {}
    x = input("Ingrese cantidad de datos: ")
    for key in range(x):
        for value in x: #datos.items():
            datos = input("Clave= {}, valor{}".format(key, value))
            #datos[value] = input("valor= ")
#    print(datos())


agenda()

nodos = "abcdef"

vertices = {}

for origen in nodos:
  vertices[origen] = {}
  for destino in nodos:
    if origen == destino:
       continue # Este caso nos lo saltamos
    distancia = input("Distancia {}--{}? ".format(origen, destino))
    distancia = int(distancia)
    if distancia != 0:
       vertices[origen][destino] = distancia

print(vertices.items())"""

# -------------Funciones con parametros por defecto--------


def nombre(nom='alexis'):
    return f"hola {nom} como estas??"


print(nombre())
print(nombre("jose"))