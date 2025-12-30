import pandas as pd
import re
import unicodedata
from tkinter import filedialog, messagebox
import tkinter as tk
import traceback

ruta = ''

def seleccionar_archivos():
    """Seleccionar archivo excel de presentismo"""
    try:
        global ruta
        archivos = filedialog.askopenfilenames(
            title="Seleccionar archivos XLSX",
            filetypes=[("Archivos EXCEL", "*.XLSX")]
        )
        
        print(f"Archivo seleccionado: {archivos}")
    except Exception as e:
        print(f"Error en selección de archivos: {e}")
        traceback.print_exc()
        messagebox.showerror("Error", f"Error al seleccionar archivos: {str(e)}")

# ====== CONFIG ======3
try:
    dias = int(input("dias : "))
except (ValueError, TypeError):
    # si la entrada no es un entero válido, usar 30 por defecto
    dias = 30

if dias != 30:
    d = 35
else:
    d = 34
    
archivo_origen = ruta
output = "filtrado_presentismo_grupos.xlsx"
salida = "presentismo_resumen.xlsx"

# Procesar estas hojas → excluye 6 y 7
hojas_a_procesar = [0, 1, 2, 3, 4, 5, 8]

# Todas las hojas deben quedar exactamente con estas 42 columnas
COLUMNAS_MIN = 42

# =========================================
# UTILIDADES
# =========================================

def normalizar_texto(s):
    if pd.isna(s):
        return ""
    s = str(s)
    s = unicodedata.normalize('NFKD', s)
    s = s.encode('ascii', errors='ignore').decode('utf-8')
    return s.strip().lower()


def map_zona_text(v):
    if pd.isna(v):
        return ""
    s = normalizar_texto(v)

    if s == "":
        return ""

    if s in ('lxuc', 'lxm', 'lxp', 'fac', 'lxf', 'art'):
        return 'LM'

    if s in ('san', 'a'):
        return 'AUS'

    return str(v).strip().upper()


def normalizar_grupo(g_raw):
    """
    Extrae GRUPO I / II / III desde textos complejos:
    Ej:
        "GRUPO I A TM 06-14"
        "grupo iii 'b' tarde"
        "g1"
        "g 2"
        "grupo 3 b"
    """

    if not isinstance(g_raw, str):
        return "GRUPO DESCONOCIDO"

    g = normalizar_texto(g_raw)

    # romano
    m = re.search(r'\b(i{1,3})\b', g)
    if m:
        roman = m.group(1)
        if roman == "i": return "GRUPO I"
        if roman == "ii": return "GRUPO II"
        if roman == "iii": return "GRUPO III"

    # arábigo
    m = re.search(r'\b([1-3])\b', g)
    if m:
        num = m.group(1)
        if num == "1": 
            return "GRUPO I"
        if num == "2": 
            return "GRUPO II"
        if num == "3":
            return "GRUPO III"

    return "GRUPO DESCONOCIDO"


# Regex grupo mejorada
patron_grupo = re.compile(
    r'grupo\s*(?:i{1,3}|[1-3])\b|g\s*[1-3]\b',
    re.IGNORECASE
)

# Regex ADM mejorada (incluye lunes/martes/miércoles/jueves/viernes/sábado/domingo)
patron_adm = re.compile(
    r'\b('
    r'lun(\.|es)?|mar(\.|tes)?|mie(\.|rcoles)?|jue(\.|ves)?|'
    r'vier(\.|nes)?|sab(\.|ado|ados)?|dom(\.|ingo)?|'
    r'feriad(o|os)?'
    r')(\s*\d{1,2})?\b',
    re.IGNORECASE
)

# =========================================
# PROCESAMIENTO
# =========================================

xls = pd.ExcelFile(archivo_origen)
df_total = pd.DataFrame()

