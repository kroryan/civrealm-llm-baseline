# Copyright (C) 2023  The CivRealm project
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

# Cargar variables de entorno desde el archivo .env
import os
from dotenv import load_dotenv
load_dotenv()

import pickle
import warnings
import gymnasium
import civrealm
from agents import BaselineLanguageAgent, AutoGPTAgent, BaseLangAgent, MastabaAgent
from civrealm.freeciv.utils.freeciv_logging import fc_logger
from civrealm.configs import fc_args
from civrealm.envs.freeciv_wrapper.llm_wrapper import LLMWrapper
from agents.utils import print_step, print_action, print_current
from agents import utils
from agents.rule_based_agent import RuleBasedAgent
from agents.civ_autogpt.GPTAgent import GPTAgent
import logging
import sys
import io

# Fix Unicode encoding issues system-wide

# Force stdout and stderr to use utf-8 encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Monkey patch the logging.StreamHandler emit method to handle Unicode characters
original_emit = logging.StreamHandler.emit
def patched_emit(self, record):
    try:
        original_emit(self, record)
    except UnicodeEncodeError:
        # Fallback for Unicode errors
        msg = self.format(record)
        msg = msg.encode('utf-8', errors='replace').decode('utf-8')
        stream = self.stream
        stream.write(msg + self.terminator)
        self.flush()

logging.StreamHandler.emit = patched_emit

# Configure logging to handle Unicode characters
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log', encoding='utf-8')
    ]
)

# Ensure the StreamHandler uses utf-8 encoding
for handler in logging.getLogger().handlers:
    if isinstance(handler, logging.StreamHandler):
        handler.setStream(sys.stdout)
        handler.stream.reconfigure(encoding='utf-8')

# Also set the logging configuration for the freeciv logger specifically
fc_logger.setLevel(logging.DEBUG)
for handler in fc_logger.handlers:
    if isinstance(handler, logging.StreamHandler):
        handler.setStream(sys.stdout)
        handler.stream.reconfigure(encoding='utf-8')

# FIXME: This is a hack to suppress the warning about the gymnasium spaces. Currently Gymnasium does not support hierarchical actions.
warnings.filterwarnings('ignore',
                        message='.*The obs returned by the .* method.*')


def main():
    """
    Main entry of the program.
    Starts a single-player Freeciv game against rule-based AI.
    """
    env = gymnasium.make('civrealm/FreecivBase-v0')
    env = LLMWrapper(env)
    agent = GPTAgent(model='ollama')

    observations, info = env.reset()
    done = False
    step = 0
    while not done:
        try:
            action = agent.act(observations, info)
            observations, reward, terminated, truncated, info = env.step(
                action)
            print(
                f'Step: {step}, Turn: {info["turn"]}, Reward: {reward}, Terminated: {terminated}, '
                f'Truncated: {truncated}, action: {action}')
            step += 1
            done = terminated or truncated
        except Exception as e:
            fc_logger.error(repr(e))
            raise e
    env.close()

if __name__ == '__main__':
    main()
