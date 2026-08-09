"""
core/imputados_logic.py
=======================
Lógica extraída de productividad_imputados.pyw.
Extrae contraventores/detenidos/integrados y genera 2 archivos Excel.
"""

import sys
import unicodedata
from pathlib import Path
from typing import Callable

import pandas as pd

_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

DATOS_DIR = _ROOT / "DATOS"
DATOS_DIR.mkdir(exist_ok=True)

# Nombres de columnas
CONT_COL = "CONTRAVENTORES"
DET_COL = "DETENIDOS"
TIPIFICACION_COL = "TIPIFICACION"
CIERRE_COL = "TIPO DE CIERRE"
BARRIO_COL = "BARRIO"
ORIGEN_COL = "ORIGEN"
GAP_COL = "GAP"
SAE_COL = "SAE"
ACL_COL = "ACLARACIONES"
OPERADOR_INDEX = 6
GRUPO_COL = "GRUPO"
SISEP_COL = "SISEP/ANILLO"


def remove_accents(s: str) -> str:
    return "".join(
        ch for ch in unicodedata.normalize("NFKD", str(s)) if not unicodedata.combining(ch)
    )


def operador_df(df: pd.DataFrame) -> pd.DataFrame:
    """Extrae eventos con contraventores, detenidos e integrados por operador."""
    filas_contraventor, filas_detenido, filas_integrados = [], [], []

    for _, fila in df.iterrows():
        operador_val = fila.iloc[OPERADOR_INDEX] if len(fila) > OPERADOR_INDEX else None

        if (
            fila.get(CONT_COL, 0) >= 1
            and fila.get(CIERRE_COL, "") == "FINALIZA CON IMPUTADO/S"
        ):
            filas_contraventor.append(
                {
                    "OPERADOR": operador_val,
                    "TIPO DE EVENTO": "CONTRAVENCION",
                    "BARRIO": fila.get(BARRIO_COL),
                    "ORIGEN": fila.get(ORIGEN_COL),
                    "GAP": fila.get(GAP_COL),
                    "SAE": fila.get(SAE_COL),
                }
            )

        if (
            fila.get(DET_COL, 0) >= 1
            and fila.get(CIERRE_COL, "") == "FINALIZA CON IMPUTADO/S"
        ):
            tipo = (
                "ROBO/HURTO"
                if fila.get(TIPIFICACION_COL, "").strip().upper() == "ROBO/HURTO"
                else "DELITO"
            )
            filas_detenido.append(
                {
                    "OPERADOR": operador_val,
                    "TIPO DE EVENTO": tipo,
                    "BARRIO": fila.get(BARRIO_COL),
                    "ORIGEN": fila.get(ORIGEN_COL),
                    "GAP": fila.get(GAP_COL),
                    "SAE": fila.get(SAE_COL),
                }
            )

        tip_val = remove_accents(str(fila.get(ACL_COL, ""))).strip().lower()
        if "integ" in tip_val or "dest" in tip_val:
            filas_integrados.append(
                {
                    "OPERADOR": operador_val,
                    "TIPO DE EVENTO": "INTERVENCION DESTACADA",
                    "BARRIO": fila.get(BARRIO_COL),
                    "ORIGEN": fila.get(ORIGEN_COL),
                    "GAP": fila.get(GAP_COL),
                    "SAE": fila.get(SAE_COL),
                }
            )

    return pd.concat(
        [pd.DataFrame(filas_contraventor), pd.DataFrame(filas_detenido), pd.DataFrame(filas_integrados)],
        ignore_index=True,
    )


def sisep_df(df: pd.DataFrame) -> pd.DataFrame:
    """Extrae eventos SISEP con contraventores, detenidos e integrados."""
    filas_c, filas_d, filas_i = [], [], []

    for _, fila in df.iterrows():
        es_sisep = fila.get(SISEP_COL, "") in ["SISEP", "SISEP "]
        if not es_sisep:
            continue

        grupo = fila.get(GRUPO_COL, "")

        if fila.get(CONT_COL, 0) >= 1 and fila.get(CIERRE_COL, "") == "FINALIZA CON IMPUTADO/S":
            filas_c.append(
                {"GRUPO": grupo, "TIPO DE EVENTO": "CONTRAVENCION",
                 "BARRIO": fila.get(BARRIO_COL), "ORIGEN": fila.get(ORIGEN_COL),
                 "GAP": fila.get(GAP_COL), "SAE": fila.get(SAE_COL)}
            )

        if fila.get(DET_COL, 0) >= 1 and fila.get(CIERRE_COL, "") == "FINALIZA CON IMPUTADO/S":
            tipo = (
                "ROBO/HURTO"
                if fila.get(TIPIFICACION_COL, "").strip().upper() == "ROBO/HURTO"
                else "DELITO"
            )
            filas_d.append(
                {"GRUPO": grupo, "TIPO DE EVENTO": tipo,
                 "BARRIO": fila.get(BARRIO_COL), "ORIGEN": fila.get(ORIGEN_COL),
                 "GAP": fila.get(GAP_COL), "SAE": fila.get(SAE_COL)}
            )

        tip_val = remove_accents(str(fila.get(ACL_COL, ""))).strip().lower()
        if "integ" in tip_val or "dest" in tip_val:
            filas_i.append(
                {"GRUPO": grupo, "TIPO DE EVENTO": "INTERVENCION DESTACADA",
                 "BARRIO": fila.get(BARRIO_COL), "ORIGEN": fila.get(ORIGEN_COL),
                 "GAP": fila.get(GAP_COL), "SAE": fila.get(SAE_COL)}
            )

    return pd.concat(
        [pd.DataFrame(filas_c), pd.DataFrame(filas_d), pd.DataFrame(filas_i)],
        ignore_index=True,
    )


def process_file(
    ruta_archivo: str,
    log_fn: Callable[[str], None],
) -> tuple[bool, str]:
    """Procesa el archivo y guarda los 2 resultados en DATOS/."""
    try:
        log_fn(f"📂 Cargando: {Path(ruta_archivo).name}")
        df = pd.read_excel(ruta_archivo, engine="openpyxl")

        if BARRIO_COL in df.columns:
            df[BARRIO_COL] = df[BARRIO_COL].str.lower()

        log_fn("→ Procesando eventos por operador...")
        resultado = operador_df(df)

        log_fn("→ Procesando eventos SISEP...")
        resultado_sisep = sisep_df(df)

        salida_operador = DATOS_DIR / "productividad_imputados.xlsx"
        salida_sisep = DATOS_DIR / "productividad_imputados_sisep.xlsx"

        resultado.to_excel(salida_operador, index=False, engine="openpyxl")
        resultado_sisep.to_excel(salida_sisep, index=False, engine="openpyxl")

        log_fn(f"✅ productividad_imputados.xlsx → {len(resultado)} registros")
        log_fn(f"✅ productividad_imputados_sisep.xlsx → {len(resultado_sisep)} registros")

        msg = (
            f"✅ Proceso completado\n\n"
            f"  • Total operador: {len(resultado)} eventos\n"
            f"  • Total SISEP: {len(resultado_sisep)} eventos\n\n"
            f"Archivos en: {DATOS_DIR}"
        )
        return True, msg

    except Exception as e:
        import traceback
        return False, f"Error: {e}\n\n{traceback.format_exc()}"
