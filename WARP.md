# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Repository Overview

This is a Python learning and practice repository containing various educational projects and exercises. The codebase is organized into several distinct areas focusing on different aspects of Python development, from basic syntax to GUI applications and data processing.

## Directory Structure

- **`practicas/`** - Core Python concept practice files covering fundamentals like loops, classes, functions, and data structures
- **`Ejercicios/`** - Problem-solving exercises and challenges, including MoureDev coding challenges
- **`Python en 30 dias/`** - Structured learning materials covering Python basics (variables, strings, operators)
- **`flet/`** - GUI application development using the Flet framework
- **`pdf_a_excel/`** - PDF processing and data extraction tools for converting PDF documents to Excel format
- **`excel_work/`** - Data manipulation and file processing utilities with drag-and-drop interfaces

## Common Development Commands

### Running Individual Scripts
```bash
# Run any Python script directly
python script_name.py

# Run Flet application
cd flet
python main.py

# Run PDF to Excel converter with GUI
cd pdf_a_excel
python pdf_a_excel.py

# Run drag-and-drop file reader
cd excel_work
python app.py
```

### Installing Dependencies
```bash
# For Flet applications
cd flet
pip install -r requirements.txt

# Common packages used across projects
pip install pandas pypdf openpyxl tkinter flet tkinterdnd2
```

### Testing and Development
```bash
# Run any exercise or practice file to see output
python practicas/clases.py
python Ejercicios/conversion.py

# Run MoureDev challenges
python Ejercicios/MoureDev/reto1.py
```

## Code Architecture

### Project Categories

**Learning Scripts**: Standalone educational files that demonstrate specific Python concepts
- Located in `practicas/`, `Python en 30 dias/`, and `Ejercicios/`
- Each file is self-contained and can be run independently
- Focus on core language features like classes, functions, loops, and data types

**GUI Applications**: Interactive applications with user interfaces
- `flet/main.py` - Web-based GUI using Flet framework
- `excel_work/app.py` - Tkinter-based drag-and-drop file reader
- `pdf_a_excel/pdf_a_excel.py` - PDF processing tool with Tkinter GUI

**Data Processing Tools**: Scripts for handling documents and data conversion
- PDF text extraction and parsing with regex pattern matching
- Excel file manipulation and JSON conversion
- File system operations and batch processing

### Common Patterns

**Class-Based Design**: Educational examples demonstrate OOP principles
- Constructor patterns with `__init__` methods
- Attribute initialization and method definitions
- Object instantiation and method calling

**GUI Development**: Consistent patterns across Tkinter applications
- Main window setup with geometry and styling
- Event handling for user interactions (drag-and-drop, button clicks)
- File processing with error handling

**Data Processing Pipeline**: PDF to Excel workflow
- Text extraction from PDF files using PyPDF
- Regex pattern matching for data normalization
- DataFrame creation and Excel output generation

## Key Dependencies

- **pandas** - Data manipulation and Excel operations
- **pypdf** - PDF text extraction
- **openpyxl** - Excel file handling
- **tkinter** - GUI framework (built-in)
- **tkinterdnd2** - Drag-and-drop functionality
- **flet** - Modern GUI framework for web/desktop apps

## Development Notes

This repository serves as a learning environment with progression from basic Python concepts to more complex applications. Each directory represents a different learning stage or application type. Scripts are designed to be executed individually for learning and experimentation purposes.

The codebase demonstrates various Python paradigms including procedural programming, object-oriented design, GUI development, and data processing workflows. Most scripts include practical examples that can be modified and extended for learning purposes.
