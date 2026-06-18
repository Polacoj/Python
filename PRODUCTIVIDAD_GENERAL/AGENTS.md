# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview
Excel event processing system ("Procesador de Eventos") that extracts, organizes, and consolidates data from CMU (Centro de Monitoreo Urbano) files into unified reports for operator productivity scoring. Written in Spanish for internal use.

## Running the Application
```bash
# Main GUI application (Excel event processor)
python principal.pyw

# Attendance processor (independent module)
python presentismo_grafica.py
```

## Dependencies
```bash
# Install dependencies
pip install pandas openpyxl
```
Requirements: Python 3.13+, pandas, openpyxl, tkinter (built-in)

## Architecture

### Main Components
- `principal.pyw` - GUI entry point using tkinter. Orchestrates all processing, handles file selection, and generates unified Excel output (`eventos_unificados.xlsx`)
- `presentismo_grafica.py` - Standalone attendance processor (independent workflow)

### Processor Modules (`complementos/`)
Each processor follows a consistent pattern with a class containing `process_df(df)` and `process_file(path)` methods:

- `contraventores_detenidos.py` - `ContraventoresProcessor`: Filters events with contraventors ≥1 and closure "FINALIZA CON IMPUTADO/S"
- `integrados.py` - `IntegradosProcessor`: Detects "integrad" or "destacad" keywords in ACLARACIONES column
- `colaboradores.py` - `ColaboradoresProcessor`: Extracts collaborator data from COLABORADOR 1-6 columns, distinguishes between "APOYO OPTICO" and "EVENTO" types based on TIPIFICACIÓN

### Data Flow
1. User selects CMU Excel file via GUI
2. `procesar_excel()` loads and cleans data (GAP/SAE normalization, empty row removal)
3. Each processor extracts specific event types from the source DataFrame
4. Results are concatenated vertically into single "eventos" sheet
5. Optional: narration data from "Control Diario" files can be merged using SAE column as key

### Key Column Mappings (1-indexed in source)
- Col 1: FECHA, Col 2: HORA, Col 7: OPERADOR, Col 17: TIPIFICACIÓN → "TIPO DE EVENTO"
- Col 21: BARRIO, Col 33: ORIGEN, Col 14: GAP, Col 15: SAE

### Data Directory
`DATOS/` - Stores CMU reference files (format: `CMU - {MES}.xlsx`) and presentismo output files

## Code Conventions
- Spanish variable names and comments throughout
- Use `norm()` function for Unicode normalization when comparing text
- Processors should maintain the standard output columns: FECHA, HORA, OPERADOR, TIPO DE EVENTO, BARRIO, ORIGEN, GAP, SAE
- Log messages use `log_mensaje()` for both console and GUI output
