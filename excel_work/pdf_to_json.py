import os
import csv
import PyPDF2
import re

def pdf_to_csv(pdf_path, csv_path):
    if not pdf_path.lower().endswith('.pdf'):
        raise ValueError("El archivo debe tener extensión .pdf")
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"No se encontró el archivo: {pdf_path}")

    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

    # Buscar encabezados y contenido
    # Suponiendo que el formato es: "fecha: ...\nsae: ...\noperador: ...\noficial: ...\n"
    # y el resto es contenido
    encabezados = {'fecha': '', 'sae': '', 'operador': '', 'oficial': ''}
    contenido = ""
    lines = text.splitlines()
    found_headers = 0

    for line in lines:
        for key in encabezados.keys():
            match = re.match(rf"{key}\s*:\s*(.*)", line, re.IGNORECASE)
            if match:
                encabezados[key] = match.group(1).strip()
                found_headers += 1
                break
        else:
            # Si ya se encontraron todos los encabezados, el resto es contenido
            if found_headers == len(encabezados):
                contenido = "\n".join(lines[lines.index(line):]).strip()
                break

    with open(csv_path, 'w', encoding='utf-8', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['fecha', 'sae', 'operador', 'oficial', 'contenido'])
        writer.writerow([
            encabezados['fecha'],
            encabezados['sae'],
            encabezados['operador'],
            encabezados['oficial'],
            contenido
        ])

# Ejemplo de uso:
pdf_to_csv("1DETENIDO-HURTO-BOEDO O116.docx.pdf", "documento.csv")