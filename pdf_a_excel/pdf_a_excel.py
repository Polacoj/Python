import pandas as pd
from pypdf import PdfReader
import re
import os
import openpyxl
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD

pdf_files = [
    '/Users/alexisjankowicz/Python/pdf_a_excel/BALVANERA96 -DOS (02) DETENIDOS.pdf',
    '/Users/alexisjankowicz/Python/pdf_a_excel/RETIRO55 - UN (01) DETENIDO.pdf',
    '/Users/alexisjankowicz/Python/pdf_a_excel/PARTE SUCESO 45688136.pdf',
    '/Users/alexisjankowicz/Python/pdf_a_excel/PARTE SUCESO 45688962.pdf',
    '/Users/alexisjankowicz/Python/pdf_a_excel/PARTE SUCESO 45705933.pdf',
    '/Users/alexisjankowicz/Python/pdf_a_excel/PARTE SUCESO 45705157.pdf',
    '/Users/alexisjankowicz/Python/pdf_a_excel/CONSTITUCIÓN74 - DOS (02) DETENIDOS.pdf',
]


def pegar(evento):
    # This function will be called when files are dropped onto the label
    archivo = evento.data
    # Convert the string of file paths to a list (handles multiple files)
    rutas = archivo.split() if isinstance(archivo, str) else archivo
    # Create a string with each file path on a new line
    archivos_texto = "Pegado:\n" + "\n".join(rutas)
    ventana_pegado.config(text=archivos_texto)
    print(f"Archivos pegados: {rutas}")  # For debugging purposes

# def aceptar():
    # Cambia el texto del label para indicar aceptación
    ventana_pegado.config(text="Archivos aceptados")
    print("Archivos aceptados")


reemplazo = {
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


def renombrar(texto):
    for patron, sustituir in reemplazo.items():
        texto = re.sub(patron, sustituir, texto, flags=re.IGNORECASE)
    return texto


with open('/Users/alexisjankowicz/Python/pdf_a_excel/pdf_contents.txt', 'w', encoding='utf-8') as f:
    for pdf_file in pdf_files:
        leer = PdfReader(
            "./Users/alexisjankowicz/Python/pdf_a_excel/pdf_contents.txt" + pdf_file)
        texto = ""
        for pagina in leer.pages:
            texto_pagina = pagina.extract_text() or ""
            texto_pagina = renombrar(texto_pagina)
            texto += texto_pagina
        f.write(f"Archivo: {pdf_file}\n")
        f.write(texto)
        f.write("\n" + "="*100 + "\n")

        # Leer el archivo de texto generado
with open('/Users/alexisjankowicz/Python/pdf_a_excel/pdf_contents.txt', 'r', encoding='utf-8') as f:
    contenido = f.read()

    # Separar por archivos
    archivos = contenido.split("="*100 + "\n")

    datos = []
    for archivo in archivos:
        if not archivo.strip():
            continue
            # Extraer nombre de archivo
        match_archivo = re.search(r'Archivo: (.+)\n', archivo)
        nombre_archivo = match_archivo.group(1) if match_archivo else ""
        # Extraer fecha, causa y sae
        # limitar que solo copie hasta 2025 o varios espacios
        match_fecha = re.search(r'fecha:\s*(.*?2025)', archivo, re.IGNORECASE)
        match_causa = re.search(r'causa:\s*([^\n]+)', archivo, re.IGNORECASE)
        match_sae = re.search(r'sae:\s*([^\n]+)', archivo, re.IGNORECASE)
        match_jefe_de_servicio = re.search(
            r'jefe:\s*([^\n]+)', archivo, re.IGNORECASE)
        match_oficial_de_servicio = re.search(
            r'oficial:\s*([^\n]+)', archivo, re.IGNORECASE)
        match_operador_de_camara = re.search(
            r'operador:\s*([^\n]+)', archivo, re.IGNORECASE)
        match_breve = re.search(
            r'hora:\s*.*?(\d{1,2}:\d{2})', archivo, re.IGNORECASE)
        match_resultado = re.search(
            r'resultado:\s*([^\n]+)', archivo, re.IGNORECASE)
        # Agregar los datos extraídos a la lista
        datos.append({
            'archivo': os.path.basename(nombre_archivo),
            'fecha': match_fecha.group(1).strip() if match_fecha else "S/D",
            'causa': match_causa.group(1).strip() if match_causa else "S/D",
            'sae': match_sae.group(1).strip() if match_sae else "S/D",
            'jefe de servicio': match_jefe_de_servicio.group(1).strip() if match_jefe_de_servicio else "S/D",
            'oficial de servicio': match_oficial_de_servicio.group(1).strip() if match_oficial_de_servicio else "S/D",
            'operador de camara': match_operador_de_camara.group(1).strip() if match_operador_de_camara else "S/D",
            'hora': match_breve.group(1).strip() if match_breve else "S/D",
            'resultado': match_resultado.group(1).strip() if match_resultado else "S/D"
        })

        # Crear DataFrame y guardar en Excel
        df = pd.DataFrame(datos)
        df.to_excel(
            '/Users/alexisjankowicz/Python/pdf_a_excel/datos_extraidos.xlsx', index=False)

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
boton_aceptar = tk.Button(frame, text="Aceptar", command=exit)
boton_aceptar.pack(pady=10)

# Register the label as a drop target
ventana_pegado.drop_target_register(DND_FILES)
ventana_pegado.dnd_bind('<<Drop>>', pegar)

# Run the application
if __name__ == "__main__":
    root.mainloop()
