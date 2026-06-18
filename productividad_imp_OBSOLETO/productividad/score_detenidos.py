import pandas as pd
import unicodedata

# Cargar archivo
df = pd.read_excel(r"Z:\ESTADISTICA Y CALIDAD\Area Estadisticas y Gestion de Servicio\MAESTROS\CONTROL DIARIO\2025\NOVIEMBRE\NOVIEMBRE.xlsx")
def remove_accents(s):
    s = str(s)
    return ''.join(ch for ch in unicodedata.normalize('NFKD', s) if not unicodedata.combining(ch))

gap_col = "GAP"
sae_col = "SAE"
tip_col = "TIPIFICACIÓN"
barr_col = "BARRIO"
org_col = "ORIGEN"
acl_col = "ACLARACIONES"
op_col = "OPERADOR"
cierre_col = "TIPO DE CIERRE"

# Listas de salida
dato = []
lista = ["daños", "ensuciar bienes", "exhibiciones obscenas", "foco igneo", "homicidio/tentativa de homicidio", "identificacion de personas", "incidencia en via publica", "ley bloomberg", "ley de marcas"]

#-----columnas para eventos integrados
columnas_a_extraer = [7, 15, 29, 8, 9]
columnas_a_extraer = [i - 1 for i in columnas_a_extraer]

# Extraer las columnas principales
df_integrado = df.iloc[:, columnas_a_extraer].copy()
df_renombrado_intergados = df_integrado.rename(columns={'ACLARACIONES': 'TIPO DE EVENTO'})

for idx, fila in df.iterrows():
    cierre = remove_accents(fila.get(cierre_col, '')).strip().lower()
    tipificacion = remove_accents(fila.get(tip_col, '')).strip().lower()
    if ('imputado' in cierre and 'robo' in tipificacion) or ('imputado' in cierre and tipificacion in lista):
        dato.append({
            "OPERADOR": fila.get(op_col),
            "TIPO DE EVENTO": "ROBO/HURTO",
            "BARRIO": fila.get(barr_col),
            "ORIGEN": fila.get(org_col),
            "GAP": fila.get(gap_col),
            "SAE": fila.get(sae_col),
            "CIERRE":fila.get(cierre_col)
        })

for idx, fila in df.iterrows():
    tip_val = remove_accents(fila.get(acl_col, '')).strip().lower()
    if 'integrad' in tip_val or 'destacad' in tip_val:
        dato.append({
            "OPERADOR": fila.get(op_col),
            "TIPO DE EVENTO": "INTERVENCION DESTACADA",
            "BARRIO": fila.get(barr_col),
            "ORIGEN": fila.get(org_col),
            "GAP": fila.get(gap_col),
            "SAE": fila.get(sae_col)
        })

# DataFrame final
resultado = pd.DataFrame(dato)

# Exportar
resultado.to_excel("score_detenidos.xlsx", index=False)
print("Archivo 'resultado.xlsx' generado correctamente.")


print("LISTO. Se generó resultado_colaboradores.xlsx con colaboradores SOLO de eventos de COLABORACION.")