"""Aplicacion de conversion de temperatura de celcius a farenheit y viceversa"""

conv = ''
resultado = 0
tabla = ['f', 'F', 'c', 'C']
num = [".", ",", 0-9]
# temp.isnumeric() == True:
# temp = float(input("ingrese temperatura a convertir: "))
temp = float(input("numero a convertir"))
print("fofof")
print(type(temp))
if type(temp) == (int or float or complex):
    
    # temp = float(temp)
    conv = input(f"Convertir {temp}° a farenheit(F) o celcius(C): ")
    if conv == 'C' or conv == 'c':
        resultado = (temp-32)/1.8
        print(f"de {temp}° farenheit a celsius es: {resultado} Centigrados")
    elif conv == 'F' or conv == 'f':
        resultado = (temp*1.8)+32
        print(f"de {temp}° centigrados a farenheit es: {resultado} Farenheit")
    elif conv != tabla:
        print("debe ingresar una escala")
else:
    print("saliendo")

# print("hol")
# if temp == float(temp):
#     conv = input(f"Convertir {temp}° a farenheit(F) o celcius(C): ")
#     if conv == 'C' or conv == 'c':
#         resultado = (temp-32)/1.8
#         print(f"de {temp}° farenheit a celsius es: {resultado} Centigrados")
#     elif conv == 'F' or conv == 'f':
#         resultado = (temp*1.8)+32
#         print(f"de {temp}° centigrados a farenheit es: {resultado} Farenheit")
#     elif conv != tabla:
#         print("debe ingresar una escala")
