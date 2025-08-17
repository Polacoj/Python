def largo(texto):
    resultado = 0
    # ------_(guion bajo para no tener advertencia por variable qu eno se define o usa)
    for _ in texto:
        resultado += 1
    return resultado


palabra = largo("hola mundo loco")
print(palabra)

"""tocar en play+cucaracha, crear archivo jason, crar un print con un breackpoint, darle al play de depuracion, punto con media flecha inicia aplicaion, cuando llega al breackpoint con flecha abajo y punto entra al codigo, seguir con media flecha y punto (avanza lina alinea del codigo mostrando el resultado instantanio en el paner de depuracion)"""