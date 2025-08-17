"""1 alumno es profesor 
    1 alumno es ayudante
    
    A-pedir la edad de todos los compañeros que asistieron hoy y ordenarlos de menor a mayor
    B-el mayor es el profesor y el menor es el asistente, quien es quien"""

alumnos = []

pregunta = str


while pregunta != "S":
    pregunta = input("ingresamos o salimos: ")
    nombre = input("nombre: ")
    edad = input('edad: ')
    alumnos.append(nombre)
    alumnos.append(edad)

print(type(alumnos))
print(alumnos)

print('hola')
