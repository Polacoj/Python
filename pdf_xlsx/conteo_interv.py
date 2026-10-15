import json
import os
import sys
from datetime import date, datetime, timedelta

import openpyxl


def _normalizar_texto(valor):
    if valor is None:
        return ""
    return str(valor).strip()


def _es_vacio(valor):
    if valor is None:
        return True
    texto = str(valor).strip()
    if texto == "":
        return True
    if texto.upper() in {"S/D", "SD", "N/A", "NULL"}:
        return True
    return False


def _fecha_excel_a_datetime(valor):
    if valor is None:
        return None

    if isinstance(valor, datetime):
        return valor
    if isinstance(valor, date):
        return datetime.combine(valor, datetime.min.time())
    if isinstance(valor, (int, float)) and not isinstance(valor, bool):
        try:
            return datetime(1899, 12, 30) + timedelta(days=float(valor))
        except Exception:
            return None

    texto = str(valor).strip()
    if not texto:
        return None

    texto = texto.replace("T", " ")
    formatos = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d/%m/%y",
        "%d-%m-%Y",
        "%d-%m-%y",
        "%Y/%m/%d",
    ]
    for formato in formatos:
        try:
            return datetime.strptime(texto, formato)
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(texto)
    except ValueError:
        pass

    return None


def _buscar_columna(ws, palabras_clave):
    for fila in ws.iter_rows(min_row=1, max_row=1, values_only=False):
        for celda in fila:
            valor = celda.value
            if valor is None:
                continue
            texto = str(valor).strip().lower()
            if any(p in texto for p in palabras_clave):
                return celda.column
    return None


def _es_colaboracion_tipificacion(valor):
    if valor is None:
        return False
    texto = str(valor).strip().lower()
    if texto == "":
        return False
    return "colaboracion" in texto or "colaboración" in texto or "colaborador" in texto


def _es_pc_invalida(valor):
    if valor is None:
        return True
    texto = str(valor).strip().lower()
    if texto == "":
        return True
    texto_limpio = (
        texto.replace(".", "")
        .replace(" ", "")
        .replace("_", "")
        .replace("–", "-")
        .replace("—", "-")
    )
    return texto_limpio in {"", "-", "--", "n/a", "s/d", "sd"}


def contar_tipificaciones_por_fecha(ruta_archivo):
    """
    Cuenta la cantidad de tipificaciones por fecha excluyendo:
      - filas con tipificación de colaboración,
      - filas donde la columna PC está vacía o es '-'.

    Regla: cuenta sólo si:
      - hay fecha válida,
      - la celda de TIPIFICACION no está vacía,
      - la tipificación no corresponde a una colaboración,
      - la columna PC tiene un valor distinto de vacío y distinto de '-'.

    Devuelve dos diccionarios:
      - {'DD/MM': cantidad}
      - {'YYYY-MM-DD': cantidad}
    """
    conteo_dd_mm = {}
    conteo_completo = {}

    try:
        wb = openpyxl.load_workbook(ruta_archivo, data_only=True)
        ws = wb.active

        columna_fecha = _buscar_columna(ws, ["fecha"])
        columna_tipificacion = _buscar_columna(
            ws, ["tipificacion", "tipif", "tipificación"]
        )
        columna_pc = _buscar_columna(ws, ["pc", "p.c.", "p c"])

        if columna_fecha is None:
            print(f"No se encontró la columna 'FECHA' en {ruta_archivo}")
            return {}, {}
        if columna_tipificacion is None:
            print(f"No se encontró la columna 'TIPIFICACION' en {ruta_archivo}")
            return {}, {}

        for fila in range(2, ws.max_row + 1):
            fecha_valor = ws.cell(row=fila, column=columna_fecha).value
            fecha_dt = _fecha_excel_a_datetime(fecha_valor)
            if fecha_dt is None:
                continue

            tipificacion = ws.cell(row=fila, column=columna_tipificacion).value
            if _es_vacio(tipificacion):
                continue
            if _es_colaboracion_tipificacion(tipificacion):
                continue

            if columna_pc is not None:
                valor_pc = ws.cell(row=fila, column=columna_pc).value
                if _es_pc_invalida(valor_pc):
                    continue

            fecha_dd_mm = fecha_dt.strftime("%d/%m")
            fecha_iso = fecha_dt.strftime("%Y-%m-%d")

            conteo_dd_mm[fecha_dd_mm] = conteo_dd_mm.get(fecha_dd_mm, 0) + 1
            conteo_completo[fecha_iso] = conteo_completo.get(fecha_iso, 0) + 1

        wb.close()
        return conteo_dd_mm, conteo_completo

    except Exception as exc:
        print(f"Error al leer el archivo {ruta_archivo}: {exc}")
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
    rutas = (
        rutas_archivo if isinstance(rutas_archivo, (list, tuple)) else [rutas_archivo]
    )
    print("=== Conteo de tipificaciones por fecha ===")
    for fecha, cantidad in sorted(conteo_dd_mm.items(), key=lambda x: x[0]):
        print(f"{fecha}: {cantidad} tipificaciones")
    print(f"\nTotal de tipificaciones: {sum(conteo_completo.values())}")
    print(f"Total de días con tipificaciones: {len(conteo_completo)}")
    if len(rutas) > 1:
        print(f"Archivos procesados: {len(rutas)}")


def main(argv=None):
    """CLI del script:
    python conteo_interv.py <ruta_excel> [ruta_excel_2] [--json]
    """
    args = sys.argv[1:] if argv is None else argv
    if not args:
        print("Uso: python conteo_interv.py <ruta_excel> [ruta_excel_2] [--json]")
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
        conteos.append(contar_tipificaciones_por_fecha(ruta_archivo))

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
