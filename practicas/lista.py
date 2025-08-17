char = list("palabra para desarmar")
print(char)

rango = list(range(2, 15))
print(rango)

j = 0
for i in rango:
    j += 1
print(j)

numeros = [1, 2, 3, 4, 5, 6, 7, 8, 9]
primero, *resto = numeros
print(primero, resto)

#-------con * indicamos parte a no desempaquetar, conteniendolo en una lista
primero, segundo, *medio, ante, ultimo = numeros
print(medio)
print(primero, segundo, ante, ultimo)
