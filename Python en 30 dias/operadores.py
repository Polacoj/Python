edad:int = 45
peso = 86.5
print(type(peso))

base = int(input("ingrese la base: "))
altura = int(input("ingrese la altura: "))
area = (base * altura) /2
print("el area del triangulo es ",area)

text = "python"

flot = len(text)
print(flot)
flot = float(flot)
print(flot)
flot = str(flot)
print(flot)
print(type(flot))

#-----saber si un numero es par-----

numero = float(input("numero: "))
res = numero % 2
print( res == 0)

n = 7//3
n2 = int(n)
print(n, n2)

Enter hours: 40
Enter rate per hour: 28
Your weekly earning is 1120

hora = int(input("cantidad de horas: "))
pago = float(input("valor de la hora: "))
res = hora*pago
print(res)