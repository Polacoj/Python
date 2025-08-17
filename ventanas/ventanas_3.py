from tkinter import Tk, Button, Label, Entry

ventana = Tk()
ventana.title("Titulo en la ventana")
ventana.geometry("400x200")


def suma():
    dato_1 = valor_1.get()
    dato_2 = valor_2.get()
    resultado = float(dato_1) + float(dato_2)
    valor_resultado.delete(0, 'end')
    valor_resultado.insert(0, resultado)


etiqueta_1 = Label(ventana, background="yellowgreen", text="Valor 1:")
etiqueta_1.place(x=10, y=10, height=30, width=80)

valor_1 = Entry(ventana, background="#B9C8D5")
valor_1.place(x=100, y=10, height=30, width=80)

etiqueta_2 = Label(ventana, background="yellowgreen", text="Valor 2:")
etiqueta_2.place(x=10, y=60, height=30, width=80)

valor_2 = Entry(ventana, background="#B9C8D5")
valor_2.place(x=100, y=60, height=30, width=80)

etiqueta_resultado = Label(ventana, background="#778693", text="Resultado: ")
etiqueta_resultado.place(x=10, y=130, height=30, width=80)

valor_resultado = Entry(ventana, background="#98B7D1")
valor_resultado.place(x=100, y=130, relheight=0.20, relwidth=0.250)

boton = Button(ventana, text="SUMA", command=suma)
boton.place(x=200, y=10, width=100, height=100)

ventana.mainloop()
