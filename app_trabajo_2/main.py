import tkinter as tk
from tkinter import filedialog
import pandas as pd

def seleccionar_archivo():
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal
    archivo = filedialog.askopenfilename(
        title="Selecciona un archivo Excel",
        filetypes=[("Archivos Excel", "*.xlsx *.xls")]
    )
    return archivo

def main():
    archivo_excel = seleccionar_archivo()
    if archivo_excel:
        df = pd.read_excel(archivo_excel)
        print("Archivo cargado correctamente.")
        print(df.head())  # Muestra las primeras filas
        # Aquí puedes buscar los parámetros que necesitas en el DataFrame
    else:
        print("No se seleccionó ningún archivo.")

if __name__ == "__main__":
    main()
