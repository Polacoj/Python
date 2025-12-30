import re

patron = "hola"
texto = "hola que tal, hola como estas"

resultado = re.search(patron, texto)

#.search() devuelve un objeto Match si encuentra el patron, None si no lo encuentra
#.group() devuelve el texto que coincide con el patron funciona solo si .search() encontro el patron

if resultado:
    print("se encontro el patron")
    print(f"el patron se encontro en la posicion {resultado.start()} a {resultado.end()}")
    print(resultado.group())
else:
    print("no se encontro el patron")

# encontrar todas las coincidencias
# .findall()
texto =  "esta es una cadena de texto para probar expresiones regulares y en este caso buscar todo el texto que se repita de la palabra texto"

patron = "texto"

resultado = re.findall(patron, texto)
print(resultado)
print(len(resultado))

#.iterfindall() devuelve un iterador con las coincidencias en lugar de una lista
texto = "lorem ipsum dolor sit amet, consectetur adipiscing elit. ipsum do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation lorem laboris nisi ut aliquip ex ea commodo loro. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu loru nulla pariatur. Excepteur sint occaecat cupidatat non proident, lorem in culpa qui officia deserunt mollit anim id est laborum."

patron = "lor.."# el . indica que puede haber cualquier caracter en esa posicion

resultado = re.finditer(patron, texto)
for i in resultado:
    print(f"{i.group()} -- coincidencia en la posicion {i.start()} a {i.end()}")

# los modificadores
# re.IGNORECASE o re.I sirve para ignorar mayusculas y minusculas en la busqueda
texto = "Hola que tal, como estas? HOLA"
patron = "hola"
resultado = re.findall(patron, texto, re.IGNORECASE)
print(resultado)


#.sub() sirve para reemplazar coincidencias en un texto
texto = "hola que tal, como estas? HOLA"
patron = "hola"
nuevo_texto = re.sub(patron, "buenas", texto, flags=re.IGNORECASE)
print(nuevo_texto)