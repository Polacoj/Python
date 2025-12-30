#Las ventanas son contenedores de widget( botones, casillas, formularios, otra ventana)
#Los widget se pueden configurar sus parametros de 3 maneras
'''
CONSTRUCTOR: 
    boton = Button(self, fg="blue")

METODO CONFIG: 
    boton.config(fg="blue")
    
ACCEDIENDO A LA PROPIEDAD (como diccionario)
    boton[fg] = "blue"
    boton[text] = "texto en pantalla"
'''

from tkinter import Tk, Button

ventana = Tk()
ventana.title("Ventana de prueba !!")
ventana.geometry("800x600")
ventana.config(background='silver', cursor='pirate', relief='groove')

boton = Button(ventana, text="boton", command=exit)
boton.config(fg="red", background="green")
boton["justify"] = "left"
boton.pack()

ventana.mainloop()