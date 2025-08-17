
# ----------MANERA de crear una clase con atributos FIJO, y uso del objeto con uno de sus atributos-----

class Camisetas:
    def __init__(self):
        self.marca = "NIKE"
        self.talle = 'L'
        self.precio = 1378


camiseta = Camisetas()
print(camiseta.talle)

# -------------- MANERA mas funcional con el uso de atributos --------------------


class Nombres:
    def __init__(self, nom_uno, nom_dos, nom_tres):
        self.nom_uno = nom_uno
        self.nom_dos = nom_dos
        self.nom_tres = nom_tres

alexis = Nombres("alexis", "leonel", "jankowicz")
paola = Nombres("paola", "cristina", "petti")

print(alexis.nom_dos)
print(paola.nom_tres)

# ---------------Funcion con atributos y metodos --------COMPLETO asi se usaria ------------


class Autos:
    def __init__(self, modelo, color, precio):      # ------------------> METODO CONSTRUCTOR o INICIAL
        self.marca = modelo                     # ---------> ATRIBUTOS
        self.color = color                      # ---------> ATRIBUTOS
        self.precio = precio                    # ---------> ATRIBUTOS
        self.desc = 0                           # ---------> ATRIBUTOS
        self.promo = False                      # ---------> ATRIBUTOS

    def descuento(self, porcentaje):            # ---------------------> METODO de la CLASE
        self.desc = self.precio - self.precio * porcentaje / 100
        if porcentaje < 100:
            self.promo = True
        return self.desc

    def info_auto(self):                        # ---------------------> METODO de la CLASE
        info = f"********\nDescripcion del vehiculo {self.marca}\nde color {self.color}\ncon un precio de {self.precio}\n"
        if self.promo:
            info += f"TIENE DESCUENTO quedando en --> {self.desc}"
        return info

audi = Autos("audi", "blanco", 1320)
renault = Autos("trafic", "negro", 890)
ford = Autos("focus", "rojo", 1100)

print(f"Valor original audi: {audi.precio}")
print(f"descuento para audi {audi.descuento(37)}, con valor original de {audi.precio}")
print(f"clase Auto {ford.marca}, con descuento de 30%: {ford.descuento(30)}")
print(renault.descuento(27))
print(audi.info_auto())
