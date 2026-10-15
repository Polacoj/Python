import json
import os
import sys
from datetime import datetime

import openpyxl


def contar_eventos_por_fecha(ruta_archivo):
    """
    Lee el archivo Excel y cuenta la cantidad de eventos por fecha.

    Args:
        ruta_archivo (str): Ruta al archivo Excel

    Returns:
        dict: Diccionario con formato {"DD/MM": cantidad_eventos}
        dict: Diccionario con formato {"YYYY-MM-DD": cantidad_eventos} (formato completo)
    """
    eventos_por_fecha = {}
    eventos_por_fecha_completa = {}

    try:
        # Abrir el workbook
        wb = openpyxl.load_workbook(ruta_archivo, data_only=True)
        ws = wb.active  # Primera hoja (Hoja1)

        # Encontrar la columna de fecha (columna A)
        columna_fecha = None
        for celda in ws[1]:
            if celda.value and "FECHA" in str(celda.value).strip().upper():
                columna_fecha = celda.column
                break

        if columna_fecha is None:
            print("No se encontró la columna 'FECHA'")
            return {}, {}

        # Leer datos desde la fila 2 hasta el final
        for fila in range(2, ws.max_row + 1):
            celda_fecha = ws.cell(row=fila, column=columna_fecha)

            if not celda_fecha.value:
                continue

            fecha = celda_fecha.value

            # Manejar diferentes tipos de fecha
            if isinstance(fecha, datetime):
                fecha_str = fecha.strftime("%d/%m")
                fecha_anual = fecha.strftime("%d/%m/%Y")
                fecha_completa = fecha.strftime("%Y-%m-%d")
            elif isinstance(fecha, (int, float)):
                # Número serial de Excel
                try:
                    fecha_dt = datetime(1899, 12, 30) + __import__(
                        "datetime"
                    ).timedelta(days=fecha)
                    fecha_str = fecha_dt.strftime("%d/%m")
                    fecha_anual = fecha_dt.strftime("%d/%m/%Y")
                    fecha_completa = fecha_dt.strftime("%Y-%m-%d")
                except:
                    continue
            else:
                # Si es string, intentar parsear
                try:
                    # Intentar diferentes formatos
                    for formato in [
                        "%Y-%m-%d %H:%M:%S",
                        "%Y-%m-%d",
                        "%d/%m/%Y",
                        "%d-%m-%Y",
                    ]:
                        try:
                            fecha_dt = datetime.strptime(str(fecha).strip(), formato)
                            fecha_str = fecha_dt.strftime("%d/%m")
                            fecha_anual = fecha_dt.strftime("%d/%m/%Y")
                            fecha_completa = fecha_dt.strftime("%Y-%m-%d")
                            break
                        except:
                            continue
                    else:
                        continue
                except:
                    continue

            # Acumular contadores
            eventos_por_fecha[fecha_str] = eventos_por_fecha.get(fecha_str, 0) + 1
            eventos_por_fecha_completa[fecha_completa] = (
                eventos_por_fecha_completa.get(fecha_completa, 0) + 1
            )

        wb.close()
        return eventos_por_fecha, eventos_por_fecha_completa

    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return {}, {}


# Función alternativa usando pandas (más rápido para archivos grandes)
def contar_eventos_con_pandas(ruta_archivo):
    """
    Versión usando pandas para mayor velocidad.

    Args:
        ruta_archivo (str): Ruta al archivo Excel

    Returns:
        dict: Diccionario con formato {"DD/MM": cantidad_eventos}
    """
    try:
        import pandas as pd

        # Leer solo la columna A (fechas)
        df = pd.read_excel(ruta_archivo, usecols="A", header=0)

        # Renombrar columna
        df.columns = ["FECHA"]

        # Convertir a datetime
        df["FECHA"] = pd.to_datetime(df["FECHA"], errors="coerce")

        # Eliminar filas con fechas nulas
        df = df.dropna(subset=["FECHA"])

        # Crear columna con formato DD/MM
        df["FECHA_FORMATO"] = df["FECHA"].dt.strftime("%d/%m")

        # Contar eventos por fecha
        conteo = df["FECHA_FORMATO"].value_counts().to_dict()

        # También devolver con fecha completa
        df["FECHA_COMPLETA"] = df["FECHA"].dt.strftime("%Y-%m-%d")
        conteo_completo = df["FECHA_COMPLETA"].value_counts().to_dict()

        return conteo, conteo_completo

    except ImportError:
        print("Pandas no está instalado. Instálalo con: pip install pandas openpyxl")
        return {}, {}


def sumar_conteos(conteos):
    """Suma varios conteos por fecha para devolver un único diccionario."""
    total_dd_mm = {}
    total_completo = {}

    for conteo_dd_mm, conteo_completo in conteos:
        for fecha, cantidad in conteo_dd_mm.items():
            total_dd_mm[fecha] = total_dd_mm.get(fecha, 0) + cantidad
        for fecha, cantidad in conteo_completo.items():
            total_completo[fecha] = total_completo.get(fecha, 0) + cantidad

    return total_dd_mm, total_completo


def _imprimir_resultados(rutas_archivo, conteo_dd_mm, conteo_completo):
    """Muestra por consola el conteo en formato legible."""
    rutas = (
        rutas_archivo if isinstance(rutas_archivo, (list, tuple)) else [rutas_archivo]
    )
    print("=== Conteo por fecha (DD/MM) ===")
    for fecha, cantidad in sorted(conteo_dd_mm.items(), key=lambda x: x[0]):
        print(f"{fecha}: {cantidad} eventos")
    print(f"\nTotal de eventos: {sum(conteo_completo.values())}")
    print(f"Total de días con eventos: {len(conteo_completo)}")
    if len(rutas) > 1:
        print(f"Archivos procesados: {len(rutas)}")


def main(argv=None):
    """CLI del script: python conteo_fechas.py ruta_excel [ruta_excel2] [--json]."""
    args = sys.argv[1:] if argv is None else argv
    if not args:
        print("Uso: python conteo_fechas.py <ruta_excel> [ruta_excel_2] [--json]")
        return 1

    mostrar_json = "--json" in args or "-j" in args
    rutas_archivo = [arg for arg in args if arg not in {"--json", "-j"}]
    if not rutas_archivo:
        print("Debe indicar al menos una ruta de Excel.")
        return 1
    if len(rutas_archivo) > 2:
        print("Este script acepta como máximo dos archivos Excel.")
        return 1

    if len(rutas_archivo) == 2:
        print(
            "Se procesarán 2 archivos y se sumará el conteo por fecha.",
            file=sys.stderr,
        )

    conteos = []
    for ruta_archivo in rutas_archivo:
        if not os.path.exists(ruta_archivo):
            print(f"No existe el archivo: {ruta_archivo}")
            return 1
        conteos.append(contar_eventos_por_fecha(ruta_archivo))

    conteo_dd_mm, conteo_completo = sumar_conteos(conteos)
    if mostrar_json:
        print(
            json.dumps(
                {
                    "DD/MM": conteo_dd_mm,
                    "YYYY-MM-DD": conteo_completo,
                },
                ensure_ascii=False,
            )
        )
        return 0

    _imprimir_resultados(rutas_archivo, conteo_dd_mm, conteo_completo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
