#los decoradores en python son una forma de modificar o mejorar el comportamiento de funciones o metodos sin cambiar su codigo fuente original.
def decorador_funcion(funcion):
    def funcion_decorada():
        print("Antes de llamar a la función")
        funcion()
        print("Después de llamar a la función")
    return funcion_decorada

@decorador_funcion
def saludar():
    print("Hola!")
    
saludar()

def decorador_con_argumentos(funcion):
    def funcion_decorada(*args, **kwargs):
        print("Antes de llamar a la función con argumentos")
        resultado = funcion(*args, **kwargs)
        print("Después de llamar a la función con argumentos")
        return resultado
    return funcion_decorada

@decorador_con_argumentos
def sumar(a, b):
    return a + b
resultado = sumar(5, 3)
print("Resultado de la suma:", resultado)
#en este caso el decorador_con_argumentos puede aceptar cualquier numero de argumentos posicionales y de palabras clave gracias a *args y **kwargs.

#decoradores para clases
class DecoradorClase:
    def __init__(self, clase):
        self.clase = clase

    def nueva_metodo(self):
        print("Este es un nuevo método agregado por el decorador de clase")
    def __call__