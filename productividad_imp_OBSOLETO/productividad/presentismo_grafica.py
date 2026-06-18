import pandas as pd
import re
import unicodedata
from tkinter import filedialog, messagebox
import tkinter as tk
from tkinter import scrolledtext
import traceback

ruta = []
ventana_log = None

output = "filtrado_presentismo_grupos.xlsx"
salida = "presentismo_resumen.xlsx"
hojas_a_procesar = [0, 1, 2, 3, 4, 5, 8]
COLUMNAS_MIN = 42

# CONFIG: valores por defecto y lista de meses con 31 días
dias = 30
d = 34 if dias == 30 else 35
meses_31 = ["enero", "marzo", "mayo", "julio", "agosto", "octubre", "diciembre"]


# funccion para normalizar texto (eliminar acentos, pasar a minusculas, etc)
def normalizar_texto(s):
    if pd.isna(s):
        return ""
    s = str(s)
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", errors="ignore").decode("utf-8")
    return s.strip().lower()


def map_zona_text(v):
    if pd.isna(v):
        return ""
    s = normalizar_texto(v)
    if s == "":
        return ""
    if s in ("lxuc", "lxm", "lxp", "fac", "lxf", "art"):
        return "LM"
    if s in ("san", "a"):
        return "AUS"
    return str(v).strip().upper()


# funcion para normalizar el nombre del grupo
def normalizar_grupo(g_raw):
    if not isinstance(g_raw, str):
        return "GRUPO DESCONOCIDO"
    g = normalizar_texto(g_raw)
    m = re.search(r"\b(i{1,3})\b", g)
    if m:
        roman = m.group(1)
        if roman == "i":
            return "GRUPO I"
        if roman == "ii":
            return "GRUPO II"
        if roman == "iii":
            return "GRUPO III"
    m = re.search(r"\b([1-3])\b", g)
    if m:
        num = m.group(1)
        if num == "1":
            return "GRUPO I"
        if num == "2":
            return "GRUPO II"
        if num == "3":
            return "GRUPO III"
    return "GRUPO DESCONOCIDO"


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


# Regex para detectar grupos y días administrativos
patron_grupo = re.compile(r"grupo\s*(?:i{1,3}|[1-3])\b|g\s*[1-3]\b", re.IGNORECASE)
patron_adm = re.compile(
    r"\b(lun(\.|es)?|mar(\.|tes)?|mie(\.|rcoles)?|jue(\.|ves)?|"
    r"vier(\.|nes)?|sab(\.|ado|ados)?|dom(\.|ingo)?|feriad(o|os)?)(\s*\d{1,2})?\b",
    re.IGNORECASE,
)


# Funcion principal de procesamiento
def procesar_presentismo(archivo_origen):
    """Función principal de procesamiento"""
    try:
        log_mensaje("\n[INICIANDO PROCESO]")
        log_mensaje(f"Archivo: {archivo_origen}")

        xls = pd.ExcelFile(archivo_origen)
        df_total = pd.DataFrame()

        for i in hojas_a_procesar:
            nombre_hoja = xls.sheet_names[i]
            log_mensaje(f"\n→ Procesando hoja: {nombre_hoja}")

            df = pd.read_excel(archivo_origen, sheet_name=nombre_hoja)

            if i != 0:
                df.insert(3, "col_extra_P", "ext.")

            if df.shape[1] < COLUMNAS_MIN:
                faltan = COLUMNAS_MIN - df.shape[1]
                for k in range(faltan):
                    df[f"extra_{k}"] = "P"

            if df.shape[1] > COLUMNAS_MIN:
                df = df.iloc[:, :COLUMNAS_MIN]

            df.columns = list(range(COLUMNAS_MIN))
            columnas_a_borrar = [3, 4, 5] + list(range(37, 42))
            df = df.drop(columns=columnas_a_borrar, errors="ignore")

            filas_a_agregar = []
            grupo_actual = None
            modo_adm = False

            for idx, fila in df.iterrows():
                txt = normalizar_texto(fila.iloc[0])

                if patron_adm.search(txt):
                    modo_adm = True
                    continue

                m = patron_grupo.search(txt)
                if m:
                    grupo_actual = normalizar_grupo(m.group(0))
                    modo_adm = False
                    continue

                if "nivel" in txt or "contratado" in txt:
                    etiqueta = str(nombre_hoja) + (" ADM" if modo_adm else "")
                    etiqueta_final = (
                        f"{etiqueta} - {grupo_actual or 'GRUPO DESCONOCIDO'}"
                    )
                    nueva_fila = fila.copy()
                    nueva_fila["HOJA_ORIGEN"] = etiqueta_final
                    filas_a_agregar.append(nueva_fila)

            if filas_a_agregar:
                df_filtrado = pd.DataFrame(filas_a_agregar)
                cols = ["HOJA_ORIGEN"] + [
                    c for c in df_filtrado.columns if c != "HOJA_ORIGEN"
                ]
                df_filtrado = df_filtrado[cols]

                cols_a_mapear = list(range(4, 37))
                for c in cols_a_mapear:
                    if c in df_filtrado.columns:
                        df_filtrado[c] = df_filtrado[c].apply(map_zona_text)

                zona = (
                    df_filtrado.iloc[:, 4:d]
                    .astype(str)
                    .apply(lambda x: x.str.upper().str.strip())
                )
                df_filtrado["-LM-"] = zona.apply(lambda r: r.eq("LM").sum(), axis=1)
                df_filtrado["-LLT-"] = zona.apply(lambda r: r.eq("LLT").sum(), axis=1)
                df_filtrado["-AUS-"] = zona.apply(lambda r: r.eq("AUS").sum(), axis=1)
                df_filtrado["-LA-"] = zona.apply(lambda r: r.eq("LA").sum(), axis=1)

                df_total = pd.concat([df_total, df_filtrado], ignore_index=True)
                log_mensaje(f"  ✓ {len(filas_a_agregar)} filas procesadas")

        df_final = df_total.reindex(
            [2, 1, 0, "HOJA_ORIGEN", "-LM-", "-LLT-", "-AUS-", "-LA-"], axis=1
        )
        df_final.rename(
            columns={
                0: "JERARQUIA",
                1: "NOMBRE",
                2: "LP/DNI",
                "HOJA_ORIGEN": "TURNO & GRUPO",
            },
            inplace=True,
        )

        df_total.to_excel(output, index=False)
        df_final.to_excel(salida, index=False)

        log_mensaje(f"\n✅ EXPORTADO: {output}")
        log_mensaje(f"✅ EXPORTADO: {salida}")
        messagebox.showinfo("Éxito", f"Archivos generados:\n{output}\n{salida}")

    except Exception as e:
        log_mensaje(f"\n❌ ERROR: {str(e)}")
        traceback.print_exc()
        messagebox.showerror("Error", f"Error al procesar: {str(e)}")


