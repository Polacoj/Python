#  Escribe un programa que muestre cómo transcurre un juego de tenis y quién lo ha ganado.
#  El programa recibirá una secuencia formada por "P1" (Player 1) o "P2" (Player 2), según quien
#  gane cada punto del juego.
 
#  - Las puntuaciones de un juego son "Love" (cero), 15, 30, 40, "Deuce" (empate), ventaja.
#  - Ante la secuencia [P1, P1, P2, P2, P1, P2, P1, P1], el programa mostraría lo siguiente:
#    15 - Love
#    30 - Love
#    30 - 15
#    30 - 30
#    40 - 30
#    Deuce
#    Ventaja P1
#    Ha ganado el P1
# - Si quieres, puedes controlar errores en la entrada de datos.   
# - Consulta las reglas del juego si tienes dudas sobre el sistema de puntos.



def secuencia():
    puntos = [0, 15, 30, 40, "deuce", "ventaja"]
    player1, j1 = 0, 0
    player2, j2 = 0, 0
    ganador = False
    print("algo")
    while ganador != True:
            print("Player 1 ---- Player 2")
            print(f"  {puntos[j1]}   ------ {puntos[j2]}")
            jugador = input("Jugador (1 / 2) que gano punto: \n")
            if jugador == '1' or jugador == '2':
                if jugador == '1':
                    j1 += 1
                    player1 = puntos[j1]
                    if (j1 == 4) & (j2 == 5):
                        j2 -= 1
                if (j1 == 4) & (j2 < 3):
                    ganador = True
                    print("Player 1 GANADOR")
                    break
                elif jugador == '2':  
                    j2 += 1
                    player2 = puntos[j2]
                    if (j2 == 4) & (j1 == 5):
                        j1 -= 1
                if (j2 == 4) & (j1 < 3):
                    ganador = True
                    print("Player 2 GANADOR")
                    break
            else: 
                print("Intente nuevamente")      
            

secuencia()

#-------------NO ME SALIO-------------