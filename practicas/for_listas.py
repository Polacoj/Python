
usuarios = [["carlos", 3],
            ["jose", 6],
            ["basualdo", 1],
            ["felipe", 2],
            ["juan", 9]]

# -------creando una LISTA de ususarios por NOMBRE con bucle for----

nombres = []
for i in usuarios:
    nombres.append(i[0])
print(nombres)

# -----lo mismo pero mas corto y lindo--------
# -------nombres = [expresion for item in items]---
# --creando lista = transformacion para sser aplicadaen la lista---for---nombre de cada elemnto que iteramos---lista que iteramos-
#----conocido tambien como MAP-----
nombres_2 = [usuario[0] for usuario in usuarios]
print(nombres_2)

nombres_2 = [id[1] for id in usuarios]
print(nombres_2)

# -----filtrar enn base a una condicion----en este caso al listado donde el id sea mayor a 2-----
#----conocido tambien como FILTER-----
nombres_3 = [usuario for usuario in usuarios if usuario[1] > 2]
print(nombres_3)

#----filtrar una lista y tranformada en otra, en este caso -----por usuario---
nombres_3 = [usuario[0] for usuario in usuarios if usuario[1] > 3]
print(nombres_3)
