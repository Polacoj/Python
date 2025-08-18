import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from pypdf import PdfReader
import re

# Variables globales para almacenar rutas y contenido
rutas_global = []
contenido_global = ""


def pegar(evento):
    global rutas_global, contenido_global
    archivo = evento.data
    # Extrae rutas entre llaves o rutas simples
    rutas = re.findall(r'\{([^}]+)\}|([^\s]+)', archivo)
    # Normaliza la lista de rutas
    rutas = [ruta[0] if ruta[0] else ruta[1] for ruta in rutas]
    rutas_global = rutas  # Guarda las rutas para usarlas al aceptar
    archivos_texto = "Pegado:\n" + "\n".join(rutas)
    ventana_pegado.config(text=archivos_texto)
    print(f"Archivos pegados: {rutas}")

    contenido = ""
    for ruta in rutas:
        try:
            documento = PdfReader(ruta)
            contenido += "----------" + ruta + "----------------\n"
            for pagina in documento.pages:
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    contenido += texto_pagina + "\n"
        except Exception as e:
            contenido += f"Error al leer {ruta}: {str(e)}\n"
    contenido_global = contenido  # Guarda el contenido para usarlo al aceptar
    print(contenido)


def aceptar():
    global rutas_global, contenido_global
    # Cambia el texto del label para indicar aceptación
    ventana_pegado.config(text="Archivos aceptados")
    print("Archivos aceptados")
    # Guarda el contenido en un archivo .txt
    if contenido_global:
        with open("contenido_archivos.txt", "a", encoding="utf-8") as f:
            f.write(contenido_global)
            f.write("\n\n")
        print("Contenido guardado en contenido_archivos.txt")


# Initialize the TkinterDnD window
root = TkinterDnD.Tk()
root.title("Ventana para el archivo")
root.geometry("600x200")

# Create a frame to hold our content
frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

# Create a label that can receive dropped files
ventana_pegado = tk.Label(
    frame,
    text="Copia y pega archivos aquí",
    bg="#2ba8be",
    font=("Helvetica", 14),
    relief="ridge",
    height=4
)
ventana_pegado.pack(fill=tk.BOTH, expand=True)

# Add the "Aceptar" button
boton_aceptar = tk.Button(frame, text="Aceptar", command=aceptar)
boton_aceptar.pack(side=tk.LEFT)

boton_cerrar = tk.Button(frame, text="Cerrar",
                         command=exit)
boton_cerrar.pack(side=tk.RIGHT)

# Register the label as a drop target
ventana_pegado.drop_target_register(DND_FILES)
ventana_pegado.dnd_bind('<<Drop>>', pegar)

# Run the application
if __name__ == "__main__":
    root.mainloop()
