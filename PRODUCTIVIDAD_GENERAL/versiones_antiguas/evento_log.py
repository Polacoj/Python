import pandas as pd
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog, scrolledtext
from typing import Optional
from contraventores_detenidos import ContraventoresProcessor
from integrados import IntegradosProcessor
from colaboradores import ColaboradoresProcessor
from pathlib import Path as _Path
import time

#SCRIPT_DIR = Path(__file__).parent
#DATOS_DIR = SCRIPT_DIR / "DATOS"
#DATOS_DIR.mkdir(exist_ok=True)

# funcion para log visual y consola
def log_mensaje(msg):
    """Añade mensaje al log visual"""
    global ventana_log
    if ventana_log:
        ventana_log.config(state=tk.NORMAL)
        ventana_log.insert(tk.END, msg + "\n")
        ventana_log.see(tk.END)
        ventana_log.config(state=tk.DISABLED)
        ventana_log.update()
    print(msg)

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

#procesa control diario x hojas para extraer y comparar narracion
def procesar_narracion_file(ruta_archivo_narracion: str, mes_cmu: Optional[str] = None):
    """Procesa un archivo de narración: pide hoja, extrae columnas, compara con CMU y guarda resultado."""
    try:
        log_mensaje(f"\n Procesando:------> {"Archivo Control Diario para NARRACION"}")        
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

    # Limpiar GAP y SAE - VERSIÓN CORREGIDA
    for col in (3, 4):
        if col < len(df_n.columns):
            col_name = df_n.columns[col]
            df_n[col_name] = (
                df_n.iloc[:, col]
                .fillna("")
                .astype(str)
                .str.split("/", n=1)
                .str[0]
                .str.strip()
            )

    # Columnas a extraer (posiciones 2,3,4 en base 0)
    columnas_a_extraer = [2, 3, 4]
    max_idx = max(columnas_a_extraer)
    if df_n.shape[1] <= max_idx:
        return (
            False,
            f"La hoja no tiene las columnas requeridas (necesita al menos {max_idx + 1}).",
        )

    # 1. Condición: Columna 5 sea "si" (limpiando espacios y minúsculas)
    condicion_si = df_n.iloc[:, 5].fillna("").astype(str).str.strip().str.lower() == "si"

# 2. Condición: Columna 2 NO esté vacía
# Verificamos que tras quitar espacios, el largo de la cadena sea mayor a 0
    condicion_no_vacia = df_n.iloc[:, 2].fillna("").astype(str).str.strip() != ""

# Combinar ambas condiciones con & (operador AND)
    mask = condicion_si & condicion_no_vacia

# Extraer los datos aplicando la máscara combinada
    df_eventos = (
        df_n.loc[mask].iloc[:, columnas_a_extraer].copy().reset_index(drop=True))

    #mask = df_n.iloc[:, 5].fillna("").astype(str).str.strip().str.lower() == "si"
    #df_eventos = (
     #   df_n.loc[mask].iloc[:, columnas_a_extraer].copy().reset_index(drop=True)
    #)
    df_eventos.columns = ["OPERADOR", "GAP", "SAE"]

    # Convertir SAE a numérico, manejando errores
    df_eventos["SAE"] = pd.to_numeric(df_eventos["SAE"], errors="coerce")
    # Eliminar filas donde SAE es NaN (no pudo convertirse a número)
    df_eventos = df_eventos.dropna(subset=["SAE"])
    # Convertir a int64
    df_eventos["SAE"] = df_eventos["SAE"].astype("Int64")

    # Abrir CMU y comparar
    try:
        cmu_dir = _Path(__file__).parent / "DATOS"
        cmu_path = None
        if mes_cmu:
            candidate = cmu_dir / f"CMU - {mes_cmu.upper()}.xlsx"
            if candidate.exists():
                cmu_path = candidate

        if cmu_path is None:
            # buscar cualquier CMU disponible como fallback
            matches = list(cmu_dir.glob("CMU - *.xlsx"))
            if matches:
                cmu_path = matches[0]
            else:
                raise FileNotFoundError(f"No se encontró archivo CMU en {cmu_dir}")

        maestro = pd.read_excel(cmu_path, engine="openpyxl")
    except Exception as e:
        return False, f"No se pudo abrir CMU: {e}"

    if maestro.shape[1] < 33:
        return (
            False,
            f"El archivo CMU no tiene suficientes columnas ({maestro.shape[1]}).",
        )

    col_sae_cmu = maestro.columns[14]
    col_origen = maestro.columns[32]

    # Convertir SAE en maestro a numérico también
    maestro["SAE"] = pd.to_numeric(maestro[col_sae_cmu], errors="coerce")
    maestro = maestro.dropna(subset=["SAE"])
    maestro["SAE"] = maestro["SAE"].astype("Int64")

    # Deduplicate maestro
    if maestro["SAE"].duplicated().any():
        maestro = maestro.drop_duplicates(subset=["SAE"], keep="first")

    # Ahora el merge funcionará porque ambos son Int64
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

    resultado = resultado.rename(columns={col_origen: "ORIGEN"})
    salida = _Path(ruta_archivo_narracion).parent / "narracion_origen.xlsx"
    resultado.to_excel(salida, index=False)
    return True, f"Archivo generado: {salida}"

