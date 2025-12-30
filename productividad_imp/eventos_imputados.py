import pandas as pd
from pathlib import Path
import unicodedata

# Configuración de columnas
CONT_COL = "CONTRAVENTORES"
DET_COL = "DETENIDOS"
TIPIFICACION_COL = "TIPIFICACIÓN"
CIERRE_COL = "TIPO DE CIERRE"
BARRIO_COL = "BARRIO"
ORIGEN_COL = "ORIGEN"
GAP_COL = "GAP"
SAE_COL = "SAE"
ACL_COL = "ACLARACIONES"
OPERADOR_INDEX = 6
GRUPO_COL = "GRUPO"
SISEP_COL = "SISEP/ANILLO"


def remove_accents(s):
    """Elimina acentos y diacríticos de un string."""
    s = str(s)
    return "".join(
        ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch)
    )


def operador_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Procesa el DataFrame extrayendo eventos con contraventores y detenidos.

    Args:
        df: DataFrame con los datos de eventos

    Returns:
        DataFrame con los eventos procesados
    """
    filas_contraventor = []
    filas_detenido = []
    filas_integrados = []

    # Procesar contraventores
    for idx, fila in df.iterrows():
        if (
            fila.get(CONT_COL, 0) >= 1
            and fila.get(CIERRE_COL, "") == "FINALIZA CON IMPUTADO/S"
        ):
            operador_val = (
                fila.iloc[OPERADOR_INDEX] if len(fila) > OPERADOR_INDEX else None
            )
            filas_contraventor.append(
                {
                    "FECHA": fila.get("FECHA", ""),
                    "HORA": fila.get("HORA", ""),
                    "OPERADOR": operador_val,
                    "TIPO DE EVENTO": "EVENTO CON CONTRAVENTOR",
                    "ORIGEN": fila.get(ORIGEN_COL),
                    "GAP": fila.get(GAP_COL),
                    "SAE": fila.get(SAE_COL),
                }
            )

    # Procesar detenidos
    for idx, fila in df.iterrows():
        if (
            fila.get(DET_COL, 0) >= 1
            and fila.get(CIERRE_COL, "") == "FINALIZA CON IMPUTADO/S"
        ):
            operador_val = (
                fila.iloc[OPERADOR_INDEX] if len(fila) > OPERADOR_INDEX else None
            )
            if fila.get(TIPIFICACION_COL, "").strip().upper() == "ROBO/HURTO":
                filas_detenido.append(
                    {
                        "FECHA": fila.get("FECHA", ""),
                        "HORA": fila.get("HORA", ""),
                        "OPERADOR": operador_val,
                        "TIPO DE EVENTO": "ROBO/HURTO",
                        "ORIGEN": fila.get(ORIGEN_COL),
                        "GAP": fila.get(GAP_COL),
                        "SAE": fila.get(SAE_COL),
                    }
                )
            else:
                filas_detenido.append(
                    {
                        "FECHA": fila.get("FECHA", ""),
                        "HORA": fila.get("HORA", ""),
                        "OPERADOR": operador_val,
                        "TIPO DE EVENTO": "DELITO",
                        "ORIGEN": fila.get(ORIGEN_COL),
                        "GAP": fila.get(GAP_COL),
                        "SAE": fila.get(SAE_COL),
                    }
                )

    # Procesar eventos integrados/destacados
    for idx, fila in df.iterrows():
        tip_val = remove_accents(str(fila.get(ACL_COL, ""))).strip().lower()
        if "integ" in tip_val or "dest" in tip_val:
            operador_val = (
                fila.iloc[OPERADOR_INDEX] if len(fila) > OPERADOR_INDEX else None
            )
            filas_integrados.append(
                {
                    "FECHA": fila.get("FECHA", ""),
                    "HORA": fila.get("HORA", ""),
                    "OPERADOR": operador_val,
                    "TIPO DE EVENTO": "EVENTO INTEG./DESTAC. (LO DETERMINA CALIDAD)",
                    "ORIGEN": fila.get(ORIGEN_COL),
                    "GAP": fila.get(GAP_COL),
                    "SAE": fila.get(SAE_COL),
                }
            )

    # Combinar resultados
    resultado = pd.concat(
        [
            pd.DataFrame(filas_contraventor),
            pd.DataFrame(filas_detenido),
            pd.DataFrame(filas_integrados),
        ],
        ignore_index=True,
    )

    return resultado


def sisep_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Procesa el DataFrame extrayendo eventos SISEP con contraventores y detenidos.

    Args:
        df: DataFrame con los datos de eventos

    Returns:
        DataFrame con los eventos SISEP procesados
    """
    filas_contraventor_sisep = []
    filas_detenido_sisep = []
    filas_integrados_sisep = []

    # Procesar contraventores SISEP
    for idx, fila in df.iterrows():
        if (
            fila.get(CONT_COL, 0) >= 1
            and fila.get(CIERRE_COL, "") == "FINALIZA CON IMPUTADO/S"
            and fila.get(SISEP_COL, "") == "SISEP"
        ):
            filas_contraventor_sisep.append(
                {
                    "HORA": fila.get("HORA", ""),
                    "GRUPO": fila.get(GRUPO_COL, ""),
                    "TIPO DE EVENTO": "EVENTO CON CONTRAVENTOR",
                    "ORIGEN": fila.get(ORIGEN_COL),
                    "GAP": fila.get(GAP_COL),
                    "SAE": fila.get(SAE_COL),
                }
            )

    # Procesar detenidos SISEP
    for idx, fila in df.iterrows():
        if (
            fila.get(DET_COL, 0) >= 1
            and fila.get(CIERRE_COL, "") == "FINALIZA CON IMPUTADO/S"
            and fila.get(SISEP_COL, "") == "SISEP"
        ):
            if fila.get(TIPIFICACION_COL, "").strip().upper() == "ROBO/HURTO":
                filas_detenido_sisep.append(
                    {
                        "HORA": fila.get("HORA", ""),
                        "GRUPO": fila.get(GRUPO_COL, ""),
                        "TIPO DE EVENTO": "ROBO/HURTO",
                        "ORIGEN": fila.get(ORIGEN_COL),
                        "GAP": fila.get(GAP_COL),
                        "SAE": fila.get(SAE_COL),
                    }
                )
            else:
                filas_detenido_sisep.append(
                    {
                        "HORA": fila.get("HORA", ""),
                        "GRUPO": fila.get(GRUPO_COL, ""),
                        "TIPO DE EVENTO": "DELITO",
                        "ORIGEN": fila.get(ORIGEN_COL),
                        "GAP": fila.get(GAP_COL),
                        "SAE": fila.get(SAE_COL),
                    }
                )

    # Procesar eventos integrados/destacados SISEP
    for idx, fila in df.iterrows():
        if fila.get(SISEP_COL, "") == "SISEP":
            tip_val = remove_accents(str(fila.get(ACL_COL, ""))).strip().lower()
            if "integ" in tip_val or "dest" in tip_val:
                filas_integrados_sisep.append(
                    {
                        "HORA": fila.get("HORA", ""),
                        "GRUPO": fila.get(GRUPO_COL, ""),
                        "TIPO DE EVENTO": "EVENTO INTEG./DESTAC. (LO DETERMINA CALIDAD)",
                        "ORIGEN": fila.get(ORIGEN_COL),
                        "GAP": fila.get(GAP_COL),
                        "SAE": fila.get(SAE_COL),
                    }
                )

    # Combinar resultados
    resultado_sisep = pd.concat(
        [
            pd.DataFrame(filas_contraventor_sisep),
            pd.DataFrame(filas_detenido_sisep),
            pd.DataFrame(filas_integrados_sisep),
        ],
        ignore_index=True,
    )

    return resultado_sisep


