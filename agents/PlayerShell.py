from agents.Player import *


class PlayerShell(Player):
    def copy(self):
        player = PlayerShell(self.uuid)
        player.stack = self.stack
        return player

    def act(self, game_state, actions_avail):
        raise NotImplementedError
