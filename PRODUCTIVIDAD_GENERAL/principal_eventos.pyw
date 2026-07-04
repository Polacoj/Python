"""
NOMBRE DE SCRIPT: PRODUCTIVIDAD GENERAL
DESCRIPCION DEL SCRIPT: Procesa datos para scoring de operadores
VERSION: 2.5.2
AUTOR: JANKOWICZ ALEXIS
FECHA: 2026-05-23

HISTORIAL DE CAMBIOS:
---------------------
[2026-05-23] v2.5.2: Eliminacion de separador entre archivos unificados en narracion, IA corrige
                        error en linea 618 (El tamaño de la tuple no coincide; se esperaba 3 pero se recibió 2PylancereportAssignmentType), eliminacion de acentos en los encabezados, Agregue barrio "ADICIONAL".
[2026-01-28] v2.5.1: Mejora general y unificacion de narracion en solo un archivo general.
[2026-01-25] v2.4.1: Corregido error en formula.
[2026-01-23] v2.4.0: Se agrega manejo de logs.
[2026-01-20] v2.3.0: Cambios visuales y optimizacion.
[2026-01-20] v2.2.0: Reversion hacia objetos.
[2026-01-12] v1.2.0: Agregada exportación a formato Excel.
[2026-01-10] v1.1.0: Optimización carga de datos.
[2026-01-05] v1.0.0: Versión inicial modelo prueba.
"""

import pandas as pd
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog, scrolledtext
from typing import Optional
from complementos.contraventores_detenidos import ContraventoresProcessor
from complementos.integrados import IntegradosProcessor
from complementos.colaboradores import ColaboradoresProcessor
from pathlib import Path as _Path
import time

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


def agregar_narracion_a_unificado(ruta_unificado: str, df_narracion: pd.DataFrame):
    """Agrega los datos de narración al archivo unificado existente."""
    try:
        # Leer el archivo unificado existente
        df_existente = pd.read_excel(ruta_unificado, engine="openpyxl")

        # Combinar: existente + separador + narración
        df_combinado = pd.concat([df_existente, df_narracion], ignore_index=True)

        # Guardar de vuelta
        with pd.ExcelWriter(ruta_unificado, engine="openpyxl") as writer:
            df_combinado.to_excel(writer, sheet_name="eventos", index=False)

        return True, f"Narración agregada exitosamente a {ruta_unificado}"
    except Exception as e:
        return False, f"Error al agregar narración: {str(e)}"


