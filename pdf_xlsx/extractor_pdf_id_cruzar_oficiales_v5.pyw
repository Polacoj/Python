import json
import os
import re
import subprocess
import sys
import tkinter as tk
import traceback
import unicodedata
from datetime import date, datetime
from tkinter import filedialog, messagebox
from urllib.parse import unquote

import openpyxl
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
from docx.shared import Pt, RGBColor
from openpyxl.styles import Alignment, Font
from openpyxl.worksheet.hyperlink import Hyperlink
from pypdf import PdfReader

"""
Extractor de datos desde archivos PDF y conversión a Excel y Word"""
# Variable global para almacenar rutas
rutas_global = []


def obtener_siguiente_id(carpeta_pdfs):
    """
    Escanea la carpeta de los PDF buscando archivos que ya fueron
    renombrados con el patrón "N_nombre.pdf" (donde N es el número que
    se les puso al principio) y devuelve el próximo número disponible.

    Ya no se basa en ninguna columna del Excel (esa columna "ID" se
    sacó) — el número ahora vive únicamente en el nombre del archivo
    en disco, así que basta con mirar qué números ya se usaron ahí.

    Si la carpeta está vacía o no tiene ningún PDF renombrado todavía,
    empieza en 1.
    """
    numeros_usados = []
    if os.path.isdir(carpeta_pdfs):
        for nombre in os.listdir(carpeta_pdfs):
            id_encontrado = id_desde_nombre_pdf(nombre)
            if id_encontrado is not None:
                numeros_usados.append(id_encontrado)
    return max(numeros_usados, default=0) + 1


def id_desde_nombre_pdf(nombre_archivo):
    """
    Extrae el ID que está al inicio del nombre de un PDF ya renombrado
    por este programa (ej: "1~constitucion34.pdf" -> 1).

    Devuelve None si el nombre no empieza con un número seguido de "~",
    es decir, si no fue renombrado por este programa.
    """
    coincidencia = re.match(r"^(\d+)~", nombre_archivo)
    return int(coincidencia.group(1)) if coincidencia else None


def normalizar_texto(texto):
    """
    Unifica la forma en que están escritos los acentos en un texto.

    El mismo caracter visible (ej: "Ó") se puede guardar de dos formas
    distintas por dentro: como un solo caracter ("Ó", forma NFC) o como
    la letra suelta más el acento aparte ("O" + "´", forma NFD). Visualmente
    son iguales, pero como texto NO son iguales, y por eso una comparación
    tipo "está contenido en" puede fallar sin ningún error visible.

    Esto pasa seguido con nombres de archivo guardados desde macOS.
    unicodedata.normalize("NFC", ...) reescribe todo a la forma de "un
    solo caracter", así que dos textos que se ven igual, comparan igual.
    """
    return unicodedata.normalize("NFC", texto)


def nombre_desde_ruta(ruta):
    """
    Recorta una ruta completa (o un hipervínculo) y se queda solo con
    el nombre del archivo: todo lo que hay DESPUÉS de la última "/" (o
    "\\", por si la ruta viene con formato de Windows).

    Ejemplos:
      "/Users/alexis/Trabajo/Dias/31.VIERNES/8_constitucion.pdf" -> "8_constitucion.pdf"
      "../../Trabajo/Dias/31.VIERNES%2031-07-2026/8_constitucion.pdf" -> "8_constitucion.pdf"

    Antes se comparaba "¿el nombre del PDF aparece en algún lugar
    dentro de la ruta completa?", pero esa comparación es frágil: un
    espacio de más, un "%20" sin decodificar, etc. hacen que falle.
    Comparar únicamente el nombre final es mucho más preciso.
    """
    # Los hipervínculos de Excel codifican los espacios como "%20";
    # unquote() los devuelve a como se ven realmente (" ").
    ruta_decodificada = unquote(ruta)

    # Partimos tanto por "/" como por "\" y nos quedamos con el último
    # trozo, que es el nombre del archivo solo, sin ninguna carpeta.
    partes = re.split(r"[\\/]", ruta_decodificada)
    return partes[-1].strip() if partes else ruta_decodificada.strip()


def leer_rutas_excel(ruta_excel):
    """
    Lee TODAS las hojas del Excel indicado y, de la columna "RUTA",
    desglosa cada ruta y cada hipervínculo para quedarse solo con el
    NOMBRE del archivo (lo que hay después de la última "/").

    Devuelve una lista con esos nombres, ya normalizados. Más adelante,
    para saber si un PDF "ya está" en el Excel, alcanza con comparar
    su nombre contra esta lista.

    Recorrer todas las hojas (y no solo la primera) es importante
    porque el archivo "DETENIDOS_OFICIALES_2026.xlsx" tiene una hoja
    distinta por mes (ENERO, FEBRERO, ...).
    """
    nombres_encontrados = []
    wb = openpyxl.load_workbook(ruta_excel, data_only=True)
    for nombre_hoja in wb.sheetnames:
        ws = wb[nombre_hoja]

        # Ubicar en qué columna está el encabezado "RUTA" en esta hoja
        # (por si algún día cambia de posición, no lo dejamos fijo en "A").
        col_ruta = None
        for celda in ws[1]:
            if celda.value and str(celda.value).strip().upper() == "RUTA":
                col_ruta = celda.column
                break
        if col_ruta is None:
            continue  # esta hoja no tiene columna "RUTA" (ej: hoja "T.E")

        for fila in range(2, ws.max_row + 1):
            celda = ws.cell(row=fila, column=col_ruta)
            if celda.value:
                nombre = nombre_desde_ruta(str(celda.value))
                nombres_encontrados.append(normalizar_texto(nombre))
            if celda.hyperlink and celda.hyperlink.target:
                nombre = nombre_desde_ruta(str(celda.hyperlink.target))
                nombres_encontrados.append(normalizar_texto(nombre))

    return nombres_encontrados


