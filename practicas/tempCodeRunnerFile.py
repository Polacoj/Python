patron =  "esta es una cadena de texto para probar expresiones regulares y en este caso buscar todo el texto que se repita de la palabra texto"

texto = "texto"

resultado = re.findall(patron, texto)
print(resultado)