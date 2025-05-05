import random
from civrealm.agents.base_agent import BaseAgent
from civrealm.freeciv.utils.freeciv_logging import fc_logger

class RuleBasedAgent(BaseAgent):
    def __init__(self):
        super().__init__()

    def random_action_by_name(self, valid_action_dict, name):
        """
        Return a random action whose name contains the input name.
        """
        action_choices = [
            key for key in valid_action_dict.keys() if name in key
        ]
        if action_choices:
            return random.choice(action_choices)
        else:
            return None

    def act(self, observations, info):
        """
        Choose an action for the first valid actor who has not acted yet.
        """
        unit_actor, unit_action_dict = self.get_next_valid_actor(
            observations, info, 'unit')
        fc_logger.info(f'Observations: {observations}')
        fc_logger.info(f'Info: {info}')
        fc_logger.info(f'Valid actions for unit {unit_actor}: {unit_action_dict}')
        
        if not unit_actor:
            fc_logger.info('No valid unit actor found. Ending turn.')
            return None

        # Try to build a city with 80% probability
        build_action = self.random_action_by_name(unit_action_dict, 'build')
        if build_action and random.random() > 0.2:
            fc_logger.info(f'Chosen action: Build city with unit {unit_actor}')
            return 'unit', unit_actor, build_action

        # Otherwise, choose a random move action
        move_action = self.random_action_by_name(unit_action_dict, 'goto')
        if move_action:
            fc_logger.info(f'Chosen action: Move unit {unit_actor} to {move_action}')
            return 'unit', unit_actor, move_action

        # If no valid action is found, return None
        fc_logger.info(f'No valid actions for unit {unit_actor}. Ending turn.')
        return None