import os
import time
import threading
from datetime import datetime
from utils.config import URL, SAVE_DIRECTORY, INTERVAL, FREECIV_PORT, update_url_with_port
from screenshot import take_screenshot
from dotenv import load_dotenv

# Función para monitorear cambios en el puerto
def monitor_port_changes():
    global URL
    current_port = FREECIV_PORT
    
    # Obtener la ruta del archivo .env
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
    last_modified = 0
    
    if os.path.exists(env_path):
        last_modified = os.path.getmtime(env_path)
    
    print(f"[Monitor de Puertos] Iniciado. Vigilando cambios en {env_path}")
    print(f"[Monitor de Puertos] Puerto inicial: {current_port}")
    
    while True:
        try:
            # Comprobar si el archivo .env ha sido modificado
            if os.path.exists(env_path):
                current_modified = os.path.getmtime(env_path)
                
                # Verificar si el archivo ha sido modificado o si ha pasado tiempo suficiente para volver a verificar
                if current_modified > last_modified:
                    print(f"\n[Monitor] Archivo .env modificado. Recargando variables de entorno...")
                    last_modified = current_modified
                    
                    # Guardar el contenido anterior para comparar
                    old_content = ""
                    try:
                        with open(env_path, 'r') as file:
                            old_content = file.read()
                    except Exception as e:
                        print(f"Error al leer .env: {str(e)}")
                    
                    # Recargar variables de entorno
                    load_dotenv(dotenv_path=env_path, override=True)
                    new_port = os.environ.get("FREECIV_PORT", "6302")
                    
                    print(f"[Monitor] Contenido del archivo .env: {old_content}")
                    print(f"[Monitor] Puerto detectado: {new_port}")
                    
                    if new_port != current_port:
                        print(f"\n[Puerto actualizado] Cambiando de {current_port} a {new_port}")
                        current_port = new_port
                        # Actualizar URL con el nuevo puerto
                        new_url = update_url_with_port(current_port)
                        print(f"Nueva URL para capturas: {new_url}")
            
            # En lugar de esperar 5 segundos, comprobamos cada segundo para ser más reactivos
            time.sleep(1)  
        except Exception as e:
            print(f"Error en monitor de puertos: {str(e)}")
            time.sleep(5)  # En caso de error, esperar un poco más

if __name__ == "__main__":
    # Cargar variables de entorno con más detalle para el depurado
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
    print(f"[INICIO] Buscando archivo .env en: {env_path}")
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as file:
            content = file.read()
        print(f"[INICIO] Contenido del archivo .env: {content}")
        
        load_dotenv(dotenv_path=env_path, override=True)
    else:
        print(f"[ADVERTENCIA] No se encontró archivo .env en {env_path}")
        load_dotenv()
    
    # Obtener puerto después de cargar variables
    current_port = os.environ.get("FREECIV_PORT", "6302")
    # Actualizar URL con el puerto actual antes de iniciar
    current_url = update_url_with_port(current_port)
    
    print("=" * 50)
    print("  SISTEMA DE CAPTURAS DE PANTALLA AUTOMÁTICAS")
    print("=" * 50)
    print(f"Puerto FreeCiv actual: {current_port}")
    print(f"URL: {current_url}")
    print(f"Directorio de guardado: {SAVE_DIRECTORY}")
    print(f"Intervalo: {INTERVAL} segundos ({INTERVAL/60} minutos)")
    print("\nEl programa está ejecutándose. Presiona Ctrl+C para detener.")
    print("-" * 50)
    
    # Crear directorio si no existe
    os.makedirs(SAVE_DIRECTORY, exist_ok=True)
    
    # Iniciar hilo para monitorear cambios en el puerto
    port_monitor = threading.Thread(target=monitor_port_changes, daemon=True)
    port_monitor.start()
    
    try:
        while True:
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"\n[{current_time}] Tomando captura de pantalla...")
            
            # Recargar puerto actual antes de tomar la captura
            # Leer directamente el archivo .env para obtener el puerto más actualizado
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
            if os.path.exists(env_path):
                load_dotenv(dotenv_path=env_path, override=True)
                
            # Obtener el puerto actual
            current_port = os.environ.get("FREECIV_PORT", "6302")
            print(f"[Captura] Usando puerto: {current_port}")
            
            # Actualizar URL con el puerto actual
            current_url = update_url_with_port(current_port)
            print(f"[Captura] URL: {current_url}")
            
            # Tomar la captura de pantalla
            take_screenshot(current_url, SAVE_DIRECTORY)
            print(f"Esperando {INTERVAL/60} minutos para la próxima captura...")
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("\n\nPrograma detenido por el usuario.")
        print("Gracias por usar el sistema de capturas automáticas.")