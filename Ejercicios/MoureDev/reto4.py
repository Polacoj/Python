""" Escribe un programa que se encargue de comprobar si un número es o no primo.
Hecho esto, imprime los números primos entre 1 y 100."""




def primo():
    print("lla")
    n1 = int(input("Desde que numero: "))
    n2 = int(input("Hasta que numero: "))
    for i in range(n1, n2):
        if i % 2 == 0:
            print(f"{i}_ No es primo")
        else:
            print(f"{i}_Es primo")


primo()