# Procesar archivo de eventos (contraventores y detenidos)
def procesar_excel(ruta_archivo):
    """Procesa el archivo Excel y genera el archivo de salida"""
    log_mensaje("\n[---INICIANDO PROCESO---]")
    log_mensaje(f"Archivo: {ruta_archivo}")
    
    time.sleep(2) # Pausa por 3.5 segundos
    try:
        
        log_mensaje(f"\n→ Procesando: {"--DETENIDOS--"}")
        time.sleep(1) # Pausa por 3.5 segundos
        #log_mensaje(f"Carpeta de salida: {"corregir esto"}")
        df = pd.read_excel(ruta_archivo, engine="openpyxl")

        # Truncar filas a partir del primer "salto de línea" (fila completamente vacía)
        # Normalizar celdas vacías/espacios como NA y detectar la primera fila totalmente vacía
        df_temp = df.replace(r"^\s*$", pd.NA, regex=True)
        empty_rows = df_temp.isna().all(axis=1)
        if empty_rows.any():
            first_empty_idx = empty_rows.idxmax()  # primer True
            pos = df_temp.index.get_loc(first_empty_idx)
            df = df.iloc[:pos].reset_index(drop=True)

        # Limpiar GAP y SAE - VERSIÓN CORREGIDA (solo una vez)
        for col in (14, 15):
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

                # volver a numérico
                df[col_name] = pd.to_numeric(df[col_name], errors="coerce")

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
        ]
        columnas_a_extraer = [i - 1 for i in columnas_a_extraer]
        log_mensaje("\n--TIPIFICACION--")
        time.sleep(1) # Pausa por 3.5 segundos

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
#        backup_eventos = ruta_dir / "eventos_backup.xlsx"
#        df_eventos.to_excel(backup_eventos, index=False)

        # Intentar generar resumen de contraventores/detenidos
        df_contra = None
#        backup_contra = None
        contra_error = None
        try:
            proc = ContraventoresProcessor()
            log_mensaje(f"\n Procesando: {"-------> Eventos con CONTRAVENTORES"}")
            time.sleep(1) # Pausa por 3.5 segundos
            df_contra = proc.process_df(df)
#            backup_contra = ruta_dir / "contraventores_detenidos_backup.xlsx"
#            df_contra.to_excel(backup_contra, index=False)
        except Exception as e:
            df_contra = None
#            backup_contra = None
            contra_error = str(e)

        # Intentar generar resumen de integrados/destacados
        df_integrados = None
#        backup_integrados = None
        integ_error = None
        try:
            iproc = IntegradosProcessor()
            log_mensaje(f"\n Procesando: {"-------> Eventos con INTEGRADOS"}")
            time.sleep(1) # Pausa por 3.5 segundos
            df_integrados = iproc.process_df(df)
#            backup_integrados = ruta_dir / "integrados_backup.xlsx"
#            df_integrados.to_excel(backup_integrados, index=False)
        except Exception as e:
            df_integrados = None
#            backup_integrados = None
            integ_error = str(e)

        # Intentar generar resumen de colaboradores
        df_colab = None
