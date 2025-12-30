# bucle FOR anidado

fila = int(input("ingrese numero de filas: "))
columna = int(input("ingrese numero de columnas: "))
simbolo = input("simbolo a dibujar: ")

for i in range(fila):
    for j in range(columna):
        print(" ",simbolo," ", end="") #end ==> para que no proboque salto de linea
    print("↓")
    
    
#CLASE enumerate
programas = ["Python", "Java", "C++", "JavaScript"]

for indice, valor in enumerate(programas):
    print(f"indice del iterable {indice}, y su valor o contenido {valor}")    
#indice ==> posicion del elemento
#valor ==> valor del elemento
#enumerate ==> devuelve un objeto enumerado que contiene pares de indice y valor    

#comprension de listas (list comprehension)
cuadrados = [x**2 for x in range(10)]
print(cuadrados)

animales = ["perro", "gato", "pez", "loro"]
mayusculas = [animal.upper() for animal in animales]
print(mayusculas)  

#comprension de lista con condicion
pares = [i for i in range(20) if i % 2 == 0]
print(pares)    


#convecion de variable sin uso _
for _ in range(5):
    print(f"bucle for {_} Hola")