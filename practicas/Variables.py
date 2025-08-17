print("Esto es una suma")
num_uno = 2
num_dos = 4.7
resultado = num_uno + num_dos
print("resultado: ", num_uno + num_dos, resultado)
nombre = "alexis"
edad = 44
print("mi nombre es: ", nombre, "edad: ", edad)

# Concatenación con una misma variable ------------------------------
variable = "Leonel"
variable += " "
variable += "Jankowicz"
variable += " edad de "
variable += "44"
print(variable)

print(variable + nombre)

# convertir un entero en un texto ----------------------
edad = str(edad)
print(variable + edad)

# EXTRACCIÓN de una palabra o letra----------------
extraer = variable[4:10]
print(extraer)

# COMPARACION--------------
print(edad == "44")
var = num_uno == edad
print(var)

# DIVISION entera---------------------
num_uno = 9
num_dos = 7
resultado = num_uno // num_dos
print("Division entera", resultado)

"----------Comentarios--------------"
"""=======Este tambien es comentario ===
    ==== MULTILINEA tambien pueden ser 
    comillas simples-------"""

# -----Para saber tipo de variable------------
print(type(variable))

# -----Solicitar datos---------
nombre = input("Dame el nombre: ")
edad = int(input("Ahora la edad: "))
print("entonces tu nombre es ", nombre, " y tienes ", edad)

# -------------Condicionales------
if edad == 44:
    print("es viejito")
    print("fin de la condicion")

print("la condicion termino")

# -------------Condicionales compuestos----------
if edad == 40:
    print("eres adulto")
else:
    print("no eres mayor jaja")

# -----Condicionales MULTIPLES---------
num_uno = int(input("1er numero: "))

if num_uno == 1:
    print("el numero es 1")
elif num_uno == 2:
    print("el numero es 2")
else:
    print("numero desconocido")

# ----------Parametro END y SEP--------
print("algo para", end=" - ")
print("unir")

print("1", "2", "3", "4", "5", "6", "7")
print("1", "2", "3", "4", "5", "6", "7", sep="**")

''' Comentario multilinea
lastima quieda en verde '''