def process_file(ruta_archivo: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Procesa un archivo de Excel y retorna ambos DataFrames procesados.

    Args:
        ruta_archivo: Ruta al archivo Excel

    Returns:
        Tupla con (DataFrame operador, DataFrame SISEP)
    """
    df = pd.read_excel(ruta_archivo, engine="openpyxl")
    return operador_df(df), sisep_df(df)


if __name__ == "__main__":
    # Solicitar ruta del archivo
    ruta_archivo = input("Ingrese la ruta del archivo de Excel a procesar: ")
    ruta_path = Path(ruta_archivo)

    if not ruta_path.exists():
        print(f"Error: El archivo '{ruta_archivo}' no existe.")
    else:
        try:
            # Procesar archivo
            resultado, resultado_sisep = process_file(ruta_path)

            # Guardar resultado operador
            salida_operador = Path.cwd() / "productividad_imputados.xlsx"
            resultado.to_excel(salida_operador, index=False, engine="openpyxl")

            # Guardar resultado SISEP
            salida_sisep = Path.cwd() / "productividad_imputados_sisep.xlsx"
            resultado_sisep.to_excel(salida_sisep, index=False, engine="openpyxl")

            print("\n✓ Archivos procesados exitosamente")
            print(f"✓ Total de eventos operador: {len(resultado)}")
            print(f"✓ Archivo guardado en: {salida_operador}")
            print(f"✓ Total de eventos SISEP: {len(resultado_sisep)}")
            print(f"✓ Archivo guardado en: {salida_sisep}")

        except Exception as e:
            print(f"Error al procesar el archivo: {e}")
            import traceback

            traceback.print_exc()
