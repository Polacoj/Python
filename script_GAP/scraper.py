from playwright.sync_api import sync_playwright
import pandas as pd
import time
import re


# =========================
# FUNCIÓN DE FORMATO (ARRIBA SIEMPRE)
# =========================
def formatear_texto(texto):
    if not texto:
        return texto

    texto = texto.upper()

    # SIENDO LAS XX:XX HS
    patron_siendo = r"(SIENDO LAS\s+\d{2}:\d{2}\s*HS)"

    # HORARIOS SUELTOS XX:XX HS (no precedidos por SIENDO LAS)
    patron_hora = r"(?<!SIENDO LAS\s)(\d{2}:\d{2}\s*HS)"

    texto = re.sub(patron_siendo, r"\n\1", texto)
    texto = re.sub(patron_hora, r"\n\1", texto)

    texto = re.sub(r"\n+", "\n", texto).strip()

    return texto


# =========================
# EXCEL
# =========================
df = pd.read_excel(r"C:\Users\20289922130\Desktop\Script extraer reseñas GAP\gaps.xlsx")
gaps = df["GAP"].tolist()
resultados = []


# =========================
# PLAYWRIGHT
# =========================
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

            texto = formatear_texto(locator.input_value())

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