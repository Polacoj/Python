"""
cruzar_colaboradores.py
=======================
Cruza dos archivos Excel por la columna SAE e inserta
las columnas COLABORADOR 1..5 en el Archivo 1.

Archivo 1 (ej. archivo1.xlsx):
  - Encabezados en FILA 1
  - Columna SAE existe (se detecta automáticamente)

Archivo 2 (ej. archivo2.xlsx):
  - Encabezados en FILA 2
  - Columnas usadas: SAE  → clave de cruce
                     COLABORADO         → → COLABORADOR 1
                     COLABORADO RES 2   → → COLABORADOR 2
                     COLABO RADORE S 3  → → COLABORADOR 3
                     SAE (archivo2)     → → COLABORADOR 4
                     SISEP              → → COLABORADOR 5

Salida: archivo1_con_colaboradores.xlsx  (en la misma carpeta del script)

Dependencias:
    pip install pandas openpyxl
"""

import pandas as pd
from pathlib import Path

# ─────────────────────────────────────────────
# 1. CONFIGURACIÓN  ← Modificar solo estos valores
# ─────────────────────────────────────────────
print("----------------------------------\n----ANTES DE CARGAR LOS ARCHIVOS VERIFIQUE QUE LOS NOMBRES DE COLUMNAS COINCIDAN EXACTAMENTE ---\n----CON LOS DE LOS ARCHIVOS EXCEL (incluyendo espacios y acentos)---\n-------------------------------------------")
print("fecha -- operador -- gap -- sae -- origen -- tipificacion -- colaborador 1 -- colaborador 2 -- colaborador 3 -- colaborador 4 -- colaborador 5")


ARCHIVO_1 = input("archivo 1:")  # Ruta al primer archivo
ARCHIVO_2 = input("archivo 2:")  # Ruta al segundo archivo
SALIDA = "archivo1_con_colaboradores.xlsx"

# Nombres EXACTOS de las columnas en Archivo 2 (revisar con extract-text si hay dudas)
COL_SAE_A2 = "SAE"
COL_COLABORADO_1 = "COLABORADOR 1"  # → COLABORADOR 1
COL_COLABORADO_2 = "COLABORADOR 2"  # → COLABORADOR 2
COL_COLABORADO_3 = "COLABORADOR 3"  # → COLABORADOR 3
COL_COLABORADO_4 = "COLABORADOR 4"  # → COLABORADOR 4
COL_COLABORADO_5 = "COLABORADOR 5"  # → COLABORADOR 5

# Nombre de la columna SAE en Archivo 1
COL_SAE_A1 = "SAE"

# ─────────────────────────────────────────────
# 2. LECTURA DE ARCHIVOS
# ─────────────────────────────────────────────
print("📂 Leyendo archivos...")

# Archivo 1: encabezados en fila 1 → header=0 (por defecto)
df1 = pd.read_excel(ARCHIVO_1, header=0, dtype=str)

# Archivo 2: encabezados en fila 2 → header=1 (índice 1 = fila 2 de Excel)
df2 = pd.read_excel(ARCHIVO_2, header=1, dtype=str)

# Limpiamos espacios en blanco de los nombres de columnas (frecuente en Excel)
df1.columns = df1.columns.str.strip()
df2.columns = df2.columns.str.strip()

print(f"  Archivo 1: {len(df1)} filas, columnas: {list(df1.columns)}")
print(f"  Archivo 2: {len(df2)} filas, columnas: {list(df2.columns)}")


# ─────────────────────────────────────────────
# 3. VALIDACIÓN RÁPIDA DE COLUMNAS REQUERIDAS
# ─────────────────────────────────────────────
def verificar_columna(nombre_col, dataframe, nombre_archivo):
    """Lanza un error claro si falta una columna requerida."""
    if nombre_col not in dataframe.columns:
        disponibles = list(dataframe.columns)
        raise KeyError(
            f"\n❌ Columna '{nombre_col}' NO encontrada en {nombre_archivo}.\n"
            f"   Columnas disponibles: {disponibles}\n"
            f"   → Ajustá la variable correspondiente al inicio del script."
        )


