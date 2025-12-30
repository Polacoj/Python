#la abstraccion es un principio de la programacion orientada a objetos que consiste en ocultar los detalles complejos de implementacion
#y mostrar solo las caracteristicas esenciales de un objeto. Esto permite a los desarrolladores centrarse en la interaccion con el objeto sin preocuparse por su complejidad interna.

class Libros():
    def __init__(self, titulo, autor, anio_publicacion):
        self.titulo = titulo
        self.autor = autor
        self.anio_publicacion = anio_publicacion

    def obtener_informacion(self):
        return f"Título: {self.titulo}, Autor: {self.autor}, Año de Publicación: {self.anio_publicacion}"
    
    def __eq__(self, value):  #metodo especial "propia de python" para comparar objetos
        return self.titulo == value.titulo and self.autor == value.autor and self.anio_publicacion == value.anio_publicacion
            
    
# Ejemplo de uso
libro1 = Libros("Cien Años de Soledad", "Gabriel García Márquez", 1967)
libro2 = Libros("1984", "George Orwell", 1949)
libro3 = Libros("Cien Años de Soledad", "Gabriel García Márquez", 1967)

print(libro1.obtener_informacion())
print(libro2.obtener_informacion()) 
print("¿libro1 es igual a libro2?", libro1 == libro2)  # Debería ser False
print("¿libro1 es igual a libro3?", libro1 == libro3)   # Debería ser True