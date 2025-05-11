"""
Test script para simular el cambio de puerto en .env
Esto es útil para probar la integración entre el sistema de capturas
y el script loop.py
"""
import os
import time
import random
from dotenv import load_dotenv

def simulate_port_change():
    # Cargar variables de entorno
    load_dotenv()
    
    # Obtener el puerto actual
    current_port = os.environ.get("FREECIV_PORT", "6302")
    print(f"Puerto actual: {current_port}")
    
    # Generar un nuevo puerto aleatorio entre 6000 y 7000
    new_port = str(random.randint(6000, 7000))
    
    # Ruta al archivo .env
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    
    # Leer el contenido del archivo .env
    with open(env_path, 'r') as file:
        content = file.read()
    
    # Reemplazar el puerto antiguo con el nuevo
    if f"FREECIV_PORT={current_port}" in content:
        updated_content = content.replace(f"FREECIV_PORT={current_port}", f"FREECIV_PORT={new_port}")
    else:
        # Si no existe la línea, añadirla
        updated_content = content + f"\nFREECIV_PORT={new_port}\n"
    
    # Escribir el nuevo contenido
    with open(env_path, 'w') as file:
        file.write(updated_content)
    
    print(f"Puerto cambiado a: {new_port}")
    print(f"Archivo .env actualizado: {env_path}")
    
    # Verificar si el sistema de capturas está en ejecución
    print("\nVerificando si el sistema de capturas está en ejecución...")
    import subprocess
    import sys
    
    # Comprobamos si hay procesos de Python ejecutando main.py del sistema de capturas
    if sys.platform == "win32":
        cmd = 'tasklist /FI "IMAGENAME eq python.exe" /V | findstr screenshot'
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if "screenshot" in result.stdout:
            print("El sistema de capturas está en ejecución. El cambio de puerto debería ser detectado pronto.")
        else:
            print("No se detectó el sistema de capturas en ejecución. Inicia loop.py primero.")
    else:
        # Para sistemas Unix/Linux
        cmd = 'ps aux | grep "[p]ython.*screenshot"'
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.stdout:
            print("El sistema de capturas está en ejecución. El cambio de puerto debería ser detectado pronto.")
        else:
            print("No se detectó el sistema de capturas en ejecución. Inicia loop.py primero.")

if __name__ == "__main__":
    # Simular un cambio de puerto
    simulate_port_change()
    
    # Esperar un momento para que el monitor detecte el cambio
    print("\nEsperando a que el monitor de capturas detecte el cambio...")
    time.sleep(5)
    print("Hecho! El sistema de capturas debería estar usando el nuevo puerto ahora.")
