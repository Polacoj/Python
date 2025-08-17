"""Porcentaje de material inservible que se reduce en 

-el promedio de los cursos
-este curso """

crudo_curso = 3.5
crudo_otros = 5
total_dalto = 1.5
total_otros = 4

horas_dalto = 100 - (total_dalto / crudo_curso * 100)
print(f'el promedio de video eliminado dalto es {round(horas_dalto, 2)}%')

horas_otros = 100 - (total_otros / crudo_otros * 100)
print(f'el promedio de video eliminado dalto es {round(horas_otros, 2)}%')