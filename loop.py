import subprocess
import time
import os
import sys
import signal
import re
import threading
from dotenv import load_dotenv

# Variable global para mantener referencia al proceso de captura de pantalla
screenshot_process = None
# Variable para controlar el inicio retrasado del sistema de capturas
start_time = None

def update_env_file(port):
    """
    Actualiza el puerto en el archivo .env
    """
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    
    # Asegurarse de que el puerto es un string
    port = str(port)
    
    print(f"[update_env_file] Actualizando puerto a: {port} en {env_path}")
    
    try:
        if os.path.exists(env_path):
            # Leer el archivo .env
            with open(env_path, 'r') as file:
                content = file.read()
            
            # Imprimir contenido actual para depuración
            print(f"[update_env_file] Contenido actual del archivo .env: {content}")
            
            # Actualizar el puerto en el contenido
            if re.search(r'FREECIV_PORT=\d+', content):
                # Si ya existe la variable, actualiza su valor
                updated_content = re.sub(r'FREECIV_PORT=\d+', f'FREECIV_PORT={port}', content)
            else:
                # Si no existe, añade la variable al final
                updated_content = content.rstrip() + f'\nFREECIV_PORT={port}\n'
            
            # Escribir el contenido actualizado
            with open(env_path, 'w') as file:
                file.write(updated_content)
            
            # Actualizar variables de entorno en el proceso actual
            os.environ["FREECIV_PORT"] = port
            
            print(f"[update_env_file] .env actualizado con puerto: {port}")
        else:
            # Si no existe el archivo .env, créalo
            with open(env_path, 'w') as file:
                file.write(f'FREECIV_PORT={port}\n')
            
            # Actualizar variables de entorno en el proceso actual
            os.environ["FREECIV_PORT"] = port
            
            print(f"[update_env_file] Archivo .env creado con puerto: {port}")
    except Exception as e:
        print(f"[update_env_file] ERROR al actualizar .env: {str(e)}")

