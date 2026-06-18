import pandas as pd
import unicodedata

def normalize_str(s):
    if pd.isna(s):
        return ""
    s = str(s).strip().lower()
    s = unicodedata.normalize('NFKD', s)
    return ''.join(ch for ch in s if not unicodedata.combining(ch))

# =======================
# CARGAR NARRACION
# =======================
narracion = pd.read_excel("narracion.xlsx")

# Normalizar columna SAE de narracion
narracion['sae_norm'] = narracion['SAE'].fillna('').astype(str).apply(normalize_str)

# =======================
# CARGAR MAESTRO CMU
# =======================
maestro = pd.read_excel(
    r"/Users/alexisjankowicz/Python/productividad/archivos_xlsx/CMU - OCTUBRE.xlsx"
)

# Validar que tiene columna 15 y 32
if maestro.shape[1] <= 31:
    raise ValueError(f"El archivo CMU no tiene suficientes columnas. Necesita al menos 32 (tiene {maestro.shape[1]}).")

# Columna 15 → índice 14
col_sae_cmu = maestro.columns[14]

# Columna 33 → índice 31 (esto es lo que pediste)
col_origen = maestro.columns[32]

# Normalizar SAE del CMU
maestro['sae_norm'] = maestro[col_sae_cmu].fillna('').astype(str).apply(normalize_str)

# =======================
# MERGE → unir narracion.SAE con CMU.SAE
# =======================
df_resultado = narracion.merge(
    maestro[['sae_norm', col_origen]],
    on='sae_norm',
    how='inner'
)

# Si encontramos coincidencias → exportar
if not df_resultado.empty:
    df_resultado = df_resultado.drop(columns=['sae_norm'])
    df_resultado = df_resultado.rename(columns={col_origen: 'ORIGEN'})
    df_resultado.to_excel("narracion_origen.xlsx", index=False)
    print("✅ Archivo 'narracion_origen.xlsx' generado correctamente.")
    print(f"   Coincidencias encontradas: {len(df_resultado)}")
else:
    print("⚠️ No se encontraron coincidencias entre SAE(narracion) y SAE(CMU).")
