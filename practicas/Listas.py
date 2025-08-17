# --------Listas--------
import heapq
lista = ["ale", 44, "pao", 38, "tomy", 10]

print(lista)
print(lista[1:4])
print(lista[-3:len(lista)])

otra_lista = [1, 4, 7, ["ale", "pao", "tomy"]]

print(otra_lista[3:])
print(len(otra_lista))

lista.append("agregado")

print(lista)

otra_lista.extend(['s', 'r', 'b'])
print(otra_lista)

# -------CONCATENAR listas-------

mi_lista = [1, 2, 3, 4]
su_lista = [5, 6, 7, 8, 9]

print(mi_lista + su_lista)

lis = ['a', 'c', 'f', 'z', 'b']
lis.sort()
print(lis)

# --------Tupla de variable-------
variable = 'tupl',
print(variable, type(variable))


# ----------asignacion de variables con valores unicos en forma de tupla------------------
var, var_uno, var_dos = (2, 6, 'z')
print(var)
print(var_uno)
print(var_dos)

# ----------MINIMOS y MAXIMOS importando funcion HEAPQ (en la cual podemos elegir la cantidad-------------
listado = [110, 34, 3, 67, 98, 5, 23, 756, 23,
           10, 1, 4, 76, 34, 23, 98, 34, 12, 19, 122]


print('minimo', min(listado))
print('maximo', max(listado))

print('cantidad de maximos: ', heapq.nlargest(5, listado))
print('cantidad de 3 minimos: ', heapq.nsmallest(3, listado))
