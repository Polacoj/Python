"""
core/diccionario_logic.py
==========================
Lógica extraída de diccionario_CIVILES.pyw.
Reconcilia nombres con Diccionario Maestro y genera archivos _PROCESADO / _REVERTIDO.
"""

import shutil
import sys
from pathlib import Path
from typing import Callable

import pandas as pd

_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# Columnas esperadas
COL_ID = "LP/DNI"
COL_NOMBRE = "APELLIDO Y NOMBRE"
COLS_FISCALIZACION = ["OPERADOR"]
COLS_CONTROL = [
    "OPERADOR",
    "COLABORADORES 1",
    "COLABORADORES 2",
    "COLABORADORES 3",
    "COLABORADORES 4",
    "COLABORADORES 5",
]


# ──────────────────────────────────────────────────────────────────
#  Utilidades
# ──────────────────────────────────────────────────────────────────

def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(col).strip().upper() for col in df.columns]
    return df


def normalizar_nombre(valor) -> str:
    if pd.isna(valor) or str(valor).strip() == "":
        return ""
    return " ".join(str(valor).upper().split())


def construir_mapa_nombres(df_dict: pd.DataFrame) -> dict[str, str]:
    mapa: dict[str, str] = {}
    for _, fila in df_dict.iterrows():
        nombre_raw = fila[COL_NOMBRE]
        id_raw = fila[COL_ID]
        if pd.isna(nombre_raw) or str(nombre_raw).strip() == "":
            continue
        nombre_norm = normalizar_nombre(nombre_raw)
        id_str = "" if pd.isna(id_raw) else str(id_raw).strip()
        mapa[nombre_norm] = id_str
    return mapa


def leer_excel(ruta: Path) -> dict[str, pd.DataFrame]:
    return pd.read_excel(ruta, sheet_name=None, dtype=str)


def get_sheet_names(ruta: str) -> list[str]:
    return pd.ExcelFile(ruta, engine="openpyxl").sheet_names


def guardar_diccionario_con_bak(df_actualizado: pd.DataFrame, ruta_original: Path) -> None:
    from openpyxl import load_workbook

    ruta_bak = ruta_original.parent / "ANTIGUO_DICCIONARIO.xlsx"
    shutil.copy2(ruta_original, ruta_bak)

    wb = load_workbook(ruta_original)
    nombre_sheet1 = next(
        (s for s in wb.sheetnames if s.strip().upper() == "SHEET1"), None
    )
    if nombre_sheet1 is None:
        ws = wb.create_sheet("Sheet1")
    else:
        ws = wb[nombre_sheet1]
        ws.delete_rows(1, ws.max_row)

    for col_idx, encabezado in enumerate(df_actualizado.columns, start=1):
        ws.cell(row=1, column=col_idx, value=encabezado)

    for fila_idx, fila in enumerate(df_actualizado.itertuples(index=False), start=2):
        for col_idx, valor in enumerate(fila, start=1):
            ws.cell(row=fila_idx, column=col_idx, value="" if pd.isna(valor) else valor)

    wb.save(ruta_original)


# ──────────────────────────────────────────────────────────────────
#  Carga con selección de hoja
# ──────────────────────────────────────────────────────────────────

def cargar_con_hoja(ruta: Path, hoja: str) -> pd.DataFrame:
    """Carga un archivo Excel, seleccionando la hoja indicada."""
    hojas = leer_excel(ruta)
    return normalizar_columnas(hojas[hoja])


# ──────────────────────────────────────────────────────────────────
#  Reconciliación
# ──────────────────────────────────────────────────────────────────