#        backup_colab = None
        colab_error = None
        try:
            cproc = ColaboradoresProcessor()
            log_mensaje(f"\n Procesando: {"-------> Eventos con COLABORADORES"}")
            
            time.sleep(1) # Pausa por 3.5 segundos
            df_colab = cproc.process_df(df)
#            backup_colab = ruta_dir / "colaboradores_backup.xlsx"
#            df_colab.to_excel(backup_colab, index=False)
        except Exception as e:
            df_colab = None
#            backup_colab = None
            colab_error = str(e)

        # Crear un único archivo unificado con una sola hoja (eventos continuados con contraventores)
        ruta_unificado = ruta_dir / "eventos_unificados.xlsx"
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
#            msg += f"\nCon Backups:\n{backup_eventos}"
#            if backup_contra is not None:
#                msg += f"\n{backup_contra}"
#            else:
#                msg += f"\nNo se generó contraventores (error: {contra_error})"

#            if backup_integrados is not None:
#                msg += f"\n{backup_integrados}"
#            else:
#                msg += f"\nNo se generó integrados (error: {integ_error})"

#            if backup_colab is not None:
#                msg += f"\n{backup_colab}"
#            else:
#                msg += f"\nNo se generó colaboradores (error: {colab_error})"

            return True, msg
        except Exception as e:
            return False, f"Error al generar archivo unificado:\n{e}"

    except Exception as e:
        return False, f"Error al procesar:\n{str(e)}"

def _extraer_mes_de_nombre(nombre: str) -> Optional[str]:
    meses = [
        "enero",
        "febrero",
        "marzo",
        "abril",
        "mayo",
        "junio",
        "julio",
        "agosto",
        "septiembre",
        "octubre",
        "noviembre",
        "diciembre",
    ]
    ln = nombre.lower()
    for m in meses:
        if m in ln:
            return m
    return None

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
    estado_var.set("Procesando......")
    root.update_idletasks()

    ok, mensaje = procesar_excel(archivo)

    estado_var.set(mensaje)
    if ok:
        messagebox.showinfo("✅ Proceso finalizado", mensaje)
        # Después del procesamiento principal, preguntar al usuario si desea procesar narración
        sel = messagebox.askyesno(
            "Procesar narración",
            "¿Procesar un archivo de narración ahora? Seleccione 'Sí' para elegir el archivo.",
        )
        if sel:
            ruta_narr = filedialog.askopenfilename(
                title="Seleccionar archivo de narración",
                filetypes=[("Archivos Excel", "*.xlsx *.xls")],
            )
            if ruta_narr:
                estado_var.set("Procesando narración...")
                root.update_idletasks()
                mes = _extraer_mes_de_nombre(Path(archivo).name)
                ok_n, msg_n = procesar_narracion_file(ruta_narr, mes)
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
root.geometry("960x600")
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

ttk.Button(
    frame,
    text="❌ CERRAR",
    command=root.destroy,
    width=50,
).pack(side="bottom", pady=5)

ttk.Label(frame, textvariable=archivo_var).pack(pady=5)
ttk.Label(frame, textvariable=estado_var, foreground="green").pack(pady=30)

ttk.Separator(frame).pack(fill="x", pady=10)

ttk.Label(
    frame,
    text="Columnas a procesar:\n 1 (FECHA), 2 (HORA), 7 (OPERADOR), 17 (TIPIFICACIÓN), 21 (BARRIO), 33 (ORIGEN), 14 (GAP), 15 (SAE)",
    font=("Segoe UI", 9, "italic"),
    foreground="gray",
).pack()

# Frame log (área de texto)
frame_log = tk.Frame(root, bg="#B8B8B8")
frame_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

label_log = tk.Label(
    frame_log,
    text="        ESTADO DE PROCESAMIENTO",
    bg="#B8B8B8",
    fg="#232247",
    font=("Helvetica", 10, "bold"),
)

label_log.pack(anchor=tk.W, pady=5)

ventana_log = scrolledtext.ScrolledText(
    frame_log,
    height=20,
    fg="green",
    font=("Courier", 11),
    insertbackground="green",
    wrap=tk.WORD,
)

ventana_log.pack(fill=tk.BOTH, expand=True)
ventana_log.config(state=tk.DISABLED)

log_mensaje(
    "Sistema en espera...... \n\nSeleccione archivo MAESTRO XLSX para comenzar."
)

root.mainloop()