def start_screenshot_system(screenshot_script, delay=180):
    """
    Inicia el sistema de capturas de pantalla después de un retraso
    """
    global screenshot_process
    
    # Esperar el tiempo especificado
    print(f"Esperando {delay} segundos antes de iniciar el sistema de capturas...")
    time.sleep(delay)
    
    # Asegurarse de que el puerto esté actualizado antes de iniciar el sistema de capturas
    load_dotenv(override=True)
    print(f"Iniciando sistema de capturas con puerto {os.environ.get('FREECIV_PORT', '6302')}...")
    
    try:
        screenshot_process = subprocess.Popen(
            [sys.executable, screenshot_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            env=os.environ  # Pasar las variables de entorno al proceso
        )
        
        # Mostrar la salida del sistema de capturas
        def print_output():
            for line in screenshot_process.stdout:
                print(f"[Screenshot System] {line}", end='')
        
        output_thread = threading.Thread(target=print_output, daemon=True)
        output_thread.start()
        
        print("Sistema de capturas iniciado correctamente después del retraso.")
    except Exception as e:
        print(f"Error al iniciar el sistema de capturas: {str(e)}")

def main():
    """
    Ejecuta main.py en bucle, con un intervalo de 30 segundos entre ejecuciones
    para permitir que se libere el puerto 6302.
    """
    global screenshot_process
    
    # Cargar variables de entorno desde el archivo .env
    load_dotenv()
    
    # Obtener el puerto preferido, por defecto 6302
    freeciv_port = os.environ.get("FREECIV_PORT", "6302")
    print(f"Utilizando puerto {freeciv_port} para FreeCiv")
    
    # Verificar si el sistema de capturas está instalado
    screenshot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                "screenshot-capture-system")
    screenshot_script = os.path.join(screenshot_dir, "src", "main.py")
    
    # Variable para controlar el inicio retrasado del sistema de capturas
    screenshot_delay = 180  # 3 minutos de retraso
    screenshot_started = False
    
    print("Iniciando bucle de ejecución para main.py...")
    # Obtener la ruta absoluta del directorio actual
    current_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(current_dir, "main.py")
    
    # Verificar que main.py existe
    if not os.path.exists(main_script):
        print(f"Error: No se encontró el archivo {main_script}")
        return
    
    # Configurar manejo de señales para cerrar correctamente
    def signal_handler(sig, frame):
        print("\nDetectada señal de interrupción. Cerrando el bucle...")
        # Detener el proceso de capturas de pantalla si está activo
        if screenshot_process is not None:
            print("Cerrando sistema de capturas de pantalla...")
            screenshot_process.terminate()
            screenshot_process.wait()
            print("Sistema de capturas cerrado.")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
      # Bucle principal
    iteration_count = 0
    start_time = time.time()
    while True:
        try:
            print("\n" + "="*60)
            print(f"Iniciando ejecución de main.py a las {time.strftime('%H:%M:%S')}")
            print("="*60)
              # Ejecutar main.py como un proceso independiente
            process = subprocess.Popen([sys.executable, main_script], 
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT,
                                      universal_newlines=True,
                                      bufsize=1)  # Usar buffering por línea
            
            # Iniciar el sistema de capturas después de 3 minutos en la primera iteración
            if not screenshot_started and os.path.exists(screenshot_script):
                iteration_count += 1
                
                # Iniciar un hilo para el sistema de capturas con retraso
                def delayed_start():
                    time.sleep(screenshot_delay)  # Esperar 3 minutos
                    global screenshot_process
                    
                    # Asegurarse de que el puerto esté actualizado
                    load_dotenv(override=True)
                    current_port = os.environ.get("FREECIV_PORT", "6302")
                    
                    # Configurar intervalo de capturas
                    os.environ["SCREENSHOT_INTERVAL"] = os.environ.get("SCREENSHOT_INTERVAL", "60")
                    
                    print(f"\nIniciando sistema de capturas después de {screenshot_delay} segundos...")
                    print(f"Puerto actual para capturas: {current_port}")
                    
                    try:
                        screenshot_process = subprocess.Popen(
                            [sys.executable, screenshot_script],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            universal_newlines=True,
                            bufsize=1,
                            env=os.environ
                        )
                        
                        # Crear un hilo para la salida del sistema de capturas
                        def print_screenshot_output():
                            try:
                                for line in screenshot_process.stdout:
                                    print(f"[Screenshot System] {line}", end='')
                            except Exception as e:
                                print(f"[Screenshot Error] {str(e)}")
                        
                        screenshot_thread = threading.Thread(target=print_screenshot_output, daemon=True)
                        screenshot_thread.start()
                            
                    except Exception as e:
                        print(f"Error al iniciar sistema de capturas: {str(e)}")
                
                # Iniciar el hilo de lanzamiento retrasado
                delay_thread = threading.Thread(target=delayed_start, daemon=True)
                delay_thread.start()
                
                screenshot_started = True
                print(f"Sistema de capturas programado para iniciar en {screenshot_delay} segundos...")            # Configurar un hilo para monitorear la salida del proceso principal
            # sin bloquear la ejecución
            port_found = False
            actual_port = None
            
            def monitor_process_output():
                nonlocal port_found, actual_port
                try:
                    for line in process.stdout:
                        print(line, end='', flush=True)
                        
                        # Capturar el puerto real del log
                        if not port_found and ("Reset with port:" in line or "Log in to port" in line):
                            # Extraer el puerto del mensaje de log
                            port_match = re.search(r'port:?\s*(\d+)', line)
                            if port_match:
                                actual_port = port_match.group(1)
                                port_found = True
                                print(f"\n[INFO] Puerto real detectado: {actual_port}")
                                # Actualizar inmediatamente el archivo .env con el puerto real
                                if actual_port != os.environ.get("FREECIV_PORT", "6302"):
                                    update_env_file(actual_port)
                                    print(f"[INFO] Archivo .env actualizado con puerto real: {actual_port}")
                except Exception as e:
                    print(f"[Monitor Error] Error al leer la salida: {str(e)}")
            
            # Iniciar el hilo para monitorear la salida
            output_thread = threading.Thread(target=monitor_process_output, daemon=True)
            output_thread.start()
            
            # Esperar a que el proceso termine, pero sin bloquear la lectura de la salida
            process.wait()
            
            print("\n" + "="*60)
            print(f"main.py terminó con código {process.returncode} a las {time.strftime('%H:%M:%S')}")
            
            # Usar el puerto que detectamos durante la ejecución si está disponible
            if actual_port:
                freeciv_port = actual_port
                print(f"[INFO] Usando puerto detectado durante la ejecución: {freeciv_port}")
            else:
                # Posiblemente actualizar el puerto para la próxima ejecución
                # En un entorno real, esto podría variar según cómo se manejen los puertos
                freeciv_port = os.environ.get("FREECIV_PORT", "6302")
                print(f"[INFO] No se detectó puerto en la ejecución, usando valor por defecto: {freeciv_port}")
            
            # Actualizar el archivo .env para que el sistema de capturas lo lea
            # Solo lo actualizamos si el sistema de capturas ya está iniciado
            if screenshot_started:
                update_env_file(freeciv_port)
                print(f"Puerto actualizado para el sistema de capturas: {freeciv_port}")
            
            print(f"Esperando 30 segundos antes de reiniciar para liberar el puerto {freeciv_port}...")
            print("="*60)
            
            # Esperar 30 segundos entre ejecuciones
            time.sleep(30)
            
        except Exception as e:
            print(f"\nError al ejecutar main.py: {str(e)}")
            print("Esperando 30 segundos antes de reintentar...")
            time.sleep(30)

if __name__ == "__main__":
    main()
