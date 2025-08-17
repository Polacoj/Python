class Persona:
    def __init__(self, nombre, apellido, alias = "Sin alias"):
        self.nombre = nombre
        self.apellido = apellido
        self.alias = alias
        
    def camina(self):
        nombre_completo = f"de nombre {self.nombre} apellido {self.apellido}, con el alias {self.alias}"
        return nombre_completo
        
        
variable = Persona("Alexis", "jankowicz")
print(variable.camina())

variable = Persona("ale", "jankowicz", "JANKO")
print(variable.camina())

variable.alias = "solo alias"
print(variable.nombre)