mascotas = ["patan", "dash", "batuca", "heman"]

for nombre in mascotas:
    print(nombre)

#-----funcion enumerate crea una tupla con indice   
for nombre in enumerate(mascotas):
    print(nombre) 

#------al asignar un indice con enumerate podemos acceder al indice o el elemento
for nombre in enumerate(mascotas):
    print(nombre[0])
    print(nombre[1])
    
#--------lo mismo que lo anterior pero en forma de lista
for indice, nombre in enumerate(mascotas):
    print(indice, nombre)
    
mascotas.append("gato")
mascotas.insert(3, "gato")
del mascotas[0]
print(mascotas)