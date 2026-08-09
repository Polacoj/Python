"""
core/productividad_logic.py
===========================
Lógica extraída de productividad_general.pyw.
Procesa archivo CMU Excel → eventos_unificados.xlsx + narración.
"""

import sys
import time
from pathlib import Path
from typing import Callable, Optional
import pandas as pd

# Asegurar que el directorio raíz (informe_scoring/) está en el path
_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from complementos.contraventores_detenidos import ContraventoresProcessor
from complementos.integrados import IntegradosProcessor
from complementos.colaboradores import ColaboradoresProcessor
from complementos.narracion import NarracionProcessor

DATOS_DIR = _ROOT / "DATOS"
DATOS_DIR.mkdir(exist_ok=True)


def norm(s):
    import unicodedata
    return (
        ""
        if pd.isna(s)
        else "".join(
            c
            for c in unicodedata.normalize("NFKD", str(s).strip().lower())
            if not unicodedata.combining(c)
        )
    )


def procesar_excel(
    ruta_archivo: str,
    log_fn: Callable[[str], None],
) -> tuple[bool, str, Optional[str]]:
    """
    Procesa el archivo CMU Excel y genera eventos_unificados.xlsx.

    Returns:
        (ok, mensaje, ruta_unificado)
    """
    log_fn("\n═══════════════════════════════════════════════════════════════")
    log_fn("🚀 INICIANDO PROCESO PRINCIPAL")
    log_fn("═══════════════════════════════════════════════════════════════")
    log_fn(f"📂 Archivo: {Path(ruta_archivo).name}")
    log_fn(f"📁 Carpeta: {Path(ruta_archivo).parent}")
    time.sleep(0.5)

    try:
        log_fn("\n─────────────────────────────────────────────────────────────")
        log_fn("📊 PASO 1: CARGANDO Y PREPARANDO DATOS")
        log_fn("─────────────────────────────────────────────────────────────")

        df = pd.read_excel(ruta_archivo, engine="openpyxl")
        log_fn("✓ Archivo cargado exitosamente")
        log_fn(f"  Dimensiones: {df.shape[0]} filas × {df.shape[1]} columnas")

        # Truncar filas vacías al final
        df_temp = df.replace(r"^\s*$", pd.NA, regex=True)
        empty_rows = df_temp.isna().all(axis=1)
        if empty_rows.any():
            pos = df_temp.index.get_loc(empty_rows.idxmax())
            df = df.iloc[:pos].reset_index(drop=True)
            log_fn(f"✓ Filas truncadas: {pos} filas procesadas")

        # Limpiar GAP y SAE
        for col in (13, 14):
            if col < len(df.columns):
                col_name = df.columns[col]
                df[col_name] = (
                    df.iloc[:, col]
                    .fillna("")
                    .astype(str)
                    .str.split("/", n=1)
                    .str[0]
                    .str.strip()
                )
                df[col_name] = pd.to_numeric(df[col_name], errors="coerce")
        log_fn("✓ Columnas GAP y SAE limpias")

        # Extraer columnas
        log_fn("\n─────────────────────────────────────────────────────────────")
        log_fn("📊 PASO 2: EXTRACCIÓN DE COLUMNAS")
        log_fn("─────────────────────────────────────────────────────────────")

        columnas_a_extraer = [1, 2, 7, 16, "", "", 20, 32, 13, 14]
        columnas_seleccionadas = []
        nombres_columnas = []

        for valor in columnas_a_extraer:
            if isinstance(valor, int):
                pos = valor - 1
                if pos < 0 or pos >= len(df.columns):
                    return (
                        False,
                        f"El archivo no tiene suficientes columnas (se esperaban al menos {pos + 1}).",
                        None,
                    )
                columnas_seleccionadas.append(df.iloc[:, pos].copy())
                nombres_columnas.append(df.columns[pos])
            else:
                columnas_seleccionadas.append(
                    pd.Series([""] * len(df), index=df.index, dtype=object)
                )
                nombres_columnas.append(f"VACIO_{len(nombres_columnas) + 1}")

        df_eventos = pd.concat(columnas_seleccionadas, axis=1)
        df_eventos.columns = nombres_columnas

        if "TIPIFICACION" in df_eventos.columns:
            df_eventos.rename(columns={"TIPIFICACION": "TIPO DE EVENTO"}, inplace=True)
            log_fn("✓ Columna 'TIPIFICACION' → 'TIPO DE EVENTO'")

        log_fn(f"✓ Extracción completada — {len(df_eventos)} filas")
        ruta_dir = Path(ruta_archivo).parent

        # Paso 3: Procesamiento especializado
        log_fn("\n─────────────────────────────────────────────────────────────")
        log_fn("📊 PASO 3: PROCESAMIENTO ESPECIALIZADO")
        log_fn("─────────────────────────────────────────────────────────────")

        df_contra = df_integrados = df_colab = None

        try:
            log_fn("→ Procesando CONTRAVENTORES / DETENIDOS...")
            df_contra = ContraventoresProcessor().process_df(df)
            log_fn(f"✓ {len(df_contra)} eventos")
        except Exception as e:
            log_fn(f"✗ Error contraventores: {e}")

        try:
            log_fn("→ Procesando INTEGRADOS / DESTACADOS...")
            df_integrados = IntegradosProcessor().process_df(df)
            log_fn(f"✓ {len(df_integrados)} eventos")
        except Exception as e:
            log_fn(f"✗ Error integrados: {e}")

        try:
            log_fn("→ Procesando COLABORADORES...")
            df_colab = ColaboradoresProcessor().process_df(df)
            log_fn(f"✓ {len(df_colab)} eventos")
        except Exception as e:
            log_fn(f"✗ Error colaboradores: {e}")

        # Paso 4: Unificar
        log_fn("\n─────────────────────────────────────────────────────────────")
        log_fn("📊 PASO 4: CREACIÓN DE ARCHIVO UNIFICADO")
        log_fn("─────────────────────────────────────────────────────────────")

        ruta_unificado = ruta_dir / "eventos_unificados.xlsx"
        parts = [df_eventos]

        if df_contra is not None:
            parts.append(df_contra)
            log_fn(f"  ✓ Contraventores/Detenidos: {len(df_contra)}")
        if df_integrados is not None:
            parts.append(df_integrados)
            log_fn(f"  ✓ Integrados/Destacados: {len(df_integrados)}")
        if df_colab is not None:
            parts.append(df_colab)
            log_fn(f"  ✓ Colaboradores: {len(df_colab)}")

        df_combined = pd.concat(parts, ignore_index=True, sort=False)

        with pd.ExcelWriter(ruta_unificado, engine="openpyxl") as writer:
            df_combined.to_excel(writer, sheet_name="eventos", index=False)

        log_fn("\n═══════════════════════════════════════════════════════════════")
        log_fn("✅ PROCESO COMPLETADO EXITOSAMENTE")
        log_fn("═══════════════════════════════════════════════════════════════")
        log_fn(f"📁 Archivo: {ruta_unificado.name}")
        log_fn(f"📊 Total registros: {len(df_combined)}")

        msg = (
            f"✅ Proceso completado\n\n"
            f"📁 {ruta_unificado}\n\n"
            f"📊 Resumen:\n"
            f"  • Eventos principales: {len(df_eventos)}\n"
            f"  • Contraventores/Detenidos: {len(df_contra) if df_contra is not None else 'no procesado'}\n"
            f"  • Integrados/Destacados: {len(df_integrados) if df_integrados is not None else 'no procesado'}\n"
            f"  • Colaboradores: {len(df_colab) if df_colab is not None else 'no procesado'}\n"
            f"  • Total: {len(df_combined)}"
        )
        return True, msg, str(ruta_unificado)

    except Exception as e:
        log_fn(f"✗ ERROR CRÍTICO: {e}")
        return False, f"Error: {e}", None


def procesar_narracion(
    ruta_narr: str,
    ruta_unificado: str,
    nombre_archivo_original: str,
    log_fn: Callable[[str], None],
) -> tuple[bool, str]:
    """Procesa narración y la agrega al archivo unificado."""
    narr_proc = NarracionProcessor(log_fn=log_fn, datos_dir=DATOS_DIR)
    mes = narr_proc.extraer_mes_de_nombre(nombre_archivo_original)
    return narr_proc.procesar_narracion_file(ruta_narr, mes, ruta_unificado)
