import random
from agents.Player import Player


class RandomPlayer(Player):
    def __init__(self, uuid):
        super(RandomPlayer, self).__init__(uuid)

    def act(self, game_state, actions_avail):
        return random.choice(actions_avail)
