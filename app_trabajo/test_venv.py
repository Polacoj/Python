#!/usr/bin/env python3
"""
Script de prueba para verificar que el entorno virtual funciona correctamente
"""
import sys

print("=== PRUEBA DEL ENTORNO VIRTUAL ===")
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

# Probar importaciones
try:
    import pandas as pd
    print(f"✅ pandas {pd.__version__} - OK")
    
    import openpyxl
    print(f"✅ openpyxl {openpyxl.__version__} - OK")
    
    import pypdf
    print(f"✅ pypdf {pypdf.__version__} - OK")
    
    import tkinterdnd2
    print(f"✅ tkinterdnd2 - OK")
    
    import docx
    print(f"✅ python-docx - OK")
    
    # Probar funcionalidad básica de pandas
    df = pd.DataFrame({'test': [1, 2, 3]})
    print(f"✅ pandas DataFrame creado: {len(df)} filas")
    
    print("\n🎉 ¡Todas las dependencias funcionan correctamente!")
    
except ImportError as e:
    print(f"❌ Error importando: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