for i in hojas_a_procesar:
    
    nombre_hoja = xls.sheet_names[i]
    print(f"\nProcesando hoja: {nombre_hoja}")

    df = pd.read_excel(archivo_origen, sheet_name=nombre_hoja)

    # ----- insertar columna dummy para igualar estructura -----
    if i != 0:
        df.insert(3, "col_extra_P", "ext.")

    # ----- Normalizar a 42 columnas -----
    if df.shape[1] < COLUMNAS_MIN:
        faltan = COLUMNAS_MIN - df.shape[1]
        for k in range(faltan):
            df[f"extra_{k}"] = "P"

    if df.shape[1] > COLUMNAS_MIN:
        df = df.iloc[:, :COLUMNAS_MIN]

    df.columns = list(range(COLUMNAS_MIN))
    print(f"Normalizada a {COLUMNAS_MIN} columnas.")

    # ----- borrar columnas fijas -----
    columnas_a_borrar = [3,4,5] + list(range(37,42))
    df = df.drop(columns=columnas_a_borrar, errors="ignore")

    # ----- detectar grupo y ADM -----
    filas_a_agregar = []
    grupo_actual = None
    modo_adm = False

    for idx, fila in df.iterrows():

        txt = normalizar_texto(fila.iloc[0])

        # ADM
        if patron_adm.search(txt):
            modo_adm = True
            continue

        # GRUPO
        m = patron_grupo.search(txt)
        if m:
            grupo_actual = normalizar_grupo(m.group(0))
            modo_adm = False
            continue

        # Filas válidas (nivel o contratado)
        if "nivel" in txt or "contratado" in txt:

            etiqueta = str(nombre_hoja) + (" ADM" if modo_adm else "")
            etiqueta_final = f"{etiqueta} - {grupo_actual or 'GRUPO DESCONOCIDO'}"

            nueva_fila = fila.copy()
            nueva_fila["HOJA_ORIGEN"] = etiqueta_final

            filas_a_agregar.append(nueva_fila)

    # ---- si hay filas válidas, armar DataFrame filtrado ----
    if filas_a_agregar:

        df_filtrado = pd.DataFrame(filas_a_agregar)

        # HOJA_ORIGEN primero
        cols = ["HOJA_ORIGEN"] + [c for c in df_filtrado.columns if c != "HOJA_ORIGEN"]
        df_filtrado = df_filtrado[cols]

        # ----- aplicar mapeo LM / AUS solo aquí -----
        cols_a_mapear = list(range(4, 37))
        for c in cols_a_mapear:
            if c in df_filtrado.columns:
                df_filtrado[c] = df_filtrado[c].apply(map_zona_text)

        # ----- contar LM / LLT / AUS -----
        zona = df_filtrado.iloc[:, 4:d].astype(str).apply(lambda x: x.str.upper().str.strip())

        df_filtrado["-LM-"]  = zona.apply(lambda r: r.eq("LM").sum(), axis=1)
        df_filtrado["-LLT-"] = zona.apply(lambda r: r.eq("LLT").sum(), axis=1)
        df_filtrado["-AUS-"] = zona.apply(lambda r: r.eq("AUS").sum(), axis=1)

        # Acumular
        df_total = pd.concat([df_total, df_filtrado], ignore_index=True)

df_final = df_total.reindex([2, 1, 0, 'HOJA_ORIGEN',"-LM-", "-LLT-", "-AUS-"], axis=1)

df_final.rename(columns={0: 'JERARQUIA', 1: 'NOMBRE', 2: 'LP/DNI', 'HOJA_ORIGEN': 'TURNO & GRUPO'}, inplace=True)
# =========================================
# EXPORTAR
# =========================================
df_total.to_excel(output, index=False)
df_final.to_excel(salida, index=False)
print("\nEXPORTADO:", output)

# Crear ventana principal
root = tk.Tk()
root.title("Analizar y resumir PRESENTISMO-")
root.config(bg="#217382")
root.geometry("840x400")

frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

ventana_pegado = tk.Label(
    frame,
    text="Haz clic en 'Seleccionar Archivos' para comenzar",
    bg="#0D5B8C",
    font=("Helvetica", 14),
    relief="sunken",
    fg="white",
    height=6
)
ventana_pegado.pack(fill=tk.BOTH, expand=True)

# Botones
boton_seleccionar = tk.Button(frame, text="Seleccionar Archivos", width=20, height=2, command=seleccionar_archivos)
boton_seleccionar.config(background="#33AAFF", fg="white", activeforeground="blue")
boton_seleccionar.pack(side=tk.TOP, pady=5)

boton_ejecutar = tk.Button(frame, text="Ejecutar", width=20, height=2, command=extraer_convertir)
boton_ejecutar.config(background="#33FF41", fg="darkblue", activeforeground="green")
boton_ejecutar.pack(side=tk.LEFT)

boton_cerrar = tk.Button(frame, text="Cerrar", width=20, height=2, command=root.quit)
boton_cerrar.config(background="#FF3333", fg="darkblue", activeforeground="red")
boton_cerrar.pack(side=tk.RIGHT)

if __name__ == "__main__":
    root.mainloop()