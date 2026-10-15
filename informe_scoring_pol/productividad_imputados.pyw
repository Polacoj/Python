import logging
import tkinter as tk
import unicodedata
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Configuración de columnas
CONT_COL = "CONTRAVENTORES"
DET_COL = "DETENIDOS"
TIPIFICACION_COL = "TIPIFICACION"
CIERRE_COL = "TIPO DE CIERRE"
BARRIO_COL = "BARRIO"
ORIGEN_COL = "ORIGEN"
GAP_COL = "GAP"
SAE_COL = "SAE"
ACL_COL = "ACLARACIONES"
OFICIAL_INDEX = 5
JEFE_SERVICIO_COL = "JEFE DE SERVICIO"

logger = logging.getLogger(__name__)


def remove_accents(s):
    """Elimina acentos y diacríticos de un string."""
    s = str(s)
    return "".join(
        ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch)
    )


def oficial_df(df: pd.DataFrame) -> pd.DataFrame:
    """Extrae eventos de contraventores, detenidos, integrados y colaboración con ambos responsables."""
    filas_contraventor = []
    filas_detenido = []
    filas_integrados = []
    filas_colaboracion = []

    # Procesar contraventores
    for idx, fila in df.iterrows():
        if (
            fila.get(CONT_COL, 0) >= 1
            and fila.get(CIERRE_COL, "") == "FINALIZA CON IMPUTADO/S PROPIOS"
        ):
            oficial_val = (
                fila.iloc[OFICIAL_INDEX] if len(fila) > OFICIAL_INDEX else None
            )
            jefe_servicio_val = fila.get(JEFE_SERVICIO_COL)
            filas_contraventor.append(
                {
                    "OFICIAL": oficial_val,
                    "JEFE DE SERVICIO": jefe_servicio_val,
                    "TIPO DE EVENTO": "CONTRAVENCION",
                    "BARRIO": fila.get(BARRIO_COL),
                    "ORIGEN": fila.get(ORIGEN_COL),
                    "TURNO": "",
                    "P.EVENTO": "",
                    "% ZONA": "",
                    "P. TOTAL": "",
                    "GAP": fila.get(GAP_COL),
                    "SAE": fila.get(SAE_COL),
                }
            )

    # Procesar detenidos
    for idx, fila in df.iterrows():
        if (
            fila.get(DET_COL, 0) >= 1
            and fila.get(CIERRE_COL, "") == "FINALIZA CON IMPUTADO/S PROPIO/S"
        ):
            oficial_val = (
                fila.iloc[OFICIAL_INDEX] if len(fila) > OFICIAL_INDEX else None
            )
            jefe_servicio_val = fila.get(JEFE_SERVICIO_COL)
            if fila.get(TIPIFICACION_COL, "").strip().upper() == "ROBO/HURTO":
                filas_detenido.append(
                    {
                        "OFICIAL": oficial_val,
                        "JEFE DE SERVICIO": jefe_servicio_val,
                        "TIPO DE EVENTO": "ROBO/HURTO",
                        "BARRIO": fila.get(BARRIO_COL),
                        "ORIGEN": fila.get(ORIGEN_COL),
                        "TURNO": "",
                        "P.EVENTO": "",
                        "% ZONA": "",
                        "P. TOTAL": "",
                        "GAP": fila.get(GAP_COL),
                        "SAE": fila.get(SAE_COL),
                    }
                )
            else:
                filas_detenido.append(
                    {
                        "OFICIAL": oficial_val,
                        "JEFE DE SERVICIO": jefe_servicio_val,
                        "TIPO DE EVENTO": "DELITO",
                        "BARRIO": fila.get(BARRIO_COL),
                        "ORIGEN": fila.get(ORIGEN_COL),
                        "GAP": fila.get(GAP_COL),
                        "SAE": fila.get(SAE_COL),
                    }
                )

    # Procesar eventos integrados/destacados
    for idx, fila in df.iterrows():
        tip_val = remove_accents(str(fila.get(ACL_COL, ""))).strip().lower()
        if "integ" in tip_val or "dest" in tip_val:
            oficial_val = (
                fila.iloc[OFICIAL_INDEX] if len(fila) > OFICIAL_INDEX else None
            )
            jefe_servicio_val = fila.get(JEFE_SERVICIO_COL)
            filas_integrados.append(
                {
                    "OFICIAL": oficial_val,
                    "JEFE DE SERVICIO": jefe_servicio_val,
                    "TIPO DE EVENTO": "INTERVENCION DESTACADA",
                    "BARRIO": fila.get(BARRIO_COL),
                    "ORIGEN": fila.get(ORIGEN_COL),
                    "TURNO": "",
                    "P.EVENTO": "",
                    "% ZONA": "",
                    "P. TOTAL": "",
                    "GAP": fila.get(GAP_COL),
                    "SAE": fila.get(SAE_COL),
                }
            )

    # Procesar colaboración con intervención propia
    for idx, fila in df.iterrows():
        if fila.get(CIERRE_COL, "") == "COLABORACION CON INTERVENCION PROPIA":
            oficial_val = (
                fila.iloc[OFICIAL_INDEX] if len(fila) > OFICIAL_INDEX else None
            )
            jefe_servicio_val = fila.get(JEFE_SERVICIO_COL)
            filas_colaboracion.append(
                {
                    "OFICIAL": oficial_val,
                    "JEFE DE SERVICIO": jefe_servicio_val,
                    "TIPO DE EVENTO": "COLABORACION CON INTERVENCION PROPIA",
                    "BARRIO": fila.get(BARRIO_COL),
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
            pd.DataFrame(filas_colaboracion),
        ],
        ignore_index=True,
    )

    return resultado


