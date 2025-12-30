#la encapsulacion es un principio de la programacion orientada a objetos que restringe el acceso directo a algunos de los componentes de un objeto
#y puede prevenir la modificacion accidental de datos. Esto se logra mediante el uso de modificadores de acceso como public, protected y private.
class CuentaBancaria:
    def __init__(self, titular, saldo_inicial):
        self.titular = titular          #atributo publico
        self.__saldo = saldo_inicial    #atributo privado
        self.__numero_cuenta = "1234567890"  #atributo privado

    def depositar(self, cantidad):
        if cantidad > 0:
            self.__saldo += cantidad
            print(f"Depósito exitoso: {cantidad}. Nuevo saldo: {self.__saldo}")
        else:
            print("Cantidad de depósito inválida")

    def retirar(self, cantidad):
        if 0 < cantidad <= self.__saldo:
            self.__saldo -= cantidad
            print(f"Retiro exitoso: {cantidad}. Nuevo saldo: {self.__saldo}")
        else:
            print("Cantidad de retiro inválida o fondos insuficientes")

    def obtener_saldo(self):
        return self.__saldo
# Ejemplo de uso
cuenta = CuentaBancaria("Juan Perez", 1000)
cuenta.depositar(500)
cuenta.retirar(200)
print(f"Saldo actual: {cuenta.obtener_saldo()}")
# Intento de acceso directo al atributo privado (esto generará un error)
# print(cuenta.__saldo)  # Descomentar esta línea causará un error de atributo privado
print(f"accediendo al titualar: {cuenta.titular}")  # Acceso permitido al atributo público
print(cuenta.__numero_cuenta)  # Esto generará un error porque __numero_cuenta es privado