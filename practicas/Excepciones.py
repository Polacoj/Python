try:
    numero = int(input("Digite un numero: "))
    print(numero+10)
except:
    print("Error de ingreso")


# -------se ejecuta hasta que se introduzca un numero correcto----lo corta la funcion BREAK
while True:
    try:
        numero = int(input("Digite un numero: "))
        print(numero+10)
        break
    except:
         print("Erro de ingreso")

print("fin del programa")

# --------captura de ERRORES propios------
def validar_edad(edad):
    if edad < 0:
        raise ValueError("Error edad NEGATIVA")
    elif edad :
        raise ValueError("Debe ingresar numeros no LETRAS")
    elif edad < 18:
        print("joven")
    elif edad < 40:
        print("viejito")
edad = int(input("edad:???? "))
try:
    validar_edad(edad)
except ValueError as AliasError:
    print(AliasError)
except Exception as PalabraError:
    print(PalabraError)
print("programa terminado")