def leer_registros_excel(ruta_excel, nombre_hoja):
    """Lee las rutas y fechas de una hoja elegida del Excel."""
    wb = openpyxl.load_workbook(ruta_excel, data_only=True)
    ws = wb[nombre_hoja]
    columnas = {}
    for celda in ws[1]:
        if celda.value:
            columnas[str(celda.value).strip().upper()] = celda.column

    if "RUTA" not in columnas or "FECHA" not in columnas:
        raise ValueError(
            f'La hoja "{nombre_hoja}" debe tener las columnas "RUTA" y "FECHA".'
        )

    registros = []
    for fila in range(2, ws.max_row + 1):
        celda_ruta = ws.cell(row=fila, column=columnas["RUTA"])
        celda_fecha = ws.cell(row=fila, column=columnas["FECHA"])
        valor_ruta = celda_ruta.value or (
            celda_ruta.hyperlink.target if celda_ruta.hyperlink else ""
        )
        if not valor_ruta:
            continue

        fecha = formatear_fecha_excel(celda_fecha.value)
        valor_contraventor = (
            ws.cell(row=fila, column=columnas["CONTRAVENTORES"]).value
            if "CONTRAVENTORES" in columnas
            else 0
        )
        valor_detenido = (
            ws.cell(row=fila, column=columnas["DETENIDOS"]).value
            if "DETENIDOS" in columnas
            else 0
        )
        registros.append(
            {
                "nombre": normalizar_texto(nombre_desde_ruta(str(valor_ruta))),
                "fecha": fecha,
                "contraventores": valor_contraventor,
                "detenidos": valor_detenido,
            }
        )
    return registros


