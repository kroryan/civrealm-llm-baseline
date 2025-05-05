import json
import re
from civrealm.freeciv.utils.freeciv_logging import fc_logger

def extract_json(text):
    """
    Extract JSON from text, with enhanced handling for Ollama response formats.
    
    Args:
        text: The text to extract JSON from
    
    Returns:
        A dictionary with extracted JSON data or a default response
    """
    if not text:
        return default_command_json()
    
    # If text is already a JSON string, parse it
    if isinstance(text, str) and text.startswith('{') and text.endswith('}'):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    
    # If input is already a dictionary, return it directly
    if isinstance(text, dict):
        return text
    
    # Find JSON block in code blocks (```json...``` format)
    if isinstance(text, str):
        json_block_match = re.search(r'```(?:json)?\s*({.*?})\s*```', text, re.DOTALL)
        if json_block_match:
            json_string = json_block_match.group(1)
            try:
                json_data = json.loads(json_string)
                fc_logger.debug(f"Successfully parsed JSON from code block")
                return json_data
            except json.JSONDecodeError:
                fc_logger.debug("Failed to parse JSON from code block, trying general extraction")
        
        # Standard JSON extraction
        start_index = text.find("{")
        end_index = text.rfind("}") + 1
        
        if start_index == -1 or end_index == 0:
            # No JSON found, try to extract an action from plain text
            return extract_action_from_text(text)
        
        json_string = text[start_index:end_index]
        
        try:
            json_data = json.loads(json_string)
            fc_logger.debug(f"Successfully parsed JSON")
            return json_data
        except json.JSONDecodeError:
            # Try to clean the JSON string
            try:
                # Remove any newlines, tabs, and extra spaces
                cleaned_json = json_string.replace('\n', ' ').replace('\t', ' ')
                # Replace escaped quotes with regular quotes
                cleaned_json = cleaned_json.replace('\\"', '"').replace("\\'", "'")
                # Fix unbalanced braces if needed
                brace_diff = cleaned_json.count('{') - cleaned_json.count('}')
                if brace_diff > 0:
                    cleaned_json += '}' * brace_diff
                elif brace_diff < 0:
                    cleaned_json = '{' * abs(brace_diff) + cleaned_json
                
                # Try to parse the cleaned JSON
                json_data = json.loads(cleaned_json)
                fc_logger.debug(f"Successfully parsed cleaned JSON")
                return json_data
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract an action from the text
                return extract_action_from_text(text)
    
    # Fallback
    return default_command_json()

def extract_action_from_text(text):
    """
    Extract an action from plain text response when JSON parsing fails.
    
    Args:
        text: The text to extract an action from
    
    Returns:
        A dictionary with command structure containing the extracted action
    """
    fc_logger.debug(f"Extracting action from plain text")
    
    # Common patterns for action mentions in text
    action_patterns = [
        r'(?:action|decision)[\s:]+["\']?([a-zA-Z0-9 _]+)["\']?',
        r'(?:choose|select|use|perform)[\s:]+["\']?([a-zA-Z0-9 _]+)["\']?',
        r'(?:move|build|explore|keep)[\s:]+["\']?([a-zA-Z0-9 _]+)["\']?',
        r'I [a-z]+ (?:to )?(?:choose|select|use|perform) ["\']?([a-zA-Z0-9 _]+)["\']?'
    ]
    
    for pattern in action_patterns:
        if isinstance(text, str):
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                action = match.group(1).strip()
                fc_logger.debug(f"Extracted action from text: {action}")
                return {
                    "command": {
                        "name": "finalDecision",
                        "input": {
                            "action": action
                        }
                    }
                }
    
    # If no specific action found, return a default command
    fc_logger.debug("No action found in text, using default")
    return default_command_json()

def default_command_json():
    """Return a default command JSON for fallback"""
    return {
        "command": {
            "name": "finalDecision",
            "input": {
                "action": "keep activity"
            }
        }
    }
