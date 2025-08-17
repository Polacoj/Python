# -------------METODO find---------------
variable = "hola estamos probando Jankowicz"
buscar = variable.find("Jankowicz")
print(variable)
print(buscar, "\n\n")

# ---------METODO upper para mayusculas-----
print("Metodo UPPER----", end=" ")
variable = variable.upper()
print(variable, "\n\n")

# -------------METODO startswith y endswith-------
print("Metodo starts_with & ends_with")
string = "Diana se peina sola"
resultado = 0
starts_with = "Ejemplos con startswith(): "
ends_with = "Ejemplos con endswith(): "

print(f"\n{starts_with.rjust(50,'-')}")

resultado = string.startswith("D")
print(f"\n{string}, comienza con la subcadena 'D': {resultado}")

resultado = string.startswith("d")
print(f"\n{string}, comienza con la subcadena 'd': {resultado}")

resultado = string.startswith("Diana")
print(f"\n{string}, comienza con la subcadena 'Diana': {resultado}")

resultado = string.startswith("se", 6)
print(f"\n{string}, comienza con la subcadena 'se', desde la posicion 6: {resultado}")

resultado = string.startswith("se", 6, 7)
print(f"\n{string}, comienza con la subcadena 'se', desde la posicion 6 hasta la 7: {resultado}")

resultado = string.startswith("se", 100, 100)
print(f"\n{string}, comienza con la subcadena 'se', desde la posicion 100 hasta la 100: {resultado}")

resultado = string.startswith("se", -4, -1)
print(f"\n{string}, comienza con la subcadena 'se', desde la posicion -4 hasta la -1: {resultado}")

print(f"\n{ends_with.rjust(50,'-')}")

resultado = string.endswith("A")
print(f"\n{string}, finaliza con la subcadena 'A': {resultado}")

resultado = string.endswith("a")
print(f"\n{string}, finaliza con la subcadena 'a': {resultado}")

resultado = string.endswith("sola")
print(f"\n{string}, finaliza con la subcadena 'sola': {resultado}")

resultado = string.endswith("sola", 10)
print(f"\n{string}, finaliza con la subcadena 'sola', desde la posicion 10: {resultado}")

resultado = string.endswith("s", 9, 14)
print(f"\n{string}, finaliza con la subcadena 's', desde la posicion 9 hasta la 14: {resultado}")

resultado = string.endswith("s", 100, 100)
print(f"\n{string}, finaliza con la subcadena 's', desde la posicion 100 hasta la 100: {resultado}")

resultado = string.endswith("s", -4, -2)
print(f"\n{string}, finaliza con la subcadena 's', desde la posicion -4 hasta la -2: {resultado}")

# --------------METODO count-cantidad de caracteres en------------
texto = "algo quE se Me oCURRio"
print(f"METODO count de ({texto})", texto.count("e", 0, len(texto)))

# ----------METODO center -----------centra una frase----
print(f"\n\n", texto.center(58, '-'))

# --------METODO captalize-----------------
print(f"\n\nMETODO capitalize  {texto.capitalize()}")

# ---------METODO swapcase -------------------
print(f"\n\nMETODO swapcase  {texto.swapcase()}")

# ----------METODO rstrip y strip------------
print(f"METODO rstrip: ", texto.rstrip(" oi"))  # -----elimina desde la derecha a izquierda solo las que encuentra primero
print(f"METODO strip: ", texto.strip('aiog'))

# --------METODO format--------------

nombre = input("nombre :")
edad = int(input("edad: "))

print("Este es el METODO format '{}' ese fue la primera '{}' esta la segunda".format(nombre, edad))

# -----------METODO replace-------
cadena = "algo que se me ocurrio"

variable = cadena.replace("algo", 'f')
print(f"{cadena}\n{variable}")

# -----------METODO copy------------ para usar mismos objetos en distintas variables ---------
a = [3, 5, 7, 'b', 'f']
b = a.copy()
print('variable a: ', a, 'id', id(a))
print('variable b: ', b, 'id', id(b))

# --------- METODO fromkey para crear un diccionario desde una lista -sin valores----------
nuevo_diccionario = dict.fromkeys(a)
print('diccionario nuevo', nuevo_diccionario)
# ---------------asignando valores a una serie -------------------
nuevo_diccionario = dict.fromkeys(a, 'valores_nuevos')
print('valores nuevos', nuevo_diccionario)

# --------hacer una iteracion de un diccionario-----------
for clave, valor in nuevo_diccionario.items():
    print(clave, valor)