def leer_maestro_control_diario(ruta_maestro):
    """
    Ejecuta el script independiente de conteo_fechas como subproceso y
    devuelve el diccionario de eventos por fecha en formato DD/MM.

    Acepta una sola ruta o una lista de hasta dos rutas para sumar archivos
    de meses consecutivos cuando el período incluye días del siguiente mes.
    """
    try:
        rutas = (
            ruta_maestro if isinstance(ruta_maestro, (list, tuple)) else [ruta_maestro]
        )
        if len(rutas) > 2:
            raise ValueError("El conteo admite como máximo dos archivos maestros.")

        ruta_script = os.path.join(os.path.dirname(__file__), "conteo_fechas.py")
        comando = [sys.executable, ruta_script, *rutas, "--json"]
        resultado = subprocess.run(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        salida = (resultado.stdout or "").strip()
        if not salida:
            return {}
        payload = json.loads(salida)
        return payload.get("DD/MM", {})
    except Exception as e:
        messagebox.showerror(
            "Error",
            f"No se pudo leer el archivo maestro con el conteo de fechas:\n{str(e)}",
        )
        return {}


def leer_tipificaciones_por_fecha(ruta_archivo):
    """
    Ejecuta el script conteo_interv.py y devuelve el conteo de tipificaciones
    por fecha excluyendo las filas de colaboración.
    """
    try:
        rutas = (
            ruta_archivo if isinstance(ruta_archivo, (list, tuple)) else [ruta_archivo]
        )
        if len(rutas) > 2:
            raise ValueError("El conteo admite como máximo dos archivos Excel.")

        ruta_script = os.path.join(os.path.dirname(__file__), "conteo_interv.py")
        comando = [sys.executable, ruta_script, *rutas, "--json"]
        resultado = subprocess.run(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        salida = (resultado.stdout or "").strip()
        if not salida:
            return {}
        payload = json.loads(salida)
        return payload.get("DD/MM", {})
    except Exception as e:
        messagebox.showerror(
            "Error",
            f"No se pudo leer la tipificación del archivo:\n{str(e)}",
        )
        return {}


def formatear_fecha_excel(valor):
    """Convierte un valor de celda FECHA al mismo formato usado por los PDF."""
    if valor is None or str(valor).strip() == "":
        return "S/D"

    if isinstance(valor, (datetime, date)):
        return valor.strftime("%d/%m")

    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        try:
            # OpenPyXL guarda fechas como número de serie Excel.
            fecha_excel = datetime(1899, 12, 30) + pd.Timedelta(days=float(valor))
            return fecha_excel.strftime("%d/%m")
        except Exception:
            pass

    return formatear_fecha(str(valor))


def convertir_a_entero(valor):
    """Convierte un conteo del Excel a entero; los valores no numéricos valen cero."""
    if valor is None:
        return 0

    texto = str(valor).strip()
    if texto == "" or texto.upper() in {"S/D", "SD", "N/A"}:
        return 0

    texto = texto.replace(" ", "")
    try:
        if "," in texto and "." in texto:
            if texto.rfind(",") > texto.rfind("."):
                texto = texto.replace(".", "").replace(",", ".")
            else:
                texto = texto.replace(",", "")
        elif "," in texto:
            if texto.count(",") == 1 and len(texto.split(",")[-1]) <= 2:
                texto = texto.replace(",", ".")
            else:
                texto = texto.replace(",", "")
        elif "." in texto and texto.count(".") > 1:
            texto = texto.replace(".", "")

        return int(float(texto))
    except (TypeError, ValueError):
        return 0


def resumen_por_fecha(registros, fechas_elegidas):
    """Calcula eventos e imputados para cada fecha seleccionada."""
    resumen = []
    for fecha in fechas_elegidas:
        registros_fecha = [
            registro for registro in registros if registro["fecha"] == fecha
        ]
        imputados = sum(
            convertir_a_entero(registro["contraventores"])
            + convertir_a_entero(registro["detenidos"])
            for registro in registros_fecha
        )
        resumen.append(
            {
                "fecha": fecha,
                "imputados": imputados,
                "eventos_relevantes": len(registros_fecha),
            }
        )
    return resumen


def seleccionar_opciones_checkbutton(titulo, mensaje, opciones, max_selecciones=None):
    """Muestra una selección modal con casillas y devuelve las opciones elegidas."""
    dialogo = tk.Toplevel(root)
    dialogo.title(titulo)
    dialogo.transient(root)
    dialogo.grab_set()
    dialogo.geometry("460x420")

    tk.Label(dialogo, text=mensaje, anchor="w", justify=tk.LEFT).pack(
        fill=tk.X, padx=12, pady=(12, 6)
    )
    marco_lista = tk.Frame(dialogo)
    marco_lista.pack(fill=tk.BOTH, expand=True, padx=12)

    canvas = tk.Canvas(marco_lista, highlightthickness=0)
    scrollbar = tk.Scrollbar(marco_lista, orient=tk.VERTICAL, command=canvas.yview)
    contenido = tk.Frame(canvas)
    canvas.create_window((0, 0), window=contenido, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    variables = []
    for opcion in opciones:
        variable = tk.BooleanVar(value=False)
        tk.Checkbutton(contenido, text=opcion, variable=variable, anchor="w").pack(
            fill=tk.X
        )
        variables.append((opcion, variable))

    contenido.bind(
        "<Configure>", lambda evento: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    resultado = []

    def aceptar():
        seleccionada = [opcion for opcion, variable in variables if variable.get()]
        if max_selecciones is not None and len(seleccionada) > max_selecciones:
            messagebox.showwarning(
                "Límite excedido",
                f"Máximo permitido: {max_selecciones} fechas. "
                f"Seleccionaste {len(seleccionada)}.",
            )
            return
        resultado.extend(seleccionada)
        dialogo.destroy()

    def cancelar():
        dialogo.destroy()

    marco_botones = tk.Frame(dialogo)
    marco_botones.pack(fill=tk.X, padx=12, pady=12)
    tk.Button(
        marco_botones,
        text="Seleccionar todas",
        command=lambda: [variable.set(True) for _, variable in variables],
    ).pack(side=tk.LEFT)
    tk.Button(
        marco_botones,
        text="Limpiar",
        command=lambda: [variable.set(False) for _, variable in variables],
    ).pack(side=tk.LEFT, padx=6)
    tk.Button(marco_botones, text="Cancelar", command=cancelar).pack(side=tk.RIGHT)
    tk.Button(marco_botones, text="Aceptar", command=aceptar).pack(
        side=tk.RIGHT, padx=6
    )

    dialogo.protocol("WM_DELETE_WINDOW", cancelar)
    dialogo.wait_window()
    return resultado


def seleccionar_hoja_excel(ruta_excel):
    """Solicita al usuario qué hoja del Excel desea procesar."""
    wb = openpyxl.load_workbook(ruta_excel, read_only=True, data_only=True)
    hojas = list(wb.sheetnames)
    seleccion = seleccionar_opciones_checkbutton(
        "Seleccionar hoja", "Selecciona una hoja del Excel:", hojas
    )
    if len(seleccion) != 1:
        if seleccion:
            messagebox.showwarning("Advertencia", "Selecciona solamente una hoja.")
        return None
    return seleccion[0]


def seleccionar_hojas_parte_semanal(ruta_excel):
    """
    Para el Parte Semanal, permite seleccionar 1 o 2 hojas (meses),
    ya que un parte semanal puede abarcar fechas de dos meses distintos
    (ej: últimos 2 días de julio + primeros 5 días de agosto).

    Devuelve una lista con 1 o 2 nombres de hojas, o None si el usuario
    cancela o selecciona un número inválido de hojas.
    """
    wb = openpyxl.load_workbook(ruta_excel, read_only=True, data_only=True)
    hojas = list(wb.sheetnames)
    seleccion = seleccionar_opciones_checkbutton(
        "Seleccionar hojas (meses)",
        "Selecciona 1 o 2 hojas para el parte semanal:",
        hojas,
    )
    if not seleccion or len(seleccion) > 2:
        if seleccion:
            messagebox.showwarning(
                "Advertencia", "Debes seleccionar 1 o 2 hojas para el parte semanal."
            )
        return None
    return seleccion


def crear_documento_base():
    """
    Arma la plantilla base de un Word: encabezado institucional +
    tabla de resumen "PARTE SEMANAL". La usan tanto el botón
    "Ejecutar" (cuando reseña_archivos.docx todavía no existe) como
    el botón "Parte Semanal" (que siempre arranca un documento nuevo).
    """
    doc = Document()

    encabezado = doc.add_heading("División CENTROS DE MONITOREO URBANO", 0)
    encabezado.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    encabezado.runs[0].font.size = Pt(20)

    table = doc.add_table(rows=10, cols=5)
    table.style = "Table Grid"

    row = table.rows[0]
    row.cells[0].merge(row.cells[4])  # Combina celda 0 con celda 4

    table.cell(0, 0).text = "PARTE SEMANAL DEL --/--/2026 AL --/--/2026"
    table.cell(1, 0).text = "FECHA"
    table.cell(1, 1).text = "EVENTOS DEL PERÍODO"
    table.cell(1, 2).text = "EVENTOS POSITIVOS"
    table.cell(1, 3).text = "IMPUTADOS"
    table.cell(1, 4).text = "EVENTOS RELEVANTES"
    table.cell(9, 0).text = "TOTAL"

    celda = table.cell(0, 0).paragraphs[0]
    celda.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = celda.runs[0]
    run.font.size = Pt(14)
    run.font.name = "Arial"
    run.font.bold = True
    run.font.color.rgb = RGBColor(255, 255, 255)

    celda = table.cell(9, 0).paragraphs[0]
    celda.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = celda.runs[0]
    run.font.size = Pt(12)
    run.font.bold = True

    fondo = parse_xml(r'<w:shd {} w:fill="1F5C8B"/>'.format(nsdecls("w")))
    table.rows[0].cells[0]._tc.get_or_add_tcPr().append(fondo)

    for i in range(5):
        cell = table.cell(1, i)
        paragraph = cell.paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = paragraph.runs[0]
        run.font.size = Pt(10)
        run.font.name = "Arial"
        run.font.bold = True

    res_encabezado = doc.add_heading("\n\nReseñas extraídas", 0)
    res_encabezado.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    res_encabezado.runs[0].font.size = Pt(14)

    return doc


def completar_tabla_resumen(doc, resumen):
    """Carga el resumen por fecha en las columnas indicadas de la tabla Word."""
    tabla = doc.tables[0]
    while len(tabla.rows) < len(resumen) + 3:
        tabla.add_row()

    for indice, datos_fecha in enumerate(resumen, start=2):
        fila = tabla.rows[indice].cells
        fila[0].text = datos_fecha["fecha"]
        fila[3].text = str(datos_fecha["imputados"])
        fila[4].text = str(datos_fecha["eventos_relevantes"])

        for columna in (0, 3, 4):
            fila[columna].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    fila_total = tabla.rows[-1].cells
    fila_total[0].text = "TOTAL"
    fila_total[3].text = str(sum(dato["imputados"] for dato in resumen))
    fila_total[4].text = str(sum(dato["eventos_relevantes"] for dato in resumen))

    for columna in (0, 3, 4):
        fila_total[columna].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER


def completar_tabla_resumen_con_maestro(
    doc, resumen, eventos_maestro, eventos_positivos
):
    """
    Carga el resumen por fecha en la tabla Word.

    - EVENTOS DEL PERÍODO: se toma del archivo maestro/control diario
    - EVENTOS POSITIVOS: se toma del conteo de tipificaciones excluyendo colaboraciones
    """
    tabla = doc.tables[0]
    while len(tabla.rows) < len(resumen) + 3:
        tabla.add_row()

    for indice, datos_fecha in enumerate(resumen, start=2):
        fila = tabla.rows[indice].cells
        fecha = datos_fecha["fecha"]
        fila[0].text = fecha

        eventos_del_periodo = eventos_maestro.get(fecha, "S/D")
        fila[1].text = str(eventos_del_periodo)

        eventos_positivos_fecha = eventos_positivos.get(fecha, "S/D")
        fila[2].text = str(eventos_positivos_fecha)

        fila[3].text = str(datos_fecha["imputados"])
        fila[4].text = str(datos_fecha["eventos_relevantes"])

        # Centrar todas las columnas
        for columna in (0, 1, 2, 3, 4):
            fila[columna].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    fila_total = tabla.rows[-1].cells
    fila_total[0].text = "TOTAL"
    fila_total[1].text = str(
        sum(
            convertir_a_entero(eventos_maestro.get(dato["fecha"], 0))
            for dato in resumen
        )
    )
    fila_total[2].text = str(
        sum(
            convertir_a_entero(eventos_positivos.get(dato["fecha"], 0))
            for dato in resumen
        )
    )
    fila_total[3].text = str(sum(dato["imputados"] for dato in resumen))
    fila_total[4].text = str(sum(dato["eventos_relevantes"] for dato in resumen))

    for columna in range(5):
        parrafo = fila_total[columna].paragraphs[0]
        parrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in parrafo.runs:
            run.font.bold = True
            run.font.name = "Arial"
            run.font.size = Pt(10)

        celda = fila_total[columna]
        celda._tc.get_or_add_tcPr()
        shade = parse_xml(r'<w:shd {} w:fill="D9EAF7"/>'.format(nsdecls("w")))
        celda._tc.tcPr.append(shade)


def formatear_fecha(fecha_texto):
    """
    Convierte diferentes formatos de fecha y devuelve solo 'dd/mm'.
    Si no se puede parsear, devuelve el texto original.
    """
    if not fecha_texto or fecha_texto == "S/D":
        return "S/D"
    try:
        fecha_limpia = fecha_texto.strip()
        meses_espanol = {
            "enero": 1,
            "ene": 1,
            "febrero": 2,
            "feb": 2,
            "marzo": 3,
            "mar": 3,
            "abril": 4,
            "abr": 4,
            "mayo": 5,
            "may": 5,
            "junio": 6,
            "jun": 6,
            "julio": 7,
            "jul": 7,
            "agosto": 8,
            "ago": 8,
            "septiembre": 9,
            "sep": 9,
            "setiembre": 9,
            "octubre": 10,
            "oct": 10,
            "noviembre": 11,
            "nov": 11,
            "diciembre": 12,
            "dic": 12,
        }

        # 0) Formato ISO aaaa-mm-dd o aaaa/mm/dd (prioridad máxima para no romper 2026-06-01)
        m = re.fullmatch(r"\d{4}[/-]\d{1,2}[/-]\d{1,2}", fecha_limpia)
        if m:
            parte = re.split(r"[/-]", fecha_limpia)
            dia = int(parte[2])
            mes = int(parte[1])
            return f"{dia:02d}/{mes:02d}"

        # 1) Formatos con mes abreviado y guion: "1-ago", "31-jul", "01/ago"
        m = re.search(
            r"(\d{1,2})\s*[-/]\s*([A-Za-zÁÉÍÓÚáéíóúñÑ]+)",
            fecha_limpia,
            re.IGNORECASE,
        )
        if m:
            dia = int(m.group(1))
            mes_texto = m.group(2).lower().replace(".", "")
            mes = meses_espanol.get(mes_texto)
            if mes:
                return f"{dia:02d}/{mes:02d}"

        # 2) Formato con mes en texto: "23 de octubre", "23 octubre 2025", "23 de oct 2025"
        m = re.search(r"(\d{1,2})\s+de\s+([A-záéíóúñ]+)", fecha_limpia, re.IGNORECASE)
        if not m:
            m = re.search(r"(\d{1,2})\s+([A-záéíóúñ]+)", fecha_limpia, re.IGNORECASE)
        if m:
            dia = int(m.group(1))
            mes_texto = m.group(2).lower().replace(".", "")
            mes = meses_espanol.get(mes_texto)
            if mes:
                return f"{dia:02d}/{mes:02d}"

        # 3) Formato numérico dd/mm/yyyy o dd-mm-yyyy
        m = re.fullmatch(r"\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?", fecha_limpia)
        if m:
            parte = re.split(r"[/-]", fecha_limpia)
            dia = int(parte[0])
            mes = int(parte[1])
            return f"{dia:02d}/{mes:02d}"

        # 4) Intentar parseo con datetime para formatos comunes y extraer día/mes
        for fmt in ("%d/%m/%Y", "%d/%m", "%Y-%m-%d", "%m-%d"):
            try:
                fecha_obj = datetime.strptime(fecha_limpia, fmt)
                return fecha_obj.strftime("%d/%m")
            except Exception:
                continue

        # 5) Fecha suelta con dia/mes: "30/07", "30-07", "30/7", "30-7"
        m = re.fullmatch(r"\d{1,2}[/-]\d{1,2}", fecha_limpia)
        if m:
            parte = re.split(r"[/-]", fecha_limpia)
            dia = int(parte[0])
            mes = int(parte[1])
            return f"{dia:02d}/{mes:02d}"

        # Si no se pudo convertir, devolver el texto original
        return fecha_limpia
    except Exception as e:
        print(f"Error al formatear fecha '{fecha_texto}': {e}")
        return fecha_texto


def seleccionar_archivos():
    """Seleccionar archivos PDF usando diálogo de archivos"""
    """AI is creating summary for seleccionar_archivos
    """
    try:
        global rutas_global
        archivos = filedialog.askopenfilenames(
            title="Seleccionar archivos PDF",
            filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")],
        )

        if archivos:
            rutas_global = list(archivos)
            archivos_texto = "Archivos seleccionados:\n" + "\n".join(
                [f.split("/")[-1] for f in archivos]
            )
            ventana_pegado.config(text=archivos_texto)
            print(f"Archivos seleccionados: {archivos}")
        else:
            ventana_pegado.config(text="No se seleccionaron archivos")
    except Exception as e:
        print(f"Error en selección de archivos: {e}")
        traceback.print_exc()
        messagebox.showerror("Error", f"Error al seleccionar archivos: {str(e)}")


def extraer_datos_pdf(ruta):
    """
    Abre un único PDF, extrae su texto y aplica todas las expresiones
    regulares para reconocer fecha, causa, SAE, hora, oficial, etc.

    Se separó en su propia función (antes estaba mezclado dentro del
    bucle de extraer_convertir) para poder reutilizar exactamente la
    misma lógica de lectura desde el nuevo botón "Parte Semanal",
    sin duplicar código.

    Devuelve una tupla (fila, celda_combinada, error):
      - fila: diccionario con las columnas para la fila del Excel
      - celda_combinada: texto "Fecha / Reseña / Resultado" para el Word
      - error: mensaje de error si falló la lectura (cadena vacía si no)
    """
    error = ""
    try:
        documento = PdfReader(ruta)
        texto = ""
        for pagina in documento.pages:
            texto_pagina = pagina.extract_text()
            if texto_pagina:
                texto += texto_pagina + "\n"
    except Exception as e:
        error += f"Error al leer {ruta}: {str(e)}\n"
        texto = ""

    # Extracciones por archivo (misma lógica que antes, aplicada a 'texto' y 'ruta')
    fecha = re.search(
        r"Fecha\s*:\s*("
        r"\d{1,2}\s+de\s+[A-Za-zÁÉÍÓÚáéíóúñÑ]+\s+de(?:l)?\s+\d{4}"
        r"\d{1,2}\s+[A-Za-zÁÉÍÓÚáéíóúñÑ]+\s+de(?:l)?\s+\d{4}"
        r"|\d{1,2}[/-]\d{1,2}[/-]\d{4}"
        r"|\d{4}[/-]\d{1,2}[/-]\d{1,2}"
        r")",
        texto,
        re.IGNORECASE,
    )
    # 1) Hora dentro del bloque de reseña
    hora_resena = re.search(
        r"(breve\s+reseña|reseña)\s*[:\-]?\s*(.*?)\b(?:siendo\s+las|a\s+las)\s*(\d{1,2}:\d{2})",
        texto,
        re.IGNORECASE | re.DOTALL,
    )

    # 2) Hora general
    hora_general = re.search(
        r"(hora|horario)\s*[:\-]?\s*(\d{1,2}:\d{2})", texto, re.IGNORECASE
    )

    # 3) Selección final
    if hora_resena:
        hora_final = hora_resena.group(3)
    elif hora_general:
        hora_final = hora_general.group(2)
    else:
        hora_final = "S/D"

    causa = re.search(
        r"^\s*(?:causa|hecho)\b\s*[\s*:\-–—]?\s*(.+?)\s*$",
        texto,
        re.IGNORECASE | re.MULTILINE,
    )
    jefe = re.search(r"j\s*e\s*f\s*e\s*de\s*servicio:\s*([^\n]+)", texto, re.IGNORECASE)
    oficial = re.search(
        r"(?:Oficial\s*+de\s*+Serv[ií]cio:\s*|Oficial\s*+de\s*+Serv[ií]cio\s*)([^\n]+)",
        texto,
        re.IGNORECASE,
    )
    operador = re.search(
        r"(?:"
        r"Operador\s*de\s*C[aá]mara"
        r"|Operador\s*C[aá]mara"
        r"|Op(?:erador)?\s*C[aá]mara"
        r"|Aux(?:iliar)?\s+Operador\s+de\s+C[aá]mara"
        r"|Aux\s*"
        r")"
        r"\s*:?\s*([^\n]+)",  # ← capturar solo la MISMA línea
        texto,
        re.IGNORECASE,
    )

    sae = re.search(
        r"(?:SAE\s*Nro.\s*|SAE:\s*°\s*|SAE\s*nº\s*|sae\s*|suceso\s*:\s*|suceso\s*|cad\s*:\s*|SAECAD\s*|sae\s*:\s*|sae\s*nº.|sae\s*nº\s*+:|sae\s*nro:\s*|sae\s*+nro.|carta\s*:|carta\s*n\s*:|carta\s*+:|SAE\s*N.\s*ª\s*|SAE\s*nª\s*|SAE\s*N.\s*º\s*|N°\s*|N°\s*:\s*)\s*(\d{8})",
        texto,
        re.IGNORECASE,
    )
    resultado = re.search(r"\bresultado\b\s*[:\-–—]?\s*([^\n]+)", texto, re.IGNORECASE)
    resultado_texto = resultado.group(1).strip() if resultado else "S/D"

    if operador:
        op_texto = operador.group(1).strip()

        # si empieza con "breve", "reseña", "resultado", etc → NO ES OPERADOR
        if re.match(
            r"^(breve|rese[nñ]a|resultado|fecha|hora)\b",
            op_texto,
            re.IGNORECASE,
        ):
            operador_valor = "S/D"
        else:
            operador_valor = op_texto
    else:
        operador_valor = "S/D"

    # Condición para detenidos
    detenido_valor = ""
    contraventor_valor = ""
    resultado_final = resultado_texto
    mapa_numeros = {
        "un": 1,
        "uno": 1,
        "una": 1,
        "dos": 2,
        "tres": 3,
        "cuatro": 4,
        "cinco": 5,
        "seis": 6,
        "siete": 7,
        "ocho": 8,
        "nueve": 9,
        "diez": 10,
    }

    def extraer_numero_resultado(texto):
        t = texto.lower()

        m = re.search(r"\b(\d+)\s*\(", t)
        if m:
            return int(m.group(1))

        m = re.search(r"\b(\d+)\b", t)
        if m:
            return int(m.group(1))

        m = re.search(r"\((\d+)\)", t)
        if m:
            return int(m.group(1))

        for palabra, valor in mapa_numeros.items():
            if re.search(rf"\b{palabra}\b", t):
                return valor

        return ""

    # --- aplicar ---
    detenido_valor = contraventor_valor = ""

    if re.search(r"\bdeten", resultado_texto, re.IGNORECASE):
        detenido_valor = extraer_numero_resultado(resultado_texto)

    if re.search(r"\bcontra", resultado_texto, re.IGNORECASE):
        contraventor_valor = extraer_numero_resultado(resultado_texto)

    resultado_final = "" if detenido_valor or contraventor_valor else resultado_texto

    # Obtener y formatear la fecha
    fecha_texto = fecha.group(1).strip() if fecha else "S/D"
    # Antes: búsqueda rígida de fecha. Ahora se captura el texto después de 'Fecha:' y se parsea.
    fecha_match = re.search(
        r"Fecha\s*:\s*(.+?)(?:\s+Hora\b|\n|$)", texto, re.IGNORECASE
    )
    if fecha_match:
        fecha_texto = fecha_match.group(1).strip()
    else:
        # Fallback: buscar patrones de fecha en cualquier parte del texto
        fecha_busqueda = re.search(
            r"(\d{1,2}\s+de\s+[A-Za-zÁÉÍÓÚáéíóúñÑ]+(?:\s+de(?:l)?\s+\d{2,4})?|\d{1,2}[\/\-]\d{1,2}(?:[\/\-]\d{2,4})?|\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2})",
            texto,
            re.IGNORECASE,
        )
        fecha_texto = fecha_busqueda.group(1).strip() if fecha_busqueda else "S/D"
    fecha_formateada = formatear_fecha(fecha_texto)

    fila = {
        "RUTA": ruta,
        "FECHA": fecha_formateada,
        "TIPIFICACION": "",
        "CAUSA": causa.group(1).strip() if causa else "S/D",
        "SAE": int(sae.group(1).strip()) if sae else "S/D",
        "HORA": hora_final,
        "OFICIAL DE SERVICIO": oficial.group(1).strip() if oficial else "S/D",
        "OPERADOR DE CAMARA": operador_valor,
        "CONTRAVENTOR": contraventor_valor,
        "DETENIDO": detenido_valor,
        "OBSERVACIONES": "",
        "GRUPO QUE TRABAJO ESE DIA": "",
        "JEFE DE SERVICIO": jefe.group(1).strip() if jefe else "S/D",
        "RESULTADO": resultado_final,
    }
    # Construir bloque combinado para Word
    resena_bloque = re.search(
        r"(?:rese[nñ]a|rese[nñ]a)\s*:?\s*(.*?)Resultado\s*:",
        texto,
        re.IGNORECASE | re.DOTALL,
    )
    if resena_bloque:
        resena_limpia = re.sub(r"\s+", " ", resena_bloque.group(1)).strip()
    else:
        resena_limpia = "S/D"

    celda_combinada = (
        f"Fecha: {fecha_formateada}\n"
        f"Reseña: {resena_limpia}\n"
        f"Resultado: {resultado.group(1).strip() if resultado else 'S/D'}"
    )

    return fila, celda_combinada, error


def extraer_convertir():
    """
    Docstring para extraer_convertir

    Extraer datos de archivos PDF y guardarlos en Excel y Word"""
    try:
        if not rutas_global:
            messagebox.showwarning(
                "Advertencia", "Por favor, selecciona archivos PDF primero."
            )
            return

        datos, datos_2 = [], []
        error = ""
        carpeta_salida = (
            os.path.dirname(rutas_global[0]) if rutas_global else os.getcwd()
        )
        archivo_excel = os.path.join(carpeta_salida, "contenido_archivos.xlsx")

        # Número que se le va a poner al próximo PDF como prefijo de su
        # nombre (ej: "3_acta.pdf"). Se sigue incrementando en cada
        # archivo, incluso entre distintas ejecuciones del programa,
        # porque lo calculamos mirando los PDF ya renombrados que hay
        # en la carpeta. Ya no se guarda ninguna columna "ID" en el Excel.
        siguiente_id = obtener_siguiente_id(carpeta_salida)

        # Procesar cada PDF por separado en lugar de concatenar y split
        for ruta in rutas_global:
            id_actual = siguiente_id
            siguiente_id += 1

            # Renombrar el PDF agregando el número al inicio del nombre
            # (ej: "constitucion34.pdf" -> "1~constitucion34.pdf"). El
            # Excel no guarda ese número en ninguna columna, pero el
            # nombre del archivo y el hipervínculo de la columna "RUTA"
            # sí quedan ligados entre sí.
            carpeta_pdf = os.path.dirname(ruta)
            nombre_original = os.path.basename(ruta)
            nuevo_nombre = f"{id_actual}~{nombre_original}"
            nueva_ruta = os.path.join(carpeta_pdf, nuevo_nombre)
            try:
                os.rename(ruta, nueva_ruta)
                ruta = nueva_ruta  # de acá en adelante trabajamos con la ruta nueva
            except Exception as e:
                error += f"No se pudo renombrar {ruta}: {str(e)}\n"

            fila, celda_combinada, err = extraer_datos_pdf(ruta)
            if err:
                error += err
            datos.append(fila)
            datos_2.append(celda_combinada)

        # --- Acumulación en Excel ---
        try:
            df_existente = pd.read_excel(archivo_excel)
            df_nuevo = pd.DataFrame(datos)
            df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
        except FileNotFoundError:
            df_final = pd.DataFrame(datos)

        # Guardar el DataFrame en Excel
        df_final.to_excel(archivo_excel, index=False)

        # Configurar formato de fecha en la columna B (columna 2) del Excel
        try:
            wb = openpyxl.load_workbook(archivo_excel)
            ws = wb.active
            if ws is None:
                raise ValueError("No active worksheet found in workbook")
            # Columnas fijas del Excel: RUTA=A, FECHA=B, TIPIFICACION=C,
            # CAUSA=D, SAE=E, HORA=F, OFICIAL DE SERVICIO=G,
            # OPERADOR DE CAMARA=H, CONTRAVENTOR=I, DETENIDO=J,
            # JEFE DE SERVICIO=M, RESULTADO=N.
            columnas = ["B", "E", "F", "I", "J"]
            columnas_limpiar = ["G", "H", "M"]

            # Palabras a eliminar (sin signos)
            palabras_limpiar = [
                "personal",
                "contratado",
                "pc",
                "auxiliar",
                "pers",
                "contr",
                "aux",
                "cont",
                "oficial",
                "of",
                "operador",
                "oper",
                "lp",
                "primero",
                "mayor",
                "principal",
                "inspector",
                "insp",
                "sucrio",
                "subrio",
                "subcomisario",
            ]

            # Signos a eliminar siempre
            signos_eliminar = r"[.\-:;]"

            # Regex para palabras (tolerante a punto final)
            patrones = [
                re.compile(r"\b" + re.escape(p) + r"\.?\b", flags=re.IGNORECASE)
                for p in palabras_limpiar
            ]

            for col in columnas_limpiar:
                for celda in ws[col]:
                    if celda.row == 1:
                        continue

                    valor = celda.value
                    if not valor:
                        continue

                    texto = str(valor)

                    # 1) eliminar palabras específicas
                    for pat in patrones:
                        texto = pat.sub("", texto)

                    # 2) eliminar signos aislados (., -, :, ;)
                    texto = re.sub(signos_eliminar, " ", texto)

                    # 3) eliminar cualquier número
                    texto = re.sub(r"\d+", " ", texto)

                    # 4) limpiar espacios duplicados
                    texto = re.sub(r"\s+", " ", texto).strip()

                    # 5) guardar
                    celda.value = texto if texto else "S/D"

                for col in columnas:
                    for celda in ws[col]:
                        celda.alignment = Alignment(horizontal="center")

            # Establecer formato de fecha para la columna B
            for row in range(2, ws.max_row + 1):
                celda = ws.cell(row=row, column=2)  # Columna B = FECHA
                if celda.value and celda.value != "S/D":
                    try:
                        # Convertir a objeto fecha de Excel si es posible
                        if isinstance(celda.value, str):
                            fecha_obj = datetime.strptime(celda.value, "%d/%m/%Y")
                            celda.value = fecha_obj
                        celda.number_format = "DD/MM/AAAA"
                    except:
                        pass
            # Agregar hipervínculos en la columna "RUTA"
            col_titulo = 1  # La columna "RUTA" es la primera
            for row in range(2, ws.max_row + 1):
                ruta_pdf = ws.cell(row=row, column=col_titulo).value
                if (
                    ruta_pdf
                    and isinstance(ruta_pdf, str)
                    and ruta_pdf.lower().endswith(".pdf")
                ):
                    ws.cell(row=row, column=col_titulo).hyperlink = Hyperlink(
                        ref=f"A{row}", target=str(ruta_pdf)
                    )
                    ws.cell(row=row, column=col_titulo).font = Font(
                        color="0000FF", underline="single"
                    )

            wb.save(archivo_excel)
        except Exception as e:
            print(f"Error al formatear Excel: {e}")

        messagebox.showinfo("Éxito", f"Datos extraídos y guardados en {archivo_excel}")
        print(f"Datos extraídos y guardados en {archivo_excel}")

        # Limpiar la interfaz después de ejecutar
        ventana_pegado.config(text="Haz clic en 'Seleccionar Archivos' para comenzar")

    except Exception as e:
        print(f"Error en extracción y conversión: {e}")
        traceback.print_exc()
        messagebox.showerror("Error", f"Error durante el procesamiento: {str(e)}")


def generar_parte_semanal():
    """
    Lógica del botón "Parte Semanal":

     1. Pide el Excel "DETENIDOS_OFICIALES_2026" (o el que corresponda),
         permite elegir 1 o 2 hojas (meses) y luego las fechas de la columna "FECHA".
     2. De las hojas y fechas seleccionadas, obtiene el NOMBRE de cada
         archivo de la columna "RUTA" (texto e hipervínculo).
     3. Pide la carpeta donde están los PDF y se queda solo con los PDF
         cuyo nombre coincide
       EXACTAMENTE con alguno de esos nombres ya registrados en el
         Excel (es decir, PDF que ya fueron cargados alguna vez con
       "Ejecutar").
     4. Con esos PDF coincidentes arma un Word nuevo ("Parte_Semanal.docx"),
       igual que el de "Ejecutar" pero sin tocar ningún Excel.
    """
    try:
        messagebox.showinfo(
            "Archivo necesario",
            "A continuación, selecciona el archivo Excel de DETENIDOS OFICIALES.",
        )
        ruta_excel = filedialog.askopenfilename(
            title="Seleccionar el Excel de Detenidos Oficiales",
            filetypes=[("Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
        )
        if not ruta_excel:
            return  # el usuario canceló el diálogo

        try:
            nombres_hojas = seleccionar_hojas_parte_semanal(ruta_excel)
            if not nombres_hojas:
                return

            # Leer registros de 1 o 2 hojas y combinarlos
            registros = []
            for nombre_hoja in nombres_hojas:
                registros.extend(leer_registros_excel(ruta_excel, nombre_hoja))
        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo leer el Excel seleccionado:\n{str(e)}"
            )
            return

        if not registros:
            hojas_texto = ", ".join(nombres_hojas)
            messagebox.showwarning(
                "Advertencia",
                f'Las hojas "{hojas_texto}" no tienen rutas cargadas en la columna "RUTA".',
            )
            return

        fechas_disponibles = sorted({registro["fecha"] for registro in registros})
        hojas_texto = ", ".join(nombres_hojas)
        fechas_elegidas = seleccionar_opciones_checkbutton(
            "Seleccionar fechas",
            f'Selecciona las fechas de las hojas "{hojas_texto}":',
            fechas_disponibles,
            max_selecciones=7,
        )
        if not fechas_elegidas:
            messagebox.showwarning(
                "Advertencia", "Debes seleccionar al menos una fecha."
            )
            return

        fechas_elegidas_ordenadas = fechas_elegidas
        fechas_elegidas = set(fechas_elegidas)
        resumen = resumen_por_fecha(registros, fechas_elegidas_ordenadas)
        nombres_registrados = [
            registro["nombre"]
            for registro in registros
            if registro["fecha"] in fechas_elegidas
        ]
        if not nombres_registrados:
            messagebox.showwarning(
                "Advertencia", "No hay rutas asociadas a las fechas seleccionadas."
            )
            return

        messagebox.showinfo(
            "Carpeta necesaria",
            "A continuación, selecciona la carpeta donde están todos los PDF.",
        )
        carpeta_pdfs = filedialog.askdirectory(
            title="Seleccionar la carpeta con los PDF"
        )

        if not carpeta_pdfs:
            return

        # Nos quedamos solo con los PDF cuyo NOMBRE coincide, letra por
        # letra, con alguno de los nombres ya registrados en el Excel.
        # os.walk() permite encontrar los PDF aunque estén dentro de
        # subcarpetas de la carpeta seleccionada.
        #
        # normalizar_texto() evita que un acento guardado de forma
        # distinta (algo común viniendo de una Mac) haga fallar la
        # comparación aunque los nombres se vean idénticos.
        conjunto_nombres_registrados = {
            normalizar_texto(n).casefold() for n in nombres_registrados
        }

        rutas_por_nombre = {}
        for raiz, _, nombres in os.walk(carpeta_pdfs):
            for nombre in nombres:
                if not nombre.casefold().endswith(".pdf"):
                    continue
                nombre_normalizado = normalizar_texto(nombre).casefold()
                if (
                    nombre_normalizado in conjunto_nombres_registrados
                    and nombre_normalizado not in rutas_por_nombre
                ):
                    rutas_por_nombre[nombre_normalizado] = os.path.join(raiz, nombre)

        # Recorremos los nombres en el mismo orden en que aparecen en el Excel.
        pdfs_coincidentes = []
        nombres_ya_agregados = set()
        for nombre_registrado in nombres_registrados:
            nombre_normalizado = normalizar_texto(nombre_registrado).casefold()
            ruta_pdf = rutas_por_nombre.get(nombre_normalizado)
            if ruta_pdf and nombre_normalizado not in nombres_ya_agregados:
                pdfs_coincidentes.append(ruta_pdf)
                nombres_ya_agregados.add(nombre_normalizado)

        if not pdfs_coincidentes:
            messagebox.showwarning(
                "Advertencia",
                "Ningún PDF de esa carpeta coincide con las rutas "
                "guardadas en el Excel.",
            )
            return

        # Pedir primero un archivo maestro/control diario y, si corresponde,
        # ofrecer cargar un segundo archivo para días del mes siguiente.
        messagebox.showinfo(
            "Archivo necesario",
            "Primero selecciona el archivo maestro o control diario "
            "para rellenar la columna de EVENTOS DEL PERÍODO.",
        )
        rutas_maestro = []
        primer_maestro = filedialog.askopenfilename(
            title="Seleccionar archivo maestro o control diario",
            filetypes=[("Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
        )
        if primer_maestro:
            rutas_maestro.append(primer_maestro)

            respuesta = messagebox.askyesno(
                "Archivo adicional",
                "¿Querés cargar otro archivo del mes siguiente para sumar eventos?",
            )
            if respuesta:
                segundo_maestro = filedialog.askopenfilename(
                    title="Seleccionar archivo adicional del mes siguiente",
                    filetypes=[("Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
                )
                if segundo_maestro:
                    rutas_maestro.append(segundo_maestro)

        eventos_maestro = {}
        eventos_positivos = {}
        if rutas_maestro:
            eventos_maestro = leer_maestro_control_diario(rutas_maestro)
            eventos_positivos = leer_tipificaciones_por_fecha(rutas_maestro)

        datos_2 = []
        error = ""
        for ruta_pdf in pdfs_coincidentes:
            _, celda_combinada, err = extraer_datos_pdf(ruta_pdf)
            if err:
                error += err
            datos_2.append(celda_combinada)

        # El parte semanal siempre arranca un Word nuevo (no se acumula
        # sobre uno anterior, a diferencia de reseña_archivos.docx).
        doc = crear_documento_base()
        completar_tabla_resumen_con_maestro(
            doc, resumen, eventos_maestro, eventos_positivos
        )
        for item in datos_2:
            doc.add_paragraph(item)
            doc.add_paragraph(
                "--------------------------------------------------------------"
            )

        archivo_word = os.path.join(carpeta_pdfs, "Parte_Semanal.docx")
        doc.save(archivo_word)

        mensaje = (
            f"Parte semanal generado con {len(pdfs_coincidentes)} PDF(s) "
            f"coincidentes en:\n{archivo_word}"
        )
        if error:
            mensaje += f"\n\nAlgunos PDF tuvieron errores de lectura:\n{error}"
        messagebox.showinfo("Éxito", mensaje)
        print(mensaje)

    except Exception as e:
        print(f"Error en generar_parte_semanal: {e}")
        traceback.print_exc()
        messagebox.showerror("Error", f"Error al generar el parte semanal: {str(e)}")


# Crear ventana principal
root = tk.Tk()
root.title("Extracción de datos .PDF a: -Parte semanal-Detenidos Oficiales-")
root.config(bg="#822121")
root.geometry("840x400")

frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

ventana_pegado = tk.Label(
    frame,
    text="Haz clic en 'Seleccionar Archivos' para comenzar",
    bg="#1a1a1a",
    fg="#00FF00",
    font=("Helvetica", 12),
    relief="sunken",
    height=6,
)
ventana_pegado.pack(fill=tk.BOTH, expand=True)

# Botones
boton_seleccionar = tk.Button(
    frame,
    text="📁 Seleccionar Archivos",
    width=20,
    height=2,
    command=seleccionar_archivos,
)
boton_seleccionar.config(
    background="#33AAFF", fg="white", font=("Helvetica", 10, "bold")
)
boton_seleccionar.pack(side=tk.TOP, pady=5)

boton_ejecutar = tk.Button(
    frame, text="▶ Ejecutar", width=20, height=2, command=extraer_convertir
)
boton_ejecutar.config(background="#33FF41", fg="white", font=("Helvetica", 10, "bold"))
boton_ejecutar.pack(side=tk.LEFT)

boton_parte_semanal = tk.Button(
    frame,
    text="📄 Parte Semanal",
    width=20,
    height=2,
    command=generar_parte_semanal,
)
boton_parte_semanal.config(
    background="#F2A93B", fg="white", font=("Helvetica", 10, "bold")
)
boton_parte_semanal.pack(side=tk.LEFT)

boton_cerrar = tk.Button(frame, text="❌ Cerrar", width=20, height=2, command=root.quit)
boton_cerrar.config(background="#FF3333", fg="white", font=("Helvetica", 10, "bold"))
boton_cerrar.pack(side=tk.RIGHT)

if __name__ == "__main__":
    root.mainloop()
