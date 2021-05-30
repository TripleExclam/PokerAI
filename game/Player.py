import random
from abc import ABC, abstractmethod


class Player(ABC):
    def __init__(self, uuid):
        self.cards = []
        self.stack = 0
        self.uuid = uuid

    def set_cards(self, cards):
        assert len(cards) == 2, "Cards should be dealt in pairs"
        self.cards = cards

    def get_cards(self):
        return self.cards

    def add_stack(self, stack):
        self.stack = max(0, self.stack + stack)

    def reward(self, amount):
        self.stack += amount
        if self.stack <= 0:
            print("BUST")

    def __eq__(self, o: object) -> bool:
        return o is Player and o.uuid == self.uuid

    def __hash__(self) -> int:
        return self.uuid

    @abstractmethod
    def act(self, game_state, actions_avail):
        pass


class RandomPlayer(Player):
    def __init__(self, uuid):
        super(RandomPlayer, self).__init__(uuid)

    def act(self, game_state, actions_avail):
        return random.choice(actions_avail)
