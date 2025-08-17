lista = []
tupla = ()
diccionario = {}

print(type(lista))
print(type(tupla))
print(type(diccionario)) 

cont = 0
while cont < 3:
    cont += 1
    print(cont)
    
lista = ['alo', 'bobo', 'zeta', 'f']

print(max(lista))

#--------para ingresar en varios valores con un solo parametros-----------
def nombre(*text):
    print(text)
    
nombre("ale")
nombre("paola", "tomy")
