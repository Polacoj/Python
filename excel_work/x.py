# -*- coding: utf-8 -*-
# This script creates a simple GUI using Tkinter and tkinterdnd2 to allow users to drag and drop files.
# Import necessary libraries
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
import json
import PyPDF2

def pegar(evento):
    # This function will be called when files are dropped onto the label
    archivo = evento.data
    # Convert the string of file paths to a list (handles multiple files)
    rutas = archivo.split() if isinstance(archivo, str) else archivo
    # Create a string with each file path on a new line
    archivos_texto = "Pegado:\n" + "\n".join(rutas)
    ventana_pegado.config(text=archivos_texto)
    print(f"Archivos pegados: {rutas}")  # For debugging purposes

    def pdf_a_json(rutas):
        contenido = ""
        try:
            with open(rutas, "rb") as archivo:
                lector = PyPDF2.PdfReader(archivo)
                for pagina in lector.pages:
                    contenido += pagina.extract_text() or ""
        except Exception as e:
            contenido = f"Error al leer PDF: {e}"
        return json.dumps({"contenido": contenido}, ensure_ascii=False, indent=2)
    pdf_a_json(rutas)

def aceptar():
    # Cambia el texto del label para indicar aceptación
    ventana_pegado.config(text="Archivos aceptados")
    print("Archivos aceptados")


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
    text="copie y pege archivos aqui",
    bg="#2ba8be",
    font=("Helvetica", 14),
    relief="ridge",
    height=4
)
ventana_pegado.pack(fill=tk.BOTH, expand=True)

# Add the "Aceptar" button
boton_aceptar = tk.Button(frame, text="Aceptar", command=aceptar)
boton_aceptar.pack(pady=10)

# Register the label as a drop target
ventana_pegado.drop_target_register(DND_FILES)
ventana_pegado.dnd_bind('<<Drop>>', pegar)

# Run the application
if __name__ == "__main__":
    root.mainloop()