def reconciliar_trabajo_diario(
    df_trabajo: pd.DataFrame,
    df_dict: pd.DataFrame,
    ruta_trabajo: Path,
    ruta_dict: Path,
    log_fn: Callable[[str], None],
) -> tuple[pd.DataFrame | None, pd.DataFrame, bool]:
    """
    Reconcilia Fiscalización Diaria/Mensual con el diccionario.
    Retorna (df_modificado, df_dict_vigente, exito_100pct).
    """
    log_fn("Iniciando reconciliación de Fiscalización Diaria/Mensual...")

    if COL_ID not in df_dict.columns or COL_NOMBRE not in df_dict.columns:
        raise RuntimeError(
            f"El Diccionario debe tener columnas '{COL_ID}' y '{COL_NOMBRE}'."
        )

    mapa = construir_mapa_nombres(df_dict)
    reemplazados = no_encontrados = vacias = 0
    nombres_nuevos: dict[str, list[int]] = {}
    resultados: list[tuple[int, str, str | None]] = []

    if "OPERADOR" not in df_trabajo.columns:
        raise RuntimeError("Fiscalización no contiene columna 'OPERADOR'.")

    df_mod = df_trabajo.copy()
    for idx, valor in df_mod["OPERADOR"].items():
        idx = int(idx)
        nombre = normalizar_nombre(valor)
        if nombre == "":
            vacias += 1
            resultados.append((idx, str(valor), "VACIO"))
        elif nombre in mapa:
            reemplazados += 1
            resultados.append((idx, str(valor), mapa[nombre]))
        else:
            no_encontrados += 1
            resultados.append((idx, str(valor), None))
            nombres_nuevos.setdefault(nombre, []).append(idx + 1)

    total = reemplazados + no_encontrados
    pct = 100.0 if total == 0 else (reemplazados / total) * 100
    log_fn(f"Fiscalización: {total} celdas, {reemplazados} coincidencias, {pct:.1f}%")

    if pct < 100.0:
        log_fn("⚠ Coincidencia incompleta — actualizando diccionario...")
        nuevas = []
        for nombre, filas in nombres_nuevos.items():
            fila = {col: "" for col in df_dict.columns}
            fila[COL_NOMBRE] = nombre
            nuevas.append(fila)
            log_fn(f"  Nombre nuevo: '{nombre}' en filas {filas}")
        df_dict_act = pd.concat([df_dict, pd.DataFrame(nuevas)], ignore_index=True)
        guardar_diccionario_con_bak(df_dict_act, ruta_dict)
        log_fn(f"  ✔ Diccionario actualizado: {ruta_dict.name}")
        raise RuntimeError(
            f"Coincidencia incompleta ({pct:.1f}%). "
            f"Diccionario actualizado con nombres faltantes. "
            f"Completá la columna LP/DNI y volvé a correr."
        )

    for idx, _, id_val in resultados:
        if id_val and id_val != "VACIO":
            df_mod.at[idx, "OPERADOR"] = id_val

    salida = ruta_trabajo.parent / (ruta_trabajo.stem + "_PROCESADO" + ruta_trabajo.suffix)
    df_mod.to_excel(salida, index=False)
    log_fn(f"✔ Guardado: {salida.name}")
    return df_mod, df_dict, True


def reconciliar_control_diario(
    df_control: pd.DataFrame,
    df_dict: pd.DataFrame,
    ruta_control: Path,
    ruta_dict: Path,
    log_fn: Callable[[str], None],
) -> tuple[pd.DataFrame | None, pd.DataFrame, bool]:
    """
    Reconcilia Control Diario Mes con el diccionario.
    """
    log_fn("Iniciando reconciliación de Control Diario Mes...")
    mapa = construir_mapa_nombres(df_dict)
    reemplazados = no_encontrados = vacias = 0
    nombres_nuevos: dict[str, list[str]] = {}
    resultados: dict[str, list[tuple[int, str, str | None]]] = {col: [] for col in COLS_CONTROL}

    df_mod = df_control.copy()
    for col in COLS_CONTROL:
        if col not in df_mod.columns:
            raise RuntimeError(f"Control Diario no tiene columna '{col}'.")
        for idx, valor in df_mod[col].items():
            nombre = normalizar_nombre(valor)
            if nombre == "":
                vacias += 1
                resultados[col].append((idx, str(valor), "VACIO"))
            elif nombre in mapa:
                reemplazados += 1
                resultados[col].append((idx, str(valor), mapa[nombre]))
            else:
                no_encontrados += 1
                resultados[col].append((idx, str(valor), None))
                nombres_nuevos.setdefault(nombre, []).append(f"{col}:fila {idx + 1}")

    total = reemplazados + no_encontrados
    pct = 100.0 if total == 0 else (reemplazados / total) * 100
    log_fn(f"Control Diario: {total} celdas, {reemplazados} coincidencias, {pct:.1f}%")

    if pct < 100.0:
        log_fn("⚠ Coincidencia incompleta — actualizando diccionario...")
        nuevas = []
        for nombre, ubicaciones in nombres_nuevos.items():
            fila = {col: "" for col in df_dict.columns}
            fila[COL_NOMBRE] = nombre
            nuevas.append(fila)
            log_fn(f"  Nombre nuevo: '{nombre}' en {ubicaciones}")
        df_dict_act = pd.concat([df_dict, pd.DataFrame(nuevas)], ignore_index=True)
        guardar_diccionario_con_bak(df_dict_act, ruta_dict)
        log_fn(f"  ✔ Diccionario actualizado: {ruta_dict.name}")
        raise RuntimeError(
            f"Coincidencia incompleta ({pct:.1f}%). "
            f"Diccionario actualizado con nombres faltantes. "
            f"Completá LP/DNI y volvé a correr."
        )

    for col, lista in resultados.items():
        for idx, _, id_val in lista:
            if id_val and id_val != "VACIO":
                df_mod.at[idx, col] = id_val

    salida = ruta_control.parent / (ruta_control.stem + "_PROCESADO" + ruta_control.suffix)
    df_mod.to_excel(salida, index=False)
    log_fn(f"✔ Guardado: {salida.name}")
    return df_mod, df_dict, True


