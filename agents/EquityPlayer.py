from treys import Card

from agents.Player import Player
from game.Action import Action
from util.montecarlo import Evaluation


class EquityPlayer(Player):
    def __init__(self, uuid, iters=10000, mbe=0.3, mce=0.2):
        super(EquityPlayer, self).__init__(uuid)
        self.iters = iters
        self.min_bet_equity = mbe
        self.min_call_equity = mce

    @staticmethod
    def eval_hand(cards, hole_cards, n_players, iters=10000):
        """
        Translate alpha numerica cards to numeric and run montecarlo
        """
        CARD_RANKS_ORIGINAL = '23456789TJQKA'
        SUITS_ORIGINAL = 'CDHS'
        evaluator = Evaluation()
        c_str = Card.int_to_str(cards[0])
        card1 = [CARD_RANKS_ORIGINAL.find(c_str[0]), SUITS_ORIGINAL.find(c_str[1])]
        c_str = Card.int_to_str(cards[1])
        card2 = [CARD_RANKS_ORIGINAL.find(c_str[0]), SUITS_ORIGINAL.find(c_str[1])]

        table_cards_numeric = []
        for table_card in hole_cards:
            c_str = Card.int_to_str(table_card)
            table_cards_numeric.append([CARD_RANKS_ORIGINAL.find(c_str[0]), SUITS_ORIGINAL.find(c_str[1])])

        equity = evaluator.run_evaluation(card1=card1, card2=card2, tablecards=table_cards_numeric,
                                               iterations=iters, player_amount=n_players)

        return equity

    def act(self, game_state, actions_avail):
        equity_alive = self.eval_hand(self.cards, game_state["board"], len(game_state["history"]))
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
