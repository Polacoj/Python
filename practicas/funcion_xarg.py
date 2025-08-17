# ----funcion que contiene un parammetro el cual sirve como iterable en caso de pasarle varios argumentos a la funcion--

def suma(*numeros):
    resultado = 0
    for i in numeros:
        resultado += i
    print(f"el resultado de la sumas es: {resultado}")


suma(3, 5, 8, 4)
suma(2, 7)
suma(3, 9, 5, 4, 3, 432, 565)
