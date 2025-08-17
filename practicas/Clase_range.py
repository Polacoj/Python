range(10)   # ------STOP no toma parte de la secuencia y hasta donde llegara(10) menos 1----> 1 2 3 4 5 6 7 8 9
range(3, 10)    # -------START desde donde comienza(3) e incrementa hasta llegar al STOP(10) menos 1-----> 3 4 5 6 7 8 9
# -----START comienza en 2 y a este se le incrementa STEP(3) hasta llegar a STOP(8) ----> 2 5 listo
range(2, 8, 3)
# -----START comienza en 10 y retrocede -1 STEP hasta llegar al STOP 0 ----> 10 9 8 7 6 5 4 3 2 1
range(10, 0, -1)

for indice in range(0, 8, 2):
    print(indice, end=" ")
print("\n\nfin del programa")
