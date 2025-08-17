import os
import re
from pypdf import PdfReader

lugar = os.listdir("/Users/alexisjankowicz/Python/pdf_a_excel/pdfs")

for i in lugar:
    documento = PdfReader("/Users/alexisjankowicz/Python/pdf_a_excel/pdfs/" + i)
    contenido = ""
    contenido += "----------" + i + "----------------\n"
    for pagina in documento.pages:
        contenido += pagina.extract_text()
        print(contenido)

    
    
    
    
"""
documento = PdfReader(lugar)
num_pag = len(documento.pages)
print(f"El documento tiene {num_pag} páginas.")

for i, pagina in enumerate(documento.pages):
    texto = pagina.extract_text()
    print(f"Texto de la página {i + 1}:\n{texto}\n")
    """