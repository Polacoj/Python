"""
NOMBRE DE SCRIPT: PRODUCTIVIDAD GENERAL
DESCRIPCION DEL SCRIPT: Procesa datos para scoring de oficinas y genera un archivo unificado con eventos principales, contraventores/detenidos e integrados/destacados.
VERSION: 1.0.0
AUTOR: JANKOWICZ ALEXIS
FECHA: 27-09-2026

HISTORIAL DE CAMBIOS:
---------------------
[27-09-2026] v1.0.0: Versión inicial con copia modelo productividad_auxiliares.
"""

import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, scrolledtext, ttk

import pandas as pd

from complementos.contraventores_detenidos import ContraventoresDetenidosProcessor

# from complementos.contraventores_detenidos import ContraventoresProcessor
from complementos.integrados import IntegradosProcessor
from complementos.intervencion_directa import ColaboracionPropiaProcessor

SCRIPT_DIR = Path(__file__).parent
DATOS_DIR = SCRIPT_DIR / "DATOS"
DATOS_DIR.mkdir(exist_ok=True)


# función para log visual y consola
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


# normalizar cadena
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


# Procesar archivo de eventos (contraventores y detenidos)
def procesar_excel(ruta_archivo):
    """Procesa el archivo Excel y genera el archivo de salida"""
    log_mensaje(
        "\n═══════════════════════════════════════════════════════════════════════"
    )
    log_mensaje("🚀 INICIANDO PROCESO PRINCIPAL")
    log_mensaje(
        "═══════════════════════════════════════════════════════════════════════"
    )
    log_mensaje(f"📂 Archivo: {Path(ruta_archivo).name}")
    log_mensaje(f"📁 Carpeta: {Path(ruta_archivo).parent}")

    time.sleep(1)
    try:
        log_mensaje(
            "\n───────────────────────────────────────────────────────────────────────"
        )
        log_mensaje("📊 PASO 1: CARGANDO Y PREPARANDO DATOS")
        log_mensaje(
            "───────────────────────────────────────────────────────────────────────"
        )

        df = pd.read_excel(ruta_archivo, engine="openpyxl")
        log_mensaje("✓ Archivo cargado exitosamente")
        log_mensaje(
            f"  Dimensiones originales: {df.shape[0]} filas * {df.shape[1]} columnas"
        )

        # Truncar filas a partir del primer "salto de línea" (fila completamente vacía)
        log_mensaje("→ Eliminando filas vacías al final del archivo...")
        df_temp = df.replace(r"^\s*$", pd.NA, regex=True)
        empty_rows = df_temp.isna().all(axis=1)
        if empty_rows.any():
            first_empty_idx = empty_rows.idxmax()
            pos = df_temp.index.get_loc(first_empty_idx)
            df = df.iloc[:pos].reset_index(drop=True)
            log_mensaje(f"✓ Filas truncadas: {pos} filas procesadas")
        else:
            log_mensaje("✓ No se encontraron filas vacías para truncar")

        # Limpiar GAP y SAE
        log_mensaje("→ Limpiando columnas GAP y SAE...")
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
                # volver a numérico
                df[col_name] = pd.to_numeric(df[col_name], errors="coerce")
        log_mensaje("✓ Columnas GAP y SAE limpiadas y convertidas a numérico")

        # Columnas a extraer (base 1 → base 0)
        columnas_a_extraer = [
            1,
            2,
            4,
            6,
            16,
            20,
            32,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            29,
            30,
            13,
            14,
        ]

        log_mensaje(
            "\n───────────────────────────────────────────────────────────────────────"
        )
        log_mensaje("📊 PASO 2: EXTRACCIÓN DE COLUMNAS")
        log_mensaje(
            "───────────────────────────────────────────────────────────────────────"
        )
        log_mensaje("→ Extrayendo columnas específicas...")
        log_mensaje(f"  Columnas seleccionadas (índices 0-based): {columnas_a_extraer}")
        log_mensaje("  Correspondencia:")
        log_mensaje("    Col 1 → FECHA")
        log_mensaje("    Col 2 → HORA")
        log_mensaje("    Col 4 → JEFE SE SERVICIO")
        log_mensaje("    Col 6 → OFICIAL")
        log_mensaje("    Col 16 → TIPIFICACION")
        log_mensaje("    Col 20 → BARRIO")
        log_mensaje("    Col 32 → ORIGEN")
        log_mensaje("    Col 29 → CONTRAVENTOR")
        log_mensaje("    Col 30 → DETENIDO")
        log_mensaje("    Col 13 → GAP")
        log_mensaje("    Col 14 → SAE")

        columnas_seleccionadas = []
        nombres_columnas = []
        for valor in columnas_a_extraer:
            if isinstance(valor, int):
                pos = valor - 1
                if pos < 0 or pos >= len(df.columns):
                    return (
                        False,
                        (
                            f"El archivo no tiene suficientes columnas.\n"
                            f"Se esperaban al menos {pos + 1}"
                        ),
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
            log_mensaje("✓ Columna 'TIPIFICACION' renombrada a 'TIPO DE EVENTO'")

        log_mensaje("✓ Extracción completada")
        log_mensaje(f"  Filas extraídas: {len(df_eventos)}")

        ruta_dir = Path(ruta_archivo).parent
        log_mensaje(f"  Carpeta de salida: {ruta_dir}")

        log_mensaje(
            "\n───────────────────────────────────────────────────────────────────────"
        )
        log_mensaje("📊 PASO 3: PROCESAMIENTO ESPECIALIZADO")
        log_mensaje(
            "───────────────────────────────────────────────────────────────────────"
        )
        # Intentar generar resumen de colaboracion con intervencion propia
        df_colaboracion = None
        colab_error = None
        try:
            iproc = ColaboracionPropiaProcessor()
            log_mensaje("→ Procesando: Eventos Colaboracion con Intervencion Propia")
            df_colaboracion = iproc.process_df(df)
            log_mensaje("✓ Procesado exitosamente")
            log_mensaje(f"  Eventos encontrados: {len(df_colaboracion)}")
        except Exception as e:
            df_colaboracion = None
            colab_error = str(e)
            log_mensaje(f"✗ Error: {colab_error}")

        # Intentar generar resumen de contraventores/detenidos
        df_contra_det = None
        contra_det_error = None
        try:
            proc = ContraventoresDetenidosProcessor()
            log_mensaje("→ Procesando: Eventos con CONTRAVENTORES y DETENIDOS")
            df_contra_det = proc.process_df(df)
            log_mensaje("✓ Procesado exitosamente")
            log_mensaje(f"  Eventos encontrados: {len(df_contra_det)}")
        except Exception as e:
            df_contra_det = None
            contra_det_error = str(e)
            log_mensaje(f"✗ Error: {contra_det_error}")

        # Intentar generar resumen de integrados/destacados
        df_integrados = None
        integ_error = None
        try:
            iproc = IntegradosProcessor()
            log_mensaje("→ Procesando: Eventos INTEGRADOS y DESTACADOS")
            df_integrados = iproc.process_df(df)
            log_mensaje("✓ Procesado exitosamente")
            log_mensaje(f"  Eventos encontrados: {len(df_integrados)}")
        except Exception as e:
            df_integrados = None
            integ_error = str(e)
            log_mensaje(f"✗ Error: {integ_error}")

        log_mensaje(
            "\n───────────────────────────────────────────────────────────────────────"
        )
        log_mensaje("📊 PASO 4: CREACIÓN DE ARCHIVO UNIFICADO")
        log_mensaje(
            "───────────────────────────────────────────────────────────────────────"
        )

        # Crear un único archivo unificado
        ruta_unificado = ruta_dir / "eventos_unificados.xlsx"
        try:
            parts = [df_eventos]
            log_mensaje("→ Combinando todos los datos procesados...")

            if df_colaboracion is not None:
                parts.append(df_colaboracion)
                log_mensaje(
                    f"  ✓ Añadidos {len(df_colaboracion)} eventos de colaboracion con intervencion propia"
                )

            if df_contra_det is not None:
                parts.append(df_contra_det)
                log_mensaje(
                    f"  ✓ Añadidos {len(df_contra_det)} eventos de contraventores/detenidos"
                )

            if df_integrados is not None:
                parts.append(df_integrados)
                log_mensaje(
                    f"  ✓ Añadidos {len(df_integrados)} eventos integrados/destacados"
                )

            # Concatenar verticalmente
            df_combined = pd.concat(parts, ignore_index=True, sort=False)
            log_mensaje("✓ Datos combinados exitosamente")
            log_mensaje(f"  Total de filas en archivo unificado: {len(df_combined)}")

            with pd.ExcelWriter(ruta_unificado, engine="openpyxl") as writer:
                df_combined.to_excel(writer, sheet_name="eventos", index=False)

            log_mensaje(
                "\n═══════════════════════════════════════════════════════════════════════"
            )
            log_mensaje("✅ PROCESO COMPLETADO EXITOSAMENTE")
            log_mensaje(
                "═══════════════════════════════════════════════════════════════════════"
            )
            log_mensaje(f"📁 ARCHIVO GENERADO: {ruta_unificado.name}")
            log_mensaje(f"📂 UBICACIÓN: {ruta_dir}")
            log_mensaje(f"📊 TOTAL REGISTROS: {len(df_combined)}")
            log_mensaje(
                "═══════════════════════════════════════════════════════════════════════"
            )

            msg = "✅ Proceso completado exitosamente\n\n"
            msg += f"📁 Archivo generado:\n{ruta_unificado}\n\n"
            msg += "📊 Resumen:\n"
            msg += f"  • Eventos principales: {len(df_eventos)}\n"

            if df_colaboracion is not None:
                msg += f"  • Colaboracion con intervencion propia: {len(df_colaboracion)}\n"

            if df_contra_det is not None:
                msg += f"  • Contraventores/Detenidos: {len(df_contra_det)}\n"
            else:
                msg += "  • Contraventores/Detenidos: No procesado\n"

            if df_integrados is not None:
                msg += f"  • Integrados/Destacados: {len(df_integrados)}\n"
            else:
                msg += "  • Integrados/Destacados: No procesado\n"

            msg += f"  • Total general: {len(df_combined)}\n\n"
            msg += f"📂 Ubicación: {ruta_dir}"

            # Devolver también la ruta del archivo unificado para uso posterior
            return True, msg, str(ruta_unificado)

        except Exception as e:
            log_mensaje(
                "\n═══════════════════════════════════════════════════════════════════════"
            )
            log_mensaje("✗ ERROR AL GENERAR ARCHIVO UNIFICADO")
            log_mensaje(
                "═══════════════════════════════════════════════════════════════════════"
            )
            log_mensaje(f"Error: {str(e)}")
            return False, f"Error al generar archivo unificado:\n{e}", None

    except Exception as e:
        log_mensaje(
            "\n═══════════════════════════════════════════════════════════════════════"
        )
        log_mensaje("✗ ERROR CRÍTICO EN EL PROCESO")
        log_mensaje(
            "═══════════════════════════════════════════════════════════════════════"
        )
        log_mensaje(f"Error: {str(e)}")
        return False, f"Error al procesar:\n{str(e)}", None


# Seleccionar archivo y procesar
def seleccionar_archivo():
    archivo = filedialog.askopenfilename(
        title="Seleccionar archivo Excel",
        filetypes=[("Archivos Excel", "*.xlsx *.xls")],
    )

    if not archivo:
        estado_var.set("Selección cancelada")
        log_mensaje("✗ Selección de archivo cancelada por el usuario")
        return

    archivo_var.set(Path(archivo).name)
    estado_var.set("🔄 Procesando... Por favor espere")
    root.update_idletasks()

    ok = procesar_excel(archivo)

    estado_var.set("✅ Proceso finalizado" if ok else "✗ Error en el proceso")


# ================== UI ==================

root = tk.Tk()
root.title("Procesador de Eventos Excel")
root.geometry("960x700")
root.resizable(True, True)

archivo_var = tk.StringVar(value="📂 Ningún archivo seleccionado")
estado_var = tk.StringVar(value="🟢 Listo para procesar")

frame = ttk.Frame(root, padding=20)
frame.pack(fill="both", expand=True)

# Título principal
ttk.Label(
    frame,
    text="⚙️ Procesador de Eventos Excel",
    font=("Segoe UI", 18, "bold"),
    foreground="#2c3e50",
).pack(pady=(0, 15))

# Frame de información del archivo
info_frame = ttk.LabelFrame(frame, text="📋 Información del archivo", padding=10)
info_frame.pack(fill="x", pady=(0, 15))

ttk.Label(
    info_frame, textvariable=archivo_var, font=("Segoe UI", 10), foreground="#34495e"
).pack()

# Botón de selección
style = ttk.Style()
style.configure("Accent.TButton", font=("Segoe UI", 11), padding=10)

ttk.Button(
    frame,
    text="📁 Seleccionar archivo Excel",
    command=seleccionar_archivo,
    style="Accent.TButton",
    width=30,
).pack(pady=(0, 15))

# Estado actual
status_frame = ttk.LabelFrame(frame, text="🔄 Estado del proceso", padding=10)
status_frame.pack(fill="x", pady=(0, 15))

ttk.Label(
    status_frame,
    textvariable=estado_var,
    font=("Segoe UI", 11, "bold"),
    foreground="#27ae60",
    wraplength=800,
).pack()

# Separador
ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=15)

