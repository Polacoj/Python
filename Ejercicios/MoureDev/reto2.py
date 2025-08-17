"""Escribe una función que reciba dos palabras (String) y retorne
verdadero o falso (Bool) según sean o no anagramas.
Un Anagrama consiste en formar una palabra reordenando TODAS
las letras de otra palabra inicial.
NO hace falta comprobar que ambas palabras existan.
Dos palabras exactamente iguales no son anagrama."""


def anagrama(palabra1, palabra2):
    palabra2 = palabra2.lower()
    palabra1 = palabra1.lower()
    return sorted(palabra1) == sorted(palabra2)

resultado = anagrama("sodcfa", "cofdsa")
print(resultado)
