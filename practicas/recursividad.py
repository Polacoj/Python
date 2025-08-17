def suma(n):
    # Caso BASE
    if n <= 1:
        return 1
    # Caso recursivo, donde se repite hasta llegar a CASO BASE
    else:
        return n + suma (n -1 ) # La funcion suma se llama a si misma repitiendose hasta llegar al caso base
        

print(suma(3))
