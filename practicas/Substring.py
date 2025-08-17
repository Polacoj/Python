string = "0123456789"
substring = ""

print(f"La cadena original es: {string}\n")

substring = string[0]
print(f"La subcadena en posicion [0] es: {substring}")

substring = string[5]
print(f"La subcadena en posicion [5] es: {substring}")

substring = string[-4]
print(f"La subcadena en posicion [4] es: {substring}")

substring = string[:3]
print(f"La subcadena entre las posiciones [:3] es: {substring}")

substring = string[5:]
print(f"La subcadena en las posicions [5:] es: {substring}")

substring = string[-4: -2]
print(f"La subcadena entre las posiciones [-4:-2] es: {substring}")

substring = string[:]
print(f"La subcadena en posicion [:] es: {substring}")

substring = string[1:6:2]
print(f"La subcadena entre las posiciones [1:6] con salto [2] es: {substring}")

substring = string[1:6:3]
print(f"La subcadena entre las posiciones [1:6] con salto [2] es: {substring}")

substring = string[::2]
print(f"La subcadena entre las posiciones [:] con salto [2] es: {substring}")


frase = input("Ingrese la frase que desea: ")
print(frase, "\n")
eliminar = input("Palabra a ELIMINAR: ")
buscar = frase.find(eliminar)
frase_corta = frase[0:buscar] + frase[buscar+(len(eliminar)+1):]
print("frase recortada: ", frase_corta)