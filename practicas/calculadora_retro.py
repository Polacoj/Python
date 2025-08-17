print("Biemvenido a la calculadora")
print("operaciones disponibles \nsum\nres\nmul\ndiv\n--Salida--\n")

resultado = ""  # -----variable fuera del loop, sino dentro vuelve siempre al valor inicial----

while True:  # ------loop infinito, se ejecuta constantemente hasta que se hace un quiebre-----
    # --------como resultado es una variable vacia(false) analiza lo opuesto-----
    if not resultado:
        resultado = input("ingrese un numero: ")
        if resultado.lower() == "salir":
            break
        resultado = int(resultado)
    op = input("ingrese operacion: ")
    if op.lower() == "salir":
        break
    n2 = input("ingrese otro numero: ")
    if n2.lower == "salir":
        break
    n2 = int(n2)
    if op.lower() == "sum":
        resultado += n2
    elif op.lower() == "res":
        resultado -= n2
    elif op.lower() == "mul":
        resultado *= n2
    elif op.lower() == "div":
        resultado /= n2
    else:
        print("operacion no encontrada")
        break
    print(f"el resultado es {resultado}")