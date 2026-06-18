📊 Procesador de Eventos Excel

📋 Descripción
Sistema de procesamiento automatizado para archivos Excel de eventos, diseñado para extraer, organizar y consolidar información de múltiples fuentes en un archivo unificado. Incluye procesamiento de eventos principales, contraventores, integrados, colaboradores y narración.

✨ Características Principales
🎯 Procesamiento Principal
Extracción inteligente de columnas específicas (FECHA, HORA, OPERADOR, etc.)

Limpieza automática de datos GAP/SAE (división por "/", normalización)

Detección y eliminación de filas vacías al final del archivo

Validación de estructura de columnas

📑 Módulos Especializados
Contraventores y Detenidos

Filtra eventos con contraventores ≥ 1 y cierre "FINALIZA CON IMPUTADO/S"

Genera eventos tipo "EVENTO CON CONTRAVENTOR" y "EVENTO CON DETENIDOS"

Integrados y Destacados

Detecta eventos marcados como "integrad" o "destacad" en aclaraciones

Clasifica como "EVENTO INTEG./DESTAC. (LO DETERMINA CALIDAD)"

Colaboradores

Procesa múltiples columnas de colaboradores (COLABORADOR 1-6)

Distingue entre "COLABORACION EN APOYO OPTICO" y "COLABORACION EN EVENTO"

Basado en el valor de la columna TIPIFICACIÓN

Narración (Control Diario)

Procesa archivos de control diario con múltiples hojas

Extrae datos de operador, GAP y SAE

Cruza información con archivo CMU para obtener ORIGEN

Unificación automática al archivo principal

🎨 Interfaz de Usuario
Log detallado con separadores visuales y estadísticas

Progreso paso a paso con información de cada etapa

Estadísticas de procesamiento (filas procesadas, coincidencias, etc.)

Área de registro con fondo oscuro para mejor legibilidad

Mensajes de éxito/error descriptivos

📁 Estructura del Proyecto
text
procesador_eventos/
├── main.py                      # Punto de entrada principal
├── contraventores_detenidos.py  # Procesador de contraventores
├── integrados.py                # Procesador de integrados/destacados
├── colaboradores.py             # Procesador de colaboradores
├── presentismo_grafica.py       # Módulo de presentismo (independiente)
├── DATOS/                       # Carpeta para archivos de datos
│   └── CMU - *.xlsx             # Archivos CMU de referencia
└── README.md                    # Este archivo
🔧 Requisitos del Sistema
📦 Dependencias
txt
pandas>=1.5.0
openpyxl>=3.0.0
tkinter (incluido en Python estándar)
🐍 Versión de Python
Python 3.8 o superior recomendado

🚀 Instalación y Uso
1. Preparación inicial
bash
# Clonar o descargar los archivos del proyecto
# Crear carpeta DATOS (se crea automáticamente al ejecutar)
# Colocar archivos CMU en carpeta DATOS (ej: CMU - SEPTIEMBRE.xlsx)
2. Ejecución
bash
python main.py
3. Flujo de trabajo
Paso 1: Seleccionar archivo principal
Hacer clic en "📁 Seleccionar archivo Excel"

Elegir archivo maestro (CMU) a procesar

El sistema mostrará el nombre del archivo seleccionado

Paso 2: Procesamiento automático
El sistema ejecutará automáticamente:

✅ Carga y preparación de datos

✅ Extracción de columnas específicas

✅ Procesamiento especializado:

Contraventores y detenidos

Integrados y destacados

Colaboradores

✅ Creación de archivo unificado

Paso 3: Procesar narración (opcional)
El sistema preguntará si desea procesar Control Diario

Si selecciona "Sí", elija archivo de Control Diario

Los datos se agregarán automáticamente al archivo unificado

Paso 4: Resultados
Archivo generado: eventos_unificados.xlsx en la misma carpeta del archivo original

Registro detallado en la interfaz

