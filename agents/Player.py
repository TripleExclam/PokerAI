from abc import ABC, abstractmethod


class Player(ABC):
    def __init__(self, uuid):
        self.cards = []
        self.stack = 0
        self.uuid = uuid

    def set_cards(self, cards):
        assert len(cards) == 2, "Cards should be dealt in pairs"
        self.cards = cards

    def add_stack(self, stack):
        self.stack = max(0, self.stack + stack)

    def __eq__(self, o: object) -> bool:
        return o is Player and o.uuid == self.uuid

    def __hash__(self) -> int:
        return self.uuid

    @abstractmethod
    def act(self, game_state, actions_avail):
        pass
