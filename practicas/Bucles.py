# --------BUCLE while---------
x = 0
while x < 3:
    print(x, end=" ")
    x += 1
print("fin\n\n")

# ----------Fibonacci-------
num_uno, num_dos, ale = 0, 1, "LELO"
while num_uno <= 1597:
    print(num_uno, num_dos, end=" ")
    num_uno = num_uno + num_dos
    num_dos = num_uno + num_dos
print(f"\n{ale}\n\n")

# -------------FOR--------------
string = "Hola gente"

for char in string:
    print(char, end="~")

print("\n---fin del FOR---\n\n")

# ----------BUCLE while con BREAK-------
contador = 0

while contador < 10:
    contador += 1
    if contador == 5:
        break
    print(f"valor del Contador: {contador}")

print("---fin de la secuencia while con BREAK---\n\n")

# --------------BUCLE while con continue---------------
contador = 0

while contador < 10:
    contador += 1
    if contador <= 5:
        continue
    print(f"valor del Contador: {contador}")

print("---fin de la secuencia while con CONTINUE---")