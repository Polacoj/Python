if __name__ == '__main__':

# -----------Invertir frase con FOR-----------
    frase = input("Frase a invertir: ")
invertido = ""

for letra in frase:
    invertido = letra + invertido  # ----concatena cada letra que recorre de frase en la variable invertido
print(f"frase invertida: {invertido}")

# ------------Tabla de multiplicar-----------
numero = int(input("tabla de multiplicar del: "))
resultado = 0

for indice in range(0, 11, 1):
    resultado = numero * indice
    print(f"{numero} X {indice}= {resultado}")

# ------------Lo mismo que el ANTERIOR pero mas simplificado------
for indice in range(10):
    print(f"{numero} X {indice} = {numero*indice}")