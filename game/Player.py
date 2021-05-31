import random
from abc import ABC, abstractmethod

from treys import Card

from game.Action import Action
from util.montecarlo import Evaluation


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


class RandomPlayer(Player):
    def __init__(self, uuid):
        super(RandomPlayer, self).__init__(uuid)

    def act(self, game_state, actions_avail):
        return random.choice(actions_avail)


class EquityPlayer(Player):
    CARD_RANKS_ORIGINAL = '23456789TJQKA'
    SUITS_ORIGINAL = 'CDHS'

    def __init__(self, uuid, iters=10000, mbe=0.3, mce=0.2):
        super(EquityPlayer, self).__init__(uuid)
        self.iters = iters
        self.evaluator = Evaluation()
        self.min_bet_equity = mbe
        self.min_call_equity = mce

    def eval_hand(self, hole_cards, n_players):
        """
        Translate alpha numerica cards to numeric and run montecarlo
        """
        c_str = Card.int_to_str(self.cards[0])
        card1 = [self.CARD_RANKS_ORIGINAL.find(c_str[0]), self.SUITS_ORIGINAL.find(c_str[1])]
        c_str = Card.int_to_str(self.cards[1])
        card2 = [self.CARD_RANKS_ORIGINAL.find(c_str[0]), self.SUITS_ORIGINAL.find(c_str[1])]
        
        table_cards_numeric = []
        for table_card in hole_cards:
            c_str = Card.int_to_str(table_card)
            table_cards_numeric.append([self.CARD_RANKS_ORIGINAL.find(c_str[0]), self.SUITS_ORIGINAL.find(c_str[1])])

        equity = self.evaluator.run_evaluation(card1=card1, card2=card2, tablecards=table_cards_numeric,
                                               iterations=self.iters, player_amount=n_players)

        return equity

    def act(self, game_state, actions_avail):
        equity_alive = self.eval_hand(game_state["board"], len(game_state["history"]))
        increment1 = .1
        increment2 = .2

        if equity_alive > self.min_bet_equity + increment2 and Action.ALLIN in actions_avail:
            action = Action.ALLIN
        elif equity_alive > self.min_bet_equity + increment1 and Action.BET5BB in actions_avail:
            action = Action.BET5BB
        elif equity_alive > self.min_bet_equity and Action.BET3BB in actions_avail:
            action = Action.BET3BB
        elif equity_alive > self.min_bet_equity - increment1 and Action.BET1BB in actions_avail:
            action = Action.BET1BB
        elif equity_alive > self.min_call_equity and Action.CALL in actions_avail:
            action = Action.CALL
        elif Action.CHECK in actions_avail:
            action = Action.CHECK
        else:
            action = Action.FOLD

        return action
