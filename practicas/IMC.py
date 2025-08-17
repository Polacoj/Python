# calculo de indice masa corporal----- peso/altura x altura--------------
def imc(peso, altura):
    indice = peso/(altura**2)
    return indice

def datos():
    peso = float(input("ingrese su peso --> "))
    altura = float(input("ingrese su altura --->"))
    indice = imc(peso, altura)
    if indice < 20:
        print(f"indice --> {indice:.2f} delgado")
    elif indice < 26:
        print(f"indice --> {indice:.2f} normal")
    elif indice < 31:
        print(f"indice --> {indice:.2f} sobrepeso")
    else:
        print(f"indice --> {indice:.2f} obesidad")

datos()

if __name__ == '__main__':
    ...
