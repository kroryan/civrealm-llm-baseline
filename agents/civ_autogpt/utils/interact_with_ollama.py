import json
import requests
import os
import re
from civrealm.freeciv.utils.freeciv_logging import fc_logger
from .strategic_analysis import mejorar_prompt_estrategico, analizar_calidad_decision

def send_message_to_ollama(dialogue, config=None):
    """
    Send a message to Ollama API and get the response.
    
    Args:
        dialogue (list): A list of dictionaries with 'role' and 'content' keys
        config (dict, optional): Configuration options like temperature, top_p, etc.
    
    Returns:
        str: The response from the model
    """
    # Default configuration if none provided
    if config is None:
        config = {
            'temperature': 0.7,
            'top_p': 0.95,
            'repetition_penalty': 1.1
        }
    
    # Extract the model name from environment variable or use default
    model_name = os.environ.get("OLLAMA_MODEL", "qwen3:latest")
    
    # Ollama API endpoint (default is localhost:11434)
    ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    api_url = f"{ollama_host}/api/chat"
    
    # Pre-process dialogue to add a reminder about action constraints when needed
    processed_dialogue = preprocess_messages_for_action_constraints(dialogue)
    
    # Convert dialogue format to Ollama format
    messages = []
    for msg in processed_dialogue:
        # Skip system messages if they have empty content
        if msg['role'] == 'system' and not msg['content'].strip():
            continue
            
        # Handle case where content is already a dictionary (from previous Ollama responses)
        if isinstance(msg['content'], dict):
            # Convert dict to string to avoid Ollama API errors
            msg_content = json.dumps(msg['content'])
        else:
            msg_content = msg['content']
            
        messages.append({
            'role': msg['role'],
            'content': msg_content
        })
    
    # Prepare the request payload
    payload = {
        'model': model_name,
        'messages': messages,
        'options': {
            'temperature': config.get('temperature', 0.7),
            'top_p': config.get('top_p', 0.95),
            'num_predict': 1024  # Increase token limit
        },
        'stream': False
    }
    
    # Send request to Ollama API
    try:
        # Log the request for debugging
        fc_logger.debug(f"Sending request to Ollama API at {api_url}")
        fc_logger.debug(f"Using model: {model_name}")
        
        # Limit the log size to avoid excessive output
        if len(str(messages)) > 500:
            message_summary = f"[{len(messages)} messages, first: '{messages[0]['content'][:100]}...', last: '{messages[-1]['content'][:100]}...']"
            fc_logger.debug(f"Messages: {message_summary}")
        else:
            fc_logger.debug(f"Messages: {messages}")
        
        response = requests.post(api_url, json=payload, timeout=60)  # Increased timeout from 30 to 60 seconds
        
        if response.status_code != 200:
            fc_logger.error(f"Ollama API returned status code {response.status_code}: {response.text}")
            return json.dumps({
                "command": {
                    "name": "finalDecision",
                    "input": {
                        "action": select_fallback_action(dialogue)  # Use intelligent fallback
                    }
                }
            })
        
        result = response.json()
        
        if 'message' not in result or 'content' not in result['message']:
            fc_logger.error(f"Unexpected Ollama API response format: {result}")
            return json.dumps({
                "command": {
                    "name": "finalDecision",
                    "input": {
                        "action": select_fallback_action(dialogue)  # Use intelligent fallback
                    }
                }
            })
        
        content = result['message']['content']
        
        # Try to find JSON in the response content
        if '{' in content and '}' in content:
            try:
                # Check if the response already contains valid JSON
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                json_str = content[json_start:json_end]
                
                # Validate the JSON
                _ = json.loads(json_str)
                
                # If we get here, it's valid JSON, so return the content as is
                return content
            except json.JSONDecodeError:
                # Not valid JSON, so format as JSON
                fc_logger.debug(f"Response contains invalid JSON, wrapping in JSON format: {content[:200]}...")
                return format_result_as_json(content, dialogue)
        else:
            # No JSON found, format as JSON
            fc_logger.debug(f"Response doesn't contain JSON, wrapping in JSON format: {content[:200]}...")
            return format_result_as_json(content, dialogue)
        
    except requests.exceptions.Timeout:
        fc_logger.error("Request to Ollama API timed out")
        return json.dumps({
            "command": {
                "name": "finalDecision",
                "input": {
                    "action": select_fallback_action(dialogue)  # Use intelligent fallback
                }
            }
        })
    except requests.exceptions.ConnectionError:
        fc_logger.error("Could not connect to Ollama API")
        return json.dumps({
            "command": {
                "name": "finalDecision",
                "input": {
                    "action": select_fallback_action(dialogue)  # Use intelligent fallback
                }
            }
        })
    except Exception as e:
        fc_logger.error(f"Error communicating with Ollama: {str(e)}")
        return json.dumps({
            "command": {
                "name": "finalDecision",
                "input": {
                    "action": select_fallback_action(dialogue)  # Use intelligent fallback
                }
            }
        })

