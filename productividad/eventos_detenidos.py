import pandas as pd
import unicodedata

# Cargar archivo
df = pd.read_excel(r"Z:\ESTADISTICA Y CALIDAD\Area Estadisticas y Gestion de Servicio\MAESTROS/CMU - NOVIEMBRE.xlsx")

# Columnas que queremos extraer (posiciones base 1)
columnas_a_extraer = [1, 2, 7, 17, 21, 34, 14, 15]
columnas_a_extraer = [i - 1 for i in columnas_a_extraer]

# Extraer las columnas principales
df_eventos = df.iloc[:, columnas_a_extraer].copy()

# Renombrar columna y crear un nuevo DataFrame
df_renombrado_eventos = df_eventos.rename(columns={'TIPIFICACIÓN': 'TIPO DE EVENTO'})

gap_col = "GAP"
sae_col = "SAE"
tip_col = "TIPIFICACIÓN"
org_col = "ORIGEN"
acl_col = "ACLARACIONES"
op_col = "OPERADOR"
cierre_col = "TIPO DE CIERRE"

# DataFrame final
resultado = pd.DataFrame(df_renombrado_eventos)

# Exportar
resultado.to_excel("eventos_detenidos.xlsx", index=False)
print("Archivo 'resultado.xlsx' generado correctamente.")


print("LISTO. Se generó resultado_colaboradores.xlsx con colaboradores SOLO de eventos de COLABORACION.")