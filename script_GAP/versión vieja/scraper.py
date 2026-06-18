from playwright.sync_api import sync_playwright
import pandas as pd
import time

df = pd.read_excel(r"C:\Users\20289922130\Desktop\Script extraer reseñas GAP\gaps.xlsx")
gaps = df["GAP"].tolist()
resultados = []

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False,
        channel="chrome"
    )

    page = browser.new_page()

    page.goto("https://gap.seguridadciudad.gob.ar")

    input("Logueate y luego presioná ENTER acá...")

    for gap in gaps:

        print(f"Procesando GAP {gap}")

        url = f"https://gap.seguridadciudad.gob.ar/Gap/index.php?modulo=Personas&accion=index&sumario={gap}&tipo=T&depen=139&anio=2026&procedencia=consulta"

        page.goto(url)

        try:
            locator = page.locator("#breveReseniaSidebar")
            locator.wait_for(state="attached", timeout=10000)

            texto = locator.input_value()

        except Exception as e:
            texto = f"ERROR: {str(e)}"

        resultados.append({
            "GAP": gap,
            "RESEÑA": texto
        })

        time.sleep(1)

    pd.DataFrame(resultados).to_excel("resultado.xlsx", index=False)

    print("LISTO")

    browser.close()