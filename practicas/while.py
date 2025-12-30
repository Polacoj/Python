comando = ""

while comando != "salir":
    comando = input('ingrese algo "salir(sale jejej)":$ ')
    print(comando)
    
#capturar errores
numero = 1
while numero != 0:
    try:
        numero = int(input("ingrese un numero (0 sale): "))
        if numero < 0:                        
            print(f"el numero es: {numero}")
    except:
        print("debe ingresar un numero valido")
        
print("fin del programa")