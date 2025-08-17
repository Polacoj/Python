a = {1, 2, 4, 9, 0}
b = {3, 6, 9, 0, 2}

# --------UNE dos conjuntos--elimina los duplicados-----
c = a | b
print('union a y b =', c)
print('union de a y b = ', a.union(b))

# ----------INTERSECCION de los dos conjuntos
c = a & b
print(c)

# ----------DIFERENCIA entre conjuntos
c = a - b
print(c)
print('difference_update =', a.difference_update(b))

# -----------DIFERENCIA simetrica lo que esta en a y lo que esta b OBVIANDO los que estan en ambos
c = a ^ b
print(c)

print(id(a))
print(id(b))