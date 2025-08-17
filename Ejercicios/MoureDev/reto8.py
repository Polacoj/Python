# Crea un programa que invierta el orden de una cadena de texto
# sin usar funciones propias del lenguaje que lo hagan de forma automática.
# - Si le pasamos "Hola mundo" nos retornaría "odnum aloH"

def invertir():
    print("hola")
    texto = input("Ingrese palabra o cadena de texto: ")
    res = ""
    for letra in texto[::-1]:   #-------slice ::-1 recorre en la inversa-------------
        res += letra
    print(res)
    
invertir()