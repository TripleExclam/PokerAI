from enum import Enum


class Action(Enum):
    FOLD = (0, 0)
    CHECK = (1, 0)
    CALL = (2, 0)
    BET1BB = (3, 1)
    BET3BB = (4, 3)
    BET4BB = (5, 4)
    BET5BB = (6, 5)
    ALLIN = (7, float('inf'))

    def __init__(self, value, bet_mul):
        """
        :param value: Unique identifier
        :param bet_mul: Bet multiplier if it exists
        """
        self.id = value
        self.bet_mul = bet_mul
