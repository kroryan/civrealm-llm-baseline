# BaseLang & Mastaba: Civrealm-LLM-Agents
BaseLang and Mastaba are two LLM-based agents for the reinforcement learning environment [CivRealm](https://www.github.com/bigai-ai/civrealm). BaseLand and Mastaba share a similar interface to CivRealm over standard Gymnasium, as provided in CivRealm. BaseLang implements a paraallel controller on each unit individually and Mastaba uses an "advisor" to lead them all. Both agent models are presented in the paper of CivRealm.

## Prerequisit
`civrealm` from [CivRealm](https://www.github.com/bigai-ai/civrealm).
The list `requirements.txt` in the repository.

## USAGE:
1. Install civrealm properly with correct freeciv-web. (See [CivRealm](https://www.github.com/bigai-ai/civrealm))

2. Prepare the LLM's to use (GPT api key or local LLM URL)

3. Prepare a `PINECONE` API Key.

4. Set env varibles.

```
# Use AZURE_OPENAI_API_TYPE="azure" to use Azure LLM, otherwise use "openai"
export AZURE_OPENAI_API_TYPE="<your_open_api_type>"
export AZURE_OPENAI_API_VERSION='<your_openai_api_version>'
export AZURE_OPENAI_API_BASE='<your_openai_api_base>'
export AZURE_OPENAI_API_KEY='<your_openai_api_key>'
export LOCAL_LLM_URL='<if_need_local_llm_inference>'
export MY_PINECONE_API_KEY='<your_pinecone_api_key>'
export MY_PINECONE_ENV='<your_pinecone_env_name>'
```

5. Execute the code.
`python main.py`

## Actualizaciones recientes

### Agente basado en reglas (`RuleBasedAgent`)
Se ha implementado un agente simple basado en reglas que toma decisiones siguiendo estas reglas:
1. Selecciona el primer actor válido que no haya actuado en el turno actual.
2. Intenta construir una ciudad con una probabilidad del 80%.
3. Si no puede construir una ciudad, elige una acción de movimiento válida.

Este agente es útil para probar el entorno y garantizar que el flujo del juego funcione correctamente.

### Registros detallados
Se han añadido registros (`logs`) para inspeccionar cómo los agentes toman decisiones. Estos registros incluyen:
- Observaciones y acciones disponibles.
- Decisiones tomadas por el agente basado en reglas.
- Prompts enviados al modelo de lenguaje (en agentes basados en LLM).
- Respuestas generadas por el modelo de lenguaje.

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
```

### Cómo habilitar los registros
Para habilitar más detalles en los registros, puedes configurar el nivel de registro en el archivo principal:
```python
import logging
fc_logger.setLevel(logging.DEBUG)
```

### Cómo ejecutar el agente basado en reglas
1. Asegúrate de que el entorno esté configurado correctamente.
2. Ejecuta el script principal:
   ```
   python main.py
   ```
3. Observa los registros en la consola para entender cómo el agente toma decisiones.

### Cómo ejecutar un agente basado en LLM
1. Configura el modelo en el archivo `.env`:
   ```
   OLLAMA_MODEL=hf.co/soob3123/amoral-gemma3-4B-v2-qat-Q4_0-GGUF:latest
   ```
2. Asegúrate de que el modelo esté disponible en Ollama:
   ```
   ollama pull hf.co/soob3123/amoral-gemma3-4B-v2-qat-Q4_0-GGUF:latest
   ollama serve
   ```
3. Ejecuta el script principal y observa los registros para entender cómo el modelo toma decisiones.
