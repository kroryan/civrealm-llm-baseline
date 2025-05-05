# BaseLang & Mastaba: Civrealm-LLM-Agents
BaseLang and Mastaba are two LLM-based agents for the reinforcement learning environment [CivRealm](https://www.github.com/bigai-ai/civrealm). BaseLand and Mastaba share a similar interface to CivRealm over standard Gymnasium, as provided in CivRealm. BaseLang implements a parallel controller on each unit individually and Mastaba uses an "advisor" to lead them all. Both agent models are presented in the paper of CivRealm.

## Prerequisites
`civrealm` from [CivRealm](https://www.github.com/bigai-ai/civrealm).
The list `requirements.txt` in the repository.

## USAGE:
1. Pull the Freeciv-web Docker image:
```
docker pull krory90/freeciv-web:lastest
docker tag krory90/freeciv-web:lastest krory90/freeciv-web:lastest
```

2. Clone the CivRealm repository and start the Freeciv-web server:
```
git clone https://github.com/kroryan/civrealm
cd civrealm/src/civrealm/configs
docker compose up -d freeciv-web
```

3. Clone this repository:
```
git clone https://github.com/kroryan/civrealm-llm-baseline
```

4. Set up your environment variables (see below for details).

5. Run the application:
```
python main.py
```

# Environment Variables Setup

## Recent Updates

### Rule-Based Agent (`RuleBasedAgent`)
A simple rule-based agent has been implemented that makes decisions following these rules:
1. Selects the first valid actor that hasn't acted in the current turn.
2. Tries to build a city with an 80% probability.
3. If it can't build a city, it chooses a valid movement action.

This agent is useful for testing the environment and ensuring that the game flow works correctly.

### Optimizations for Local Models (Ollama)
Significant improvements have been implemented for using local models via Ollama:

1. **Increased Timeouts**: The system now waits up to 60 seconds (instead of 30) for model responses, avoiding disconnections in complex situations.

2. **Intelligent Error Handling**: Implementation of a fallback system that selects valid actions when:
   - The Ollama API doesn't respond (timeout)
   - There are connection problems with the model
   - The model suggests invalid actions

3. **Message Preprocessing**: Improved prompt formatting to optimize performance with local models.

4. **Robust JSON Extraction**: Improvements in command detection and extraction in text responses.

### Strategic Analysis System
A comprehensive strategic analysis system has been added to evaluate game quality:

1. **Game Situation Analysis**: Automatically extracts important contextual information:
   - Nearby resources (gold, iron, wheat, etc.)
   - Terrain types (plains, hills, rivers, etc.)
   - Present units
   - Unexplored areas

2. **Decision Quality Evaluation**: Rating of each agent decision on a scale of 0-10:
   - Contextual analysis (e.g., founding cities near resources receives a high score)
   - Score based on game phase and unit type
   - Detailed explanation of reasoning

3. **Personalized Strategic Advice**: The system automatically provides specific advice based on:
   - Unit type (Settlers, Workers, etc.)
   - Nearby resources and terrain
   - Available actions
   - Game phase

### Fully Autonomous Agent
The system has been enhanced to function completely autonomously:

1. **Independent Decision Making**: The agent analyzes the context and makes decisions without requiring human intervention.

2. **Communication through System Messages**: Strategic advice is provided as system messages, not as simulated user messages.

3. **Automatic Detection and Correction**: If the agent repeats the same action too much or makes suboptimal decisions, the system automatically adjusts the context to improve the quality of future decisions.

4. **Monitoring through Logs**: The system thoroughly records each decision and its strategic evaluation, allowing for later analysis of game quality.

### How to Run with Ollama (Local Models)
1. Configure the model in the environment variables:
   ```
   export OPENAI_API_TYPE="ollama"
   export OLLAMA_MODEL="hf.co/soob3123/amoral-gemma3-4B-v2-qat-Q4_0-GGUF:latest"
   export OLLAMA_HOST="http://localhost:11434"
   ```
2. Make sure Ollama is started and the model is available:
   ```
   ollama pull hf.co/soob3123/amoral-gemma3-4B-v2-qat-Q4_0-GGUF:latest
   ollama serve
   ```
3. Run the main script:
   ```
   python main.py
   ```

---

## Actualizaciones recientes (Spanish Version)

### Agente basado en reglas (`RuleBasedAgent`)
Se ha implementado un agente simple basado en reglas que toma decisiones siguiendo estas reglas:
1. Selecciona el primer actor válido que no haya actuado en el turno actual.
2. Intenta construir una ciudad con una probabilidad del 80%.
3. Si no puede construir una ciudad, elige una acción de movimiento válida.

Este agente es útil para probar el entorno y garantizar que el flujo del juego funcione correctamente.

### Optimizaciones para modelos locales (Ollama)
Se han implementado mejoras significativas para el uso de modelos locales mediante Ollama:

1. **Timeouts aumentados**: Ahora el sistema espera hasta 60 segundos (en lugar de 30) por respuestas del modelo, evitando desconexiones en situaciones complejas.

2. **Manejo inteligente de errores**: Implementación de un sistema de fallback que selecciona acciones válidas cuando:
   - La API de Ollama no responde (timeout)
   - Hay problemas de conexión con el modelo
   - El modelo sugiere acciones no válidas

3. **Preprocesamiento de mensajes**: Mejora del formato de los prompts para optimizar el rendimiento con modelos locales.

4. **Extracción robusta de JSON**: Mejoras en la detección y extracción de comandos en respuestas de texto.

### Sistema de análisis estratégico
Se ha añadido un completo sistema de análisis estratégico para evaluar la calidad del juego:

1. **Análisis de situación del juego**: Extrae automáticamente información contextual importante:
   - Recursos cercanos (oro, hierro, trigo, etc.)
   - Tipos de terreno (llanuras, colinas, ríos, etc.) 
   - Unidades presentes
   - Áreas inexploradas

2. **Evaluación de calidad de decisiones**: Calificación de cada decisión del agente en una escala de 0-10:
   - Análisis contextual (ej: fundar ciudades cerca de recursos recibe puntuación alta)
   - Puntuación basada en fase del juego y tipo de unidad
   - Explicación detallada del razonamiento

3. **Consejos estratégicos personalizados**: El sistema proporciona automáticamente consejos específicos según:
   - Tipo de unidad (Settlers, Workers, etc.)
   - Recursos y terreno cercanos
   - Acciones disponibles
   - Fase del juego

### Agente totalmente autónomo
El sistema ha sido mejorado para funcionar de manera completamente autónoma:

1. **Toma de decisiones independiente**: El agente analiza el contexto y toma decisiones sin requerir intervención humana.

2. **Comunicación a través de mensajes del sistema**: Los consejos estratégicos se proporcionan como mensajes del sistema, no como mensajes simulados de usuario.

3. **Detección y corrección automática**: Si el agente repite demasiado la misma acción o toma decisiones subóptimas, el sistema ajusta automáticamente el contexto para mejorar la calidad de las decisiones futuras.

4. **Monitorización mediante logs**: El sistema registra detalladamente cada decisión y su evaluación estratégica, permitiendo analizar la calidad del juego posteriormente.

### Registros detallados
Se han añadido registros (`logs`) para inspeccionar cómo los agentes toman decisiones. Estos registros incluyen:
- Observaciones y acciones disponibles.
- Decisiones tomadas por el agente basado en reglas.
- Prompts enviados al modelo de lenguaje (en agentes basados en LLM).
- Respuestas generadas por el modelo de lenguaje.
- Evaluación estratégica de cada decisión (puntuación y razonamiento)

#### Ejemplo de salida de registros:
```
INFO: Observations: {...}
INFO: Info: {...}
INFO: Valid actions for unit 101: {'build_city': {...}, 'goto_2': {...}}
INFO: Chosen action: Build city with unit 101
INFO: Observation input prompt: {...}
INFO: Available actions: ['build_city', 'goto_2']
INFO: Model response: {"command": {"name": "finalDecision", "input": {"action": "build_city"}}}
INFO: Chosen action: build_city
INFO: Calidad de decisión para city 121: 9/10 - Excelente decisión producir Settlers al inicio para expandir tu imperio.
```

### Cómo habilitar los registros
Para habilitar más detalles en los registros, puedes configurar el nivel de registro en el archivo principal:
```python
import logging
fc_logger.setLevel(logging.DEBUG)
```

### Cómo ejecutar con Ollama (modelos locales)
1. Configura el modelo en las variables de entorno:
   ```
   export OPENAI_API_TYPE="ollama"
   export OLLAMA_MODEL="hf.co/soob3123/amoral-gemma3-4B-v2-qat-Q4_0-GGUF:latest"
   export OLLAMA_HOST="http://localhost:11434"
   ```
2. Asegúrate de que Ollama esté iniciado y el modelo esté disponible:
   ```
   ollama pull hf.co/soob3123/amoral-gemma3-4B-v2-qat-Q4_0-GGUF:latest
   ollama serve
   ```
3. Ejecuta el script principal:
   ```
   python main.py
   ```

### Cómo interpretar los resultados de evaluación estratégica
Los logs incluyen evaluaciones como:
```
INFO: Calidad de decisión para Settlers 102: 8/10 - Buen movimiento hacia área inexplorada (North).
INFO: Calidad de decisión para ciudad 121: 4/10 - Coinage proporciona oro inmediato pero no es una inversión a largo plazo.
```

Estas evaluaciones califican cada decisión y proporcionan un razonamiento, permitiéndote:
1. Identificar decisiones subóptimas
2. Comprender el razonamiento estratégico
3. Evaluar el rendimiento general del agente LLM

## Configuraciones avanzadas

### Ajuste de prompts estratégicos
Puedes modificar los consejos estratégicos en `agents/civ_autogpt/utils/strategic_analysis.py`:

```python
def mejorar_prompt_estrategico(processed_dialogue, last_action_msg_idx, available_actions):
    # Personaliza los consejos estratégicos según tus preferencias
    ...
```

### Personalización del sistema de evaluación
Para ajustar los criterios de evaluación, modifica la función `analizar_calidad_decision` en el mismo archivo:

```python
def analizar_calidad_decision(accion, contexto, acciones_disponibles):
    # Modifica los pesos y criterios de evaluación
    ...
```
