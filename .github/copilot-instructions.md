# Instrucciones para Agentes de IA

## Estructura del Repositorio

Este repositorio contiene varios proyectos y ejercicios en Python, organizados en las siguientes carpetas principales:

### Proyectos Principales

- `productividad_py/`: Herramienta para procesar archivos Excel
  - Funcionalidad principal: Normalización y reorganización de columnas
  - Tecnologías: pandas, openpyxl, tkinter

- `app_trabajo/`: Aplicación para procesar archivos PDF
  - Funcionalidad: Extracción de texto y conversión a Excel/Word
  - Tecnologías: pypdf, pandas, tkinter, python-docx

### Carpetas de Aprendizaje

- `practicas/`: Ejercicios básicos y conceptos de Python
- `Ejercicios/`: Desafíos de programación incluyendo retos de MoureDev
- `Python en 30 dias/`: Tutoriales introductorios
- `ventanas/`: Ejemplos de interfaces gráficas con tkinter

## Patrones y Convenciones

### Manejo de Archivos Excel
```python
# Patrón común para lectura de Excel
df = pd.read_excel(archivo)
# Normalización de texto
def normalize(text):
    s = str(text).strip().lower()
    s = unicodedata.normalize('NFKD', s)
    return ''.join(ch for ch in s if not unicodedata.combining(ch))
```

### Interfaces Gráficas
```python
# Patrón común para ventanas de diálogo
Tk().withdraw()  # Oculta la ventana principal
archivo = askopenfilename(filetypes=[("Archivos Excel", "*.xlsx;*.xls")])
```

## Flujos de Trabajo Críticos

### Procesamiento de PDF (`app_trabajo/extraccion_pdf.pyw`)
1. Selección de archivos PDF
2. Extracción de texto con patrones específicos (fechas, IDs, etc.)
3. Exportación a Excel y Word
4. Manejo de errores con try-except

### Manipulación de Excel (`productividad_py/main.py`)
1. Selección de archivo Excel
2. Normalización de nombres de columnas
3. Reordenamiento según estructura predefinida
4. Exportación preservando formato

## Dependencias Principales

Versión de Python requerida: >=3.13

```toml
[dependencies]
pandas = ">=2.3.2"
openpyxl = ">=3.1.5"
pypdf = ">=6.0.0"
python-docx = ">=1.2.0"
```

## Convenciones de Código

- Uso de docstrings para documentación de funciones
- Manejo de errores con bloques try-except
- Nombres de variables descriptivos en español
- Interfaces gráficas con tkinter usando clases y métodos estructurados

## Ejemplo de Uso

Para aplicaciones tkinter:
```python
# Configuración básica de ventana
root = tk.Tk()
root.title("Título")
root.geometry("800x600")
root.config(background='silver')

# Configuración de botones
boton = tk.Button(ventana, text="Acción", command=funcion)
boton.config(fg="red", background="green")
boton.pack()
```