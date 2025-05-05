import os
import random
import json
import time
import requests

from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryBufferMemory

from civrealm.freeciv.utils.freeciv_logging import fc_logger
from agents.prompt_handlers.base_prompt_handler import BasePromptHandler

from .base_worker import BaseWorker


class OllamaWorker(BaseWorker):
    """
    This agent uses Ollama with the qwen3:latest model to generate actions.
    """
    def __init__(self,
                 model: str = 'qwen3:latest',
                 prompt_prefix: str = "civ_prompts",
                 **kwargs):
        self.prompt_prefix = prompt_prefix
        self.ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.ollama_model = os.environ.get("OLLAMA_MODEL", "qwen3:latest")
        super().__init__(model, **kwargs)

    def init_prompts(self):
        self.prompt_handler = BasePromptHandler(
            prompt_prefix=self.prompt_prefix)
        self._load_instruction_prompt()
        self._load_task_prompt()

    def init_llm(self):
        # Usar ConversationBufferMemory que no requiere un LLM
        from langchain.memory import ConversationBufferMemory

        # Configurar la memoria sin necesidad de un modelo de lenguaje
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.chain = None

    def init_index(self):
        # Skip Pinecone initialization for Ollama
        self.index = None
    
    def _load_instruction_prompt(self):
        instruction_prompt = self.prompt_handler.instruction_prompt()
        self.add_user_message_to_dialogue(instruction_prompt)

    def _load_task_prompt(self):
        task_prompt = self.prompt_handler.task_prompt()
        self.add_user_message_to_dialogue(task_prompt)

    def register_all_commands(self):
        self.register_command('finalDecision',
                              self.handle_command_final_decision)
        self.register_command('suggestion', self.handle_command_suggestion)

    def handle_command_suggestion(self, command_input, obs_input_prompt,
                                  current_avail_actions):
        exec_action = command_input["suggestion"]
        return exec_action, ''

    def handle_command_final_decision(self, command_input, obs_input_prompt,
                                      current_avail_actions):
        exec_action = command_input['action']
        lower_avail_actions = [x.lower() for x in current_avail_actions]
        if exec_action.lower() not in lower_avail_actions:
            print(f'{self.name}\'s chosen action "{exec_action}" not in the ' +
                  f'available action list, available actions are ' +
                  f'{current_avail_actions}, retrying...')
            fc_logger.error(
                f'{self.name}\'s chosen action "{exec_action}"',
                'not in the available action list, available',
                f'actions are {current_avail_actions}, retrying...')
            return None, self.prompt_handler.insist_avail_action()

        self.taken_actions_list.append(command_input['action'])

        for move_name in current_avail_actions:
            if move_name[:4] != "move":
                continue
            if self.taken_actions_list_needs_update(move_name, 15, 4):
                return None, self.prompt_handler.insist_various_actions(
                    action=move_name)

        return exec_action, ''

    def query_llm(self, stop=None, temperature=0.7, top_p=0.95):
        fc_logger.debug(f'Querying Ollama with dialogue: {self.dialogue}')
        
        api_url = f"{self.ollama_host}/api/chat"
        
        # Prepare payload for Ollama API
        payload = {
            "model": self.ollama_model,
            "messages": self.dialogue,
            "options": {
                "temperature": temperature,
                "top_p": top_p
            }
        }
        
        try:
            response = requests.post(api_url, json=payload)
            response.raise_for_status()
            result = response.json()
            return {
                "choices": [
                    {
                        "message": {
                            "content": result["message"]["content"]
                        }
                    }
                ]
            }
        except Exception as e:
            fc_logger.error(f"Error connecting to Ollama: {str(e)}")
            # Return a fallback response
            return {
                "choices": [
                    {
                        "message": {
                            "content": f"{{\"command\": {{\"name\": \"finalDecision\", \"input\": {{\"action\": \"{current_avail_actions[0] if current_avail_actions else ''}\"}}}}}}",
                        }
                    }
                ]
            }

    def generate_command(self, prompt: str):
        self.add_user_message_to_dialogue(prompt +
                                          self.prompt_handler.insist_json())
        self.restrict_dialogue()
        response = self.query_llm()
        return response

    def parse_response(self, response):
        content = response['choices'][0]['message']['content']
        try:
            # Try to extract JSON from the response
            start_index = content.find('{')
            end_index = content.rfind('}') + 1
            if start_index >= 0 and end_index > start_index:
                json_content = content[start_index:end_index]
                # Fix unbalanced braces
                rlack = json_content.count("{") - json_content.count("}")
                if rlack > 0:
                    json_content = json_content + "}" * rlack
                elif rlack < 0:
                    json_content = "{" * abs(rlack) + json_content
                return json.loads(json_content)
            else:
                raise ValueError("No JSON found in response")
        except Exception as e:
            fc_logger.error(f"Error parsing JSON response: {str(e)}")
            # Provide a fallback response
            return {"command": {"name": "finalDecision", "input": {"action": ""}}}

    def process_command(self, response, obs_input_prompt,
                        current_avail_actions):
        # First try to parse the response by the given json format
        fc_logger.debug(f'Processing response: {response}')
        try:
            command_json = self.parse_response(response)
            command_input = command_json['command']['input']
            command_name = command_json['command']['name']
        except Exception as e:
            fc_logger.error(
                f'\nRESPONSE:{response}\nCommand json parsing error: {e}')
            print('Not in given json format, retrying...')
            return None, self.prompt_handler.insist_json()

        # Then check if the command is valid
        if command_name not in self.command_handlers:
            fc_logger.error(f'Unknown command: {command_name}')
            available_commands = ', '.join(self.command_handlers.keys())
            prompt_addition = self.prompt_handler.insist_available_commands(
                available_commands)
            return None, prompt_addition

        return self.command_handlers[command_name](command_input,
                                                 obs_input_prompt,
                                                 current_avail_actions)
                                                 
    def get_answer_from_index(self, query):
        # Simplified version for Ollama without Pinecone
        return f"I found information about '{query}' in my knowledge base."

    def save_dialogue_to_file(self, save_path):
        """
        Save the dialogue to a file.
        
        Args:
            save_path: The path to save the file to
        """
        try:
            with open(save_path, "w", encoding='utf-8') as f:
                for message in self.dialogue:
                    f.write(str(message) + '\n')
            print(f"Dialogue saved to {save_path}")
        except Exception as e:
            fc_logger.error(f"Error saving dialogue to file: {str(e)}")
            print(f"Error saving dialogue to file: {str(e)}")

    def choose_action(self, obs_input_prompt, current_avail_actions):
        """
        Choose an action based on the observation input prompt and available actions.
        
        Args:
            obs_input_prompt: The observation input prompt
            current_avail_actions: The list of available actions
            
        Returns:
            str: The chosen action
        """
        while True:
            try:
                response = self.generate_command(obs_input_prompt)
                exec_action, prompt_addition = self.process_command(
                    response, obs_input_prompt, current_avail_actions)
                
                if exec_action is not None:
                    return exec_action
                
                if prompt_addition:
                    obs_input_prompt += prompt_addition
            except Exception as e:
                fc_logger.error(f"Error in choose_action: {str(e)}")
                print(f"Error in choose_action: {str(e)}")
                # Fallback to a random action if an error occurs
                if current_avail_actions:
                    return random.choice(current_avail_actions)
                else:
                    return "no_action"

    def restrict_dialogue(self):
        """
        Restrict the dialogue history to prevent it from growing too large.
        We'll keep only the last 10 messages to avoid context length issues.
        """
        # Simple implementation for Ollama - keep last 10 messages
        max_messages = 10
        if len(self.dialogue) > max_messages:
            # Keep the system prompt if it exists and the last messages
            system_messages = [msg for msg in self.dialogue if msg['role'] == 'system']
            recent_messages = self.dialogue[-max_messages:]
            
            # Reconstruct dialogue with system messages first, then recent messages
            self.dialogue = system_messages + [msg for msg in recent_messages if msg['role'] != 'system']