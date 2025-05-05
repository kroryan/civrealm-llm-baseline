import random
from civrealm.agents.base_agent import BaseAgent

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
        if not unit_actor:
            return None

        # Try to build a city with 80% probability
        build_action = self.random_action_by_name(unit_action_dict, 'build')
        if build_action and random.random() > 0.2:
            return 'unit', unit_actor, build_action

        # Otherwise, choose a random move action
        move_action = self.random_action_by_name(unit_action_dict, 'goto')
        if move_action:
            return 'unit', unit_actor, move_action

        # If no valid action is found, return None
        return None