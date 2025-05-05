import json
import requests
import os

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
    
    # Convert dialogue format to Ollama format
    messages = []
    for msg in dialogue:
        # Skip system messages if they have empty content
        if msg['role'] == 'system' and not msg['content'].strip():
            continue
        messages.append({
            'role': msg['role'],
            'content': msg['content']
        })
    
    # Prepare the request payload
    payload = {
        'model': model_name,
        'messages': messages,
        'options': {
            'temperature': config.get('temperature', 0.7),
            'top_p': config.get('top_p', 0.95)
        },
        'stream': False
    }
    
    # Send request to Ollama API
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        result = response.json()
        return result['message']['content']
    except Exception as e:
        print(f"Error communicating with Ollama: {str(e)}")
        return f"Error: {str(e)}"