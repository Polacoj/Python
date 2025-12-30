import pandas as pd
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog

from contraventores_detenidos import ContraventoresProcessor
from integrados import IntegradosProcessor
from colaboradores import ColaboradoresProcessor
from pathlib import Path as _Path


# normmalizar cadena
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


# Convertir valor a cadena; si es float entero, quitar .0.
def _stringify_preserve_int(val):
    if pd.isna(val):
        return ""
    try:
        f = float(val)
        if f.is_integer():
            return int(f)
        return int(f)
    except Exception:
        return int(val)


# Convertir valor a entero nullable (pd.NA) si no es entero exacto.
def _parse_int_nullable(val):
    if pd.isna(val):
        return pd.NA
    try:
        f = float(val)
    except Exception:
        s = str(val).strip()
        if s == "":
            return pd.NA
        if s.isdigit():
            return int(s)
        return pd.NA
    if f.is_integer():
        return int(f)
    return pd.NA

# Procesar archivo de narración
def procesar_narracion_file(ruta_archivo_narracion: str):
    """Procesa un archivo de narración: pide hoja, extrae columnas, compara con CMU y guarda resultado."""
    try:
        xls = pd.ExcelFile(ruta_archivo_narracion, engine="openpyxl")
        hojas = xls.sheet_names
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir el archivo de narración: {e}")
        return False, str(e)

    # pedir al usuario la hoja (por índice)

    hoja_idx = simpledialog.askinteger(
        "Seleccionar hoja",
        "Seleccione una hoja:\n\n"
        + "\n".join(f"{i} - {h}" for i, h in enumerate(hojas)),
        minvalue=0,
        maxvalue=len(hojas) - 1,
    )

    if hoja_idx is None:
        return False, "Selección de hoja cancelada"

    try:
        df_n = pd.read_excel(
            ruta_archivo_narracion, sheet_name=hoja_idx, engine="openpyxl"
        )
    except Exception as e:
        return False, f"No se pudo leer la hoja seleccionada: {e}"

    # limpiar GAP y SAE
    for col in (3, 4):
        if col < len(df_n.columns):
            df_n.iloc[:, col] = (
                df_n.iloc[:, col]
                .where(df_n.iloc[:, col].notna(), "")
                .astype(str)
                .str.split("/", n=1)
                .str[0]
                .str.strip()
            )

    # Columnas a extraer (posiciones 3,4,5)
    columnas_a_extraer = [2, 3, 4]
    max_idx = max(columnas_a_extraer)
    if df_n.shape[1] <= max_idx:
        return (
            False,
            f"La hoja no tiene las columnas requeridas (necesita al menos {max_idx + 1}).",
        )

    mask = df_n.iloc[:, 5].fillna("").astype(str).str.strip().str.lower() == "si"
    df_eventos = (
        df_n.loc[mask].iloc[:, columnas_a_extraer].copy().reset_index(drop=True)
    )
    df_eventos.columns = ["OPERADOR", "GAP", "SAE"]

    # normalizar y preparar SAE entero
    df_eventos["GAP"] = df_eventos["GAP"].apply(_stringify_preserve_int)
    df_eventos["SAE"] = df_eventos["SAE"].apply(_stringify_preserve_int)
    df_eventos["SAE_INT"] = df_eventos["SAE"].apply(_parse_int_nullable).astype("Int64")
    df_eventos["SAE"] = (df_eventos["SAE"].fillna("").astype(str)).apply(norm)

    # abrir CMU y comparar
    try:
        maestro = pd.read_excel(
            _Path(__file__).parent / "archivos_xlsx" / "CMU - OCTUBRE.xlsx",
            engine="openpyxl",
        )
    except Exception as e:
        return False, f"No se pudo abrir CMU: {e}"

    if maestro.shape[1] < 33:
        return (
            False,
            f"El archivo CMU no tiene suficientes columnas ({maestro.shape[1]}).",
        )

    col_sae_cmu = maestro.columns[14]
    col_origen = maestro.columns[32]
    maestro["SAE"] = (maestro[col_sae_cmu].fillna("").astype(str)).apply(norm)

    # deduplicate maestro
    if maestro["SAE"].duplicated().any():
        maestro = maestro.drop_duplicates(subset=["SAE"], keep="first")

    try:
        resultado = df_eventos.merge(
            maestro[["SAE", col_origen]], on="SAE", how="inner", validate="m:1"
        )
    except Exception:
        resultado = df_eventos.merge(
            maestro[["SAE", col_origen]], on="SAE", how="inner"
        )

    if resultado.empty:
        return False, "No se encontraron coincidencias entre SAE(narracion) y SAE(CMU)."

    # usar SAE_INT si existe
    if "SAE_INT" in resultado.columns:
        resultado["SAE"] = resultado["SAE_INT"]
        resultado = (
            resultado.drop(columns=["SAE_INT"])
            if "SAE_INT" in resultado.columns
            else resultado
        )
        try:
            resultado["SAE"] = resultado["SAE"].astype("Int64")
        except Exception:
            pass

    resultado = resultado.rename(columns={col_origen: "ORIGEN"})
    salida = _Path(ruta_archivo_narracion).parent / "narracion_origen.xlsx"
    resultado.to_excel(salida, index=False)
    return True, f"Archivo generado: {salida}"

