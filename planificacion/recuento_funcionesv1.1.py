"""
recuento_funciones.py
======================

QUE HACE ESTE SCRIPT
---------------------
Recorre la solapa "1236  1260" del archivo PLANIFICACION_AGOSTO_2026.xlsx y,
para cada FILA de personal (cada empleado), cuenta cuántas veces aparece
cada función/código asignado entre las columnas G y AK (que representan los
31 días del mes).

El resultado es un recuento ACUMULATIVO por fila, con el formato:

    5 GAP, 2 ADM-SAE, 1 LA

Además, variantes que significan lo mismo pero están escritas distinto
(ej. "ADM/SAE", "ADM / SAE", "SAE-ADM") se unifican automáticamente en
una única forma canónica gracias al diccionario EQUIVALENCIAS (ver más
abajo). Así el conteo no se "fragmenta" por simples diferencias de tipeo.

Los códigos "combinados" (varios puestos en una sola celda, ej.
"C10-11-12-15", "C07/C10-C11" o "C07,C10,C11" — "-", "/" y "," se tratan
como separadores equivalentes) se separan automáticamente en sus
sub-códigos individuales antes de contar: cada uno suma +1 por separado.
Por eso el TOTAL puede ser mayor a la cantidad de días del mes: si un
mismo día cubre varios puestos, ese día aporta más de una unidad al total.

Las comunas van de C01 a C15. Si aparece un número "C" fuera de ese rango
(por ejemplo por un error de tipeo), el script lo cuenta igual pero al
final imprime un aviso en pantalla para que se pueda revisar a mano.

También se agrega el TOTAL de asignaciones de esa fila (suma de todos los
sub-códigos contados, sin importar cuál).

Ambos valores se escriben en columnas nuevas de la misma planilla:
    - AQ: "RECUENTO FUNCIONES (G:AK)" (el texto con la lista)
    - AR: "TOTAL ASIGNACIONES"        (el número total)

Sin tocar ni romper nada de lo que ya existe.

CONCEPTOS DE PYTHON QUE VAS A VER ACÁ (para ir aprendiendo)
-------------------------------------------------------------
1. `openpyxl`            -> librería profesional estándar para leer/escribir Excel.
2. `collections.Counter` -> una "súper lista" que cuenta ocurrencias automáticamente.
3. Diccionarios (`dict`) -> el EQUIVALENCIAS de abajo es un diccionario, y
                             `dict.get(clave, default)` es la forma idiomática
                             de "buscar y si no está, dejar como estaba".
4. Funciones (`def`)     -> dividimos el problema en piezas chicas y reutilizables.
5. Type hints            -> anotaciones como `-> str` que documentan qué devuelve
                             cada función (buena práctica profesional).
6. f-strings              -> forma moderna de armar texto con variables adentro.
7. `pathlib.Path`         -> forma moderna de manejar rutas de archivos.
8. Comprehensions         -> formas compactas de construir listas/diccionarios.
9. `sum(...)`             -> suma funcional, sin loop manual con acumulador.

REQUISITOS
----------
    pip install openpyxl --break-system-packages   (si no lo tenés instalado)

CÓMO SE USA
-----------
    python recuento_funciones.py

Por defecto lee "PLANIFICACION_AGOSTO_2026.xlsx" de la misma carpeta y
genera "PLANIFICACION_AGOSTO_2026_con_recuento.xlsx". Podés cambiar los
nombres en la sección de CONFIGURACIÓN más abajo, o pasarlos por línea de
comando (ver el bloque `if __name__ == "__main__":` al final).
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from copy import copy
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment
from openpyxl.utils import column_index_from_string, get_column_letter
from openpyxl.worksheet.worksheet import Worksheet


# ---------------------------------------------------------------------------
# CONFIGURACIÓN — acá se ajustan los "parámetros" del script.
# Tenerlos todos juntos arriba es una práctica profesional: si mañana cambia
# el rango de columnas o el nombre de la solapa, se edita en un solo lugar.
# ---------------------------------------------------------------------------

NOMBRE_SOLAPA = "1236  1260"  # la solapa "12 36 12 60" (solapa 1)
COL_NOMBRE = "B"  # columna con "NOMBRE Y APELLIDO"
COL_DESDE = "G"  # primer día del mes
COL_HASTA = "AK"  # último día del mes (día 31)
COL_RESULTADO = "AQ"  # columna nueva y libre donde escribimos el recuento
# (AO estaba ocupada por la celda combinada AM1:AO1)
COL_TOTAL = "AR"  # columna nueva con el total numérico de la fila
FILA_ENCABEZADO = 1  # fila donde van los títulos de columna

# Textos que aparecen en la columna NOMBRE pero que en realidad son
# encabezados repetidos de tabla, no personas. Los ignoramos al contar filas.
ENCABEZADOS_A_IGNORAR = {"NOMBRE Y APELLIDO", "APELLIDO Y NOMBRE"}


def es_fila_de_persona(hoja: Worksheet, fila: int) -> bool:
    """
    Decide si una fila corresponde a un empleado real (con datos) o si es
    una fila de encabezado / separador de sección (ej: "JEFE DE SERVICIO",
    "OFICIALES DE LINEA", "CMU PUERTO MADERO", etc.).

    Regla: es fila de persona si la columna NOMBRE tiene texto y ese texto
    no es uno de los encabezados repetidos de tabla.
    """
    valor = hoja[f"{COL_NOMBRE}{fila}"].value
    if valor is None:
        return False
    texto = str(valor).strip()
    if texto == "":
        return False
    return texto.upper() not in ENCABEZADOS_A_IGNORAR


# Variantes que en la práctica significan lo mismo, pero que al escribirse
# distinto (con "/", "-", espacios, mayúsculas/minúsculas o errores de tipeo)
# terminarían contándose como códigos separados. Acá las "traducimos" todas
# a una única forma canónica ANTES de contar.
#
# Formato: "VARIANTE_YA_NORMALIZADA": "FORMA_CANONICA"
# (la clave tiene que estar en mayúsculas y sin espacios de más, porque se
# compara después de aplicar la limpieza básica de normalizar_codigo).
EQUIVALENCIAS = {
    # --- ADM / SAE ---
    "ADM / SAE": "ADM-SAE",
    "ADM/ SAE": "ADM-SAE",
    "ADM/SAE": "ADM-SAE",
    "SAE-ADM": "ADM-SAE",
    "SAE/ADM": "ADM-SAE",
    # --- SISEP / SAE ---
    "SISEP/SAE": "SISEP-SAE",
    "SISEP / SAE": "SISEP-SAE",
    # --- Oficial de línea ---
    "OFICIAL DE LINEA": "OF DE LINEA",
    "OFICIAL DE LÍNEA": "OF DE LINEA",
    "OF LINEA": "OF DE LINEA",
    "OF. LINEA": "OF DE LINEA",
    "OFI. DE LINEA": "OF DE LINEA",
    # --- Jefe de servicio (incluye error de tipeo "JEDE") ---
    "JEDE DE SERVICIO": "JEFE DE SERVICIO",
    # --- Ausente ---
    "AUS": "AUSENTE",
}


def normalizar_codigo(valor) -> str:
    """
    Limpia un valor de celda para poder agruparlo correctamente al contar,
    y aplica el diccionario EQUIVALENCIAS para unificar variantes que
    significan lo mismo (ej. "ADM/SAE" y "ADM / SAE" -> "ADM-SAE").

    Por qué hace falta: en la planilla original hay variantes como
    "LxM", "LXM", "ADM/ SAE", "ADM / SAE" que en la práctica significan
    lo mismo. Al pasar todo a mayúsculas, sacar espacios de más y después
    consultar el diccionario, esas variantes terminan en un único recuento.
    """
    texto = str(valor).strip()
    texto = " ".join(texto.split())  # colapsa espacios dobles/tabs en uno solo
    texto = texto.upper()

    # dict.get(clave, valor_por_defecto) es la forma "profesional" de buscar
    # en un diccionario sin tener que escribir un if/else explícito: si el
    # código está en EQUIVALENCIAS devuelve su forma canónica, si no, lo
    # deja tal cual.
    return EQUIVALENCIAS.get(texto, texto)


# Un "código compuesto" es algo como "C10-11-12-15", "C07/C10-C11" o
# "C07,C10,C11": varios puestos abreviados, separados por "-", "/" o ",",
# donde el prefijo de letra (la "C") a veces se repite en cada número y a
# veces no. Los tres separadores se tratan como equivalentes.
# Esta expresión regular valida que TODO el texto sea de ese estilo (solo
# letras, números y separadores), antes de intentar separarlo.
# Si el texto tiene espacios u otras palabras (ej. "OS 6796"), no matchea,
# y entonces no lo tocamos.
PATRON_CODIGO_COMPUESTO = re.compile(r"^[A-Z]{1,4}\d{1,3}(?:[\-/,][A-Z]{0,4}\d{1,3})+$")

# Las "comunas" de la Ciudad de Buenos Aires van de la C01 a la C15. Si
# aparece un número fuera de ese rango dentro de un código compuesto, lo
# marcamos como sospechoso (podría ser un error de tipeo, o no ser
# realmente una comuna) para poder revisarlo, sin que el script se rompa.
COMUNA_MINIMA = 1
COMUNA_MAXIMA = 15


def expandir_codigo_compuesto(codigo: str) -> tuple[list[str], list[str]]:
    """
    Separa un código combinado en sus sub-códigos individuales, arrastrando
    el prefijo de letra a los números "sueltos". Acepta "-", "/" y ","
    como separadores equivalentes.

    Ejemplos:
        "C10-11-12-15"   -> (["C10", "C11", "C12", "C15"], [])
        "C07/C10-C11"    -> (["C07", "C10", "C11"], [])
        "C07,C10,C11"    -> (["C07", "C10", "C11"], [])
        "C13"            -> (["C13"], [])            (código simple)
        "GAP"            -> (["GAP"], [])             (no es un código C-xx)
        "C10-11-19"      -> (["C10", "C11", "C19"], ["C19"])  (C19 no existe:
                                                        las comunas van de C01 a C15)

    Si el texto no tiene la forma de un código compuesto (por ejemplo,
    "ADM-SAE" o "OF DE LINEA"), se devuelve tal cual, sin tocarlo — así
    evitamos romper códigos que YA fueron unificados por EQUIVALENCIAS.

    Devuelve una tupla (subcodigos, avisos): `avisos` lista los sub-códigos
    "C" que quedaron fuera del rango de comunas válido (C01 a C15), para
    poder revisarlos a mano.
    """
    # Algunas celdas tienen un separador sobrante al principio o al final
    # por error de tipeo (ej. "C07-13-14-"). Lo sacamos antes de validar.
    codigo_limpio = codigo.strip("-/, ")

    if not PATRON_CODIGO_COMPUESTO.match(codigo_limpio):
        return [codigo], []

    # re.split corta el texto en cada "-", "/" o ",", quedándonos con los
    # pedacitos de a uno: ["C10", "11", "12", "15"]
    partes = re.split(r"[\-/,]+", codigo_limpio)

    subcodigos = []
    avisos = []
    prefijo_actual = ""
    for parte in partes:
        coincidencia = re.match(r"^([A-Z]{1,4})(\d{1,3})$", parte)
        if coincidencia:
            # la parte ya trae su propia letra, ej. "C10" -> prefijo "C"
            prefijo_actual, numero = coincidencia.groups()
        else:
            # la parte es solo un número, ej. "11" -> hereda el prefijo
            # del código anterior (el último "C" que vimos)
            numero = parte

        # Los códigos "C" siempre van con 2 dígitos (C01, no C1 ni C003),
        # así que normalizamos pasando por int() y rellenando con cero.
        if prefijo_actual == "C":
            numero_int = int(numero)
            numero = str(numero_int).zfill(2)
            if not (COMUNA_MINIMA <= numero_int <= COMUNA_MAXIMA):
                avisos.append(f"{prefijo_actual}{numero}")

        subcodigos.append(f"{prefijo_actual}{numero}")

    return subcodigos, avisos


def contar_funciones_de_fila(hoja: Worksheet, fila: int) -> tuple[Counter, list[str]]:
    """
    Recorre las columnas COL_DESDE..COL_HASTA de una fila y devuelve:
        - un Counter con la cantidad de veces que aparece cada código
        - una lista de avisos (códigos "C" fuera del rango C01-C15, por si
          hay que revisarlos a mano)

    Un Counter es como un diccionario {código: cantidad}, pero con métodos
    extra muy cómodos (como most_common()) que usamos más abajo.
    """
    col_ini = column_index_from_string(COL_DESDE)
    col_fin = column_index_from_string(COL_HASTA)

    contador = Counter()
    avisos_fila = []
    for col in range(col_ini, col_fin + 1):
        valor = hoja.cell(row=fila, column=col).value
        if valor is None or str(valor).strip() == "":
            continue
        codigo = normalizar_codigo(valor)

        # Si es un código combinado (ej. "C10-11-12-15"), lo separamos en
        # sub-códigos y cada uno suma +1 individualmente. Si es un código
        # simple, expandir_codigo_compuesto nos devuelve una lista de un
        # solo elemento y el comportamiento es el mismo de siempre.
        subcodigos, avisos = expandir_codigo_compuesto(codigo)
        for subcodigo in subcodigos:
            contador[subcodigo] += 1
        avisos_fila.extend(avisos)

    return contador, avisos_fila


def formatear_recuento(contador: Counter) -> str:
    """
    Convierte un Counter en el texto final, ej: "5 GAP, 2 SAE, 1 LA".

    Orden: de mayor a menor cantidad; ante empate, alfabético (para que el
    resultado sea siempre reproducible y no dependa del orden de lectura).
    """
    if not contador:
        return ""

    # sorted() con una tupla como "key" ordena primero por -cantidad
    # (de mayor a menor) y luego por nombre de código (A-Z).
    items_ordenados = sorted(contador.items(), key=lambda par: (-par[1], par[0]))

    partes = [f"{cantidad} {codigo}" for codigo, cantidad in items_ordenados]
    return ", ".join(partes)


def calcular_total(contador: Counter) -> int:
    """
    Suma todas las apariciones contadas en la fila (sin importar el código).

    Ojo: si hubo códigos combinados (ej. "C10-11-12-15"), ese único día ya
    fue expandido en 4 sub-códigos antes de llegar a este Counter, así que
    el total representa "asignaciones" y no necesariamente "días" — un
    mismo día puede aportar más de 1 al total si cubre varios puestos.

    `sum(contador.values())` es un ejemplo de "programación funcional"
    liviana: en vez de un `for` con un acumulador manual, sumamos
    directamente todos los valores del diccionario.
    """
    return sum(contador.values())


def copiar_estilo(celda_origen, celda_destino) -> None:
    """Copia fuente, relleno y alineación de una celda a otra (mismo estilo)."""
    celda_destino.font = copy(celda_origen.font)
    celda_destino.fill = copy(celda_origen.fill)
    celda_destino.alignment = copy(celda_origen.alignment)
    celda_destino.border = copy(celda_origen.border)


def procesar_archivo(ruta_entrada: Path, ruta_salida: Path) -> int:
    """
    Función principal: abre el Excel, procesa la solapa, escribe la columna
    de resultados y guarda una copia nueva (no pisa el archivo original).

    Devuelve la cantidad de filas de personal procesadas.
    """
    libro = openpyxl.load_workbook(ruta_entrada)

    if NOMBRE_SOLAPA not in libro.sheetnames:
        raise ValueError(
            f"No encontré la solapa '{NOMBRE_SOLAPA}'. "
            f"Solapas disponibles: {libro.sheetnames}"
        )

    hoja = libro[NOMBRE_SOLAPA]

    # --- Encabezados de las columnas nuevas, con el mismo estilo que los demás ---
    celda_encabezado = hoja[f"{COL_RESULTADO}{FILA_ENCABEZADO}"]
    celda_encabezado.value = "RECUENTO FUNCIONES (G:AK)"
    copiar_estilo(hoja[f"AL{FILA_ENCABEZADO}"], celda_encabezado)
    hoja.column_dimensions[COL_RESULTADO].width = 30

    celda_encabezado_total = hoja[f"{COL_TOTAL}{FILA_ENCABEZADO}"]
    celda_encabezado_total.value = "TOTAL ASIGNACIONES"
    copiar_estilo(hoja[f"AL{FILA_ENCABEZADO}"], celda_encabezado_total)
    hoja.column_dimensions[COL_TOTAL].width = 12

    # --- Recorremos todas las filas con datos de la solapa ---
    filas_procesadas = 0
    avisos_totales = []
    for fila in range(1, hoja.max_row + 1):
        if not es_fila_de_persona(hoja, fila):
            continue

        contador, avisos = contar_funciones_de_fila(hoja, fila)
        texto_recuento = formatear_recuento(contador)
        total = calcular_total(contador)

        if avisos:
            nombre = hoja[f"{COL_NOMBRE}{fila}"].value
            avisos_totales.append((fila, nombre, avisos))

        celda = hoja[f"{COL_RESULTADO}{fila}"]
        celda.value = texto_recuento
        # tomamos el estilo de una celda de datos ya existente en esa fila
        copiar_estilo(hoja[f"{COL_NOMBRE}{fila}"], celda)

        celda_total = hoja[f"{COL_TOTAL}{fila}"]
        celda_total.value = total
        copiar_estilo(hoja[f"{COL_NOMBRE}{fila}"], celda_total)
        celda_total.alignment = Alignment(horizontal="center", vertical="center")

        filas_procesadas += 1

    libro.save(ruta_salida)

    if avisos_totales:
        print("\n⚠ Avisos: códigos 'C' fuera del rango de comunas (C01-C15):")
        for fila, nombre, avisos in avisos_totales:
            print(f"  Fila {fila} ({nombre}): {', '.join(avisos)}")

    return filas_procesadas


def imprimir_resumen_en_consola(ruta_entrada: Path, top_n: int = 15) -> None:
    """
    Extra: muestra en pantalla un resumen rápido por persona, útil para
    revisar el resultado sin tener que abrir el Excel.
    """
    libro = openpyxl.load_workbook(ruta_entrada)
    hoja = libro[NOMBRE_SOLAPA]

    print(f"\nVista previa (primeras {top_n} personas con datos):\n")
    print(f"{'NOMBRE Y APELLIDO':35} | {'TOTAL':5} | RECUENTO")
    print("-" * 90)

    mostrados = 0
    for fila in range(1, hoja.max_row + 1):
        if not es_fila_de_persona(hoja, fila):
            continue
        if mostrados >= top_n:
            break
        nombre = hoja[f"{COL_NOMBRE}{fila}"].value
        contador, _avisos = contar_funciones_de_fila(hoja, fila)
        recuento = formatear_recuento(contador)
        total = calcular_total(contador)
        print(f"{str(nombre)[:35]:35} | {total:5} | {recuento}")
        mostrados += 1


if __name__ == "__main__":
    # Permite pasar los nombres de archivo por línea de comando, si se quiere:
    #   python recuento_funciones.py entrada.xlsx salida.xlsx
    # Si no se pasan argumentos, usa los valores por defecto.
    if len(sys.argv) >= 3:
        entrada = Path(sys.argv[1])
        salida = Path(sys.argv[2])
    else:
        entrada = Path(input("Ingrese el nombre del archivo de entrada: "))
        salida = Path("PLANIFICACION_AGOSTO_2026_con_recuento.xlsx")

    cantidad = procesar_archivo(entrada, salida)
    print(f"Listo. Se procesaron {cantidad} filas de personal.")
    print(f"Archivo generado: {salida.resolve()}")

    imprimir_resumen_en_consola(salida)
