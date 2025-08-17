usuarios = [["carlos", 3],
            ["jose", 6],
            ["basualdo", 1],
            ["felipe", 2],
            ["juan", 9]]

# -----transforamcion de lista con funcion MAP-------
usuario = list(map(lambda usuario: usuario[0], usuarios))
# ---=nueva lista de algo de USUARIOS---y transformamos a los usuarios con MAP y funcion lambda
print(usuario)


# ------filter ----
usuario_menor = list(filter(lambda usuario: usuario[1] > 3, usuarios))
print(usuario_menor)