# Procesar archivo de eventos (contraventores y detenidos)
def procesar_excel(ruta_archivo):
    """Procesa el archivo Excel y genera el archivo de salida"""
    try:
        df = pd.read_excel(ruta_archivo, engine="openpyxl")

        # limpiar GAP y SAE
        for col in (14, 15):
            if col < len(df.columns):
                df.iloc[:, col] = (
                    df.iloc[:, col]
                    .where(df.iloc[:, col].notna(), "")
                    .astype(str)
                    .str.split("/", n=1)
                    .str[0]
                    .str.strip()
                )

        # Columnas (base 1 → base 0)
        columnas_a_extraer = [
            1,
            2,
            7,
            17,
            21,
            33,
            14,
            15,
        ]  # representan fecha, hora, operador, tipo evento, barrio, origen, gap, sae
        columnas_a_extraer = [i - 1 for i in columnas_a_extraer]

        if len(df.columns) < max(columnas_a_extraer) + 1:
            return False, (
                f"El archivo no tiene suficientes columnas.\n"
                f"Se esperaban al menos {max(columnas_a_extraer) + 1}"
            )

        df_eventos = df.iloc[:, columnas_a_extraer].copy()

        if "TIPIFICACIÓN" in df_eventos.columns:
            df_eventos.rename(columns={"TIPIFICACIÓN": "TIPO DE EVENTO"}, inplace=True)

        ruta_dir = Path(ruta_archivo).parent

        # Guardar backups individuales
        backup_eventos = ruta_dir / "eventos_backup.xlsx"
        df_eventos.to_excel(backup_eventos, index=False)

        # Intentar generar resumen de contraventores/detenidos
        df_contra = None
        backup_contra = None
        contra_error = None
        try:
            proc = ContraventoresProcessor()
            df_contra = proc.process_df(df)
            backup_contra = ruta_dir / "contraventores_detenidos_backup.xlsx"
            df_contra.to_excel(backup_contra, index=False)
        except Exception as e:
            df_contra = None
            backup_contra = None
            contra_error = str(e)

        # Intentar generar resumen de integrados/destacados
        df_integrados = None
        backup_integrados = None
        integ_error = None
        try:
            iproc = IntegradosProcessor()
            df_integrados = iproc.process_df(df)
            backup_integrados = ruta_dir / "integrados_backup.xlsx"
            df_integrados.to_excel(backup_integrados, index=False)
        except Exception as e:
            df_integrados = None
            backup_integrados = None
            integ_error = str(e)

        # Intentar generar resumen de colaboradores
        df_colab = None
        backup_colab = None
        colab_error = None
        try:
            cproc = ColaboradoresProcessor()
            df_colab = cproc.process_df(df)
            backup_colab = ruta_dir / "colaboradores_backup.xlsx"
            df_colab.to_excel(backup_colab, index=False)
        except Exception as e:
            df_colab = None
            backup_colab = None
            colab_error = str(e)

        # Crear un único archivo unificado con una sola hoja (eventos continuados con contraventores)
        ruta_unificado = ruta_dir / "eventos_unificado.xlsx"
        try:
            parts = [df_eventos]
            if df_contra is not None:
                parts.append(df_contra)
            if df_integrados is not None:
                parts.append(df_integrados)
            if df_colab is not None:
                parts.append(df_colab)

            # Concatenar verticalmente, alineando columnas (columnas faltantes rellenas con NaN)
            df_combined = pd.concat(parts, ignore_index=True, sort=False)

            with pd.ExcelWriter(ruta_unificado, engine="openpyxl") as writer:
                df_combined.to_excel(writer, sheet_name="eventos", index=False)

            msg = f"Archivo unificado generado:\n{ruta_unificado}\n"
            msg += f"\nCon Backups:\n{backup_eventos}"
            if backup_contra is not None:
                msg += f"\n{backup_contra}"
            else:
                msg += f"\nNo se generó contraventores (error: {contra_error})"

            if backup_integrados is not None:
                msg += f"\n{backup_integrados}"
            else:
                msg += f"\nNo se generó integrados (error: {integ_error})"

            if backup_colab is not None:
                msg += f"\n{backup_colab}"
            else:
                msg += f"\nNo se generó colaboradores (error: {colab_error})"

            return True, msg
        except Exception as e:
            return False, f"Error al generar archivo unificado:\n{e}"

    except Exception as e:
        return False, f"Error al procesar:\n{str(e)}"

