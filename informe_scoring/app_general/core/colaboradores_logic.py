"""
core/colaboradores_logic.py
============================
Lógica extraída de cruzar_colaboradores.py.
Cruza 2 archivos Excel por SAE e inserta COLABORADOR 1-5 entre columnas 7 y 8.
Usa threading estándar en lugar de QThread.
"""

import threading
from pathlib import Path
from typing import Callable, Optional

import pandas as pd


COL_SAE_A1 = "SAE"
COL_SAE_A2 = "SAE"
COL_COLS = [
    "COLABORADORES 1",
    "COLABORADORES 2",
    "COLABORADORES 3",
    "COLABORADORES 4",
    "COLABORADORES 5",
]
NUEVAS_COLS = [
    "COLABORADOR 1",
    "COLABORADOR 2",
    "COLABORADOR 3",
    "COLABORADOR 4",
    "COLABORADOR 5",
]


def _normalizar_sae(serie: pd.Series) -> pd.Series:
    def _limpiar(v):
        if pd.isna(v):
            return v
        v = str(v).strip()
        try:
            return str(int(float(v)))
        except ValueError:
            return v
    return serie.map(_limpiar)


def get_sheet_names(ruta: str) -> list[str]:
    """Devuelve lista de nombres de hojas del archivo Excel."""
    return pd.ExcelFile(ruta, engine="openpyxl").sheet_names


def procesar_cruce(
    ruta1: str,
    ruta2: str,
    ruta_salida: str,
    hoja_archivo2: str,
    log_fn: Callable[[str], None],
    on_progress: Callable[[int, str], None],
    on_done: Callable[[dict], None],
    on_error: Callable[[str], None],
) -> threading.Thread:
    """
    Lanza el procesamiento en un hilo de background.
    Devuelve el hilo para que la vista pueda monitorearlo si lo desea.
    """

    def _run():
        try:
            on_progress(10, "Leyendo Archivo 1...")
            df1 = pd.read_excel(
                ruta1, header=0,
                converters={COL_SAE_A1: lambda v: str(v).strip() if not pd.isna(v) else v},
            )
            df1.columns = [str(c).strip() for c in df1.columns]

            on_progress(25, f"Leyendo Archivo 2 (hoja: {hoja_archivo2})...")
            df2 = pd.read_excel(
                ruta2, sheet_name=hoja_archivo2, header=0,
                converters={COL_SAE_A2: lambda v: str(v).strip() if not pd.isna(v) else v},
            )
            df2.columns = [str(c).strip() for c in df2.columns]

            on_progress(35, "Validando columnas...")
            for col in [COL_SAE_A2] + COL_COLS:
                if col not in df2.columns:
                    raise KeyError(
                        f"Columna '{col}' no encontrada en Archivo 2.\n"
                        f"Disponibles: {', '.join(str(c) for c in df2.columns)}"
                    )
            if COL_SAE_A1 not in df1.columns:
                raise KeyError(
                    f"Columna 'SAE' no encontrada en Archivo 1.\n"
                    f"Disponibles: {', '.join(str(c) for c in df1.columns)}"
                )

            on_progress(50, "Construyendo tabla de cruce...")
            df1[COL_SAE_A1] = _normalizar_sae(df1[COL_SAE_A1])
            df2[COL_SAE_A2] = _normalizar_sae(df2[COL_SAE_A2])

            lookup = (
                df2[[COL_SAE_A2] + COL_COLS]
                .drop_duplicates(subset=COL_SAE_A2)
                .set_index(COL_SAE_A2)
            )

            on_progress(65, "Mapeando colaboradores...")
            nuevas = {
                nuevo: df1[COL_SAE_A1].map(lookup[orig])
                for nuevo, orig in zip(NUEVAS_COLS, COL_COLS)
            }

            on_progress(78, "Insertando columnas en posición 7-8...")
            izq = df1.iloc[:, :7]
            der = df1.iloc[:, 7:]
            nuevas_df = pd.DataFrame(nuevas, index=df1.index)
            df1 = pd.concat([izq, nuevas_df, der], axis=1)

            on_progress(90, "Guardando archivo...")
            df1.to_excel(ruta_salida, index=False)

            total = int(len(df1))
            encontrados = int(sum(df1[c].notna().sum() for c in NUEVAS_COLS))

            on_progress(100, "¡Proceso completado!")
            on_done(
                {
                    "total": total,
                    "encontrados": encontrados,
                    "no_encontrados": total - encontrados,
                    "salida": ruta_salida,
                }
            )
        except Exception as e:
            on_error(str(e))

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    return t
