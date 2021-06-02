from game.Poker import *
from agents.PlayerShell import *
from util.Node import *
import matplotlib.pyplot as plt


class GameWrapper:

    def __init__(self):
        self.game_states = {}
        self.players = [
            PlayerShell(1),
            PlayerShell(2)
        ]
        self.game = Poker(self.players, 2, 10, True)
        self.actions = []

    def hole_card_state(self, game, player):
        suited = 'o'
        if Card.get_suit_int(player.cards[0]) == Card.get_suit_int(player.cards[1]):
            suited = 's'
        card_rep = Card.STR_RANKS[Card.get_rank_int(player.cards[0])] + \
                   Card.STR_RANKS[Card.get_rank_int(player.cards[1])] + suited
        act_map = {Action.FOLD: "F", Action.CALL: "C", Action.BET1BB: "",
                   Action.BET3BB: "B", Action.ALLIN: "AI"}

        acts = str([','.join([act_map[i[0]] for i in y if i[0] != Action.BET1BB]) for x, y in game.history.items()])
        return card_rep, player.uuid, acts

    def train(self, iterations, print_interval=1000):
        ''' Do ficticious self-play to find optimal strategy'''
        util = 0.0
        utils = []
        for i in range(iterations):
            utils.append(util / (i + 1))
            if i % print_interval == 0 and i != 0:
                print("\rP1 expected value after %i iterations: %f" % (i, util / i))

            # Start a game
            game = self.game.copy()
            actions = self.start_game(game)
            util += self.cfr(actions, game, 1, 1)

        plt.plot(range(iterations), utils)
        plt.xlabel('iteration')
        plt.ylabel('average utility')
        plt.savefig('ranges/util_trend.png')
        return util / iterations

    def get_strategy(self):
        """
        Gives the action played by each player based on the game states
        """
        result = {}
        #
        events = {(1, "['', '']"): "1BET",  # P1 acts first
                  (2, "['C', '']"): "2BET",  # P2 responds to a call from P1
                  (2, "['B', '']"): "2CALLB",  # P2 responds to a bet from P1
                  (2, "['AI', '']"): "2CALLAI",  # P2 responds to a All-in from P1
                  (1, "['C', 'B']"): "1CALLB",  # P1 responds to a bet from P2
                  (1, "['C', 'AI']"): "1CALLAI"}  # P1 responds to an all in from P2
        for event in events.values():
            result[event] = {}
            if "BET" in event:
                result[event[0] + "ALLIN"] = {}
                result[event[0] + "CALL"] = {}
                result[event[0] + "FOLD"] = {}

        for state, node in self.game_states.items():
            hand = state[0]
            event = events[state[1], state[2]]
            if "BET" in events[state[1], state[2]]:
                result[event][hand] = node.strategy_[Action.BET3BB]
                result[event[0] + "ALLIN"][hand] = node.strategy_[Action.ALLIN]
                result[event[0] + "CALL"][hand] = node.strategy_[Action.CALL]
                result[event[0] + "FOLD"][hand] = node.strategy_[Action.FOLD]
            else:
                result[event][hand] = node.strategy_[Action.CALL]

        return result

    def evaluation(self, game):
        reward = sum(game.bets.values())
        p1 = game.players[game.player_list.pos]
        p2 = game.players[1 - game.player_list.pos]
        pair1 = Card.get_rank_int(p1.cards[0]) == Card.get_rank_int(p1.cards[1])
        pair2 = Card.get_rank_int(p2.cards[0]) == Card.get_rank_int(p2.cards[1])
        higher = Card.get_rank_int(p1.cards[1]) > Card.get_rank_int(p2.cards[1])
        equal = Card.get_rank_int(p1.cards[1]) == Card.get_rank_int(p2.cards[1])

        if (pair1 and not pair2) or (pair1 and pair2 and higher) \
                or (not pair1 and not pair2 and higher):
            return reward - game.bets[p1.uuid]
        elif (pair2 and pair1 and equal) or (not pair1 and not pair2 and equal):
            return (reward / 2) - game.bets[p1.uuid]
        else:
            return -game.bets[p1.uuid]

    def cfr(self, actions, game, p1, p2):
        player = game.player_list.pos

        probability_weight = p1 if player == 0 else p2

        # Check if state is terminal
        if game.player_list.visited_all():
            # Direct payout
            return self.evaluation(game)

        # Current game state
        state = self.hole_card_state(game, game.player_list.rotation[player])
        if state in self.game_states:
            node = self.game_states[state]  # Get our node if it already exists
            actions = node.actions_
        else:
            # Create new Node with possible actions we can perform
            node = Node(actions)
            self.game_states[state] = node

        strategy = node.get_strategy(probability_weight)
        util = dict()
        node_util = 0
        # for each of our possible actions, compute the utility of it
        # thus, finding the overall utility of this current state
        for action in actions:
            next_game = game.copy()  # Duplicate game
            next_actions = next_game.step_bets([x for x in actions], action)  # Make action

            if player == 0:
                util[action] = -self.cfr(next_actions, next_game, p1 * strategy[action], p2)
            else:
                util[action] = -self.cfr(next_actions, next_game, p1, p2 * strategy[action])

            node_util += strategy[action] * util[action]

        # compute regret and update Game State for the node based on utility of all actions
        for action in actions:
            regret = util[action] - node_util
            if player == 0:
                node.regret_sum_[action] += regret * p2
            else:
                node.regret_sum_[action] += regret * p1

        return node_util

    def start_game(self, game):
        game.all_in = False
        game.players = [x.copy() for x in self.game.players]
        game.player_list = PlayerList(game.players)
        game.reset_bets()
        game.deal_cards()

        game.history = {player.uuid: [] for player in game.players}
        game.step_blind(False)  # Small blind
        game.step_blind(True)  # Big Blind

        return [Action.FOLD, Action.CALL] + game.BET_ACTIONS  # First round allows players to respond to blinds
