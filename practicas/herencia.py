class vehiculo():       #clase padre
    def __init__(self, marca, modelo):
        self.marca = marca
        self.modelo = modelo
    def movimiento(self):
        print("El vehículo se está moviendo")
        
class coche(vehiculo):      #herencia de la clase vehiculo
    def __init__(self, marca, modelo, color):
        super().__init__(marca, modelo)
        self.color = color
    def puertas(self):
        print("El coche tiene 4 puertas")
        
mi_coche = coche("Toyota", "Corolla", "Rojo")
print(f"Marca: {mi_coche.marca}")
print(f"Modelo: {mi_coche.modelo}")
print(f"Color: {mi_coche.color}")
mi_coche.movimiento()
mi_coche.puertas()