# Function to select a valid fallback action from available actions
def select_fallback_action(dialogue):
    """
    Selects a valid action from the available actions list in the dialogue.
    Falls back to "produce Settlers" for cities or "keep activity" otherwise if no actions found.
    """
    # Extract available actions from the dialogue
    available_actions = []
    for msg in reversed(dialogue):
        if msg['role'] == 'user' and 'available action list is' in msg['content']:
            # Extract the list of available actions
            match = re.search(r'available action list is \[(.*?)\]', msg['content'], re.IGNORECASE)
            if match:
                actions_text = match.group(1)
                # Parse the actions
                available_actions = [action.strip(" '\"") for action in actions_text.split(',')]
                break
    
    # If no available actions found or list is empty, use defaults
    if not available_actions:
        # Check if this is a city action
        is_city = any('city' in msg['content'] for msg in dialogue if msg['role'] == 'user')
        return "produce Settlers" if is_city else "keep activity"
    
    # Prioritize actions based on type - useful defaults for different scenarios
    if "produce Settlers" in available_actions:
        return "produce Settlers"
    elif "build city" in available_actions:
        return "build city"
    elif "irrigation" in available_actions:
        return "irrigation"
    elif "build road" in available_actions:
        return "build road"
    elif "mine" in available_actions:
        return "mine"
    elif any(action.startswith("move") for action in available_actions):
        # Find any move action
        move_actions = [action for action in available_actions if action.startswith("move")]
        return move_actions[0]  # Return the first move action
    else:
        # Just return the first available action
        return available_actions[0]

def preprocess_messages_for_action_constraints(dialogue):
    """
    Preprocesa los mensajes del diálogo para mejorar el comportamiento del modelo
    añadiendo recordatorios sobre las limitaciones de acciones disponibles y consejos estratégicos.
    """
    # Crear una copia para no modificar el original
    processed_dialogue = dialogue.copy()
    
    # Solo procesar si hay al menos un mensaje
    if not processed_dialogue:
        return processed_dialogue
    
    # Buscar el último mensaje del usuario que contiene información sobre acciones disponibles
    last_action_msg_idx = -1
    available_actions = None
    
    for i in range(len(processed_dialogue) - 1, -1, -1):
        msg = processed_dialogue[i]
        if msg['role'] == 'user' and 'available action list' in msg['content'].lower():
            # Extraer la lista de acciones disponibles usando una expresión regular
            match = re.search(r'available action list is \[(.*?)\]', msg['content'], re.IGNORECASE)
            if match:
                actions_str = match.group(1)
                # Convertir la cadena de acciones en una lista
                available_actions = [action.strip(" '\"") for action in actions_str.split(',')]
                last_action_msg_idx = i
                break
    
    # Si encontramos un mensaje con acciones disponibles, usar nuestro mejorador de prompts estratégicos
    if last_action_msg_idx >= 0 and available_actions:
        return mejorar_prompt_estrategico(processed_dialogue, last_action_msg_idx, available_actions)
    
    return processed_dialogue

def format_result_as_json(text, dialogue=None):
    """Format text response as a JSON with action decision"""
    
    # Try to extract an action decision from the text using a more comprehensive pattern
    action_match = re.search(r'(?:action|decision|move|build|choose|goto|cultivate|plant|join|fortify|produce)[\s:"\']+([a-zA-Z0-9 _]+)', text, re.IGNORECASE)
    
    if action_match:
        action = action_match.group(1).strip()
        # Clean up the action by removing quotes and extra spaces
        action = action.strip('"\'').strip()
        
        # Attempt to map free-form text to valid game actions
        action_mapping = {
            'north': 'move North',
            'south': 'move South',
            'east': 'move East', 
            'west': 'move West',
            'northeast': 'move NorthEast',
            'northwest': 'move NorthWest',
            'southeast': 'move SouthEast',
            'southwest': 'move SouthWest',
            'build a city': 'build city',
            'city': 'build city',
            'road': 'build road',
            'keep': 'keep activity',
            'irrigate': 'irrigation',
            'settlers': 'produce Settlers',
            'warriors': 'produce Warriors',
            'barracks': 'produce Barracks'
        }
        
        # Check if the extracted action needs to be mapped
        for key, value in action_mapping.items():
            if key.lower() in action.lower():
                action = value
                break
                
        # Log extracted action for debugging
        fc_logger.debug(f"Extracted action from text response: '{action}'")
        
        # Verify that the action is valid by checking available actions
        if dialogue:
            available_actions = []
            for msg in reversed(dialogue):
                if msg['role'] == 'user' and 'available action list is' in msg['content']:
                    match = re.search(r'available action list is \[(.*?)\]', msg['content'], re.IGNORECASE)
                    if match:
                        actions_text = match.group(1)
                        available_actions = [a.strip(" '\"") for a in actions_text.split(',')]
                        break
            
            # If action is not in available actions, use fallback
            if available_actions and action not in available_actions:
                fc_logger.warning(f"Action '{action}' not in available actions: {available_actions}")
                action = select_fallback_action(dialogue)
                fc_logger.debug(f"Using fallback action: '{action}'")
    else:
        # Try to find any movement direction in the text
        direction_match = re.search(r'\b(north|south|east|west|northeast|northwest|southeast|southwest)\b', text, re.IGNORECASE)
        if direction_match:
            direction = direction_match.group(1).capitalize()
            if direction.lower() in ['northeast', 'northwest', 'southeast', 'southwest']:
                # Capitalize the second part for compound directions
                direction = direction[:1].upper() + direction[1:].replace('east', 'East').replace('west', 'West')
            action = f"move {direction}"
            fc_logger.debug(f"Extracted direction from text: 'move {direction}'")
        else:
            # Default to a safe action if no specific action found
            action = select_fallback_action(dialogue) if dialogue else "keep activity"
            fc_logger.debug(f"No specific action found in response, defaulting to: '{action}'")
    
    # Create a JSON string with the extracted action
    json_response = {
        "command": {
            "name": "finalDecision",
            "input": {
                "action": action
            }
        }
    }
    
    # Log the final JSON response for debugging
    fc_logger.debug(f"Formatted JSON response: {json.dumps(json_response)}")
    
    return json.dumps(json_response)

def format_error_as_json(error_message):
    """Format error message as JSON with a fallback action"""
    json_response = {
        "command": {
            "name": "finalDecision",
            "input": {
                "action": "keep activity"
            }
        },
        "error": error_message
    }
    
    return json.dumps(json_response)