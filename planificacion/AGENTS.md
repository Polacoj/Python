# Instrucciones para agentes

## Alcance del proyecto

- Es un proyecto Python pequeño que procesa archivos `.xlsx` con `openpyxl`.
- El script principal es [`recuento_funciones.py`](recuento_funciones.py). Lee `PLANIFICACION_AGOSTO_2026.xlsx` y genera `PLANIFICACION_AGOSTO_2026_con_recuento.xlsx`.
- La configuración del proyecto y sus dependencias está en [`pyproject.toml`](pyproject.toml); el entorno reproducible está fijado en [`uv.lock`](uv.lock).
- Se requiere Python `>=3.14`, según `pyproject.toml` y `uv.lock`.

## Entorno y dependencias

- Usar `uv` como gestor de entorno y dependencias. No recomendar `pip install --break-system-packages` ni instalar paquetes globalmente.
- Para preparar el proyecto desde cero, ejecutar `uv sync` desde la raíz. Esto crea o actualiza `.venv` y sincroniza `uv.lock`.
- Ejecutar el script con `uv run python recuento_funciones.py`; no asumir que el intérprete global tiene las dependencias.
- Para agregar una dependencia externa, usar `uv add <paquete>` y luego `uv sync` si hace falta. Para una dependencia de desarrollo, usar `uv add --dev <paquete>`.
- `openpyxl` es la dependencia externa necesaria para este script. `collections.Counter` y `pathlib.Path` pertenecen a la biblioteca estándar de Python y no deben instalarse desde PyPI.
- Revisar antes de agregar paquetes duplicados o innecesarios: las entradas `counter`, `path` y `pathlib` de `pyproject.toml` no corresponden a los imports usados por `recuento_funciones.py` y solo deben conservarse si otro código del proyecto demuestra que las necesita.
- Si `uv add` falla, comprobar primero `uv --version`, `python --version`, que el intérprete sea Python 3.14 o superior y que el comando se ejecute en la raíz que contiene `pyproject.toml`.

## Ejecución y validación

- Los archivos Excel de entrada y salida son datos locales; no reemplazar el archivo original. Usar argumentos para nombres alternativos:
  `uv run python recuento_funciones.py entrada.xlsx salida.xlsx`.
- Antes de procesar un archivo, comprobar que existe y que contiene la solapa `1236  1260` esperada por el script.
- Validar cambios de dependencias con `uv lock --check` y `uv tree`.
- Validar la sintaxis del script con `uv run python -m py_compile recuento_funciones.py`.
- Después de una ejecución real, comprobar que se creó el `.xlsx` de salida y que las columnas `AQ` y `AR` contienen el recuento y el total de días.
- No editar `uv.lock` manualmente; actualizarlo mediante los comandos de `uv`.

## Convenciones de cambios

- Mantener cambios pequeños y conservar la lógica existente de normalización de códigos y copia de estilos.
- No modificar el Excel original ni añadir archivos de datos al control de versiones salvo que se solicite expresamente.
- Actualizar [`README.md`](README.md) si se documenta un flujo de instalación o ejecución que deba conocer una persona usuaria; no duplicar aquí documentación extensa.