# Información de columnas
info_label = ttk.Label(
    frame,
    text="📊 Columnas a procesar:\n"
    "  • Col 1: FECHA\n"
    "  • Col 2: HORA\n"
    "  • Col 7: OPERADOR\n"
    "  • Col 16: TIPIFICACION\n"
    "  • Col 20: BARRIO\n"
    "  • Col 32: ORIGEN\n"
    "  • Col 13: GAP\n"
    "  • Col 14: SAE",
    font=("Segoe UI", 10),
    foreground="#7f8c8d",
    justify="left",
)
info_label.pack()

# Botón de cerrar
ttk.Button(frame, text="❌ Cerrar aplicación", command=root.destroy, width=25).pack(
    side="right", pady=(20, 0)
)

# Frame log (área de texto)
frame_log = ttk.LabelFrame(root, text="📝 Registro de proceso", padding=10)
frame_log.pack(fill="both", expand=True, padx=10, pady=(0, 10))

ventana_log = scrolledtext.ScrolledText(
    frame_log,
    height=20,
    font=("Consolas", 10),
    wrap=tk.WORD,
    bg="#1e1e1e",
    fg="#d4d4d4",
    insertbackground="#ffffff",
)

ventana_log.pack(fill="both", expand=True)
ventana_log.config(state=tk.DISABLED)

# Mensaje inicial
log_mensaje("=" * 70)
log_mensaje("⚙️ SISTEMA DE PROCESAMIENTO DE EVENTOS EXCEL")
log_mensaje("=" * 70)
log_mensaje("")
log_mensaje("🟢 Sistema listo y en espera...")
log_mensaje("")
log_mensaje("📌 Instrucciones:")
log_mensaje("   1. Haga clic en 'Seleccionar archivo Excel'")
log_mensaje("   2. Elija el archivo maestro (CMU) a procesar")
log_mensaje("   3. Espere a que se complete el proceso")
log_mensaje("")
log_mensaje("📁 Los archivos se guardarán en la misma carpeta del archivo seleccionado")
log_mensaje("=" * 70)

root.mainloop()
