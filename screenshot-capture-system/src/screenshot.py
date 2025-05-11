import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from utils.config import WINDOW_SIZE

def take_screenshot(url, save_path):
    # Configurar opciones de Chrome en modo headless
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(f"--window-size={WINDOW_SIZE}")

    # Inicializar el driver
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    
    try:
        driver.get(url)
        time.sleep(3)  # Esperar a que cargue la página
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        full_path = os.path.join(save_path, filename)
        
        # Crear directorio si no existe
        os.makedirs(save_path, exist_ok=True)
        
        driver.save_screenshot(full_path)
        print(f"Captura guardada: {full_path}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        driver.quit()