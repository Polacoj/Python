import pandas as pd
from pathlib import Path
import unicodedata
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from calculo import CalculadorPuntajes  # Importar la clase desde el módulo
import logging

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
OPERADOR_INDEX = 6
GRUPO_COL = "GRUPO"
SISEP_COL = "SISEP/ANILLO"

logger = logging.getLogger(__name__)


def remove_accents(s):
    """Elimina acentos y diacríticos de un string."""
    s = str(s)
    return "".join(
        ch for ch in unicodedata.normalize("NFKD", s) if not unicodedata.combining(ch)
    )


def operador_df(df: pd.DataFrame) -> pd.DataFrame:
    """Procesa el DataFrame extrayendo eventos con contraventores y detenidos."""
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
                    "OPERADOR": operador_val,
                    "TIPO DE EVENTO": "CONTRAVENCION",
                    "BARRIO": fila.get(BARRIO_COL),
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
                        "OPERADOR": operador_val,
                        "TIPO DE EVENTO": "ROBO/HURTO",
                        "BARRIO": fila.get(BARRIO_COL),
                        "ORIGEN": fila.get(ORIGEN_COL),
                        "GAP": fila.get(GAP_COL),
                        "SAE": fila.get(SAE_COL),
                    }
                )
            else:
                filas_detenido.append(
                    {
                        "OPERADOR": operador_val,
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
            operador_val = (
                fila.iloc[OPERADOR_INDEX] if len(fila) > OPERADOR_INDEX else None
            )
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
    """Procesa el DataFrame extrayendo eventos SISEP con contraventores y detenidos."""
    filas_contraventor_sisep = []
    filas_detenido_sisep = []
    filas_integrados_sisep = []

    # Procesar contraventores SISEP
    for idx, fila in df.iterrows():
        if (
            fila.get(CONT_COL, 0) >= 1
            and fila.get(CIERRE_COL, "") == "FINALIZA CON IMPUTADO/S"
            and fila.get(SISEP_COL, "") in ["SISEP", "SISEP "]
        ):
            filas_contraventor_sisep.append(
                {
                    "GRUPO": fila.get(GRUPO_COL, ""),
                    "TIPO DE EVENTO": "CONTRAVENCION",
                    "BARRIO": fila.get(BARRIO_COL),
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
            and fila.get(SISEP_COL, "") in ["SISEP", "SISEP "]
        ):
            if fila.get(TIPIFICACION_COL, "").strip().upper() == "ROBO/HURTO":
                filas_detenido_sisep.append(
                    {
                        "GRUPO": fila.get(GRUPO_COL, ""),
                        "TIPO DE EVENTO": "ROBO/HURTO",
                        "BARRIO": fila.get(BARRIO_COL),
                        "ORIGEN": fila.get(ORIGEN_COL),
                        "GAP": fila.get(GAP_COL),
                        "SAE": fila.get(SAE_COL),
                    }
                )
            else:
                filas_detenido_sisep.append(
                    {
                        "GRUPO": fila.get(GRUPO_COL, ""),
                        "TIPO DE EVENTO": "DELITO",
                        "BARRIO": fila.get(BARRIO_COL),
                        "ORIGEN": fila.get(ORIGEN_COL),
                        "GAP": fila.get(GAP_COL),
                        "SAE": fila.get(SAE_COL),
                    }
                )

    # Procesar eventos integrados/destacados SISEP
    for idx, fila in df.iterrows():
        if fila.get(SISEP_COL, "") in ["SISEP", "SISEP "]:
            tip_val = remove_accents(str(fila.get(ACL_COL, ""))).strip().lower()
            if "integ" in tip_val or "dest" in tip_val:
                filas_integrados_sisep.append(
                    {
                        "GRUPO": fila.get(GRUPO_COL, ""),
                        "TIPO DE EVENTO": "INTERVENCION DESTACADA",
                        "BARRIO": fila.get(BARRIO_COL),
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
    """
    try:
        # Leer archivo
        df = pd.read_excel(ruta_archivo, engine="openpyxl")

        # Convertir columna BARRIO a minúsculas
        if BARRIO_COL in df.columns:
            df[BARRIO_COL] = df[BARRIO_COL].str.lower()

        # Procesar ambos DataFrames
        resultado = operador_df(df)
        resultado_sisep = sisep_df(df)

        # Guardar resultado operador
        salida_operador = Path(__file__).parent / "productividad_imputados.xlsx"
        resultado.to_excel(salida_operador, index=False, engine="openpyxl")

        # Guardar resultado SISEP
        salida_sisep = Path(__file__).parent / "productividad_imputados_sisep.xlsx"
        resultado_sisep.to_excel(salida_sisep, index=False, engine="openpyxl")

        mensaje = (
            f"✓ Archivos procesados exitosamente\n"
            f"✓ Total eventos operador: {len(resultado)}\n"
            f"✓ Total eventos SISEP: {len(resultado_sisep)}\n"
            f"✓ Archivos guardados en:\n"
            f"  ‣ {salida_operador}\n"
            f"  ‣ {salida_sisep}"
        )

        return True, mensaje

    except Exception as e:
        import traceback

        error_detallado = traceback.format_exc()
        return False, f"Error al procesar el archivo:\n{str(e)}\n\n{error_detallado}"


# ... (código anterior igual hasta la función ejecutar_calculo)


def ejecutar_calculo():
    """Función para ejecutar el cálculo de puntajes."""
    try:
        # Crear instancia del calculador
        calculador = CalculadorPuntajes()

        # Verificar si existen los archivos procesados
        archivo_operador = Path(__file__).parent / "productividad_imputados.xlsx"
        archivo_sisep = Path(__file__).parent / "productividad_imputados_sisep.xlsx"

        if not archivo_operador.exists():
            messagebox.showwarning(
                "Advertencia",
                f"No se encontró el archivo: {archivo_operador.name}\n"
                "Primero debes procesar un archivo Excel.",
                icon="warning",
            )
            return

        estado_var.set("Cargando datos...")
        root.update_idletasks()

        # Cargar archivos con manejo de errores
        try:
            df_operador = pd.read_excel(archivo_operador, engine="openpyxl")
            logger.info(f"Archivo operador cargado: {len(df_operador)} registros")
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo cargar {archivo_operador.name}:\n{str(e)}",
                icon="error",
            )
            estado_var.set("Error cargando archivo operador")
            return

        # Procesar archivo SISEP si existe
        df_sisep = None
        if archivo_sisep.exists():
            try:
                df_sisep = pd.read_excel(archivo_sisep, engine="openpyxl")
                logger.info(f"Archivo SISEP cargado: {len(df_sisep)} registros")
            except Exception as e:
                logger.warning(f"No se pudo cargar archivo SISEP: {e}")

        # Calcular puntajes
        estado_var.set("Calculando puntajes...")
        root.update_idletasks()

        # Procesar archivo de operador
        resultado_operador = calculador.guardar_con_puntajes(
            df_operador,
            Path(__file__).parent / "productividad_imputados_con_puntaje.xlsx",
        )

        if resultado_operador is None:
            messagebox.showerror(
                "Error",
                "No se pudieron calcular los puntajes para el archivo de operador.\n"
                "Verifique que el archivo tenga las columnas necesarias.",
                icon="error",
            )
            estado_var.set("Error en cálculo")
            return

        # Procesar archivo SISEP si existe
        resultado_sisep = None
        if df_sisep is not None and not df_sisep.empty:
            resultado_sisep = calculador.guardar_con_puntajes(
                df_sisep,
                Path(__file__).parent
                / "productividad_imputados_sisep_con_puntaje.xlsx",
            )

        # Generar resumen
        estado_var.set("Generando resumen...")
        root.update_idletasks()

        resumen_operador = calculador.generar_resumen(resultado_operador)

        # Mostrar mensaje de éxito
        if "error" in resumen_operador:
            mensaje = f"✓ Cálculo completado\n✓ Archivo guardado: productividad_imputados_con_puntaje.xlsx\n⚠ {resumen_operador['error']}"
        else:
            mensaje = (
                f"✓ Cálculo de puntajes completado\n"
                f"✓ Total registros: {resumen_operador['total_registros']}\n"
                f"✓ Puntaje total: {resumen_operador['puntaje_total']:.2f}\n"
                f"✓ Puntaje promedio: {resumen_operador['puntaje_promedio']:.2f}\n"
                f"✓ Archivos guardados:\n"
                f"  ‣ productividad_imputados_con_puntaje.xlsx"
            )

            if resultado_sisep is not None:
                resumen_sisep = calculador.generar_resumen(resultado_sisep)
                mensaje += "\n  ‣ productividad_imputados_sisep_con_puntaje.xlsx"
                if "puntaje_total" in resumen_sisep:
                    mensaje += (
                        f"\n✓ Puntaje total SISEP: {resumen_sisep['puntaje_total']:.2f}"
                    )

        estado_var.set(mensaje)
        messagebox.showinfo(
            "Cálculo Completado", "Los puntajes han sido calculados exitosamente."
        )

    except Exception as e:
        import traceback

        error_detallado = traceback.format_exc()
        logger.error(f"Error en ejecutar_calculo: {error_detallado}")
        mensaje_error = f"Error al calcular puntajes:\n{str(e)}"
        estado_var.set("Error en el cálculo")
        messagebox.showerror("Error", mensaje_error, icon="error")


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

    ttk.Button(
        frame_botones,
        text="📊 Calcular Puntajes",
        command=ejecutar_calculo,
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
        text="Genera: productividad_imputados.xlsx y productividad_imputados_sisep.xlsx",
        font=("Segoe UI", 9, "italic"),
        foreground="gray",
    ).pack(side="bottom", pady=10)

    root.mainloop()
