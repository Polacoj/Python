import pandas as pd
from pathlib import Path
import unicodedata
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

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

# TODO:convertir a mayuscula todos los caracteres de las columnas al leer el excel


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


def process_file(ruta_archivo: str) -> tuple[bool, str]:
    """
    Procesa un archivo de Excel y guarda los resultados.

    Args:
        ruta_archivo: Ruta al archivo Excel

    Returns:
        Tupla con (éxito: bool, mensaje: str)
    """
    try:
        # Leer archivo
        df = pd.read_excel(ruta_archivo, engine="openpyxl")

        #df = df.apply(lambda c: c.str.upper() if c.dtype == "object" or c.dtype == "int64" else c )
        
        # Procesar ambos DataFrames
        resultado = operador_df(df)
        resultado_sisep = sisep_df(df)

        # Guardar resultado operador
        salida_operador = Path.cwd() / "productividad_imputados.xlsx"
        resultado.to_excel(salida_operador, index=False, engine="openpyxl")

        # Guardar resultado SISEP
        salida_sisep = Path.cwd() / "productividad_imputados_sisep.xlsx"
        resultado_sisep.to_excel(salida_sisep, index=False, engine="openpyxl")

        mensaje = (
            f"✓ Archivos procesados exitosamente\n"
            f"✓ Total eventos operador: {len(resultado)}\n"
            f"✓ Total eventos SISEP: {len(resultado_sisep)}\n"
            f"✓ Archivos guardados en:\n \t‣{Path.cwd() / 'salida_operador.xlsx'}\n \t‣{Path.cwd() / 'salida_sisep.xlsx'}"
        )

        return True, mensaje

    except Exception as e:
        import traceback

        error_detallado = traceback.format_exc()
        return False, f"Error al procesar el archivo:\n{str(e)}\n\n{error_detallado}"


def seleccionar_archivo():
    """Función para seleccionar y procesar un archivo desde la GUI."""
    archivo = filedialog.askopenfilename(
        title="Seleccionar archivo Excel",
        filetypes=[("Archivos Excel", "*.xlsx *.xls")],
    )

    if not archivo:
        estado_var.set("Selección cancelada")
        return

    archivo_var.set(Path(archivo).name)
    estado_var.set("Procesando...")
    root.update_idletasks()

    ok, mensaje = process_file(archivo)

    estado_var.set(mensaje if ok else "Error en el procesamiento")

    if ok:
        messagebox.showinfo(title=None, message="Proceso finalizado", icon="info")
    else:
        messagebox.showerror("Error", mensaje, icon="error")


# ================== UI ==================

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Procesador de Eventos Excel")
    root.geometry("600x400")
    root.resizable(False, False)

    archivo_var = tk.StringVar(value="Ningún archivo seleccionado")
    estado_var = tk.StringVar(value="Listo para procesar archivos")

    frame = ttk.Frame(root, padding=20)
    frame.pack(fill="both", expand=True)

    ttk.Label(
        frame,
        text="Procesador de Eventos Excel",
        font=("Segoe UI", 16, "bold"),
    ).pack(pady=(0, 20))

    ttk.Button(
        frame,
        text="Seleccionar archivo Excel",
        command=seleccionar_archivo,
        width=30,
    ).pack(pady=10)

    ttk.Button(
        frame,
        text="❌ CERRAR",
        command=root.destroy,
        width=50,
    ).pack(side="bottom", pady=5)

    ttk.Label(
        frame,
        textvariable=archivo_var,
        font=("Segoe UI", 10),
    ).pack(pady=5)

    ttk.Label(
        frame,
        textvariable=estado_var,
        foreground="green",
        wraplength=550,
    ).pack(pady=20, fill="x")

    ttk.Separator(frame).pack(fill="x", pady=20)

    ttk.Label(
        frame,
        text="Genera: productividad_imputados.xlsx y productividad_imputados_sisep.xlsx",
        font=("Segoe UI", 9, "italic"),
        foreground="gray",
    ).pack()

    root.mainloop()
