# Configuración del sistema de capturas de pantalla
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener el puerto de FreeCiv de las variables de entorno
FREECIV_PORT = os.environ.get("FREECIV_PORT", "6302")

# URL del sitio web a capturar
BASE_URL = "http://localhost:8080/game/details?host=unknown&port="
URL = f"{BASE_URL}{FREECIV_PORT}"

# Función para actualizar la URL con un nuevo puerto
def update_url_with_port(port):
    global URL
    URL = f"{BASE_URL}{port}"
    return URL

# Directorio donde se guardarán las capturas (relativo al directorio raíz del proyecto)
# Usa os.path.join para crear rutas compatibles con cualquier sistema operativo
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DEFAULT_SAVE_DIR = os.path.join(PROJECT_ROOT, "screenshots")
SAVE_DIRECTORY = os.environ.get("SCREENSHOT_SAVE_DIR", DEFAULT_SAVE_DIR)

# Intervalo de tiempo entre capturas (en segundos)
DEFAULT_INTERVAL = 300  # 300 segundos = 5 minutos
INTERVAL = int(os.environ.get("SCREENSHOT_INTERVAL", DEFAULT_INTERVAL))

# Resolución de las capturas
DEFAULT_WINDOW_SIZE = "1920,1080"
WINDOW_SIZE = os.environ.get("SCREENSHOT_WINDOW_SIZE", DEFAULT_WINDOW_SIZE)