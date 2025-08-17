# bucle FOR anidado

fila = int(input("ingrese numero de filas: "))
columna = int(input("ingrese numero de columnas: "))
simbolo = input("simbolo a dibujar: ")

for i in range(fila):
    for j in range(columna):
        print(" ",simbolo," ", end="") #end ==> para que no proboque salto de linea
    print("↓")