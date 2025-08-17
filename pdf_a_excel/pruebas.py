import pandas as pd
from pypdf import PdfReader
import re
import os
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import messagebox


class PDFtoExcelConverter:
    def __init__(self):
        self.reemplazo = {
            r'fecha\s*:': 'fecha:',
            r'causa\s*:': 'causa:',
            r'sae\s*:': 'sae:',
            r'Jefe de Servicio\s*:': 'Jefe:',
            r'Oficial de servicio\s*:': 'Oficial:',
            r'Operador de cámara\s*:': 'Operador:',
            r'Breve[^\:]*:\s*': 'hora:',
            r'Siendo\s*las\s*': '',
            r'resultado\s*:': 'resultado:',
        }
        self.pdf_files = []
        
    def renombrar(self, texto):
        """Normaliza el texto reemplazando patrones."""
        for patron, sustituir in self.reemplazo.items():
            texto = re.sub(patron, sustituir, texto, flags=re.IGNORECASE)
        print(f"Texto renombrado: {texto}")  # Para depuración
        return texto
        
        
    def extraer_datos(self, pdf_file):
        """Extrae y procesa datos de un archivo PDF."""
        try:
            leer = PdfReader(pdf_file)
            texto = "".join(pagina.extract_text() or "" for pagina in leer.pages)
            texto = self.renombrar(texto)
            return {
                'archivo': os.path.basename(pdf_file),
                'fecha': self._buscar_patron(r'fecha:\s*(.*?2025)', texto),
                'causa': self._buscar_patron(r'causa:\s*([^\n]+)', texto),
                'sae': self._buscar_patron(r'sae:\s*([^\n]+)', texto),
                'jefe de servicio': self._buscar_patron(r'jefe:\s*([^\n]+)', texto),
                'oficial de servicio': self._buscar_patron(r'oficial:\s*([^\n]+)', texto),
                'operador de camara': self._buscar_patron(r'operador:\s*([^\n]+)', texto),
                'hora': self._buscar_patron(r'hora:\s*.*?(\d{1,2}:\d{2})', texto),
                'resultado': self._buscar_patron(r'resultado:\s*([^\n]+)', texto)
            }
        except Exception as e:
            print(f"Error procesando {pdf_file}: {str(e)}")
            return None
    
    def _buscar_patron(self, patron, texto):
        """Busca un patrón en el texto y devuelve el grupo capturado o 'S/D'."""
        match = re.search(patron, texto, re.IGNORECASE)
        return match.group(1).strip() if match else "S/D"
    
    def procesar_pdfs(self, pdf_files, output_excel):
        """Procesa una lista de PDFs y guarda los datos en un Excel."""
        datos = []
        for pdf_file in pdf_files:
            if dato := self.extraer_datos(pdf_file):
                datos.append(dato)
        if datos:
            df = pd.DataFrame(datos)
            df.to_excel(output_excel, index=False)
            print(f"Datos guardados en {output_excel}")
            return True
        return False

class PDFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF to Excel Converter")
        self.root.geometry("500x300")
        self.converter = PDFtoExcelConverter()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Label para arrastrar y soltar archivos
        self.label = tk.Label(
            self.frame,
            text="Arrastra y suelta archivos PDF aquí",
            bg="#f0f0f0",
            font=("Helvetica", 12),
            relief="groove",
            height=10,
            width=50
        )
        self.label.pack(pady=20)
        
        # Botón de procesamiento
        self.btn_procesar = tk.Button(
            self.frame, 
            text="Procesar PDFs", 
            command=self.procesar
        )
        self.btn_procesar.pack(side=tk.LEFT)
        
        self.cerrar = tk.Button(
            self.frame, 
            text="Cerrar", 
            command=exit
        )
        self.cerrar.pack(side=tk.RIGHT)
        
        # Configurar DnD
        self.label.drop_target_register(DND_FILES)
        self.label.dnd_bind('<<Drop>>', self.on_drop)
        
    def on_drop(self, event):
        """Maneja el evento de soltar archivos."""
        files = event.data.split() if isinstance(event.data, str) else event.data
        self.converter.pdf_files = [f.strip('{}') for f in files]  # Windows añade llaves
        self.label.config(text="Archivos listos:\n" + "\n".join(os.path.basename(f) for f in self.converter.pdf_files))
        
    def procesar(self):
        """Inicia el procesamiento de los PDFs."""
        if not self.converter.pdf_files:
            tk.messagebox.showwarning("Advertencia", "No hay archivos PDF cargados")
            return
        
        output_file = "/Users/alexisjankowicz/Python/pdf_a_excel/datos_extraidos.xlsx"  # Puedes hacer esto configurable
        if self.converter.procesar_pdfs(self.converter.pdf_files, output_file):
            tk.messagebox.showinfo("Éxito", f"Datos exportados a:\n{output_file}")
        else:
            tk.messagebox.showerror("Error", "No se pudo procesar los archivos PDF")


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = PDFApp(root)
    root.mainloop()
