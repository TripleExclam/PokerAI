from game.Poker import *
from agents.PlayerShell import *
from util.Node import *


class GameWrapper:

    def __init__(self):
        self.game_states = {}
        self.players = [
            PlayerShell(1),
            PlayerShell(2)
        ]
        self.game = Poker(self.players, 20, 10000, True)
        self.actions = []

    def hole_card_state(self, game, player):
        opponent_acts = [str(y) for x, y in game.history.items() if x != player.uuid]
        return ','.join(opponent_acts) + ','.join([Card.int_to_str(x) for x in player.cards])

    def train(self, iterations, print_interval=1000):
        ''' Do ficticious self-play to find optimal strategy'''
        util = 0.0

        for i in range(iterations):
            if i % print_interval == 0 and i != 0:
                print("\rP1 expected value after %i iterations: %f" % (i, util / i))
                for state, item in self.game_states.items():
                    if item.strategy_[Action.FOLD] != 1 / len(item.strategy_.values()):
                        print(state, "->", item)

            # Start a game
            game = self.game.copy()
            actions = self.start_game(game)
            util += self.cfr(actions, game, 1, 1)

        return util / iterations

    def get_strategy(self):
        """
        Gives the action played by each player based on the game states
        """
        return -1

    def evaluation(self, game):
        reward = sum(game.bets.values())
        game.comm_cards(3)
        winner = game.calculate_winner()

        if winner == self.players[game.player_list.pos]:
            return reward
        return -game.bets[self.players[game.player_list.pos].uuid]

    def cfr(self, actions, game, p1, p2):
        player = game.player_list.pos
        # game.player_list.next_player()

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
