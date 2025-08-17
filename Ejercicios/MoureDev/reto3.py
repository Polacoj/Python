"""Escribe un programa que imprima los 50 primeros números de la sucesión
    de Fibonacci empezando en 0.
    La serie Fibonacci se compone por una sucesión de números en
    la que el siguiente siempre es la suma de los dos anteriores.
    0, 1, 1, 2, 3, 5, 8, 13..."""


def fibonacci(numero: int):
    print("algo")
    posAnt=0
    posAct=1
    for i in range(numero):
        print(posAnt)
        i=posAnt+posAct
        posAnt=posAct 
        posAct = i
fibonacci(50)
