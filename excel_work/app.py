import pandas as pd

"""
Drag and Drop File Reader in Python with Tkinter

Requires: tkinter (built-in), tkinterdnd2 (install via pip: pip install tkinterdnd2)

This program creates a window where users can drag and drop a text file to display its content.
Alternatively, users can click "Open File" to choose a file manually.
"""

import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import filedialog, messagebox, scrolledtext


class DragDropFileReader(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()

        self.title("Lector de archivo por arrastrar y soltar - Python")
        self.geometry("700x500")
        self.configure(bg="#2a2a2a")

        self.font_family = ("Segoe UI", 11)

        self.label = tk.Label(
            self,
            text="Arrastra un archivo de texto aquí",
            font=("Segoe UI", 16, "bold"),
            fg="#eee",
            bg="#3a3a3a",
            relief="ridge",
            borderwidth=2,
            width=40,
            height=5,
        )
        self.label.pack(pady=20, padx=20, fill="both", expand=False)
        # Enable the label as drop target
        self.label.drop_target_register(DND_FILES)
        self.label.dnd_bind("<<Drop>>", self.handle_drop)

        # Button to open file dialog
        self.btn_open = tk.Button(
            self,
            text="Abrir archivo",
            font=self.font_family,
            command=self.open_file_dialog,
            bg="#764ba2",
            fg="white",
            activebackground="#9f7aea",
            relief="flat",
            padx=15,
            pady=8,
            cursor="hand2",
        )
        self.btn_open.pack(pady=(0, 15))

        # Scrolled text to display file content
        self.text_area = scrolledtext.ScrolledText(
            self,
            font=("Consolas", 11),
            bg="#1e1e1e",
            fg="#dcdcdc",
            insertbackground="white",
            wrap="word",
            borderwidth=1,
            relief="sunken",
            width=80,
            height=20,
        )
        self.text_area.pack(padx=20, pady=(0,20), fill="both", expand=True)
        self.text_area.insert("1.0", "El contenido del archivo aparecerá aquí...")

    def open_file_dialog(self):
        filepath = filedialog.askopenfilename(
            title="Selecciona un archivo de texto",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if filepath:
            self.load_file_content(filepath)

    def handle_drop(self, event):
        # event.data may contain a string with file path(s)
        files = self.split_drop_files(event.data)
        if files:
            self.load_file_content(files[0])

    def split_drop_files(self, data):
        """Split the dropped data into file paths."""
        # On Windows, paths might be wrapped with {}
        files = []
        while data:
            if data[0] == '{':
                # find closing }
                end_idx = data.find('}')
                if end_idx == -1:
                    # malformed, just break
                    break
                files.append(data[1:end_idx])
                data = data[end_idx+1:].strip()
            else:
                # until first space
                parts = data.split(' ', 1)
                files.append(parts[0])
                if len(parts) == 1:
                    break
                data = parts[1].strip()
        return files

    def load_file_content(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert(tk.END, content)
            self.label.config(text=f"Archivo cargado:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el archivo:\n{e}")


if __name__ == "__main__":
    app = DragDropFileReader()
    app.mainloop()


# Definir el archivo de origen y el archivo de destino
#archivo_origen = 'enero.xlsx'  # Cambia esto por el nombre de tu archivo de origen
archivo_destino = 'destino.xlsx'  # Cambia esto por el nombre de tu archivo de destino

# Leer el archivo Excel de origen
# Pedir al usuario la ruta del archivo
ruta_archivo = input("Por favor, introduce la ruta o el nombre del archivo que deseas leer: ")

# Intentar abrir y leer el archivo
try:
    with open(ruta_archivo, 'r') as archivo:
        contenido = archivo.read()
        print("Contenido del archivo:")
        print(contenido)
except FileNotFoundError:
    print("El archivo no se encontró. Por favor, verifica la ruta e inténtalo de nuevo.")
except Exception as e:
    print(f"Ocurrió un error: {e}")

df = pd.read_excel(ruta_archivo)

# Especificar las columnas que deseas extraer
columnas_a_extraer = ['Columna1', 'Columna2']  # Cambia esto por los nombres de las columnas que necesitas

# Aplicar filtros a los datos
# Ejemplo: Filtrar donde 'Columna3' es igual a un valor específico
filtro = df['Columna3'] == 'ValorEspecifico'  # Cambia 'Columna3' y 'ValorEspecifico' según tus necesidades

# Filtrar el DataFrame
df_filtrado = df[filtro]

# Extraer las columnas deseadas del DataFrame filtrado
df_extraido = df_filtrado[columnas_a_extraer]

# Convertir a JSON
json_data = df_extraido.to_json(orient='records')

# Guardar el DataFrame extraído en un nuevo archivo Excel
df_extraido.to_excel(archivo_destino, index=False)

# Imprimir el JSON (opcional)
print(json_data)