# procesa control diario x hojas para extraer y comparar narracion
def procesar_narracion_file(
    ruta_archivo_narracion: str,
    mes_cmu: Optional[str] = None,
    ruta_unificado: Optional[str] = None,
):
    """Procesa un archivo de narración: pide hoja, extrae columnas, compara con CMU."""
    try:
        log_mensaje(
            "\n═══════════════════════════════════════════════════════════════════════"
        )
        log_mensaje("📋 PROCESANDO ARCHIVO DE NARRACIÓN")
        log_mensaje(
            "═══════════════════════════════════════════════════════════════════════"
        )
        log_mensaje(f"Archivo: {Path(ruta_archivo_narracion).name}")

        xls = pd.ExcelFile(ruta_archivo_narracion, engine="openpyxl")
        hojas = xls.sheet_names
        log_mensaje("✓ Archivo abierto exitosamente")
        log_mensaje(f"  Hojas disponibles: {len(hojas)}")
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

    log_mensaje(f"✓ Hoja seleccionada: {hoja_idx} - {hojas[hoja_idx]}")

    try:
        df_n = pd.read_excel(
            ruta_archivo_narracion, sheet_name=hoja_idx, engine="openpyxl"
        )
        log_mensaje("✓ Hoja leída exitosamente")
        log_mensaje(f"  Dimensiones: {df_n.shape[0]} filas × {df_n.shape[1]} columnas")
    except Exception as e:
        return False, f"No se pudo leer la hoja seleccionada: {e}"

    # Limpiar GAP y SAE
    log_mensaje("→ Limpiando columnas GAP y SAE...")
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
    log_mensaje("✓ Columnas GAP/SAE limpiadas")

    # Columnas a extraer (posiciones 2,3,4 en base 0)
    columnas_a_extraer = [2, 3, 4]
    max_idx = max(columnas_a_extraer)
    if df_n.shape[1] <= max_idx:
        return (
            False,
            f"La hoja no tiene las columnas requeridas (necesita al menos {max_idx + 1}).",
        )

    # 1. Condición: Columna 5 sea "si" (limpiando espacios y minúsculas)
    condicion_si = (
        df_n.iloc[:, 5].fillna("").astype(str).str.strip().str.lower() == "si"
    )

    # 2. Condición: Columna 2 NO esté vacía
    condicion_no_vacia = df_n.iloc[:, 2].fillna("").astype(str).str.strip() != ""

    # Combinar ambas condiciones con & (operador AND)
    mask = condicion_si & condicion_no_vacia

    # Contar filas que cumplen condiciones
    filas_cumplen = mask.sum()
    log_mensaje("→ Aplicando filtros...")
    log_mensaje(f"  Filas que cumplen condiciones: {filas_cumplen} de {len(df_n)}")

    # Extraer los datos aplicando la máscara combinada
    df_eventos = (
        df_n.loc[mask].iloc[:, columnas_a_extraer].copy().reset_index(drop=True)
    )

    df_eventos.columns = ["OPERADOR", "GAP", "SAE"]
    log_mensaje("✓ Columnas extraídas: OPERADOR, GAP, SAE")

    # Convertir SAE a numérico, manejando errores
    log_mensaje("→ Convirtiendo SAE a numérico...")
    df_eventos["SAE"] = pd.to_numeric(df_eventos["SAE"], errors="coerce")

    # Eliminar filas donde SAE es NaN (no pudo convertirse a número)
    filas_antes = len(df_eventos)
    df_eventos = df_eventos.dropna(subset=["SAE"])
    filas_eliminadas = filas_antes - len(df_eventos)
    if filas_eliminadas > 0:
        log_mensaje(f"  Eliminadas {filas_eliminadas} filas con SAE inválido")

    # Convertir a int64
    df_eventos["SAE"] = df_eventos["SAE"].astype("Int64")
    log_mensaje("✓ SAE convertido a formato numérico")
    log_mensaje(f"  Filas restantes: {len(df_eventos)}")

    # Abrir CMU y comparar
    try:
        cmu_dir = _Path(__file__).parent / "DATOS"
        cmu_path = None
        if mes_cmu:
            candidate = cmu_dir / f"CMU - {mes_cmu.upper()}.xlsx"
            if candidate.exists():
                cmu_path = candidate
                log_mensaje(f"→ Buscando archivo CMU del mes: {mes_cmu.upper()}")
                log_mensaje(f"  Encontrado: {candidate.name}")

        if cmu_path is None:
            # buscar cualquier CMU disponible como fallback
            log_mensaje("→ Buscando cualquier archivo CMU disponible...")
            matches = list(cmu_dir.glob("CMU - *.xlsx"))
            if matches:
                cmu_path = matches[0]
                log_mensaje(f"  Usando: {cmu_path.name}")
            else:
                raise FileNotFoundError(f"No se encontró archivo CMU en {cmu_dir}")

        maestro = pd.read_excel(cmu_path, engine="openpyxl")
        log_mensaje("✓ Archivo CMU cargado exitosamente")
        log_mensaje(
            f"  Dimensiones: {maestro.shape[0]} filas * {maestro.shape[1]} columnas"
        )
    except Exception as e:
        return False, f"No se pudo abrir CMU: {e}"

    if maestro.shape[1] < 33:
        return (
            False,
            f"El archivo CMU no tiene suficientes columnas ({maestro.shape[1]}).",
        )

    col_sae_cmu = maestro.columns[13]
    col_origen = maestro.columns[31]
    log_mensaje("→ Identificando columnas en CMU...")
    log_mensaje(f"  Columna SAE: {col_sae_cmu}")
    log_mensaje(f"  Columna Origen: {col_origen}")

    # Convertir SAE en maestro a numérico también
    log_mensaje("→ Preparando SAE del CMU para merge...")
    maestro["SAE"] = pd.to_numeric(maestro[col_sae_cmu], errors="coerce")
    filas_antes_cmu = len(maestro)
    maestro = maestro.dropna(subset=["SAE"])
    filas_eliminadas_cmu = filas_antes_cmu - len(maestro)
    if filas_eliminadas_cmu > 0:
        log_mensaje(
            f"  Eliminadas {filas_eliminadas_cmu} filas con SAE inválido en CMU"
        )

    maestro["SAE"] = maestro["SAE"].astype("Int64")

    # Deduplicate maestro
    if maestro["SAE"].duplicated().any():
        duplicados = maestro["SAE"].duplicated().sum()
        maestro = maestro.drop_duplicates(subset=["SAE"], keep="first")
        log_mensaje(f"  Eliminados {duplicados} duplicados de SAE en CMU")

    # Ahora el merge funcionará porque ambos son Int64
    log_mensaje("→ Realizando merge entre narración y CMU...")
    try:
        resultado = df_eventos.merge(
            maestro[["SAE", col_origen]], on="SAE", how="inner", validate="m:1"
        )
    except Exception:
        resultado = df_eventos.merge(
            maestro[["SAE", col_origen]], on="SAE", how="inner"
        )

    log_mensaje("✓ Merge completado")
    log_mensaje(f"  Coincidencias encontradas: {len(resultado)} de {len(df_eventos)}")

    if resultado.empty:
        return False, "No se encontraron coincidencias entre SAE(narracion) y SAE(CMU)."

    resultado = resultado.rename(columns={col_origen: "ORIGEN"})
    # Agregar columnas faltantes para mantener estructura consistente
    resultado["FECHA"] = ""
    resultado["HORA"] = ""
    resultado["TIPO DE EVENTO"] = "NARRACION COMPLETA DE EVENTO"
    resultado["BARRIO"] = "ADICIONAL"
    resultado["GAP"] = resultado["GAP"].astype(
        str
    )  # Mantener como string si es necesario

    # Reordenar columnas para que coincidan con el formato del archivo unificado
    column_order = [
        "FECHA",
        "HORA",
        "OPERADOR",
        "TIPO DE EVENTO",
        "BARRIO",
        "ORIGEN",
        "GAP",
        "SAE",
    ]
    resultado = resultado[column_order]

    log_mensaje("✓ Estructura de datos preparada")
    log_mensaje(f"  Columnas: {', '.join(resultado.columns)}")

    # Si tenemos ruta de archivo unificado, agregar directamente
    if ruta_unificado and Path(ruta_unificado).exists():
        log_mensaje("→ Agregando narración al archivo unificado existente...")
        ok, msg = agregar_narracion_a_unificado(ruta_unificado, resultado)
        if ok:
            log_mensaje(
                "═══════════════════════════════════════════════════════════════════════"
            )
            log_mensaje("✅ NARRACIÓN PROCESADA Y AGREGADA AL ARCHIVO UNIFICADO")
            log_mensaje(
                "═══════════════════════════════════════════════════════════════════════"
            )
            return True, msg
        else:
            return False, msg
    else:
        # Guardar individualmente si no hay unificado
        salida = _Path(ruta_archivo_narracion).parent / "narracion_origen.xlsx"
        resultado.to_excel(salida, index=False)
        log_mensaje(
            "═══════════════════════════════════════════════════════════════════════"
        )
        log_mensaje("✅ ARCHIVO DE NARRACIÓN GENERADO")
        log_mensaje(
            "═══════════════════════════════════════════════════════════════════════"
        )
        return True, f"Archivo generado: {salida}"


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
        columnas_a_extraer = [1, 2, 7, 16, 20, 32, 13, 14]
        columnas_a_extraer = [i - 1 for i in columnas_a_extraer]

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
        log_mensaje("    Col 7 → OPERADOR")
        log_mensaje("    Col 16 → TIPIFICACION")
        log_mensaje("    Col 20 → BARRIO")
        log_mensaje("    Col 32 → ORIGEN")
        log_mensaje("    Col 13 → GAP")
        log_mensaje("    Col 14 → SAE")

        if len(df.columns) < max(columnas_a_extraer) + 1:
            return (
                False,
                (
                    f"El archivo no tiene suficientes columnas.\n"
                    f"Se esperaban al menos {max(columnas_a_extraer) + 1}"
                ),
                None,
            )

        df_eventos = df.iloc[:, columnas_a_extraer].copy()

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

        # Intentar generar resumen de contraventores/detenidos
        df_contra = None
        contra_error = None
        try:
            proc = ContraventoresProcessor()
            log_mensaje("→ Procesando: Eventos con CONTRAVENTORES y DETENIDOS")
            df_contra = proc.process_df(df)
            log_mensaje("✓ Procesado exitosamente")
            log_mensaje(f"  Eventos encontrados: {len(df_contra)}")
        except Exception as e:
            df_contra = None
            contra_error = str(e)
            log_mensaje(f"✗ Error: {contra_error}")

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

        # Intentar generar resumen de colaboradores
        df_colab = None
        colab_error = None
        try:
            cproc = ColaboradoresProcessor()
            log_mensaje("→ Procesando: Eventos con COLABORADORES")
            df_colab = cproc.process_df(df)
            log_mensaje("✓ Procesado exitosamente")
            log_mensaje(f"  Eventos encontrados: {len(df_colab)}")
        except Exception as e:
            df_colab = None
            colab_error = str(e)
            log_mensaje(f"✗ Error: {colab_error}")

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

            if df_contra is not None:
                parts.append(df_contra)
                log_mensaje(
                    f"  ✓ Añadidos {len(df_contra)} eventos de contraventores/detenidos"
                )

            if df_integrados is not None:
                parts.append(df_integrados)
                log_mensaje(
                    f"  ✓ Añadidos {len(df_integrados)} eventos integrados/destacados"
                )

            if df_colab is not None:
                parts.append(df_colab)
                log_mensaje(f"  ✓ Añadidos {len(df_colab)} eventos con colaboradores")

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

            if df_contra is not None:
                msg += f"  • Contraventores/Detenidos: {len(df_contra)}\n"
            else:
                msg += "  • Contraventores/Detenidos: No procesado\n"

            if df_integrados is not None:
                msg += f"  • Integrados/Destacados: {len(df_integrados)}\n"
            else:
                msg += "  • Integrados/Destacados: No procesado\n"

            if df_colab is not None:
                msg += f"  • Colaboradores: {len(df_colab)}\n"
            else:
                msg += "  • Colaboradores: No procesado\n"

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
        log_mensaje("✗ Selección de archivo cancelada por el usuario")
        return

    archivo_var.set(Path(archivo).name)
    estado_var.set("🔄 Procesando... Por favor espere")
    root.update_idletasks()

    ok, mensaje, ruta_unificado = procesar_excel(archivo)

    estado_var.set("✅ Proceso finalizado" if ok else "✗ Error en el proceso")

    if ok:
        messagebox.showinfo("✅ Proceso finalizado", mensaje)

        # Después del procesamiento principal, preguntar al usuario si desea procesar narración
        sel = messagebox.askyesno(
            "Procesar narración",
            "¿Desea procesar un archivo de Control Diario (Narración) ahora?\n\n"
            "Los datos de narración se agregarán directamente al archivo unificado.",
            icon="question",
        )

        if sel:
            ruta_narr = filedialog.askopenfilename(
                title="Seleccionar archivo de Control Diario (Narración)",
                filetypes=[("Archivos Excel", "*.xlsx *.xls")],
            )

            if ruta_narr:
                estado_var.set("🔄 Procesando narración...")
                root.update_idletasks()

                # Extraer mes del nombre del archivo original
                mes = _extraer_mes_de_nombre(Path(archivo).name)

                # Pasar la ruta del archivo unificado para agregar directamente
                ok_n, msg_n = procesar_narracion_file(ruta_narr, mes, ruta_unificado)

                estado_var.set(
                    "✅ Narración procesada" if ok_n else "✗ Error en narración"
                )

                if ok_n:
                    messagebox.showinfo(
                        "✅ Narración procesada",
                        f"{msg_n}\n\n"
                        f"Los datos de narración han sido agregados al archivo unificado:\n"
                        f"{ruta_unificado}",
                    )
                    log_mensaje(
                        "\n═══════════════════════════════════════════════════════════════════════"
                    )
                    log_mensaje("✅ NARRACIÓN AGREGADA AL ARCHIVO UNIFICADO")
                    log_mensaje(
                        "═══════════════════════════════════════════════════════════════════════"
                    )
                else:
                    messagebox.showerror("✗ Narración", msg_n)
                    log_mensaje(
                        "\n═══════════════════════════════════════════════════════════════════════"
                    )
                    log_mensaje("✗ ERROR EN PROCESAMIENTO DE NARRACIÓN")
                    log_mensaje(
                        "═══════════════════════════════════════════════════════════════════════"
                    )
    else:
        messagebox.showerror("✗ Error", mensaje)
        log_mensaje(
            "\n═══════════════════════════════════════════════════════════════════════"
        )
        log_mensaje("✗ PROCESO FINALIZADO CON ERRORES")
        log_mensaje(
            "═══════════════════════════════════════════════════════════════════════"
        )


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
log_mensaje("   4. Opcionalmente, procese un archivo de Control Diario (Narración)")
log_mensaje("")
log_mensaje("📁 Los archivos se guardarán en la misma carpeta del archivo seleccionado")
log_mensaje("=" * 70)

root.mainloop()
