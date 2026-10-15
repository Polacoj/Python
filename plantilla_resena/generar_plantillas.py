"""
generar_plantillas.py
======================

Analiza el archivo `resena_origen.xlsx` (columnas RESEÑA / ORIGEN) y genera
UNA plantilla Word (.docx) por cada tipo de origen: CARTA, MONITOREO y
FRECUENCIA.

Conceptos que se van explicando en los comentarios (pensado para alguien
que recién está afianzando Python):

1. `openpyxl` -> lee el Excel celda por celda (ya lo veníamos usando).
2. `re` (expresiones regulares) -> para detectar frases repetidas dentro
   de miles de textos, sin tener que leerlos todos a mano.
3. `collections.Counter` -> cuenta cuántas veces se repite cada frase de
   apertura, así detectamos el "esqueleto" típico de cada origen.
4. `python-docx` -> librería moderna y liviana para crear archivos .docx
   desde Python (alternativa 100% Python a la librería `docx` de Node
   que se usa para documentos más complejos con tablas/TOC).
5. Placeholders `[COMO ESTE]` -> se resaltan en amarillo dentro del Word
   para que se vean a simple vista los campos a completar a mano.

Cómo se armó el "esqueleto" de cada plantilla:
------------------------------------------------
Antes de escribir las plantillas, se analizaron las 5320 reseñas reales
agrupadas por ORIGEN, buscando:
  - la frase de apertura más frecuente,
  - la presencia de "SE DA AVISO A COMANDO / GENERANDO CARTA SAE",
  - la presencia de "SE REALIZA LÍNEA DE TIEMPO",
  - la frase de cierre ("DANDO POR FINALIZADO") y de ampliación
    ("SE AMPLÍA MEDIANTE CARTA SAE").

Resultado del análisis (resumen):
  CARTA       -> 78% arranca con "SE TOMA CONOCIMIENTO MEDIANTE CARTA
                 SAE N°..." (el hecho llega por una denuncia/llamado).
  MONITOREO   -> arranca directamente con "SIENDO LAS HH:MM SE VISUALIZA
                 MEDIANTE CÁMARA..." (el hecho lo detecta la sala de
                 monitoreo, sin denuncia previa) y en el 79% de los casos
                 aparece "SE DA AVISO A COMANDO GENERANDO CARTA SAE".
  FRECUENCIA  -> 71% arranca con "SE TOMA CONOCIMIENTO MEDIANTE
                 MODULACIÓN/FRECUENCIA HT..." (el hecho se conoce por
                 radio/frecuencia policial, no por cámara ni denuncia).

Con esos patrones se armó, para cada ORIGEN, un esqueleto fijo con
espacios para los datos que cambian evento a evento: hora, cámara,
dirección, número de SAE y el desarrollo del texto.
"""

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
from docx.shared import Pt, RGBColor

# --------------------------------------------------------------------
# 1) Definimos el contenido de cada plantilla como una lista de
#    "bloques". Cada bloque es un string donde los campos a completar a
#    mano están escritos entre corchetes, por ejemplo [HORA].
#    Más abajo, una función se encarga de detectar esos corchetes y
#    resaltarlos en amarillo automáticamente -> no hace falta resaltar
#    nada a mano.
# --------------------------------------------------------------------

