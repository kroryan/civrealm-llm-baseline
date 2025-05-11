# Automatic Screenshot Capture System | Sistema de Capturas de Pantalla Automáticas

[English](#english) | [Español](#español)

<a name="english"></a>
# Automatic Screenshot Capture System

This system allows you to automatically capture screenshots of a specific URL at regular intervals. It uses Selenium and Chrome in headless mode to capture high-quality images without needing a graphical interface.

## Features

- Automatic screenshots of any website or web application
- Headless mode for background operation without graphical interface
- Configurable intervals between captures (default every 5 minutes)
- Filenames with timestamps for easy organization (format: screenshot_YYYYMMDD_HHMMSS.png)
- Configurable capture resolution (default 1920x1080)
- Error handling and automatic recovery
- Simple and clear command line interface
- Automatic creation of the destination directory if it doesn't exist
- Ability to stop the process with Ctrl+C

## Requirements

- Python 3.7 or higher
- Google Chrome installed
- Internet connection (for the first execution, when the WebDriver is downloaded)
- Operating system: Windows, macOS, or Linux

## Dependencies

The system uses the following Python libraries:
- `selenium`: For browser automation
- `webdriver-manager`: To automatically manage the Chrome driver installation
- `requests`: For HTTP operations (optional)
- `pillow`: For image processing (optional)

## Installation

1. Clone or download this repository:
```bash
git clone <repository-URL>
cd screenshot-capture-system
```

2. Navigate to the project folder:
```bash
cd c:\Users\adryl\Pictures\screenshot\screenshot-capture-system
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

You can modify the configuration in the `src/utils/config.py` file:

- `URL`: The web address you want to capture
  - Default: "http://localhost:8080/game/details?host=unknown&port=6302"
  - Example: "https://www.example.com"

- `SAVE_DIRECTORY`: The folder where images will be saved
  - Default: "C:\Users\adryl\Pictures\screenshot\capturas"
  - Make sure the path exists or the program will create it automatically

- `INTERVAL`: The time in seconds between each capture
  - Default: 300 (5 minutes)
  - You can reduce it for more frequent captures or increase it for more spaced captures

- `WINDOW_SIZE`: The resolution of the captures in "width,height" format
  - Default: "1920,1080"
  - Common formats: "1366,768", "1280,720", "3840,2160" (4K)

## Usage

### Basic Execution

To run the program:

```bash
cd c:\Users\adryl\Pictures\screenshot\screenshot-capture-system\src
python main.py
```

The program will display information about its configuration and begin to take screenshots automatically.

### Information Shown During Execution

When starting the program, you will see the following information:
- URL being captured
- Directory where captures are saved
- Interval between captures
- Instructions to stop the program

For each capture taken, the program will display:
- Capture timestamp
- Full path where the image was saved
- Wait time until the next capture

### Stopping the Program

To stop the program, simply press `Ctrl+C` in the terminal. The program will display a farewell message and close correctly.

## Project Structure

```
screenshot-capture-system/
├── requirements.txt      # Project dependencies
├── README.md             # This documentation file
└── src/                  # Source code
    ├── main.py           # Program entry point
    ├── screenshot.py     # Functions for taking screenshots
    └── utils/            # Utilities and configuration
        └── config.py     # System configuration
```

## Internal Operation

1. **Initialization**:
   - The program loads the configuration from `config.py`
   - Verifies and creates the save directory if it doesn't exist
   - Displays information about the current configuration

2. **Screenshot Capture**:
   - Initializes Chrome in headless mode (without graphical interface)
   - Navigates to the specified URL
   - Waits for the page to load completely (3 seconds by default)
   - Takes the screenshot
   - Saves the image with a name based on the current date and time
   - Closes the browser to free resources

3. **Main Cycle**:
   - After each capture, the program waits the specified time
   - The cycle continues until the user stops the program with Ctrl+C

## Troubleshooting

### The Program Doesn't Start or Shows Errors

- Verify that Chrome is installed correctly
- Make sure you have all dependencies installed with `pip install -r requirements.txt`
- Verify that the URL is accessible from your normal browser

### Captures Don't Show the Expected Content

- Increase the wait time in `screenshot.py` (find `time.sleep(3)` and increase the value)
- Verify that the URL is correct and doesn't require authentication
- Check that the page loads correctly in a normal browser

### WebDriver Errors

If you see errors related to the WebDriver:
- Delete the `.wdm` folder in your user directory and let the program download the driver again
- Update Chrome to the latest version

## Advanced Customization

### Changing the Image Format

Currently, the system saves images in PNG format. If you want to change the format, modify the filename in the `take_screenshot` function in `screenshot.py`.

### Adding Authentication

If you need to capture pages that require authentication, you can modify the `take_screenshot` function to add cookies or complete login forms.

### Capturing Different Sections of the Page

You can modify the code in `screenshot.py` to capture specific elements of the page instead of the whole page.

## Final Notes

- The first execution may take a while as the appropriate Chrome driver is downloaded
- Make sure the website or server is running before starting the program
- The system is designed to be lightweight and consume few resources
- Screenshots are saved with high resolution and without compression
- If you need to run the program in the background for long periods, consider using a process manager like `nohup` on Linux or creating a service on Windows

<a name="español"></a>
# Sistema de Capturas de Pantalla Automáticas

Este sistema permite realizar capturas de pantalla automáticas de una URL específica a intervalos regulares. Utiliza Selenium y Chrome en modo headless para capturar imágenes de alta calidad sin necesidad de interfaz gráfica.

## Características

- Capturas de pantalla automáticas de cualquier sitio web o aplicación web
- Modo headless (sin interfaz gráfica) para funcionamiento en segundo plano
- Intervalos configurables entre capturas (por defecto cada 5 minutos)
- Nombres de archivo con timestamp para fácil organización (formato: screenshot_YYYYMMDD_HHMMSS.png)
- Resolución de captura configurable (por defecto 1920x1080)
- Manejo de errores y recuperación automática
- Interfaz de línea de comandos simple y clara
- Creación automática del directorio de destino si no existe
- Posibilidad de detener el proceso con Ctrl+C

## Requisitos

- Python 3.7 o superior
- Google Chrome instalado
- Conexión a internet (para la primera ejecución, cuando se descarga el WebDriver)
- Sistema operativo: Windows, macOS o Linux

## Dependencias

El sistema utiliza las siguientes bibliotecas de Python:
- `selenium`: Para la automatización del navegador
- `webdriver-manager`: Para gestionar automáticamente la instalación del controlador de Chrome
- `requests`: Para operaciones HTTP (opcional)
- `pillow`: Para procesamiento de imágenes (opcional)

## Instalación

1. Clona o descarga este repositorio:
```bash
git clone <URL-del-repositorio>
cd screenshot-capture-system
```

2. Navega hasta la carpeta del proyecto:
```bash
cd c:\Users\adryl\Pictures\screenshot\screenshot-capture-system
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Configuración

Puedes modificar la configuración en el archivo `src/utils/config.py`:

- `URL`: La dirección web de la que quieres tomar capturas
  - Default: "http://localhost:8080/game/details?host=unknown&port=6302"
  - Ejemplo: "https://www.ejemplo.com"

- `SAVE_DIRECTORY`: La carpeta donde se guardarán las imágenes
  - Default: "C:\Users\adryl\Pictures\screenshot\capturas"
  - Asegúrate de que la ruta exista o el programa la creará automáticamente

- `INTERVAL`: El tiempo en segundos entre cada captura
  - Default: 300 (5 minutos)
  - Puedes reducirlo para capturas más frecuentes o aumentarlo para capturas más espaciadas

- `WINDOW_SIZE`: La resolución de las capturas en formato "ancho,alto"
  - Default: "1920,1080"
  - Formatos comunes: "1366,768", "1280,720", "3840,2160" (4K)

## Uso

### Ejecución básica

Para ejecutar el programa:

```bash
cd c:\Users\adryl\Pictures\screenshot\screenshot-capture-system\src
python main.py
```

El programa mostrará información sobre su configuración y comenzará a tomar capturas automáticamente.

### Información mostrada durante la ejecución

Al iniciar el programa verás la siguiente información:
- URL que se está capturando
- Directorio donde se guardan las capturas
- Intervalo entre capturas
- Instrucciones para detener el programa

Por cada captura tomada, el programa mostrará:
- Timestamp de la captura
- Ruta completa donde se guardó la imagen
- Tiempo de espera hasta la próxima captura

### Detener el programa

Para detener el programa, simplemente presiona `Ctrl+C` en la terminal. El programa mostrará un mensaje de despedida y se cerrará correctamente.

## Estructura del proyecto

```
screenshot-capture-system/
├── requirements.txt      # Dependencias del proyecto
├── README.md             # Este archivo de documentación
└── src/                  # Código fuente
    ├── main.py           # Punto de entrada del programa
    ├── screenshot.py     # Funciones para tomar capturas
    └── utils/            # Utilidades y configuración
        └── config.py     # Configuración del sistema
```

## Funcionamiento interno

1. **Inicialización**:
   - El programa carga la configuración desde `config.py`
   - Verifica y crea el directorio de guardado si no existe
   - Muestra información sobre la configuración actual

2. **Captura de pantalla**:
   - Inicializa Chrome en modo headless (sin interfaz gráfica)
   - Navega a la URL especificada
   - Espera a que la página cargue completamente (3 segundos por defecto)
   - Toma la captura de pantalla
   - Guarda la imagen con un nombre basado en la fecha y hora actual
   - Cierra el navegador para liberar recursos

3. **Ciclo principal**:
   - Después de cada captura, el programa espera el tiempo especificado
   - El ciclo continúa hasta que el usuario detiene el programa con Ctrl+C

## Solución de problemas

### El programa no inicia o muestra errores

- Verifica que Chrome esté instalado correctamente
- Asegúrate de tener todas las dependencias instaladas con `pip install -r requirements.txt`
- Verifica que la URL sea accesible desde tu navegador normal

### Las capturas no muestran el contenido esperado

- Aumenta el tiempo de espera en `screenshot.py` (busca `time.sleep(3)` y aumenta el valor)
- Verifica que la URL sea correcta y que no requiera autenticación
- Comprueba que la página cargue correctamente en un navegador normal

### Errores con el WebDriver

Si ves errores relacionados con el WebDriver:
- Borra la carpeta `.wdm` en tu directorio de usuario y deja que el programa descargue de nuevo el controlador
- Actualiza Chrome a la última versión

## Personalización avanzada

### Cambiar el formato de la imagen

Actualmente el sistema guarda las imágenes en formato PNG. Si deseas cambiar el formato, modifica el nombre del archivo en la función `take_screenshot` en `screenshot.py`.

### Añadir autenticación

Si necesitas capturar páginas que requieren autenticación, puedes modificar la función `take_screenshot` para añadir cookies o completar formularios de inicio de sesión.

### Capturar diferentes secciones de la página

Puedes modificar el código en `screenshot.py` para capturar elementos específicos de la página en lugar de la página completa.

## Notas finales

- La primera ejecución puede tardar un poco mientras se descarga el driver adecuado para Chrome
- Asegúrate de que el sitio web o servidor esté funcionando antes de iniciar el programa
- El sistema está diseñado para ser ligero y consumir pocos recursos
- Las capturas de pantalla se guardan con alta resolución y sin compresión
- Si necesitas ejecutar el programa en segundo plano por largos períodos, considera usar un administrador de procesos como `nohup` en Linux o crear un servicio en Windows

## Requisitos

- Python 3.7 o superior
- Google Chrome instalado
- Conexión a internet (para la primera ejecución, cuando se descarga el WebDriver)
- Sistema operativo: Windows, macOS o Linux

## Dependencias

El sistema utiliza las siguientes bibliotecas de Python:
- `selenium`: Para la automatización del navegador
- `webdriver-manager`: Para gestionar automáticamente la instalación del controlador de Chrome
- `requests`: Para operaciones HTTP (opcional)
- `pillow`: Para procesamiento de imágenes (opcional)

## Instalación

1. Clona o descarga este repositorio:
```bash
git clone <URL-del-repositorio>
cd screenshot-capture-system
```

2. Navega hasta la carpeta del proyecto:
```bash
cd c:\Users\adryl\Pictures\screenshot\screenshot-capture-system
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## Configuración

Puedes modificar la configuración en el archivo `src/utils/config.py`:

- `URL`: La dirección web de la que quieres tomar capturas
  - Default: "http://localhost:8080/game/details?host=unknown&port=6302"
  - Ejemplo: "https://www.ejemplo.com"

- `SAVE_DIRECTORY`: La carpeta donde se guardarán las imágenes
  - Default: "C:\Users\adryl\Pictures\screenshot\capturas"
  - Asegúrate de que la ruta exista o el programa la creará automáticamente

- `INTERVAL`: El tiempo en segundos entre cada captura
  - Default: 300 (5 minutos)
  - Puedes reducirlo para capturas más frecuentes o aumentarlo para capturas más espaciadas

- `WINDOW_SIZE`: La resolución de las capturas en formato "ancho,alto"
  - Default: "1920,1080"
  - Formatos comunes: "1366,768", "1280,720", "3840,2160" (4K)

## Uso

### Ejecución básica

Para ejecutar el programa:

```bash
cd c:\Users\adryl\Pictures\screenshot\screenshot-capture-system\src
python main.py
```

El programa mostrará información sobre su configuración y comenzará a tomar capturas automáticamente.

### Información mostrada durante la ejecución

Al iniciar el programa verás la siguiente información:
- URL que se está capturando
- Directorio donde se guardan las capturas
- Intervalo entre capturas
- Instrucciones para detener el programa

Por cada captura tomada, el programa mostrará:
- Timestamp de la captura
- Ruta completa donde se guardó la imagen
- Tiempo de espera hasta la próxima captura

### Detener el programa

Para detener el programa, simplemente presiona `Ctrl+C` en la terminal. El programa mostrará un mensaje de despedida y se cerrará correctamente.

## Estructura del proyecto

```
screenshot-capture-system/
├── requirements.txt      # Dependencias del proyecto
├── README.md             # Este archivo de documentación
└── src/                  # Código fuente
    ├── main.py           # Punto de entrada del programa
    ├── screenshot.py     # Funciones para tomar capturas
    └── utils/            # Utilidades y configuración
        └── config.py     # Configuración del sistema
```

## Funcionamiento interno

1. **Inicialización**:
   - El programa carga la configuración desde `config.py`
   - Verifica y crea el directorio de guardado si no existe
   - Muestra información sobre la configuración actual

2. **Captura de pantalla**:
   - Inicializa Chrome en modo headless (sin interfaz gráfica)
   - Navega a la URL especificada
   - Espera a que la página cargue completamente (3 segundos por defecto)
   - Toma la captura de pantalla
   - Guarda la imagen con un nombre basado en la fecha y hora actual
   - Cierra el navegador para liberar recursos

3. **Ciclo principal**:
   - Después de cada captura, el programa espera el tiempo especificado
   - El ciclo continúa hasta que el usuario detiene el programa con Ctrl+C

## Solución de problemas

### El programa no inicia o muestra errores

- Verifica que Chrome esté instalado correctamente
- Asegúrate de tener todas las dependencias instaladas con `pip install -r requirements.txt`
- Verifica que la URL sea accesible desde tu navegador normal

### Las capturas no muestran el contenido esperado

- Aumenta el tiempo de espera en `screenshot.py` (busca `time.sleep(3)` y aumenta el valor)
- Verifica que la URL sea correcta y que no requiera autenticación
- Comprueba que la página cargue correctamente en un navegador normal

### Errores con el WebDriver

Si ves errores relacionados con el WebDriver:
- Borra la carpeta `.wdm` en tu directorio de usuario y deja que el programa descargue de nuevo el controlador
- Actualiza Chrome a la última versión

## Personalización avanzada

### Cambiar el formato de la imagen

Actualmente el sistema guarda las imágenes en formato PNG. Si deseas cambiar el formato, modifica el nombre del archivo en la función `take_screenshot` en `screenshot.py`.

### Añadir autenticación

Si necesitas capturar páginas que requieren autenticación, puedes modificar la función `take_screenshot` para añadir cookies o completar formularios de inicio de sesión.

### Capturar diferentes secciones de la página

Puedes modificar el código en `screenshot.py` para capturar elementos específicos de la página en lugar de la página completa.

## Notas finales

- La primera ejecución puede tardar un poco mientras se descarga el driver adecuado para Chrome
- Asegúrate de que el sitio web o servidor esté funcionando antes de iniciar el programa
- El sistema está diseñado para ser ligero y consumir pocos recursos
- Las capturas de pantalla se guardan con alta resolución y sin compresión
- Si necesitas ejecutar el programa en segundo plano por largos períodos, considera usar un administrador de procesos como `nohup` en Linux o crear un servicio en Windows
│   └── utils
│       └── config.py    # Configuration settings for the application
├── requirements.txt      # Lists the project dependencies
├── README.md             # Documentation for the project
└── .gitignore            # Specifies files to ignore in Git
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd screenshot-capture-system
   ```

2. **Install the required dependencies:**
   ```
   pip install -r requirements.txt
   ```

3. **Configure the application:**
   - Open `src/utils/config.py` to set the desired URL and save directory for screenshots.

4. **Run the application:**
   ```
   python src/main.py
   ```

## Usage

The application will take a screenshot of the specified URL every 5 minutes and save it in the designated directory with a timestamped filename. To stop the application, press `Ctrl+C` in the terminal.

## Dependencies

- `selenium`: For browser automation.
- `webdriver-manager`: To manage the Chrome WebDriver automatically.

## Notes

- Ensure that Google Chrome is installed on your system.
- Make sure the local server hosting the specified URL is running before starting the application.