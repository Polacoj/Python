# la barra invertida \ sirve para escapar caracteres especiales en las expresiones regulares
# por ejemplo si queremos buscar un punto . en un texto debemos usar \. ya que el punto
# es un caracter especial que representa cualquier caracter en una expresion regular
import re

patron = "."
texto = "hola que tal. hola como estas."

resultado = re.findall(patron, texto)   
if resultado:
    print(resultado)
    
# se corrige con \.
patron = r"\."
resultado = re.findall(patron, texto)
if resultado:
    print(resultado)
    
patron = r"\d" # busca cualquier digito del 0 al 9
texto = "hola que tal, hoy es 20 de junio de 2023"
resultado = re.findall(patron, texto)
print(resultado)
    
#para definir una cantidad de repeticiones se usan los cuantificadores
# * 0 o mas veces
resultado = re.findall(r"\d{4}", texto) # busca cualquier digito que se repita 4 veces
print(resultado)

#\w: busca cualquier caracter alfanumerico (letras y numeros) y el guion bajo _
texto = "hola_que tal, @ hoy es 20 de junio de 2023!!!"
resultado = re.findall(r"\w+", texto) # el + indica que puede haber uno o mas caracteres alfanumericos
print(resultado)

#\s: busca cualquier espacio en blanco (espacios, tabulaciones, saltos de linea)
texto = "hola que tal,\ncomo\testas?"
resultado = re.findall(r"\s", texto)
print(resultado)

#^ busca el inicio de una cadena, $ busca el final de una cadena
texto = "hola que tal, como estas?"
resultado = re.findall(r"^hola", texto) # busca si la cadena empieza con hola
print(resultado)
resultado = re.findall(r"\?$", texto) # busca si la cadena termina con estas?
print(resultado)

telefono = "+5422 9 351 1234567"
patron = r"^\+\d{2} " # busca un numero de telefono con el formato +54; el espacio luego del {2} es literal porque busca solo 2 digitos y un espacio
resultado = re.findall(patron, telefono)
print(resultado)

#\b: busca un limite de palabra (espacio, inicio o fin de cadena, caracteres especiales)
texto = "hola que tal, como estas? que es lo queso que quieres?"
resultado = re.findall(r"\bque\b", texto) # busca la palabra que
print(resultado)
resultado = re.findall(r"\bque", texto) # busca la palabra que al inicio
print(resultado)

#*: busca 0 o mas repeticiones del caracter anterior
texto = "holaaaaaa que tal, como estas y que hora es?"
resultado = re.findall(r"hol*a", texto) # busca la palabra hola con 0 o mas letras a
print(resultado)
resultado = re.findall(r"hol*a+", texto) # busca la palabra hola con 0 o mas letras a, pero al menos una
print(resultado)
#+: busca 1 o mas repeticiones del caracter anterior
#?: busca 0 o 1 repeticion del caracter anterior
#{}: busca una cantidad exacta de repeticiones del caracter anterior
#|: operador OR, busca una cosa u otra
texto = "hola que tal, como estas? que es lo queso que quieres?"
resultado = re.findall(r"que|queso", texto) # busca la palabra que o queso
print(resultado)
#(): agrupa una expresion regular
#ejemplo: validar un numero de telefono con codigo de area opcional
telefono1 = "+54 9 351 1234567"
telefono2 = "351 1234567"
patron = r"^(\+\d{2,3} )?" # el ? despues del parentesis indica que el codigo de area es opcional
resultado1 = re.findall(patron, telefono1)
resultado2 = re.findall(patron, telefono2)
print(resultado1)
print(resultado2)   

#{n,m}: busca entre n y m repeticiones del caracter anterior
#{n,}: busca n o de mas repeticiones del caracter anterior


usuario = "alexis_jankowicz123$%"
patron = r"^[\w.$%]+"# busca un usuario que empiece con letras, numeros, guion bajo, punto, dolar o porcentaje y que tenga al menos un caracter
resultado = re.search(patron, usuario)

if resultado:
    print("usuario valido", resultado.group())
else:
    print("usuario invalido")
    
# [^]: busca cualquier caracter que no este dentro de los corchetes
texto = "hola que tal, como estas? que es lo queso que quieres?"
resultado = re.findall(r"[^aeiou\s]+", texto) # busca todas las consonantes
print(resultado)
