'''Diferencia en % de este curso y .....

a-el mas rapido de otro curso
b-el mas lento de otro curso
c-el promedio de los cursos

este curso = 1.5 hs.
rapido = 2.5 hs.
lento = 7 hs.
promedio = 4 hs.
'''
curso = 1.5
rapido = 2.5
lento = 7
promedio = 4

resultado = 100 - (curso / rapido * 100)
print(f'el curso dalto es {(resultado)}% mas rapido')

#-------funcion ROUND(numero o variable, cantidad de decimales o nada para redondeo hacia arriba)
resultado = 100 - (curso / lento * 100)
print(f'el curso dalto es {round(resultado, 2)}% mas rapido que el lento')

resultado = 100 - (curso / promedio * 100)
print(f'el curso dalto es {(resultado)}% mas rapido que el promedio')
