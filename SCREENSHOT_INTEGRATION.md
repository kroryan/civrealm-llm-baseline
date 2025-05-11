# Integración de los sistemas de capturas y loop

Este proyecto integra dos sistemas:

1. **Sistema de bucle (loop.py)**: Ejecuta el agente CivRealm de manera continua, reiniciando el juego automáticamente después de cada partida.
2. **Sistema de capturas de pantalla**: Toma capturas automáticas del estado del juego a intervalos regulares.

## Cómo funciona

### Detección automática del puerto

- El sistema ahora detecta automáticamente el puerto real que utiliza el juego en los mensajes de log
- Cuando detecta mensajes como "Reset with port: 6310" o "Log in to port 6310", actualiza el archivo .env
- La detección es en tiempo real durante la ejecución del programa

### Procesamiento no bloqueante

- Utiliza **hilos separados** para procesar la salida del juego sin interferir con su ejecución
- Permite que el juego avance desde la fase de preparación (pregame) hasta la partida real
- Monitorea los mensajes de log en segundo plano para detectar cambios de puerto

### Inicio retrasado

- El sistema de capturas se inicia **3 minutos después** de que comience la primera ejecución de `main.py`.
- Esto asegura que el agente ya esté funcionando y que el puerto esté activo cuando se toman las capturas.

### Sistema de puertos dinámicos

El sistema está diseñado para manejar cambios en el puerto de FreeCiv:

- El puerto se detecta directamente de los logs del juego durante su ejecución
- `loop.py` actualiza el archivo `.env` con el puerto real detectado
- El sistema de capturas monitorea continuamente los cambios en el archivo `.env`
- Cuando detecta un cambio de puerto, actualiza la URL de captura automáticamente

### Configuración

Puedes configurar diferentes aspectos del sistema de capturas modificando estas variables de entorno:

- `FREECIV_PORT`: Puerto de FreeCiv (por defecto: 6302, pero se actualiza automáticamente)
- `SCREENSHOT_SAVE_DIR`: Directorio donde se guardan las capturas (por defecto: carpeta "screenshots" en el directorio raíz)
- `SCREENSHOT_INTERVAL`: Intervalo entre capturas en segundos (por defecto: 300 = 5 minutos)
- `SCREENSHOT_WINDOW_SIZE`: Resolución de las capturas (por defecto: "1920,1080")

### Ejecución

Para iniciar todo el sistema, simplemente ejecuta:

```
python loop.py
```

Esto iniciará el bucle principal del agente y, después de 3 minutos, el sistema de capturas automáticas.

### Pruebas

Para probar el cambio de puerto sin tener que esperar a que cambie naturalmente:

```
python test_port_change.py
```

Este script simula un cambio de puerto en el archivo `.env` para verificar que el sistema de capturas pueda detectarlo.

## Diagnóstico

Si el sistema de capturas no se inicia correctamente:

1. Verifica que el directorio `screenshot-capture-system` esté instalado correctamente
2. Asegúrate de que todas las dependencias estén instaladas: `pip install -r screenshot-capture-system/requirements.txt`
3. Verifica los permisos de acceso al directorio donde se guardan las capturas
4. Revisa los logs para asegurarte de que el puerto se está detectando correctamente

## Resolución de problemas comunes

- **El juego se queda en modo "pregame"**: Este problema ha sido solucionado con la implementación de hilos no bloqueantes. Si persiste, reinicia el sistema completo.
- **Las capturas se realizan en un puerto incorrecto**: El sistema ahora detecta automáticamente el puerto en los logs. Si sigue usando un puerto incorrecto, verifica que los mensajes de log contengan el formato correcto como "Reset with port: XXXX" o "Log in to port XXXX".
- **El archivo .env no se actualiza**: Verifica los permisos de escritura en la carpeta del proyecto.
- **Las capturas no se guardan**: Asegúrate de que el directorio de capturas exista y tenga permisos de escritura.

## Cambios recientes

El sistema ha sido mejorado para:

1. **Evitar bloqueos en la ejecución del juego**:
   - Implementación de hilos separados para monitorear la salida sin bloquear el proceso principal
   - Mejor gestión de la comunicación entre procesos

2. **Mejorar la detección de puertos**:
   - Análisis en tiempo real de los logs del juego
   - Actualización inmediata de la configuración cuando se detecta un puerto nuevo

3. **Mejorar la robustez**:
   - Mejor manejo de errores en todos los componentes
   - Monitoreo continuo de cambios en la configuración

---

# Screenshot & Loop Systems Integration

This project integrates two systems:

1. **Loop system (loop.py)**: Continuously runs the CivRealm agent, automatically restarting the game after each match.
2. **Screenshot system**: Takes automatic screenshots of the game state at regular intervals.
