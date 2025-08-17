'''----Pedirle al usuario que pida cualquier texto real

a-calcular cuanto tardaria en decir esa frase, cuantas palabras dijo
b-si se tarda mas de 1 minuto, "para flaco tampoco te pedi un testamento"
c-dalto habla 30% mas rapido, cuanto tardaria el en decirlo

persona habla 2 palabras por segundo------- '''

frase = ()
frase = input("decime una frase: ")
print(frase)
resultado = frase.count(" ",)
print(resultado+1)
print('------------------')
if resultado > 60:
    print("para flaco tampoco te pedi un testamento")
else:    
    print(f'usted duro {(resultado + 1) /2} segundos en decir su frase, en total fueron {resultado+1} palabras') 
print(f" el dalto tardaria {round(resultado*.3,2)} segundos")
print('------------------')

