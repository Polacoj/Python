print("------------------------------")
print("-    Sistema de Vacaciones   -")
print("------------------------------\n\n")

nombre = input("A continuacion digite su nombre: ")
clave = int(input("Introduzcan su clave de jerarquia: "))
antiguedad = int(input("Ingrese su antiguedad: "))

if clave == 1:
    if antiguedad <= 1:
        print(nombre, "Le corresponden 6 dias de vacaciones")
    elif antiguedad >= 2 and antiguedad <= 6:
        print(nombre, "Le corresponden 14 dias de vacaciones")
    elif antiguedad >= 7:
        print(nombre, "Le corresponden 20 dias de vacaciones")
elif clave == 2:
    if antiguedad <= 1:
        print(nombre, "Le corresponden 7 dias de vacaciones")
    elif antiguedad >= 2 and antiguedad <= 6:
        print(nombre, "Le corresponden 15 dias de vacaciones")
    elif antiguedad >= 7:
        print(nombre, "Le corresponden 22 dias de vacaciones")
elif clave == 3:
    if antiguedad <= 1:
        print(nombre, "Le corresponden 10 dias de vacaciones")
    elif antiguedad >= 2 and antiguedad <= 6:
        print(nombre, "Le corresponden 20 dias de vacaciones")
    elif antiguedad >= 7:
        print(nombre, "Le corresponden 30 dias de vacaciones")
else:
    print("-----El codigo ingresado no se encuantra en la base de datos-----")

print("------------------------------")
print("-    Numero PAR o IMPAR      -")
print("------------------------------\n\n")

numero = int(input("A continuacion digite un numero ENTERO: "))
if numero >=1:
    resultado = numero % 2
    if resultado == 0:
        print("El numero ", numero, "es PAR")
    elif resultado != 0:
        print("el numero ", numero, "es IMPAR")
else:
    print("El numero debe ser mayor o igual a 1")