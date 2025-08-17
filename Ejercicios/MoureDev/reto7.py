#   Crea una única función (importante que sólo sea una) que sea capaz
#   de calcular y retornar el área de un polígono.
#- La función recibirá por parámetro sólo UN polígono a la vez.
#- Los polígonos soportados serán Triángulo, Cuadrado y Rectángulo.
#- Imprime el cálculo del área de un polígono de cada tipo.

def poligono():
    print("algo")
    pol = {'T':"triangulo", 'C':"cuadrado", 'R':"rectangulo"}
    tipo = input("Que tipo de poligono se calcula=\n T -triangulo-\n C -cuadrado-\n R -rectangulo-\n").upper()
    base = float(input(f"indique la base del {pol[tipo]}: "))
    altura = float(input(f"indique la altura del {pol[tipo]}: "))
    if tipo == "T":
        res = (base * altura)/2
        print(res)
    elif tipo == "C":
        res = (base * altura) **2
        print(res)
    elif tipo == "R":
        res = base * altura
        print(res)

poligono()