# Seleccionar archivo y procesar
def seleccionar_archivo():
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

    ok, mensaje = procesar_excel(archivo)

    estado_var.set(mensaje)
    if ok:
        messagebox.showinfo("Proceso finalizado", mensaje)
        # Después del procesamiento principal, preguntar al usuario si desea procesar narración
        sel = messagebox.askyesno(
            "Procesar narración",
            "¿Desea procesar un archivo de narración ahora? Seleccione 'Sí' para elegir el archivo.",
        )
        if sel:
            ruta_narr = filedialog.askopenfilename(
                title="Seleccionar archivo de narración",
                filetypes=[("Archivos Excel", "*.xlsx *.xls")],
            )
            if ruta_narr:
                estado_var.set("Procesando narración...")
                root.update_idletasks()
                ok_n, msg_n = procesar_narracion_file(ruta_narr)
                estado_var.set(msg_n)
                if ok_n:
                    messagebox.showinfo("Narración finalizada", msg_n)
                else:
                    messagebox.showerror("Narración", msg_n)
    else:
        messagebox.showerror("Error", mensaje)


# ================== UI ==================

root = tk.Tk()
root.title("Procesador de Eventos Excel")
root.geometry("800x400")
root.resizable(False, False)

archivo_var = tk.StringVar(value="Ningún archivo seleccionado")
estado_var = tk.StringVar()

frame = ttk.Frame(root, padding=20)
frame.pack(fill="both", expand=True)

ttk.Label(
    frame,
    text="Procesador de Eventos Excel",
    font=("Segoe UI", 16, "bold"),
).pack(pady=(0, 10))

ttk.Button(
    frame,
    text="Seleccionar archivo Excel",
    command=seleccionar_archivo,
).pack(pady=10)

ttk.Label(frame, textvariable=archivo_var).pack(pady=5)
ttk.Label(frame, textvariable=estado_var, foreground="green").pack(pady=50)

ttk.Separator(frame).pack(fill="x", pady=20)

ttk.Label(
    frame,
    text="Columnas a procesar: 1, 2, 7, 17, 21, 33, 14, 15",
    font=("Segoe UI", 9, "italic"),
    foreground="gray",
).pack()

root.mainloop()
