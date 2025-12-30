class Perro:
    pass

class Perro:
    def __init__(self, nombre, ladra, sexo) -> None:
        self.nombre = nombre
        self.ladra = ladra
        self.sexo = sexo


mi_perro = Perro("dash", "si", "macho")
print(mi_perro.ladra)
print(mi_perro.nombre, mi_perro.sexo)


#----otra alternativa con el uso de parametros---------
class Persona:
    def __init__(self, nombre, apellido):
        self.nombre_completo = f"{nombre}, , , {apellido}"
        
variable = Persona("alexis", "jankowicz")
print(variable.nombre_completo)


#-----clase con constructor y funcion--------
class Ave:
    atributo = "tiene alas"#atributo de clase, no de instancia
    
    def __init__(self, tipo):#constructor
        self.especie = tipo#atributo de instancia

    def vuela(self):#metodo
        print(f"{self.especie}, de ave voladora")#metodo

variable = Ave("gaviota")        
print(variable.especie)
variable.vuela()

print(Ave.atributo)