def process_file(ruta_archivo: str) -> tuple[bool, str]:
    """
    Procesa un archivo de Excel y guarda los resultados.
    """
    try:
        # Leer archivo
        df = pd.read_excel(ruta_archivo, engine="openpyxl")

        # Convertir columna BARRIO a minúsculas
        if BARRIO_COL in df.columns:
            df[BARRIO_COL] = df[BARRIO_COL].str.lower()

        # Procesar eventos por oficial y jefe de servicio
        resultado = oficial_df(df)

        # Guardar resultado por oficial y jefe de servicio
        salida_eventos = Path(__file__).parent / "DATOS/productividad_imputados.xlsx"
        resultado.to_excel(salida_eventos, index=False, engine="openpyxl")

        mensaje = (
            f"✓ Archivos procesados exitosamente\n"
            f"✓ Total eventos: {len(resultado)}\n"
            f"✓ Archivos guardados en:\n"
            f"  ‣ {salida_eventos}\n"
        )

        return True, mensaje

    except Exception as e:
        import traceback

        error_detallado = traceback.format_exc()
        return False, f"Error al procesar el archivo:\n{str(e)}\n\n{error_detallado}"


# ... (código anterior igual hasta la función ejecutar_calculo)


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
        messagebox.showinfo("Proceso Completado", "Archivo procesado exitosamente.")
    else:
        messagebox.showerror("Error", mensaje, icon="error")


# ================== UI ==================

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Procesador de Eventos Excel")
    root.geometry("960x500")
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

    # Frame para botones principales
    frame_botones = ttk.Frame(frame)
    frame_botones.pack(pady=10)

    ttk.Button(
        frame_botones,
        text="📁 Seleccionar archivo Excel",
        command=seleccionar_archivo,
        width=25,
    ).pack(side="left", padx=5)

    ttk.Label(
        frame,
        text="Archivo seleccionado:",
        font=("Segoe UI", 10, "bold"),
    ).pack(pady=(10, 5))

    ttk.Label(
        frame,
        textvariable=archivo_var,
        font=("Segoe UI", 10),
        foreground="blue",
    ).pack(pady=(0, 10))

    ttk.Label(
        frame,
        text="Estado:",
        font=("Segoe UI", 10, "bold"),
    ).pack(pady=(10, 5))

    estado_label = ttk.Label(
        frame,
        textvariable=estado_var,
        wraplength=600,
        justify="left",
    )
    estado_label.pack(pady=(0, 20), fill="x")

    ttk.Separator(frame).pack(fill="x", pady=20)

    # Frame para botones de acción
    frame_accion = ttk.Frame(frame)
    frame_accion.pack(side="bottom", pady=10)

    ttk.Button(
        frame_accion,
        text="❌ CERRAR",
        command=root.destroy,
        width=20,
    ).pack(side="left", padx=5)

    ttk.Label(
        frame,
        text="Genera: productividad_imputados.xlsx",
        font=("Segoe UI", 9, "italic"),
        foreground="gray",
    ).pack(side="bottom", pady=10)

    root.mainloop()
