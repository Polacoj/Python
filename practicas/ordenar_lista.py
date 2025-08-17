#-----ordenado de una lista con listas dentro, donde el indice o el valor "ordenable" esta al final

lista = [["algo", 1],
         ["otro", 4], 
         ["final", 3], 
         ["nada", 9],
         ["arreglo", 7]]

print(lista)

def ordenar(elemnto):
    return elemnto[1]
    
lista.sort(key=ordenar)
print(lista)

lista.sort(key=ordenar, reverse=True)
print(lista)

#-----usando funcion LAMBDA en lugar de crear una funcion especifica------
#---lista.sort(key=lambda parametro:elemento)---

lista.sort(key=lambda elemento:elemento[1])
print(f"con lambda: {lista}")