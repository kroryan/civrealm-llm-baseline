import os
import openai
import time
import random
import json
import requests
import warnings
import re

from civrealm.freeciv.utils.freeciv_logging import fc_logger
from .utils import num_tokens_from_messages, send_message_to_llama, send_message_to_vicuna, extract_json, send_message_to_llama, send_message_to_ollama, TOKEN_LIMIT_TABLE
from langchain.chat_models import ChatOpenAI, AzureChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryBufferMemory

import pinecone
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.llms import OpenAI, AzureOpenAI
from langchain.chains.question_answering import load_qa_chain
from agents.prompt_handlers.base_prompt_handler import BasePromptHandler

warnings.filterwarnings('ignore')

cwd = os.getcwd()
OPENAI_KEYS_FILE = os.path.join(cwd, "agents/civ_autogpt/openai_keys.txt")
SAVED_DIALOGUE_FILE = os.path.join(
    cwd, "agents/civ_autogpt/saved_dialogues/saved_dialogue.txt")
task_prompt_file = os.path.join(cwd,
                                "agents/civ_autogpt/prompts/task_prompt.txt")
GPT_MODEL_NAME = "gpt-3.5-turbo-16k"


class GPTAgent:
    """
    This agent uses GPT-3 to generate actions.
    """
    def __init__(self, model):
        self.model = model
        self.dialogue = []
        self.taken_actions_list = []
        self.message = ''
        self.retry_count = 0  # Initialize retry count

        self.openai_api_keys = self.load_openai_keys()
        self.prompt_handler = BasePromptHandler()
        self.state_prompt = self._load_state_prompt()
        self.task_prompt = self._load_task_prompt()

        # For Azure OpenAI API only
        self.deployment_name = os.environ['DEPLOYMENT_NAME']

        # Check if we're using Ollama
        api_type = os.environ.get('OPENAI_API_TYPE', '').lower()
        if api_type == 'ollama':
            # For Ollama, we don't need to initialize the OpenAI client
            llm = ChatOpenAI(temperature=0.7)  # Placeholder, won't be used
        elif api_type == 'azure':
            self.change_api_base('azure')
            llm = AzureChatOpenAI(openai_api_base=openai.api_base,
                                  openai_api_version=openai.api_version,
                                  openai_api_key=openai.api_key,
                                  openai_api_type=openai.api_type,
                                  deployment_name=self.deployment_name,
                                  temperature=0.7)
            self.chain = load_qa_chain(AzureOpenAI(
                deployment_name=self.deployment_name, model_name=self.model),
                                       chain_type="stuff")
        else:
            # Default to OpenAI
            self.change_api_base('openai')
            llm = ChatOpenAI(temperature=0.7, openai_api_key=openai.api_key)
            self.chain = load_qa_chain(OpenAI(model_name=GPT_MODEL_NAME),
                                       chain_type="stuff")

        self.memory = ConversationSummaryBufferMemory(llm=llm,
                                                      max_token_limit=500)

        # Initialize Pinecone only if not using Ollama
        if api_type != 'ollama':
            try:
                pinecone.init(api_key=os.environ["MY_PINECONE_API_KEY"],
                            environment=os.environ["MY_PINECONE_ENV"])

                self.index = Pinecone.from_existing_index(
                    index_name='langchain-demo',
                    embedding=OpenAIEmbeddings(model="text-embedding-ada-002"))
            except Exception as e:
                fc_logger.warning(f"Failed to initialize Pinecone: {str(e)}. Using Ollama without vector search.")
                self.index = None
        else:
            self.index = None

    def add_user_message_to_dialogue(self, message):
        self.dialogue.append({'role': 'user', 'content': message})

    def get_similiar_docs(self, query, k=2, score=False):
        index = self.index
        if score:
            similar_docs = index.similarity_search_with_score(query, k=k)
        else:
            similar_docs = index.similarity_search(query, k=k)
        return similar_docs

    def get_answer(self, query):
        # For Ollama or when index is not available, return a generic answer
        if self.index is None:
            fc_logger.info(f"Vector search not available, returning generic response for query: {query}")
            return f"Based on your question about '{query}', here's a general suggestion: When building a city, look for tiles with resources, preferably near rivers or on plains/grassland. For other actions, follow the game's strategic principles."
            
        # Standard Pinecone vector search for other configurations
        similar_docs = self.get_similiar_docs(query)
        while True:
            try:
                answer = self.chain.run(input_documents=similar_docs,
                                        question=query)
                break
            except Exception as e:
                fc_logger.error(f'Error in get_answer: {str(e)}')
                fc_logger.error(f'similar_docs: {similar_docs}')
                fc_logger.error(f'query: {query}')
                self.update_openai_api_key()
        return answer

    def change_api_base(self, to_type):
        openai.api_type = to_type
        if to_type == 'azure':
            openai.api_version = os.environ["OPENAI_API_VERSION"]
            openai.api_base = os.environ["OPENAI_API_BASE"]
            openai.api_key = os.environ["OPENAI_API_KEY"]
        else:
            assert openai.api_type == "openai"
            openai.api_version = ""
            openai.api_base = 'https://api.openai.com/v1'
            self.update_openai_api_key()

    @staticmethod
    def load_openai_keys():
        with open(OPENAI_KEYS_FILE, "r") as f:
            context = f.read()
        return context.split('\n')

    def _load_state_prompt(self):
        state_prompt = self.prompt_handler.state_prompt()
        self.add_user_message_to_dialogue(state_prompt)
        return state_prompt

    def _load_task_prompt(self):
        task_prompt = self.prompt_handler.task_prompt()
        self.add_user_message_to_dialogue(task_prompt)
        return task_prompt

    def load_saved_dialogue(self, load_path=SAVED_DIALOGUE_FILE):
        # print("reading task prompt from {}".format(task_prompt_file))
        with open(load_path, "r") as f:
            self.dialogue = eval(f.read())

    def save_dialogue_to_file(self, save_path=SAVED_DIALOGUE_FILE):
        with open(save_path, "w", encoding='utf-8') as f:
            for message in self.dialogue:
                f.write(str(message) + '\n')

    def update_openai_api_key(self):
        if openai.api_type != 'openai':
            return

        curr_key = self.openai_api_keys[0]
        openai.api_key = os.environ["OPENAI_API_KEY"] = curr_key
        self.openai_api_keys.pop(0)
        self.openai_api_keys.append(curr_key)

    def check_if_the_taken_actions_list_needed_update(self,
                                                      check_content,
                                                      check_num=3,
                                                      top_k_charactors=0):
        if top_k_charactors == 0:
            if len(self.taken_actions_list) >= check_num:
                for i in range(check_num):
                    if self.taken_actions_list[-1 - i] == check_content:
                        if i == check_num - 1:
                            return True
                        else:
                            continue
                    else:
                        return False

            return False
        else:
            if len(self.taken_actions_list) >= check_num:
                for i in range(check_num):
                    if self.taken_actions_list[
                            -1 - i][:top_k_charactors] == check_content:
                        if i == check_num - 1:
                            return True
                        else:
                            continue
                    else:
                        return False

            return False

    def process_command(self, command_json, obs_input_prompt,
                        current_unit_name, current_avail_actions):
        '''
        manualAndHistorySearch
        askCurrentGameInformation
        finalDecision
        '''
        fc_logger.debug(f'Processing command: {command_json}')
        try:
            command_input = command_json['command']['input']
            command_name = command_json['command']['name']
        except Exception as e:
            print(e)
            print('Not in given json format, retrying...')
            if random.random() > 0.5:
                self.update_dialogue(obs_input_prompt +
                                     self.prompt_handler.insist_json(),
                                     pop_num=2)
                return None
            else:
                self.update_dialogue(obs_input_prompt, pop_num=2)
                return None
        if (command_name == 'finalDecision') and command_input['action']:
            # Here to implement controller
            print(command_input)
            exec_action = command_input['action']

            # Verificar si la acción está en la lista de acciones disponibles
            if exec_action not in current_avail_actions:
                print('Not in the available action list, retrying...')
                
                # Si el modelo recomienda consistentemente la misma acción no disponible
                # o si ya hemos intentado demasiadas veces, usar un fallback
                if self.check_if_the_taken_actions_list_needed_update(exec_action, 2, 0) or \
                   (hasattr(self, 'retry_count') and self.retry_count > 2):
                    # Usar la función utilitaria para seleccionar una acción fallback válida
                    from .utils.interact_with_ollama import select_fallback_action
                    
                    # Crear un diálogo simplificado para select_fallback_action
                    simple_dialogue = [
                        {'role': 'user', 'content': f'available action list is {current_avail_actions}'}
                    ]
                    fallback_action = select_fallback_action(simple_dialogue)
                    
                    # Si el fallback sigue sin estar en las acciones disponibles, elegir la primera de la lista
                    if fallback_action not in current_avail_actions and current_avail_actions:
                        fallback_action = current_avail_actions[0]
                    
                    self.add_user_message_to_dialogue(
                        f"The action '{exec_action}' is not available. Choosing '{fallback_action}' instead from: {current_avail_actions}.")
                    fc_logger.info(f"Using fallback action '{fallback_action}' instead of unavailable '{exec_action}'")
                    self.taken_actions_list = []
                    self.retry_count = 0  # Reset retry count
                    return fallback_action
                
                # Incrementar contador de reintentos
                if not hasattr(self, 'retry_count'):
                    self.retry_count = 1
                else:
                    self.retry_count += 1
                    
                # Insistir en que el modelo elija una acción disponible
                emphasis_prompt = f"IMPORTANT: Your action '{exec_action}' is not in the available action list. " + \
                                 f"Please select only from these available actions: {current_avail_actions}. " + \
                                 "You must choose a valid action."
                
                # Añadir el mensaje con énfasis y reintentar
                self.update_dialogue(obs_input_prompt + emphasis_prompt, pop_num=2)
                return None
            else:
                # La acción es válida, procesarla normalmente
                self.taken_actions_list.append(exec_action)
                self.retry_count = 0  # Reset retry count
                
                # Evaluar la calidad de la decisión tomada
                from .utils.strategic_analysis import analizar_calidad_decision
                puntuacion, razon = analizar_calidad_decision(exec_action, obs_input_prompt, current_avail_actions)
                fc_logger.info(f"Calidad de decisión para {current_unit_name}: {puntuacion}/10 - {razon}")
                
                # En lugar de añadir mensajes al diálogo, usamos la información para
                # ajustar estrategias internas (registrando en logs)
                if puntuacion < 5:
                    fc_logger.warning(f"Decisión subóptima detectada: '{exec_action}'. {razon}")
                    # Podríamos implementar un sistema de memoria para recordar malas decisiones
                    # pero NO añadimos mensajes artificiales al diálogo
                
                # Comprobar si estamos repitiendo demasiado la misma acción
                if self.check_if_the_taken_actions_list_needed_update('goto', 15, 4) or \
                   self.check_if_the_taken_actions_list_needed_update('keep_activity', 15, 0):
                    # En lugar de añadir un mensaje al diálogo, modificamos directamente el prompt
                    # para la próxima interacción
                    fc_logger.warning(f"Detectada repetición excesiva de acción: {exec_action}")
                    # Podríamos implementar una forma de diversificar acciones sin depender de mensajes
                    variation_prompt = obs_input_prompt + \
                        "\nIMPORTANT: You seem to be repeating the same action multiple times. " + \
                        "Consider exploring different strategies and actions to make progress in the game."
                    self.update_dialogue(variation_prompt, pop_num=2)
                    self.taken_actions_list = []
                    return None
                else:
                    print('exec_action:', exec_action)
                    return exec_action

        elif command_name == 'askCurrentGameInformation' and command_input[
                'query']:
            print(command_input)
            self.taken_actions_list.append('askCurrentGameInformation')
            return None

        elif command_name == 'manualAndHistorySearch' and command_input[
                'look_up']:
            print(command_input)

            if self.check_if_the_taken_actions_list_needed_update(
                    'look_up', 3, 0):
                answer = self.prompt_handler.generate("finish_look_for")
                print('answer:', answer)
                self.add_user_message_to_dialogue(answer)
                self.taken_actions_list = []
            else:
                query = command_input['look_up']
                answer = self.get_answer(query)
                print('answer:', answer)
                if random.random() > 0.5:
                    self.add_user_message_to_dialogue(
                        answer + self.prompt_handler.finish_look_for())
                else:
                    self.add_user_message_to_dialogue(answer)

                self.memory.save_context({'assistant': query},
                                         {'user': answer})
                self.taken_actions_list.append('look_up')

            return None
        else:
            print('error')
            print(command_json)

            if random.random() < 0.8:
                self.dialogue.pop(-1)
            else:
                self.add_user_message_to_dialogue(
                    'You should only use the given commands!')
            # self.update_dialogue(obs_input_prompt, pop_num = 1)

            return None

    def query(self, stop=None, temperature=0.7, top_p=0.95):
        self.restrict_dialogue()
        # TODO add retreat mech to cope with rate limit
        self.update_openai_api_key()

        fc_logger.debug(f'Querying with dialogue: {self.dialogue}')

        if self.model in ['gpt-3.5-turbo-0301', 'gpt-3.5-turbo']:
            assert openai.api_type == 'openai'
            response = openai.ChatCompletion.create(model=self.model,
                                                    messages=self.dialogue,
                                                    temperature=temperature,
                                                    top_p=top_p)
        elif self.model in ["gpt-35-turbo", "gpt-35-turbo-16k"]:
            assert openai.api_type == 'azure'
            response = openai.ChatCompletion.create(
                deployment_id=self.deployment_name,
                model=self.model,
                messages=self.dialogue)
        
        elif self.model in ['ollama', 'qwen3:latest']:
            local_config = {
                'temperature': temperature,
                'top_p': top_p,
                'repetition_penalty': 1.1
            }
            response = send_message_to_ollama(self.dialogue, local_config)

        elif self.model in ['vicuna-33B', 'Llama2-70B-chat']:
            local_config = {
                'temperature': temperature,
                'top_p': top_p,
                'repetition_penalty': 1.1
            }
            response = send_message_to_vicuna(self.dialogue, local_config)

        elif self.model in ['Llama2-70B-chat']:
            local_config = {
                'temperature': temperature,
                'top_p': top_p,
                'repetition_penalty': 1.1
            }
            response = send_message_to_llama(self.dialogue, local_config)

        else:
            response = openai.Completion.create(model=self.model,
                                                prompt=str(self.dialogue),
                                                max_tokens=1024,
                                                stop=stop,
                                                temperature=temperature,
                                                n=1,
                                                top_p=top_p)

        return response

    def update_dialogue(self, chat_content, pop_num=0):
        if pop_num != 0:
            for i in range(pop_num):
                self.dialogue.pop(-1)

        return self.communicate(chat_content)

    def parse_response(self, response):
        fc_logger.debug(f'Parsing response: {response}')

        if self.model in [
                'gpt-3.5-turbo-0301', 'gpt-3.5-turbo', 'gpt-4', 'gpt-4-0314'
        ]:
            return dict(response["choices"][0]["message"])

        elif self.model in ["gpt-35-turbo", "gpt-35-turbo-16k"]:
            try:
                ans = self.extract_json(
                    response['choices'][0]['message']['content'])
            except:
                return response["choices"][0]["message"]
            return {'role': 'assistant', 'content': ans}
            
        elif self.model in ['ollama', 'qwen3:latest']:
            extracted = self.extract_json(response)
            return {'role': 'assistant', 'content': extracted}

        elif self.model in ['vicuna-33B', 'Llama2-70B-chat']:
            return {'role': 'assistant', 'content': self.extract_json(response)}

        else:
            # self.model in ['text-davinci-003', 'code-davinci-002']
            return {
                'role': 'assistant',
                'content': response["choices"][0]["text"][2:]
            }

    def restrict_dialogue(self):
        """
        Limits the dialogue context to prevent it from growing too large.
        For OpenAI models, uses token counting. For other models like Ollama,
        uses a simple message count approach.
        """
        # For Ollama and other non-OpenAI models, use a simpler approach based on message count
        if self.model in ['ollama', 'qwen3:latest', 'vicuna-33B', 'Llama2-70B-chat']:
            # Keep only the last 20 messages for local models
            max_messages = 20
            if len(self.dialogue) > max_messages:
                # Save the last message if it's from the user
                temp_message = None
                if self.dialogue[-1]['role'] == 'user':
                    temp_message = self.dialogue[-1]
                
                # Keep only essential context and the most recent messages
                essential_messages = self.dialogue[:2]  # Keep initial prompts
                recent_messages = self.dialogue[-(max_messages-2):]  # Keep recent conversation
                self.dialogue = essential_messages + recent_messages
                
                # Add back the user message if it was saved
                if temp_message and self.dialogue[-1] != temp_message:
                    self.dialogue.append(temp_message)
            
            return

        # For OpenAI models, use token counting
        try:
            limit = TOKEN_LIMIT_TABLE.get(self.model, 4096)
            
            while num_tokens_from_messages(self.dialogue, self.model) >= limit:
                temp_message = {}
                user_tag = 0
                if self.dialogue[-1]['role'] == 'user':
                    temp_message = self.dialogue[-1]
                    user_tag = 1

                while len(self.dialogue) >= 3:
                    self.dialogue.pop(-1)

                while True:
                    try:
                        self.add_user_message_to_dialogue(
                            'The former chat history can be summarized as: \n' +
                            self.memory.load_memory_variables({})['history'])
                        break
                    except Exception as e:
                        print(e)
                        self.update_openai_api_key()

                if user_tag == 1:
                    self.dialogue.append(temp_message)
                    user_tag = 0
        except Exception as e:
            fc_logger.warning(f"Error in token counting: {str(e)}. Falling back to message count based restriction.")
            # Fallback to message count based approach
            if len(self.dialogue) > 20:
                essential_messages = self.dialogue[:2]
                recent_messages = self.dialogue[-18:]
                self.dialogue = essential_messages + recent_messages

    def communicate(self, content, parse_choice_tag=False):
        self.add_user_message_to_dialogue(content)
        while True:
            try:
                raw_response = self.query()
                self.message = self.parse_response(raw_response)
                self.dialogue.append(self.message)

                # Get the response content
                response = self.message["content"]
                
                # If response is already a dictionary (from Ollama), use it directly
                if isinstance(response, dict):
                    return response
                    
                # Otherwise try to parse it as JSON
                try:
                    response = json.loads(response)
                except Exception as e:
                    fc_logger.error(f"Error parsing JSON response: {str(e)}")
                    self.add_user_message_to_dialogue(
                        'You should only respond in JSON format as described')
                    fc_logger.debug('Not response json, retrying...')
                    continue
                    
                break

            except Exception as e:
                fc_logger.debug(f'Error in communicate: {str(e)}')
                fc_logger.debug(f'content: {content}')
                fc_logger.error(f"Error communicating with LLM: {str(e)}")
                
                # Return a fallback response after several retries
                if hasattr(self, 'retry_count') and self.retry_count > 3:
                    fc_logger.debug("Too many retries, returning fallback response")
                    return {
                        "command": {
                            "name": "finalDecision",
                            "input": {
                                "action": "keep activity"
                            }
                        }
                    }
                    
                # Increment retry count
                if not hasattr(self, 'retry_count'):
                    self.retry_count = 1
                else:
                    self.retry_count += 1
                    
                fc_logger.debug(f"Retrying... (attempt {self.retry_count})")
                continue
                
        # Reset retry count after successful response
        self.retry_count = 0
        return response

    def reset(self):

        self.dialogue = []
        self.message = ''
        self.taken_actions_list = []

        self.openai_api_keys = self.load_openai_keys()
        self.state_prompt = self._load_state_prompt()
        self.task_prompt = self._load_task_prompt()

    def act(self, observations, info):
        """
        Process observations and info to decide on an action using the LLM.
        This method is called by the environment at each step.
        """
        available_actions = info['available_actions']
        for ctrl_type in available_actions.keys():
            if ctrl_type in info['llm_info']:
                for actor_id, actor_dict in info['llm_info'][ctrl_type].items():
                    actor_name = actor_dict['name']
                    current_obs = actor_dict['observations']['minimap']
                    
                    # Get available actions for this actor
                    actor_actions = actor_dict['available_actions']
                    if not actor_actions:
                        continue
                    
                    # Determine unit type from name for enhanced context
                    unit_type = "unknown"
                    if "Settlers" in actor_name:
                        unit_type = "Settlers"
                    elif "Workers" in actor_name:
                        unit_type = "Workers"
                    elif "Explorer" in actor_name:
                        unit_type = "Explorer"
                    
                    # Extract key resources and terrain from current tile
                    current_tile_info = []
                    resources = []
                    terrain_types = []
                    
                    # Extract information from the current tile observation
                    if 'current_tile' in current_obs:
                        current_tile_info = current_obs['current_tile']
                        for item in current_tile_info:
                            if any(resource in item for resource in ["Gold", "Iron", "Coal", "Wheat", "Silk", "Whale", "Resources", "Pheasant", "Fish"]):
                                resources.append(item)
                            if any(terrain in item for terrain in ["Plains", "Grassland", "Hills", "Mountains", "Forest", "Desert", "Ocean", "River", "Swamp"]):
                                terrain_types.append(item)
                    
                    # Create a more informative prompt
                    obs_input_prompt = f"""The {ctrl_type} is {actor_name} ({unit_type}), currently on {', '.join(terrain_types) if terrain_types else 'unknown terrain'}{' with ' + ', '.join(resources) if resources else ''}. 

Complete observation is {current_obs}.

Your available action list is {actor_actions}. 

IMPORTANT: You can ONLY choose actions from this list. Do not suggest any action that is not in this list.

"""
                    
                    # Add unit-specific strategic advice
                    if unit_type == "Settlers":
                        obs_input_prompt += """For Settlers, your priorities should be:
1. Build cities on or near resources, especially near rivers or on plains/grassland
2. If no good city location is found, move towards unexplored areas or areas with resources
3. Avoid building on desert or ocean tiles"""
                    elif unit_type == "Workers":
                        obs_input_prompt += """For Workers, your priorities should be:
1. Build irrigation on plains/grassland, especially those with resources
2. Build mines on hills, especially those with resources
3. Build roads to connect cities
4. If no improvements are needed, move towards unexplored areas or where improvements will be needed"""
                    elif unit_type == "Explorer":
                        obs_input_prompt += """For Explorers, your priorities should be:
1. Explore unexplored areas (tiles showing as 'unexplored')
2. Look for good city locations and resources
3. Move towards mountain/hill tiles for better visibility"""
                    
                    fc_logger.info(f'Processing {ctrl_type} {actor_name} with {len(actor_actions)} actions')
                    
                    # Get action from LLM
                    exec_action = self.communicate(obs_input_prompt)
                    try:
                        # Process the command to get an actual action
                        action_name = self.process_command(exec_action, obs_input_prompt, actor_name, actor_actions)
                        if action_name:
                            fc_logger.info(f'Chosen action for {actor_name}: {action_name}')
                            return (ctrl_type, actor_id, action_name)
                    except Exception as e:
                        fc_logger.error(f'Error choosing action: {str(e)}')
                        # If there's an error, try another actor
                        continue
        
        # If no action could be determined, return None to end the turn
        return None

    def extract_json(self, response):
        """
        Extract JSON from response text. Enhanced to better handle Ollama responses.
        """
        try:
            # Handle case where response is already a valid JSON object
            if isinstance(response, dict):
                return response
                
            # First look for standard JSON pattern
            if '{' in response and '}' in response:
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                json_str = response[start_idx:end_idx]
                
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    # Try to clean up the JSON string
                    cleaned_json = re.sub(r'```json\s*|\s*```', '', json_str)
                    cleaned_json = re.sub(r'```\s*|\s*```', '', cleaned_json)
                    
                    try:
                        return json.loads(cleaned_json)
                    except json.JSONDecodeError:
                        pass
            
            # Handle plain text responses from Ollama
            # Look for direct action patterns
            action_pattern = r'(?:action|decision|move|build|goto|cultivate|plant|join|fortify)[\s:"\']+([a-zA-Z0-9_ ]+)'
            match = re.search(action_pattern, response, re.IGNORECASE)
            if match:
                action = match.group(1).strip()
                # Construct a JSON-like structure
                return {
                    "command": {
                        "name": "finalDecision",
                        "input": {
                            "action": action
                        }
                    }
                }
                
            # If no JSON found, create a generic response structure
            fc_logger.warning(f"Could not extract JSON from response: {response}")
            return {
                "command": {
                    "name": "finalDecision",
                    "input": {
                        "action": "keep activity"
                    }
                }
            }
            
        except Exception as e:
            fc_logger.error(f"Error extracting JSON: {str(e)}")
            return {
                "command": {
                    "name": "finalDecision",
                    "input": {
                        "action": "keep activity"
                    }
                }
            }