verificar_columna(COL_SAE_A1, df1, "Archivo 1")
for col in [
    COL_SAE_A2,
    COL_COLABORADO_1,
    COL_COLABORADO_2,
    COL_COLABORADO_3,
    COL_COLABORADO_4,
    COL_COLABORADO_5,
]:
    verificar_columna(col, df2, "Archivo 2")

# ─────────────────────────────────────────────
# 4. CONSTRUCCIÓN DEL DICCIONARIO DE CRUCE
# ─────────────────────────────────────────────
# Limpiar espacios en los valores de SAE para evitar falsos no-match
df1[COL_SAE_A1] = df1[COL_SAE_A1].str.strip()
df2[COL_SAE_A2] = df2[COL_SAE_A2].str.strip()

# Crear tabla de lookup: SAE → {col1, col2, col3, col4, col5}
# Si hay varias filas con el mismo SAE en df2, se toma la PRIMERA ocurrencia.
lookup = (
    df2[
        [
            COL_SAE_A2,
            COL_COLABORADO_1,
            COL_COLABORADO_2,
            COL_COLABORADO_3,
            COL_COLABORADO_4,
            COL_COLABORADO_5,
        ]
    ]
    .drop_duplicates(subset=COL_SAE_A2)  # primera ocurrencia por SAE
    .set_index(COL_SAE_A2)  # SAE como índice para búsqueda rápida
)

print(f"\n🔑 Tabla de cruce construida: {len(lookup)} SAEs únicos en Archivo 2")

# ─────────────────────────────────────────────
# 5. MAPEO + INSERCIÓN ENTRE COLUMNAS 7 Y 8
# ─────────────────────────────────────────────
# Primero calculamos los 5 valores mapeados para cada fila
nuevas_cols = {
    "COLABORADOR 1": df1[COL_SAE_A1].map(lookup[COL_COLABORADO_1]),
    "COLABORADOR 2": df1[COL_SAE_A1].map(lookup[COL_COLABORADO_2]),
    "COLABORADOR 3": df1[COL_SAE_A1].map(lookup[COL_COLABORADO_3]),
    "COLABORADOR 4": df1[COL_SAE_A1].map(lookup[COL_COLABORADO_4]),
    "COLABORADOR 5": df1[COL_SAE_A1].map(lookup[COL_COLABORADO_5]),
}

# Separamos df1 en dos mitades: columnas 0-6 (primeras 7) y columnas 7+ (resto)
# pd.concat pega los DataFrames horizontalmente (axis=1)
#
#   ANTES:  [col1|col2|col3|col4|col5|col6|col7 | col8|col9|...|colN]
#   DESPUÉS:[col1|col2|col3|col4|col5|col6|col7 | COLAB1..5 | col8|...|colN]
#
mitad_izq = df1.iloc[:, :7]  # columnas 1 a 7 (índices 0-6)
mitad_der = df1.iloc[:, 7:]  # columnas 8 en adelante (índice 7+)
nuevas_df = pd.DataFrame(nuevas_cols, index=df1.index)

df1 = pd.concat([mitad_izq, nuevas_df, mitad_der], axis=1)

print(f"\n📋 Orden final de columnas ({len(df1.columns)} total):")
for i, col in enumerate(df1.columns, start=1):
    marca = " ◄ NUEVA" if col.startswith("COLABORADOR") else ""
    print(f"   {i:>2}. {col}{marca}")

# ─────────────────────────────────────────────
# 6. REPORTE DE COINCIDENCIAS
# ─────────────────────────────────────────────
total = len(df1)
encontrados = df1["COLABORADOR 1"].notna().sum()
no_encontrados = total - encontrados

print("\n📊 Resultado del cruce:")
print(f"   Total filas Archivo 1 : {total}")
print(f"   SAEs encontrados      : {encontrados}")
print(f"   SAEs sin coincidencia : {no_encontrados}")

if no_encontrados > 0:
    sin_match = df1[df1["COLABORADOR 1"].isna()][COL_SAE_A1].unique()
    print(f"   ⚠️  SAEs sin match (primeros 10): {sin_match[:10]}")

# ─────────────────────────────────────────────
# 7. GUARDADO
# ─────────────────────────────────────────────
df1.to_excel(SALIDA, index=False)
print(f"\n✅ Archivo guardado: {Path(SALIDA).resolve()}")