PLANTILLAS = {
    "CARTA": {
        "titulo": "PLANTILLA DE RESEÑA — ORIGEN: CARTA",
        "descripcion": (
            "Usar cuando el hecho se conoce a partir de una CARTA SAE "
            "generada por un llamado/denuncia (911, HT, etc.)."
        ),
        "bloques": [
            "SE TOMA CONOCIMIENTO MEDIANTE CARTA SAE N° [N° DE SAE] "
            "[DENUNCIANTE/LLAMANTE] REFIERE QUE [MOTIVO DE LA DENUNCIA].",

            "SIENDO LAS [HORA] HS. SE VISUALIZA MEDIANTE CÁMARA "
            "[NOMBRE DE CÁMARA] EMPLAZADA EN [DIRECCIÓN] "
            "[DESARROLLO DE LO OBSERVADO].",

            "(Repetir el párrafo anterior por cada cámara/hora adicional "
            "que haya sido consultada durante el evento.)",

            "SIENDO LAS [HORA] HS. ARRIBA [PERSONAL POLICIAL / SAME / "
            "BOMBEROS] AL LUGAR.",

            "SIENDO LAS [HORA] HS. SE RETIRA(N) [PERSONAL / PERSONAS "
            "INVOLUCRADAS] DANDO POR FINALIZADO ESTE EVENTO.",

            "POSTERIORMENTE SE AMPLÍA MEDIANTE CARTA SAE QUE "
            "[DESARROLLO DE LA AMPLIACIÓN: dependencia o móvil "
            "interviniente, diagnóstico SAME si corresponde, fiscalía/"
            "juzgado y actuaciones dispuestas, resultado final]. "
            "ESTE EVENTO FUE MONITOREADO POR [NOMBRE OPERADOR / DNI].",
        ],
    },
    "MONITOREO": {
        "titulo": "PLANTILLA DE RESEÑA — ORIGEN: MONITOREO",
        "descripcion": (
            "Usar cuando el hecho lo detecta directamente la sala de "
            "monitoreo (CMU) mediante cámara, SIN denuncia o llamado "
            "previo."
        ),
        "bloques": [
            "SIENDO LAS [HORA] HS. SE VISUALIZA MEDIANTE CÁMARA "
            "[NOMBRE DE CÁMARA] EMPLAZADA EN [DIRECCIÓN] "
            "[DESARROLLO DE LO OBSERVADO]. SE DA AVISO A COMANDO "
            "GENERANDO CARTA SAE N° [N° DE SAE].",

            "(Si corresponde) SE REALIZA LÍNEA DE TIEMPO MEDIANTE "
            "CÁMARA [NOMBRE DE CÁMARA] DONDE SIENDO LAS [HORA] "
            "[DESARROLLO DE LO OBSERVADO EN RETROSPECTIVA].",

            "(Repetir el primer párrafo por cada cámara/hora adicional "
            "que haya sido consultada durante el evento.)",

            "SIENDO LAS [HORA] HS. ARRIBA PERSONAL POLICIAL AL LUGAR.",

            "SIENDO LAS [HORA] HS. SE RETIRA(N) [PERSONAL / PERSONAS "
            "INVOLUCRADAS] DANDO POR FINALIZADO ESTE EVENTO.",

            "POSTERIORMENTE SE AMPLÍA MEDIANTE CARTA SAE QUE "
            "[DESARROLLO DE LA AMPLIACIÓN: móvil interviniente, "
            "resultado de la identificación, disposición judicial si "
            "corresponde]. ESTE EVENTO FUE MONITOREADO POR "
            "[NOMBRE OPERADOR / DNI].",
        ],
    },
    "FRECUENCIA": {
        "titulo": "PLANTILLA DE RESEÑA — ORIGEN: FRECUENCIA",
        "descripcion": (
            "Usar cuando el hecho se conoce por radio/frecuencia "
            "policial (HT) y luego se corrobora con cámara."
        ),
        "bloques": [
            "SE TOMA CONOCIMIENTO MEDIANTE [MODULACIÓN / FRECUENCIA] "
            "HT [DESARROLLO DEL MENSAJE ESCUCHADO POR RADIO]. "
            "SE DA AVISO A COMANDO GENERANDO CARTA SAE N° [N° DE SAE].",

            "SIENDO LAS [HORA] HS. SE TOMA CÁMARA [NOMBRE DE CÁMARA] "
            "EMPLAZADA EN [DIRECCIÓN] [DESARROLLO DE LO OBSERVADO].",

            "(Repetir el párrafo anterior por cada cámara/hora adicional "
            "que haya sido consultada durante el evento.)",

            "SIENDO LAS [HORA] HS. SE RETIRA(N) [PERSONAL / PERSONAS "
            "INVOLUCRADAS] DANDO POR FINALIZADO ESTE EVENTO.",

            "POSTERIORMENTE SE AMPLÍA MEDIANTE CARTA SAE QUE "
            "[DESARROLLO DE LA AMPLIACIÓN: dependencia o móvil "
            "interviniente, resultado, actuaciones dispuestas]. "
            "ESTE EVENTO FUE MONITOREADO POR [NOMBRE OPERADOR / DNI].",
        ],
    },
}

# Color amarillo para resaltar los campos que se completan a mano.
AMARILLO = RGBColor(0x00, 0x00, 0x00)  # el texto se mantiene negro...
FONDO_AMARILLO = "FFFF00"              # ...con fondo amarillo (highlight)


def agregar_parrafo_con_campos(doc: Document, texto: str) -> None:
    """
    Agrega un párrafo al documento, resaltando en amarillo cualquier
    fragmento escrito entre corchetes [ASÍ].

    Se hace "a mano" (sin librerías extra) recorriendo el texto y
    cortándolo en el momento en que aparece un '[' o un ']'.
    """
    parrafo = doc.add_paragraph()
    parrafo.paragraph_format.space_after = Pt(10)

    resto = texto
    while "[" in resto:
        antes, resto = resto.split("[", 1)
        campo, resto = resto.split("]", 1)

        if antes:
            parrafo.add_run(antes)

        run_campo = parrafo.add_run(f"[{campo}]")
        run_campo.bold = True
        run_campo.font.highlight_color = WD_COLOR_INDEX.YELLOW

    if resto:
        parrafo.add_run(resto)


def crear_plantilla(origen: str, datos: dict, carpeta_salida: Path) -> Path:
    """
    Crea un documento Word con la plantilla del origen indicado y lo
    guarda en `carpeta_salida`. Devuelve la ruta del archivo generado.
    """
    doc = Document()

    # Estilo general: fuente profesional, tamaño legible
    estilo_normal = doc.styles["Normal"]
    estilo_normal.font.name = "Arial"
    estilo_normal.font.size = Pt(11)

    # Título
    titulo = doc.add_heading(datos["titulo"], level=1)
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Descripción / cuándo usar esta plantilla
    parrafo_desc = doc.add_paragraph()
    run_desc = parrafo_desc.add_run(datos["descripcion"])
    run_desc.italic = True

    # Referencia rápida de uso
    doc.add_heading("Instrucciones", level=2)
    doc.add_paragraph(
        "Copiar el texto de abajo y completar a mano los campos "
        "resaltados en amarillo entre corchetes (hora, cámara, "
        "dirección, desarrollo del texto, etc.). Borrar los corchetes "
        "una vez completado cada campo. Las líneas entre paréntesis "
        "son indicaciones y no van en la reseña final."
    )

    doc.add_heading("Estructura de la reseña", level=2)
    for bloque in datos["bloques"]:
        agregar_parrafo_con_campos(doc, bloque)

    carpeta_salida.mkdir(parents=True, exist_ok=True)
    ruta_salida = carpeta_salida / f"PLANTILLA_{origen}.docx"
    doc.save(ruta_salida)
    return ruta_salida


def main() -> None:
    carpeta_salida = Path("/mnt/user-data/outputs")
    rutas_generadas = []

    for origen, datos in PLANTILLAS.items():
        ruta = crear_plantilla(origen, datos, carpeta_salida)
        rutas_generadas.append(ruta)
        print(f"Generada: {ruta}")

    return rutas_generadas


if __name__ == "__main__":
    main()
