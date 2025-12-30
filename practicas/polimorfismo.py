class Animal():
    def hablar(self, sonido):
        print(sonido)
        
class Perro(Animal):
    def ladrar(self):
        print("guau, guau")
        
class Gato(Animal):
    def maullar(self):
        print("miau, miau") 
        
class Vaca(Animal):
    def mua(self):
        print("mu, mu")

mi_perro = Perro()
mi_perro.ladrar()

mi_gato = Gato()
mi_gato.maullar()

mi_vaca = Vaca()
mi_vaca.mua()

#Usando el polimorfismo
class AnimalDos():
    def hablar(self, sonido):
        print(sonido)
        
class Perro(AnimalDos):
    pass
class Gato(AnimalDos):
    pass
class Vaca(AnimalDos):
    pass

mi_perro = Perro()
mi_perro.hablar("guau, guau")

mi_gato = Gato()
mi_gato.hablar("miau, miau")

mi_vaca = Vaca()
mi_vaca.hablar("mu, mu")

        
    