# funciones de la interfaz gráfica
def seleccionar_archivos():
    """Seleccionar archivo excel de presentismo"""
    global ruta
    try:
        archivos = filedialog.askopenfilenames(
            title="Seleccionar archivos XLSX", filetypes=[("Archivos EXCEL", "*.XLSX")]
        )
        if archivos:
            ruta = archivos[0]  # Tomar el primer archivo
            log_mensaje(f"Archivo seleccionado: {ruta}")
            boton_ejecutar.config(state=tk.NORMAL)
    except Exception as e:
        log_mensaje(f"Error: {str(e)}")
        messagebox.showerror("Error", f"Error al seleccionar: {str(e)}")


def ejecutar_procesamiento():
    global dias, d
    if not ruta:
        messagebox.showwarning(
            "Advertencia", "Por favor, selecciona un archivo primero"
        )
        return

    nombre = str(ruta).lower()

    # Si el nombre de archivo contiene alguno de los meses con 31 días, ajusta 'd'
    if any(m in nombre for m in meses_31):
        dias = 31
        d = 35
    elif "febrero" in nombre:
        dias = 28
        d = 32
    else:
        dias = 30
        d = 34

    procesar_presentismo(ruta)


# Crear ventana principal
root = tk.Tk()
root.title("Analizar y resumir PRESENTISMO")
root.config(bg="#217382")
root.geometry("900x600")

# Frame superior (botones)
frame_botones = tk.Frame(root, bg="#217382")
frame_botones.pack(fill=tk.X, padx=10, pady=10)

boton_seleccionar = tk.Button(
    frame_botones,
    text="📁 Seleccionar Archivos",
    width=20,
    height=2,
    command=seleccionar_archivos,
    bg="#33AAFF",
    fg="white",
    font=("Helvetica", 10, "bold"),
)
boton_seleccionar.pack(side=tk.LEFT, padx=5)

boton_ejecutar = tk.Button(
    frame_botones,
    text="▶ Ejecutar",
    width=20,
    height=2,
    command=ejecutar_procesamiento,
    bg="#33FF41",
    fg="white",
    font=("Helvetica", 10, "bold"),
    state=tk.DISABLED,
)
boton_ejecutar.pack(side=tk.LEFT, padx=5)

boton_cerrar = tk.Button(
    frame_botones,
    text="❌ Cerrar",
    width=20,
    height=2,
    command=root.quit,
    bg="#FF3333",
    fg="white",
    font=("Helvetica", 10, "bold"),
)
boton_cerrar.pack(side=tk.RIGHT, padx=5)

# Frame log (área de texto)
frame_log = tk.Frame(root, bg="#0D5B8C")
frame_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

label_log = tk.Label(
    frame_log,
    text="ESTADO DE PROCESAMIENTO",
    bg="#0D5B8C",
    fg="white",
    font=("Helvetica", 10, "bold"),
)
label_log.pack(anchor=tk.W, pady=5)

ventana_log = scrolledtext.ScrolledText(
    frame_log,
    height=20,
    bg="#1a1a1a",
    fg="#00FF00",
    font=("Courier", 11),
    insertbackground="#00FF00",
    wrap=tk.WORD,
)

ventana_log.pack(fill=tk.BOTH, expand=True)
ventana_log.config(state=tk.DISABLED)

log_mensaje(
    "Sistema en espera...... \n\nSeleccione un archivo XLSX de PRESENTISMO para comenzar."
)

if __name__ == "__main__":
    root.mainloop()
