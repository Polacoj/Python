import pandas as pd
import unicodedata

ARCHIVO_PATH = r"/Users/alexisjankowicz/Python/productividad/archivos_xlsx/CONTROL DIARIO  (2).xlsx"


def normalize_str(s):
    if pd.isna(s):
        return ""
    s = str(s).strip().lower()
    s = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in s if not unicodedata.combining(ch))


# Cargar archivo
df = pd.read_excel(ARCHIVO_PATH)

# generar un listado con los nombres de las hojas
hojas = pd.ExcelFile(ARCHIVO_PATH).sheet_names
print("Hojas disponibles en el archivo:")
for i, nombre_hoja in enumerate(hojas, 0):
    print(f"{i} - {nombre_hoja}")

hoja = int(input("mes de: "))

# buscar coincidencia de hoja dentro del libro para trabajar
df = pd.read_excel(
    ARCHIVO_PATH,
    sheet_name=hoja,
)


# Columnas a extraer (posiciones 3,4,5)
columnas_a_extraer = [2, 3, 4]

# Validar existencia
max_idx = max(columnas_a_extraer)
if df.shape[1] <= max_idx:
    raise ValueError(
        f"El archivo no contiene la columna requerida. Se esperaba al menos {max_idx + 1} columnas, encontró {df.shape[1]}."
    )

# Filtro columna 6 == "si"
mask = df.iloc[:, 5].fillna("").astype(str).str.strip().str.lower() == "si"

# Extraer columnas
df_eventos = df.loc[mask].iloc[:, columnas_a_extraer].copy().reset_index(drop=True)

# Renombrar encabezados correctamente
df_eventos.columns = ["OPERADOR", "GAP", "SAE"]


def _stringify_preserve_int(val):
    """Convertir valor a cadena; si es float entero, quitar .0.

    Devuelve cadena vacía para NA, o la representación sin '.0' cuando es entero.
    """
    if pd.isna(val):
        return ""
    try:
        f = float(val)
        if f.is_integer():
            return int(f)
        return int(f)
    except Exception:
        return str(val).strip()


def _parse_int_nullable(val):
    """Parsear valor y devolver entero nullable (pd.NA) si no es entero exacto."""
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


# Coercionar columnas críticas a texto para evitar que pandas las deje como float
df_eventos["GAP"] = df_eventos["GAP"].apply(_stringify_preserve_int)
df_eventos["SAE"] = df_eventos["SAE"].apply(_stringify_preserve_int)

# Crear una columna SAE_INT (nullable) para mantener la versión entera cuando exista
df_eventos["SAE_INT"] = df_eventos["SAE"].apply(_parse_int_nullable).astype("Int64")

# Ya tenemos el DataFrame en memoria; no es necesario escribir/leer intermedio
narracion = df_eventos.copy()
# Normalizar SAE de la narración para comparar con el maestro
narracion["SAE"] = narracion["SAE"].fillna("").astype(str).apply(normalize_str)
print(f"Filas extraídas (narracion): {len(narracion)}")

maestro = pd.read_excel(
    r"/Users/alexisjankowicz/Python/productividad/archivos_xlsx/CMU - OCTUBRE.xlsx",
    engine="openpyxl",
)

# Necesitamos al menos 33 columnas (índices 0..32) para acceder a columna 15 (índice 14)
# y columna 33 (índice 32).
if maestro.shape[1] < 33:
    raise ValueError(
        f"El archivo CMU no tiene suficientes columnas. Necesita al menos 33 (tiene {maestro.shape[1]})."
    )


# Columna 15 → índice 14
col_sae_cmu = maestro.columns[14]

# Columna 33 → índice 32
col_origen = maestro.columns[32]

# Normalizar SAE del CMU
maestro["SAE"] = maestro[col_sae_cmu].fillna("").astype(str).apply(normalize_str)

# =======================
# MERGE → unir narracion.SAE con CMU.SAE
# =======================
# Asegurar que ambas columnas SAE son strings y normalizadas (ya lo hicimos)
# Comprobar duplicados en maestro para evitar errores de validación 'm:1'
dup_count = maestro["SAE"].duplicated().sum()
if dup_count > 0:
    # Eliminamos duplicados conservando la primera aparición (se puede ajustar si se prefiere otra regla)
    maestro = maestro.drop_duplicates(subset=["SAE"], keep="first")

try:
    df_resultado = narracion.merge(
        maestro[["SAE", col_origen]], on="SAE", how="inner", validate="m:1"
    )
except Exception:
    # Intento sin validación para obtener diagnóstico si sigue fallando
    try:
        df_resultado = narracion.merge(
            maestro[["SAE", col_origen]], on="SAE", how="inner"
        )
    except Exception as e:
        raise RuntimeError(f"Error al hacer merge entre narracion y CMU: {e}") from e

# Si encontramos coincidencias → exportar
if not df_resultado.empty:
    # Si existe SAE_INT en el DataFrame resultante, usarla como SAE entero
    if "SAE_INT" in df_resultado.columns:
        df_resultado["SAE"] = df_resultado["SAE_INT"]
        df_resultado = df_resultado.drop(columns=["SAE_INT"])
    try:
        df_resultado["SAE"] = df_resultado["SAE"].astype("Int64")
    except Exception:
        pass

    df_resultado = df_resultado.rename(columns={col_origen: "ORIGEN"})
    df_resultado.to_excel("narracion_origen.xlsx", index=False)
    print("✅ Archivo 'narracion_origen.xlsx' generado correctamente.")
    print(f"   Coincidencias encontradas: {len(df_resultado)}")
else:
    print("⚠️ No se encontraron coincidencias entre SAE(narracion) y SAE(CMU).")
