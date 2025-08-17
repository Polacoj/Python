# funciones LAMBDA son funciones anonimas (sin nombre) => lambda ARGUMENTO : EXPRESION
# lambda n : n * 20

def my_funcion(x):
    return lambda n: n * x

# doble = my_funcion(2)
# print(doble(8))


def main():
    onceavo = my_funcion(11)
    doble = my_funcion(2)
    print(onceavo(5), doble(8))


if __name__ == "__main__":
    main()