Mensaje de confirmación con estadísticas

📊 Columnas Procesadas
El sistema extrae y procesa las siguientes columnas:

Columna	Nombre	Descripción
1	FECHA	Fecha del evento
2	HORA	Hora del evento
7	OPERADOR	Operador asignado
17	TIPIFICACIÓN	Tipo de evento (renombrado a "TIPO DE EVENTO")
21	BARRIO	Barrio/locación del evento
33	ORIGEN	Origen del evento
14	GAP	Código GAP (limpiado automáticamente)
15	SAE	Código SAE (limpiado automáticamente)
🔍 Detalles Técnicos
🔄 Procesamiento de GAP/SAE
División por "/" (toma solo la primera parte)

Conversión a numérico con manejo de errores

Eliminación de espacios y normalización

🤝 Procesamiento de Narración
Selección de hoja: El usuario selecciona la hoja a procesar

Filtrado: Solo filas con columna 5 = "si" y columna 2 no vacía

Cruza con CMU: Busca coincidencias de SAE en archivo CMU

Unificación: Se agrega directamente al archivo principal con tipo "NARRACIÓN"

📈 Estadísticas Generadas
Total de filas procesadas por módulo

Coincidencias encontradas en cruces de datos

Errores manejados (si los hay)

Tiempo de procesamiento implícito

⚠️ Consideraciones Importantes
📁 Archivos CMU
Deben estar en carpeta DATOS/

Formato: CMU - MES.xlsx (ej: CMU - SEPTIEMBRE.xlsx)

Debe contener al menos 33 columnas

Columna 15 debe contener SAE, columna 33 debe contener ORIGEN

📝 Archivo de Control Diario (Narración)
Puede contener múltiples hojas

Debe tener columnas en posiciones específicas:

Columna 3: OPERADOR

Columna 4: GAP

Columna 5: SAE

Columna 6: Filtro ("si"/"no")

🛠️ Manejo de Errores
Validación de estructura de columnas

Manejo de archivos corruptos o con formato incorrecto

Registro detallado de errores en la interfaz

Continuación del procesamiento a pesar de errores parciales

📋 Formato de Salida
Archivo eventos_unificados.xlsx
Contiene todas las secciones en una sola hoja llamada "eventos":

Eventos principales: Datos extraídos del archivo original

Contraventores/detenidos: Eventos filtrados por condiciones específicas

Integrados/destacados: Eventos marcados en aclaraciones

Colaboradores: Datos de colaboradores extraídos

Narración (opcional): Datos de Control Diario procesados

Columnas del archivo de salida
python
[
    "FECHA", "HORA", "OPERADOR", "TIPO DE EVENTO",
    "BARRIO", "ORIGEN", "GAP", "SAE"
]

🔄 Módulo de Presentismo
El archivo presentismo_grafica.py es un módulo independiente para:

Procesar archivos de presentismo

Generar resúmenes por grupos

Crear estadísticas de asistencia

Nota: Este módulo se ejecuta por separado y no está integrado en el flujo principal.

🐛 Solución de Problemas
Problema: "El archivo no tiene suficientes columnas"
Solución: Verificar que el archivo tenga al menos 33 columnas

Problema: "No se encontró archivo CMU"
Solución: Asegurarse de que exista archivo CMU - MES.xlsx en carpeta DATOS/

Problema: "No se pudo leer la hoja seleccionada"
Solución: Verificar que el archivo no esté corrupto y que la hoja exista

Problema: Procesamiento lento
Solución: Archivos muy grandes (>50,000 filas) pueden requerir más tiempo

📈 Mejoras Futuras
...............

📄 Licencia
Este proyecto está disponible para uso interno.

📞 Soporte
Soña.....agradece que si funciona!!
---------------------------------------------------------------------------------------------------------------------------------------------------
Versión: 2.5.1
Última actualización: Enero 2026
Desarrollado por: Jankowicz alexis