def revertir_ids_a_nombres(
    ruta_dict: Path,
    ruta_trabajo_procesado: Path | None,
    ruta_control_procesado: Path | None,
    log_fn: Callable[[str], None],
) -> None:
    """Proceso inverso: IDs → Nombres usando la hoja VALIDACION."""
    log_fn("\n" + "═" * 50)
    log_fn("  PROCESO INVERSO: IDs → NOMBRES (hoja VALIDACION)")
    log_fn("═" * 50)

    todas = leer_excel(ruta_dict)
    hoja_val = next(
        (n for n in todas if n.strip().upper() == "VALIDACION"), None
    )
    if hoja_val is None:
        raise RuntimeError(
            f"No se encontró la hoja 'VALIDACION'.\nHojas disponibles: {list(todas.keys())}"
        )

    df_val = normalizar_columnas(todas[hoja_val])
    for col in [COL_ID, COL_NOMBRE]:
        if col not in df_val.columns:
            raise RuntimeError(f"Hoja VALIDACION no tiene columna '{col}'.")

    mapa_inv: dict[str, str] = {}
    for _, fila in df_val.iterrows():
        id_raw = fila[COL_ID]
        if pd.isna(id_raw) or str(id_raw).strip() == "":
            continue
        mapa_inv[str(id_raw).strip()] = str(fila[COL_NOMBRE]).strip()

    log_fn(f"  Mapa inverso: {len(mapa_inv)} entradas")

    def _revertir(ruta: Path, columnas: list[str], etiqueta: str):
        log_fn(f"\nProcesando {etiqueta}: {ruta.name}")
        hojas = leer_excel(ruta)
        df = normalizar_columnas(hojas[next(iter(hojas))])
        reemplazados = sin_match = vacias = 0

        for col in columnas:
            if col not in df.columns:
                log_fn(f"  ⚠ Columna '{col}' no encontrada, se omite.")
                continue
            for idx, valor in df[col].items():
                v = str(valor).strip()
                if pd.isna(valor) or v == "" or v.lower() == "nan":
                    vacias += 1
                    continue
                if v in mapa_inv:
                    df.at[idx, col] = mapa_inv[v]
                    reemplazados += 1
                else:
                    sin_match += 1

        log_fn(f"  ✔ Reemplazados: {reemplazados}  ○ Vacíos: {vacias}  ⚠ Sin match: {sin_match}")
        salida = ruta.parent / (ruta.stem.replace("_PROCESADO", "") + "_REVERTIDO" + ruta.suffix)
        df.to_excel(salida, index=False)
        log_fn(f"  ✔ Guardado: {salida.name}")

    if ruta_trabajo_procesado:
        _revertir(ruta_trabajo_procesado, ["OPERADOR"], "Fiscalización")
    if ruta_control_procesado:
        _revertir(ruta_control_procesado, COLS_CONTROL, "Control Diario")

    log_fn("\n" + "═" * 50)
    log_fn("  ✔ PROCESO INVERSO COMPLETADO")
    log_fn("═" * 50)
