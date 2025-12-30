from tkinter import Tk, Label, Button
from datetime import time

"""def saliendo():
    ventana_interna = Tk()
    ventana_interna.geometry("200X200")
    ventana_interna.title("Cerrando")
    ventana_interna.command(exit)
"""
ventana = Tk()
ventana.geometry("600x400")
ventana.title("Titulo de ventana")

titulo = Label(ventana, text="Titulo del marco")
titulo.pack()

boton = Button(ventana, text="cerrar", command=exit)
boton.pack()

ventana.mainloop()
