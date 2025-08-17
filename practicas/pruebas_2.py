from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Abre Chrome y WhatsApp Web
driver = webdriver.Safari()
driver.get('https://web.whatsapp.com/')

print("Escanea el código QR y presiona Enter para continuar...")
input()

# Nombre del grupo
nombre_del_grupo = "Nombre del Grupo"

# Encuentra el grupo y haz clic
grupo = driver.find_element(By.XPATH, f"//span[@title='{nombre_del_grupo}']")
grupo.click()

time.sleep(3)

# Buscar todos los mensajes que contengan un archivo PDF
pdf_links = driver.find_elements(By.XPATH, "//span[contains(text(), '.pdf')]")

for link in pdf_links:
    try:
        # Haz clic en el mensaje con el PDF
        link.click()
        time.sleep(2)
        
        # Encuentra y haz clic en el botón de descarga
        download_btn = driver.find_element(By.XPATH, "//span[@data-icon='download']")
        download_btn.click()
        time.sleep(3)  # Espera a que se descargue
    except Exception as e:
        print("Error al intentar descargar un archivo:", e)

print("Descarga completa.")
driver.quit()
