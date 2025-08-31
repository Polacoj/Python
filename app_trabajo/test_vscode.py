import sys
print("VS Code usando:")
print(f"Python: {sys.executable}")
print(f"Version: {sys.version}")

try:
    import pandas as pd
    print(f"✅ pandas {pd.__version__}")
except ImportError:
    print("❌ pandas no encontrado")
