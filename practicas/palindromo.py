def no_space(texto):
    new_text = ''
    for char in texto:
        if char != " ":
            new_text+=char
    return new_text

def reverse(texto):
    inverso=''
    for char in texto:
        inverso = char + inverso
    return inverso

reverse("hola mundo loco")

def palindromo(texto):
    texto = no_space(texto)
    alreves = reverse(texto)
    if texto.lower() == alreves.lower():
        print("es palindromo")
    else:
        print("no lo es")
    print(texto)
    print(alreves)
    
palindromo("123 321")
palindromo("somoS")


