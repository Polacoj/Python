try:
        maestro = pd.read_excel(
            _Path(__file__).parent / "archivos_xlsx" / "CMU - OCTUBRE.xlsx",
            engine="openpyxl",
        )
    except Exception as e:
        return False, f"No se pudo abrir CMU: {e}"